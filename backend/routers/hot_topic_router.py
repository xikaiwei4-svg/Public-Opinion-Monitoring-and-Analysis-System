from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime, timedelta
from db.mysql_config import get_db
from models.mysql_models import HotTopic, Opinion
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from utils.redis_cache import redis_cache, make_cache_key

router = APIRouter(
    prefix="/api/hot-topic",
    tags=["热点分析"],
    responses={404: {"description": "未找到"}},
)

# 平台名称映射（统一管理，避免在循环中重复创建）
PLATFORM_MAP = {
    "weibo": "微博", "wechat": "微信", "zhihu": "知乎",
    "sina": "新浪教育", "eol": "中国教育在线", "jyb": "中国教育新闻网",
    "youth": "中国青年网", "sohu": "搜狐教育", "163": "网易教育",
    "ifeng": "凤凰教育", "qq": "腾讯教育",
    "gx211": "中国高校之窗", "gxzs": "高校招生网",
    "chinakaoyan": "中国考研网", "chinauniversity": "中国大学网",
    "gaoxiao": "高校之窗",
    "gaokao": "高考网", "kaoyanbang": "考研帮", "zikao": "自考网",
    "jyjy": "教育界", "eduzhixin": "教育信息网", "ceiea": "中国教育装备网",
    "bjeea": "北京教育考试院", "shmeea": "上海教育考试院", "eeagd": "广东教育考试院",
    "edu_cn": "中国教育", "ict_edu": "教育信息化", "cscse": "留学服务中心",
    "cetv": "中国教育电视台", "edu_development": "教育发展",
    "jybpaper": "中国教育报", "eol_news": "EOL新闻",
    "eol_gaokao": "EOL高考", "eol_kaoyan": "EOL考研", "eol_teacher": "EOL教师",
}


@router.get("/list")
async def get_hot_topics(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    days: int = Query(7, ge=1, le=30, description="统计过去天数"),
    platform: Optional[str] = Query(None, description="平台筛选"),
    db: Session = Depends(get_db),
):
    """获取热点话题列表 (缓存优先)"""
    cache_key = make_cache_key("cache:hot:list", page=page, size=pageSize, days=days, plat=platform)

    def query_db():
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        query = db.query(HotTopic).filter(HotTopic.last_seen >= start_date, HotTopic.last_seen <= end_date)
        total = query.count()
        hot_topics = query.order_by(HotTopic.mention_count.desc()).offset((page - 1) * pageSize).limit(pageSize).all()
        hot_topics_list = []
        for topic in hot_topics:
            related_count = topic.mention_count
            platform_names = ["微博", "微信", "知乎", "新浪教育", "搜狐教育"]
            hot_topics_list.append({
                "topic": topic.topic, "count": topic.mention_count,
                "sentiment": topic.trend, "platforms": platform_names,
                "time_range": f"最近{days}天", "related_opinions": related_count,
            })
        return {"items": hot_topics_list, "total": total, "page": page, "page_size": pageSize}

    try:
        return redis_cache.cache_aside(cache_key, query_db, expire=60)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误：{str(e)}")


@router.get("/trend")
async def get_hot_topic_trend(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
):
    """获取热点话题趋势 (缓存优先)"""
    cache_key = f"cache:hot:trend:{days}"

    def query_db():
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        topics = db.query(HotTopic).filter(HotTopic.last_seen >= start_date).order_by(HotTopic.mention_count.desc()).limit(10).all()
        return [{
            "id": t.id, "topic": t.topic, "mention_count": t.mention_count,
            "trend": t.trend, "first_seen": t.first_seen.isoformat() if t.first_seen else None,
            "last_seen": t.last_seen.isoformat() if t.last_seen else None,
        } for t in topics]

    try:
        return redis_cache.cache_aside(cache_key, query_db, expire=120)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取热点话题趋势失败: {str(e)}")


@router.get("/compare")
async def get_hot_topic_compare(
    ids: str = Query("", description="话题ID, 逗号分隔"),
    db: Session = Depends(get_db),
):
    try:
        id_list = [int(i.strip()) for i in ids.split(",") if i.strip()]
        topics = db.query(HotTopic).filter(HotTopic.id.in_(id_list)).all() if id_list else []
        result = [{
            "id": t.id,
            "topic": t.topic,
            "mention_count": t.mention_count,
            "trend": t.trend,
            "sentiment_distribution": t.sentiment_distribution,
        } for t in topics]
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取话题比较数据失败: {str(e)}")


@router.get("/{id}")
async def get_hot_topic_detail(
    id: int,
    db: Session = Depends(get_db),
):
    """获取热点话题详情 (缓存优先)"""
    cache_key = f"cache:hot:detail:{id}"

    def query_db():
        hot_topic = db.query(HotTopic).filter(HotTopic.id == id).first()
        if not hot_topic:
            return None
        related_opinions = db.query(Opinion).filter(
            or_(Opinion.content.like(f"%{hot_topic.topic}%"), Opinion.keywords.like(f"%{hot_topic.keyword}%"))
        ).order_by(Opinion.publish_time.desc()).limit(10).all()
        related_list = [{
            "id": o.id, "title": o.title, "content": o.content,
            "source_platform": o.source_platform, "author": o.author,
            "publish_time": o.publish_time.isoformat() if o.publish_time else None,
            "sentiment": o.sentiment, "hot_score": o.hot_score,
        } for o in related_opinions]
        return {
            "code": 200, "message": "查询成功",
            "data": {
                "id": hot_topic.id, "topic": hot_topic.topic, "keyword": hot_topic.keyword,
                "mention_count": hot_topic.mention_count, "sentiment_distribution": hot_topic.sentiment_distribution,
                "trend": hot_topic.trend,
                "first_seen": hot_topic.first_seen.isoformat() if hot_topic.first_seen else None,
                "last_seen": hot_topic.last_seen.isoformat() if hot_topic.last_seen else None,
                "related_opinions": related_list,
            },
        }

    try:
        result = redis_cache.cache_aside(cache_key, query_db, expire=120)
        if result is None:
            raise HTTPException(status_code=404, detail="热点话题不存在")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误：{str(e)}")


@router.get("/analysis/trend")
async def get_hot_topic_trend(
    topic: str,
    days: int = Query(7, ge=1, le=30, description="趋势天数"),
    db: Session = Depends(get_db),
):
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        trend_data = []
        current_date = start_date
        while current_date <= end_date:
            next_day = current_date + timedelta(days=1)

            daily_count = (
                db.query(func.count(Opinion.id))
                .filter(
                    func.or_(
                        Opinion.content.like(f"%{topic}%"),
                        Opinion.keywords.like(f"%{topic}%"),
                    ),
                    Opinion.publish_time >= current_date,
                    Opinion.publish_time < next_day,
                )
                .scalar() or 0
            )

            heat_result = (
                db.query(func.sum(Opinion.hot_score))
                .filter(
                    func.or_(
                        Opinion.content.like(f"%{topic}%"),
                        Opinion.keywords.like(f"%{topic}%"),
                    ),
                    Opinion.publish_time >= current_date,
                    Opinion.publish_time < next_day,
                )
                .scalar() or 0
            )

            avg_heat = heat_result / daily_count if daily_count > 0 else 0
            trend_data.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "count": daily_count,
                "avg_heat": round(avg_heat, 2),
            })
            current_date = next_day

        return {
            "code": 200,
            "data": {
                "topic": topic,
                "trend_data": trend_data,
                "time_range": f"{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}",
            },
            "message": "查询成功",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误：{str(e)}")


@router.get("/analysis/comparison")
async def compare_hot_topics(
    topics: List[str] = Query(..., description="要比较的热点话题列表，最多5个"),
    days: int = Query(7, ge=1, le=30, description="比较天数"),
    db: Session = Depends(get_db),
):
    try:
        if len(topics) > 5:
            raise HTTPException(status_code=400, detail="最多只能比较5个热点话题")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        comparison_data = []
        for topic in topics:
            total_count = (
                db.query(func.count(Opinion.id))
                .filter(
                    func.or_(
                        Opinion.content.like(f"%{topic}%"),
                        Opinion.keywords.like(f"%{topic}%"),
                    ),
                    Opinion.publish_time >= start_date,
                    Opinion.publish_time <= end_date,
                )
                .scalar() or 0
            )

            result = (
                db.query(
                    func.avg(Opinion.hot_score).label("avg_heat"),
                    func.avg(Opinion.sentiment_score).label("avg_sentiment"),
                )
                .filter(
                    func.or_(
                        Opinion.content.like(f"%{topic}%"),
                        Opinion.keywords.like(f"%{topic}%"),
                    ),
                    Opinion.publish_time >= start_date,
                    Opinion.publish_time <= end_date,
                )
                .first()
            )

            avg_heat = round(result.avg_heat or 0, 2)
            avg_sentiment = round(result.avg_sentiment or 0, 2)

            comparison_data.append({
                "topic": topic,
                "total_count": total_count,
                "avg_heat": avg_heat,
                "avg_sentiment": avg_sentiment,
                "time_range": f"{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}",
            })

        return {"code": 200, "data": comparison_data, "message": "比较成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误：{str(e)}")