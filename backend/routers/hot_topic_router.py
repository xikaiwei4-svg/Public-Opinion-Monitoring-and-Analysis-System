from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from db.mongo_client import hot_topics_collection, opinion_collection
from models.opinion_model import HotTopicModel, SourcePlatform

# 创建路由实例
router = APIRouter(
    prefix="/api/热点",
    tags=["热点分析"],
    responses={404: {"description": "未找到"}},
)

@router.get("/list", response_model=dict)
async def get_hot_topics(
    days: int = Query(7, ge=1, le=30, description="统计过去天数"),
    limit: int = Query(10, ge=1, le=50, description="返回热点数量"),
    platform: Optional[SourcePlatform] = Query(None, description="平台筛选"),
    min_heat_score: float = Query(0.0, ge=0.0, le=100.0, description="最低热度分数")
):
    """
    获取热点话题列表
    """
    try:
        # 计算时间范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 构建查询条件
        query = {
            "start_time": {"$gte": start_date},
            "end_time": {"$lte": end_date},
            "heat_score": {"$gte": min_heat_score}
        }
        
        if platform:
            query["platforms"] = platform
        
        # 查询热点话题并按热度降序排序
        cursor = hot_topics_collection.find(query)
        cursor = cursor.sort("heat_score", -1).limit(limit)
        hot_topics = await cursor.to_list(length=limit)
        
        return {
            "code": 200,
            "data": {
                "items": hot_topics,
                "total": len(hot_topics),
                "time_range": f"{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}"
            },
            "message": "查询成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误：{str(e)}")

@router.get("/{id}", response_model=dict)
async def get_hot_topic_detail(id: str):
    """
    获取热点话题的详细信息
    """
    try:
        # 查询热点话题
        hot_topic = await hot_topics_collection.find_one({"id": id})
        
        if not hot_topic:
            raise HTTPException(status_code=404, detail="热点话题不存在")
        
        # 获取相关舆情数据（最新10条）
        related_opinions = await opinion_collection.find({
            "$or": [
                {"content": {"$regex": hot_topic["topic"], "$options": "i"}},
                {"keywords": {"$in": hot_topic["keywords"]}}
            ]
        }).sort("publish_time", -1).limit(10).to_list(length=10)
        
        # 添加相关舆情信息
        hot_topic["related_opinions"] = related_opinions
        
        return {
            "code": 200,
            "data": hot_topic,
            "message": "查询成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误：{str(e)}")

@router.get("/analysis/trend", response_model=dict)
async def get_hot_topic_trend(
    topic: str,
    days: int = Query(7, ge=1, le=30, description="趋势天数")
):
    """
    获取特定热点话题的趋势数据
    """
    try:
        # 计算时间范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 构建每天的查询条件
        trend_data = []
        current_date = start_date
        
        while current_date <= end_date:
            next_day = current_date + timedelta(days=1)
            
            # 查询当天该话题的舆情数量
            daily_count = await opinion_collection.count_documents({
                "$or": [
                    {"content": {"$regex": topic, "$options": "i"}},
                    {"keywords": {"$regex": topic, "$options": "i"}}
                ],
                "publish_time": {"$gte": current_date, "$lt": next_day}
            })
            
            # 查询当天该话题的热度总和
            pipeline = [
                {"$match": {
                    "$or": [
                        {"content": {"$regex": topic, "$options": "i"}},
                        {"keywords": {"$regex": topic, "$options": "i"}}
                    ],
                    "publish_time": {"$gte": current_date, "$lt": next_day}
                }},
                {"$group": {"_id": None, "total_heat": {"$sum": "$heat_score"}}}
            ]
            
            heat_result = await opinion_collection.aggregate(pipeline).to_list(length=1)
            avg_heat = heat_result[0]["total_heat"] / daily_count if daily_count > 0 else 0
            
            # 添加当天数据
            trend_data.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "count": daily_count,
                "avg_heat": round(avg_heat, 2)
            })
            
            current_date = next_day
        
        return {
            "code": 200,
            "data": {
                "topic": topic,
                "trend_data": trend_data,
                "time_range": f"{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}"
            },
            "message": "查询成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误：{str(e)}")

@router.get("/analysis/comparison", response_model=dict)
async def compare_hot_topics(
    topics: List[str] = Query(..., description="要比较的热点话题列表，最多5个"),
    days: int = Query(7, ge=1, le=30, description="比较天数")
):
    """
    比较多个热点话题的数据
    """
    try:
        # 限制话题数量
        if len(topics) > 5:
            raise HTTPException(status_code=400, detail="最多只能比较5个热点话题")
        
        # 计算时间范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        comparison_data = []
        
        for topic in topics:
            # 查询该话题的总舆情数量
            total_count = await opinion_collection.count_documents({
                "$or": [
                    {"content": {"$regex": topic, "$options": "i"}},
                    {"keywords": {"$regex": topic, "$options": "i"}}
                ],
                "publish_time": {"$gte": start_date, "$lte": end_date}
            })
            
            # 查询该话题的平均热度
            pipeline = [
                {"$match": {
                    "$or": [
                        {"content": {"$regex": topic, "$options": "i"}},
                        {"keywords": {"$regex": topic, "$options": "i"}}
                    ],
                    "publish_time": {"$gte": start_date, "$lte": end_date}
                }},
                {"$group": {"_id": None, "avg_heat": {"$avg": "$heat_score"}, "avg_sentiment": {"$avg": "$sentiment"}}}
            ]
            
            result = await opinion_collection.aggregate(pipeline).to_list(length=1)
            avg_heat = round(result[0]["avg_heat"], 2) if result and "avg_heat" in result[0] else 0
            avg_sentiment = round(result[0]["avg_sentiment"], 2) if result and "avg_sentiment" in result[0] else 0
            
            # 添加比较数据
            comparison_data.append({
                "topic": topic,
                "total_count": total_count,
                "avg_heat": avg_heat,
                "avg_sentiment": avg_sentiment,
                "time_range": f"{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}"
            })
        
        return {
            "code": 200,
            "data": comparison_data,
            "message": "比较成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误：{str(e)}")