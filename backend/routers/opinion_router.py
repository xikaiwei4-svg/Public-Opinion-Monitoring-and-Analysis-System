from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime
from pymongo import ReturnDocument
from ..db.mongo_client import opinion_collection
from ..models.opinion_model import OpinionModel, SentimentType, SourcePlatform

# 创建路由实例
router = APIRouter(
    prefix="/api/舆情",
    tags=["舆情数据"],
    responses={404: {"description": "未找到"}},
)

@router.get("/list", response_model=dict)
async def get_舆情_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    source: Optional[SourcePlatform] = Query(None, description="来源平台"),
    sentiment_type: Optional[SentimentType] = Query(None, description="情感类型"),
    start_time: Optional[str] = Query(None, description="开始时间，格式：YYYY-MM-DD HH:MM:SS"),
    end_time: Optional[str] = Query(None, description="结束时间，格式：YYYY-MM-DD HH:MM:SS"),
    is_sensitive: Optional[bool] = Query(None, description="是否敏感内容")
):
    """
    获取舆情数据列表，支持分页、关键词搜索、多条件筛选
    """
    try:
        # 构建查询条件
        query = {}
        
        if keyword:
            query["$or"] = [
                {"content": {"$regex": keyword, "$options": "i"}},
                {"keywords": {"$regex": keyword, "$options": "i"}}
            ]
        
        if source:
            query["source_platform"] = source
        
        if sentiment_type:
            query["sentiment_type"] = sentiment_type
        
        if start_time:
            try:
                start_datetime = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                query["publish_time"] = {"$gte": start_datetime}
            except ValueError:
                raise HTTPException(status_code=400, detail="开始时间格式错误，应为YYYY-MM-DD HH:MM:SS")
        
        if end_time:
            try:
                end_datetime = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
                if "publish_time" in query:
                    query["publish_time"]["$lte"] = end_datetime
                else:
                    query["publish_time"] = {"$lte": end_datetime}
            except ValueError:
                raise HTTPException(status_code=400, detail="结束时间格式错误，应为YYYY-MM-DD HH:MM:SS")
        
        if is_sensitive is not None:
            query["is_sensitive"] = is_sensitive
        
        # 计算分页
        total = await opinion_collection.count_documents(query)
        skip = (page - 1) * page_size
        
        # 查询数据并按发布时间降序排序
        cursor = opinion_collection.find(query)
        cursor = cursor.sort("publish_time", -1).skip(skip).limit(page_size)
        items = await cursor.to_list(length=page_size)
        
        return {
            "code": 200,
            "data": {
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            },
            "message": "查询成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误：{str(e)}")

@router.get("/{id}", response_model=dict)
async def get_舆情_detail(id: str):
    """
    获取单条舆情的详细信息
    """
    try:
        # 查询单条数据
        opinion = await opinion_collection.find_one({"id": id})
        
        if not opinion:
            raise HTTPException(status_code=404, detail="舆情数据不存在")
        
        return {
            "code": 200,
            "data": opinion,
            "message": "查询成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误：{str(e)}")

@router.get("/statistics/summary", response_model=dict)
async def get_舆情_statistics(
    days: int = Query(7, ge=1, le=30, description="统计天数"),
    source: Optional[SourcePlatform] = Query(None, description="来源平台")
):
    """
    获取舆情统计概览数据
    """
    try:
        # 计算起始日期
        end_date = datetime.now()
        start_date = datetime(end_date.year, end_date.month, end_date.day - days)
        
        # 构建查询条件
        query = {"publish_time": {"$gte": start_date, "$lte": end_date}}
        
        if source:
            query["source_platform"] = source
        
        # 统计总数
        total_count = await opinion_collection.count_documents(query)
        
        # 按情感类型统计
        positive_count = await opinion_collection.count_documents(
            {**query, "sentiment_type": SentimentType.POSITIVE}
        )
        negative_count = await opinion_collection.count_documents(
            {**query, "sentiment_type": SentimentType.NEGATIVE}
        )
        neutral_count = await opinion_collection.count_documents(
            {**query, "sentiment_type": SentimentType.NEUTRAL}
        )
        
        # 敏感内容统计
        sensitive_count = await opinion_collection.count_documents(
            {**query, "is_sensitive": True}
        )
        
        # 按平台统计（如果没有指定平台）
        platform_stats = []
        if not source:
            for platform in SourcePlatform:
                platform_count = await opinion_collection.count_documents(
                    {**query, "source_platform": platform}
                )
                if platform_count > 0:
                    platform_stats.append({
                        "platform": platform,
                        "count": platform_count,
                        "percentage": round((platform_count / total_count) * 100, 2) if total_count > 0 else 0
                    })
        
        return {
            "code": 200,
            "data": {
                "time_range": f"{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}",
                "total_count": total_count,
                "sentiment_distribution": {
                    "positive": positive_count,
                    "negative": negative_count,
                    "neutral": neutral_count
                },
                "sensitive_content": {
                    "count": sensitive_count,
                    "percentage": round((sensitive_count / total_count) * 100, 2) if total_count > 0 else 0
                },
                "platform_distribution": platform_stats
            },
            "message": "统计成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误：{str(e)}")

@router.delete("/{id}", response_model=dict)
async def delete_舆情(id: str):
    """
    删除单条舆情数据
    """
    try:
        result = await opinion_collection.delete_one({"id": id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="舆情数据不存在")
        
        return {
            "code": 200,
            "data": None,
            "message": "删除成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误：{str(e)}")