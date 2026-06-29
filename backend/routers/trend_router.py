from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime, timedelta
import pandas as pd
import random
from db.mysql_config import get_db
from models.mysql_models import Opinion, TrendData
from sqlalchemy.orm import Session
from sqlalchemy import func
from utils.redis_cache import redis_cache, make_cache_key

# 创建路由实例
router = APIRouter(
    prefix="/api/trend",
    tags=["趋势分析"],
    responses={404: {"description": "未找到"}},
)

# 生成模拟趋势数据
def generate_mock_trend_data(start_date: datetime, end_date: datetime):
    trend_data = []
    current_date = start_date
    
    while current_date <= end_date:
        base_count = random.randint(20, 100)
        positive_ratio = random.uniform(0.3, 0.6)
        negative_ratio = random.uniform(0.1, 0.3)
        neutral_ratio = 1 - positive_ratio - negative_ratio
        
        trend_data.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "positive_count": int(base_count * positive_ratio),
            "negative_count": int(base_count * negative_ratio),
            "neutral_count": int(base_count * neutral_ratio),
            "total_count": base_count
        })
        current_date += timedelta(days=1)
    
    return trend_data

# 生成模拟平台分布数据
def generate_mock_platform_data():
    platforms = [
        ("weibo", "微博"),
        ("wechat", "微信"), 
        ("zhihu", "知乎"),
        ("sina", "新浪"),
        ("eol", "中国教育在线"),
        ("jyb", "教育部")
    ]
    
    distribution_data = []
    total_count = random.randint(200, 500)
    remaining = total_count
    
    for i, (key, name) in enumerate(platforms):
        if i == len(platforms) - 1:
            count = remaining
        else:
            count = random.randint(remaining // (len(platforms) - i + 1), remaining // 2)
        remaining -= count
        
        percentage = round((count / total_count) * 100, 2) if total_count > 0 else 0
        
        if count > 0 and percentage >= 1:
            distribution_data.append({
                "platform": key,
                "count": count,
                "percentage": percentage
            })
    
    return distribution_data

@router.get("/analysis", response_model=dict)
async def get_trend_analysis(
    keyword: Optional[str] = Query(None, description="分析关键词"),
    start_date: str = Query(..., description="开始日期，格式：YYYY-MM-DD"),
    end_date: str = Query(..., description="结束日期，格式：YYYY-MM-DD"),
    frequency: str = Query("daily", description="时间频率：daily, weekly, monthly"),
    source: Optional[str] = Query(None, description="来源平台"),
    sentiment_type: Optional[str] = Query(None, description="情感类型"),
    db: Session = Depends(get_db)
):
    """获取舆情趋势分析数据 (缓存优先)"""
    cache_key = make_cache_key("cache:trend:analysis", start=start_date, end=end_date,
                                kw=keyword, src=source, sent=sentiment_type, freq=frequency)

    def query_db():
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
        query = db.query(func.date(Opinion.publish_time).label('date'), Opinion.sentiment,
                         func.count(Opinion.id).label('count')).filter(
            Opinion.publish_time >= start_datetime, Opinion.publish_time <= end_datetime)
        if keyword:
            query = query.filter(func.or_(Opinion.content.like(f"%{keyword}%"), Opinion.keywords.like(f"%{keyword}%")))
        if source:
            query = query.filter(Opinion.source_platform == source)
        if sentiment_type:
            query = query.filter(Opinion.sentiment == sentiment_type)
        results = query.group_by(func.date(Opinion.publish_time), Opinion.sentiment).all()

        df = pd.DataFrame([{'date': str(r.date), 'sentiment': r.sentiment, 'count': r.count} for r in results])
        if df.empty:
            trend_data = generate_mock_trend_data(start_datetime, end_datetime)
        else:
            trend_data = []
            for date in sorted(df['date'].unique()):
                pos = int(df[(df['date'] == date) & (df['sentiment'] == 'positive')]['count'].sum())
                neg = int(df[(df['date'] == date) & (df['sentiment'] == 'negative')]['count'].sum())
                neu = int(df[(df['date'] == date) & (df['sentiment'] == 'neutral')]['count'].sum())
                trend_data.append({"date": date, "positive_count": pos, "negative_count": neg,
                                   "neutral_count": neu, "total_count": pos + neg + neu})

        return {"code": 200, "data": {"trend_data": trend_data, "keyword": keyword,
                "time_range": f"{start_date} 至 {end_date}",
                "total_count": sum(i["total_count"] for i in trend_data)}, "message": "分析成功"}

    try:
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
        if start_datetime > end_datetime:
            raise HTTPException(status_code=400, detail="开始日期不能晚于结束日期")
        return redis_cache.cache_aside(cache_key, query_db, expire=180)
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式错误，应为YYYY-MM-DD")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误：{str(e)}")

@router.get("/analysis/platform", response_model=dict)
async def get_platform_distribution(
    start_date: str = Query(..., description="开始日期，格式：YYYY-MM-DD"),
    end_date: str = Query(..., description="结束日期，格式：YYYY-MM-DD"),
    keyword: Optional[str] = Query(None, description="分析关键词")
):
    """获取各平台舆情分布数据 (缓存优先)"""
    cache_key = make_cache_key("cache:trend:platform", start=start_date, end=end_date, kw=keyword)

    def query_db():
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        db_session = next(get_db())
        try:
            query = db_session.query(Opinion.source_platform, func.count(Opinion.id).label('count')).filter(
                Opinion.publish_time >= start_dt, Opinion.publish_time <= end_dt)
            if keyword:
                query = query.filter(func.or_(Opinion.content.like(f"%{keyword}%"), Opinion.keywords.like(f"%{keyword}%")))
            results = query.group_by(Opinion.source_platform).all()
            total_count = sum(r.count for r in results)
            distribution_data = []
            for r in results:
                pct = round((r.count / total_count) * 100, 2) if total_count > 0 else 0
                if r.count > 0 and pct >= 1:
                    distribution_data.append({"platform": r.source_platform, "count": r.count, "percentage": pct})
            if not distribution_data:
                distribution_data = generate_mock_platform_data()
            distribution_data.sort(key=lambda x: x["count"], reverse=True)
            return {"code": 200, "data": {"distribution_data": distribution_data,
                    "total_count": sum(i["count"] for i in distribution_data),
                    "keyword": keyword, "time_range": f"{start_date} 至 {end_date}"}, "message": "平台分布分析成功"}
        finally:
            db_session.close()

    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        if start_dt > end_dt:
            raise HTTPException(status_code=400, detail="开始日期不能晚于结束日期")
        return redis_cache.cache_aside(cache_key, query_db, expire=180)
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式错误，应为YYYY-MM-DD")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误：{str(e)}")


@router.get("/opinion")
async def get_trend_opinion(
    days: str = "7",
    platform: Optional[str] = None,
    db: Session = Depends(get_db),
):
    try:
        days_int = int(days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_int - 1)

        trend_data = (
            db.query(TrendData)
            .filter(TrendData.date >= start_date, TrendData.date <= end_date)
        )
        if platform:
            trend_data = trend_data.filter(TrendData.platform == platform)

        trend_data = trend_data.order_by(TrendData.date).all()

        result = []
        for data in trend_data:
            result.append({
                "date": data.date.strftime("%Y-%m-%d"),
                "count": data.total_count,
                "platform": platform or "all",
            })

        # 如果没有数据，生成模拟数据
        if not result:
            for i in range(days_int):
                date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
                result.append({"date": date, "count": random.randint(20, 100), "platform": platform or "all"})

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取趋势数据失败: {str(e)}")


@router.get("/sentiment")
async def get_trend_sentiment(
    days: str = "7",
    platform: Optional[str] = None,
    db: Session = Depends(get_db),
):
    try:
        days_int = int(days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_int - 1)

        trend_data = (
            db.query(TrendData)
            .filter(TrendData.date >= start_date, TrendData.date <= end_date)
        )
        if platform:
            trend_data = trend_data.filter(TrendData.platform == platform)

        trend_data = trend_data.order_by(TrendData.date).all()

        result = []
        for data in trend_data:
            result.append({
                "date": data.date.strftime("%Y-%m-%d"),
                "positive": data.positive_count,
                "negative": data.negative_count,
                "neutral": data.neutral_count,
                "platform": platform or "all",
            })

        # 如果没有数据，生成模拟数据
        if not result:
            for i in range(days_int):
                date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
                base = random.randint(20, 100)
                result.append({
                    "date": date, 
                    "positive": int(base * 0.5),
                    "negative": int(base * 0.2), 
                    "neutral": int(base * 0.3),
                    "platform": platform or "all"
                })

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取情感趋势数据失败: {str(e)}")


@router.get("/platform-distribution")
async def get_trend_platform_distribution(
    days: str = "7",
    db: Session = Depends(get_db),
):
    try:
        days_int = int(days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_int - 1)

        platform_stats = (
            db.query(Opinion.source_platform, func.count(Opinion.id).label("count"))
            .filter(Opinion.publish_time >= start_date, Opinion.publish_time <= end_date)
            .group_by(Opinion.source_platform)
            .all()
        )

        total_count = sum(stat.count for stat in platform_stats)

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
        result = []
        for platform, count in platform_stats:
            percentage = (count / total_count * 100) if total_count > 0 else 0
            result.append({
                "platform": PLATFORM_MAP.get(platform, "其他"),
                "count": count,
                "percentage": round(percentage, 1),
                "time_range": f"最近{days}天",
            })
        
        # 如果没有数据，返回模拟数据
        if not result:
            mock_data = generate_mock_platform_data()
            result = [
                {
                    "platform": PLATFORM_MAP.get(item["platform"], item["platform"]),
                    "count": item["count"],
                    "percentage": item["percentage"],
                    "time_range": f"最近{days}天"
                }
                for item in mock_data
            ]

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取平台分布数据失败: {str(e)}")
