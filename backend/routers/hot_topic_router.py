from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from db.mysql_config import get_db
from models.mysql_models import HotTopic, Opinion
from sqlalchemy.orm import Session
from sqlalchemy import func

# 创建路由实例
router = APIRouter(
    prefix="/api/hot-topic",
    tags=["热点分析"],
    responses={404: {"description": "未找到"}},
)

@router.get("/list", response_model=dict)
async def get_hot_topics(
    days: int = Query(7, ge=1, le=30, description="统计过去天数"),
    limit: int = Query(10, ge=1, le=50, description="返回热点数量"),
    platform: Optional[str] = Query(None, description="平台筛选"),
    min_heat_score: float = Query(0.0, ge=0.0, le=100.0, description="最低热度分数")
):
    """
    获取热点话题列表
    """
    try:
        # 计算时间范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 获取数据库会话
        db = next(get_db())
        
        # 构建查询
        query = db.query(HotTopic).filter(
            HotTopic.last_seen >= start_date,
            HotTopic.last_seen <= end_date
        )
        
        # 执行查询并按提及次数降序排序
        hot_topics = query.order_by(HotTopic.mention_count.desc()).limit(limit).all()
        
        # 转换为字典列表
        hot_topics_list = []
        for topic in hot_topics:
            hot_topics_list.append({
                "id": topic.id,
                "topic": topic.topic,
                "keyword": topic.keyword,
                "mention_count": topic.mention_count,
                "trend": topic.trend,
                "first_seen": topic.first_seen.isoformat() if topic.first_seen else None,
                "last_seen": topic.last_seen.isoformat() if topic.last_seen else None
            })
        
        return {
            "code": 200,
            "data": {
                "items": hot_topics_list,
                "total": len(hot_topics_list),
                "time_range": f"{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}"
            },
            "message": "查询成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误：{str(e)}")

@router.get("/{id}", response_model=dict)
async def get_hot_topic_detail(id: int):
    """
    获取热点话题的详细信息
    """
    try:
        # 获取数据库会话
        db = next(get_db())
        
        # 查询热点话题
        hot_topic = db.query(HotTopic).filter(HotTopic.id == id).first()
        
        if not hot_topic:
            raise HTTPException(status_code=404, detail="热点话题不存在")
        
        # 获取相关舆情数据（最新10条）
        related_opinions = db.query(Opinion).filter(
            func.or_(
                Opinion.content.like(f"%{hot_topic.topic}%"),
                Opinion.keywords.like(f"%{hot_topic.keyword}%")
            )
        ).order_by(Opinion.publish_time.desc()).limit(10).all()
        
        # 转换为字典列表
        related_opinions_list = []
        for opinion in related_opinions:
            related_opinions_list.append({
                "id": opinion.id,
                "title": opinion.title,
                "content": opinion.content,
                "source_platform": opinion.source_platform,
                "author": opinion.author,
                "publish_time": opinion.publish_time.isoformat() if opinion.publish_time else None,
                "sentiment": opinion.sentiment,
                "hot_score": opinion.hot_score
            })
        
        # 构建热点话题详情
        hot_topic_detail = {
            "id": hot_topic.id,
            "topic": hot_topic.topic,
            "keyword": hot_topic.keyword,
            "mention_count": hot_topic.mention_count,
            "sentiment_distribution": hot_topic.sentiment_distribution,
            "trend": hot_topic.trend,
            "first_seen": hot_topic.first_seen.isoformat() if hot_topic.first_seen else None,
            "last_seen": hot_topic.last_seen.isoformat() if hot_topic.last_seen else None,
            "related_opinions": related_opinions_list
        }
        
        return {
            "code": 200,
            "data": hot_topic_detail,
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
        
        # 获取数据库会话
        db = next(get_db())
        
        # 构建每天的查询条件
        trend_data = []
        current_date = start_date
        
        while current_date <= end_date:
            next_day = current_date + timedelta(days=1)
            
            # 查询当天该话题的舆情数量
            daily_count = db.query(func.count(Opinion.id)).filter(
                func.or_(
                    Opinion.content.like(f"%{topic}%"),
                    Opinion.keywords.like(f"%{topic}%")
                ),
                Opinion.publish_time >= current_date,
                Opinion.publish_time < next_day
            ).scalar() or 0
            
            # 查询当天该话题的热度总和
            heat_result = db.query(func.sum(Opinion.hot_score)).filter(
                func.or_(
                    Opinion.content.like(f"%{topic}%"),
                    Opinion.keywords.like(f"%{topic}%")
                ),
                Opinion.publish_time >= current_date,
                Opinion.publish_time < next_day
            ).scalar() or 0
            
            avg_heat = heat_result / daily_count if daily_count > 0 else 0
            
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
        
        # 获取数据库会话
        db = next(get_db())
        
        comparison_data = []
        
        for topic in topics:
            # 查询该话题的总舆情数量
            total_count = db.query(func.count(Opinion.id)).filter(
                func.or_(
                    Opinion.content.like(f"%{topic}%"),
                    Opinion.keywords.like(f"%{topic}%")
                ),
                Opinion.publish_time >= start_date,
                Opinion.publish_time <= end_date
            ).scalar() or 0
            
            # 查询该话题的平均热度和平均情感
            result = db.query(
                func.avg(Opinion.hot_score).label('avg_heat'),
                func.avg(Opinion.sentiment_score).label('avg_sentiment')
            ).filter(
                func.or_(
                    Opinion.content.like(f"%{topic}%"),
                    Opinion.keywords.like(f"%{topic}%")
                ),
                Opinion.publish_time >= start_date,
                Opinion.publish_time <= end_date
            ).first()
            
            avg_heat = round(result.avg_heat or 0, 2)
            avg_sentiment = round(result.avg_sentiment or 0, 2)
            
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