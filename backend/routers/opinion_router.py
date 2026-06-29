from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session

from db.mysql_config import get_db
from models.mysql_models import Opinion, HotTopic
from utils.redis_cache import redis_cache, make_cache_key

router = APIRouter(prefix="/api/opinion", tags=["舆情数据"])

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

CACHE_TTL_STATS = 120   # 统计数据缓存2分钟
CACHE_TTL_LIST = 60     # 列表数据缓存1分钟


@router.get("/statistics")
async def get_opinion_statistics(
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """获取舆情统计数据 (缓存优先)"""
    cache_key = make_cache_key("cache:opinion:stats", start_time=start_time, end_time=end_time)

    def query_db():
        total_count = db.query(Opinion).count()
        hot_topics_count = db.query(HotTopic).count()
        sentiment_stats = db.query(Opinion.sentiment, func.count(Opinion.id).label("count")).group_by(Opinion.sentiment).all()
        sentiment_distribution = {"positive": 0, "negative": 0, "neutral": 0}
        for sentiment, count in sentiment_stats:
            if sentiment in sentiment_distribution:
                sentiment_distribution[sentiment] = count
        platform_stats = db.query(Opinion.source_platform, func.count(Opinion.id).label("count")).group_by(Opinion.source_platform).all()
        platform_list = []
        for platform, count in platform_stats:
            pct = (count / total_count * 100) if total_count > 0 else 0
            platform_list.append({"platform": PLATFORM_MAP.get(platform or "", "其他"), "percentage": round(pct, 1)})
        platform_list.sort(key=lambda x: x["percentage"], reverse=True)
        top = platform_list[:6]
        rest = sum(p["percentage"] for p in platform_list[6:])
        if rest > 0 and len(platform_list) > 6:
            top.append({"platform": "其他", "percentage": round(rest, 1)})
        views_count = db.query(func.sum(Opinion.read_count)).scalar() or 0
        return {
            "total_count": total_count, "hot_topics_count": hot_topics_count,
            "views_count": views_count, "sentiment_distribution": sentiment_distribution,
            "platform_distribution": top, "time_range": "最近7天",
        }

    try:
        return redis_cache.cache_aside(cache_key, query_db, expire=CACHE_TTL_STATS)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")


@router.get("/list")
async def get_opinion_list(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = None,
    source: Optional[str] = None,
    sentiment_type: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    is_sensitive: Optional[bool] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """获取舆情列表 (缓存优先)"""
    cache_key = make_cache_key("cache:opinion:list", page=page, size=pageSize, kw=keyword,
                                src=source, sent=sentiment_type, sensitive=is_sensitive)

    def query_db():
        query = db.query(Opinion)
        if keyword:
            query = query.filter(Opinion.title.contains(keyword) | Opinion.content.contains(keyword))
        if source:
            source_map = {"微博": "weibo", "微信": "wechat", "知乎": "zhihu", "其他": "other"}
            query = query.filter(Opinion.source_platform == source_map.get(source, source))
        if sentiment_type:
            query = query.filter(Opinion.sentiment == sentiment_type)
        if is_sensitive is not None:
            query = query.filter(Opinion.is_hot == is_sensitive)
        total = query.count()
        opinions = query.offset((page - 1) * pageSize).limit(pageSize).all()
        items = []
        for o in opinions:
            plat_name = PLATFORM_MAP.get(o.source_platform, o.source_platform or "其他")
            items.append({
                "id": o.id, "content": o.content or o.title,
                "source": o.author or "匿名用户", "source_platform": plat_name,
                "publish_time": o.publish_time.isoformat() if o.publish_time else None,
                "crawl_time": o.crawl_time.isoformat() if o.crawl_time else None,
                "sentiment": 0, "sentiment_type": o.sentiment or "neutral",
                "keywords": o.keywords.split(",") if o.keywords else [],
                "url": o.source_url, "views": o.read_count or 0, "likes": o.like_count or 0,
                "comments": o.comment_count or 0, "shares": o.share_count or 0,
                "heat_score": o.hot_score or 0, "is_sensitive": bool(o.is_hot),
                "sensitive_level": 1 if o.is_hot else 0,
            })
        return {"items": items, "total": total, "page": page, "page_size": pageSize}

    try:
        return redis_cache.cache_aside(cache_key, query_db, expire=CACHE_TTL_LIST)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取舆情列表失败: {str(e)}")


@router.delete("/{opinion_id}")
async def delete_opinion(opinion_id: int, db: Session = Depends(get_db)):  # 演示环境未强制鉴权
    """删除舆情"""
    opinion = db.query(Opinion).filter(Opinion.id == opinion_id).first()
    if not opinion:
        raise HTTPException(status_code=404, detail="舆情不存在")
    db.delete(opinion)
    db.commit()
    redis_cache.delete_pattern("cache:opinion:*")
    return {"message": "删除成功", "id": opinion_id}


@router.get("/{opinion_id}")
async def get_opinion_detail(opinion_id: int, db: Session = Depends(get_db)):
    """获取舆情详情 (缓存优先)"""
    cache_key = f"cache:opinion:detail:{opinion_id}"

    def query_db():
        o = db.query(Opinion).filter(Opinion.id == opinion_id).first()
        if not o:
            return None
        return o.to_dict()

    try:
        result = redis_cache.cache_aside(cache_key, query_db, expire=300)
        if result is None:
            raise HTTPException(status_code=404, detail="舆情数据未找到")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取舆情详情失败: {str(e)}")
