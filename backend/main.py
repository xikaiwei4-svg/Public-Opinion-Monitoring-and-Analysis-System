# -*- coding: utf-8 -*-
"""
校园舆情检测与热点话题分析系统后端
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime, timedelta
import uvicorn
import json
import logging

from auth.auth_router import auth_router
# from routers.database_router import router as database_router  # MongoDB路由
from routers.mysql_database_router import router as database_router  # MySQL路由
from routers.sentiment_router import router as sentiment_router  # 情感分析路由
from routers.cnn_sentiment_router import router as cnn_sentiment_router  # CNN情感分析路由
from routers.hot_topic_router import router as hot_topic_router  # 热点话题路由
from routers.trend_router import router as trend_router  # 趋势分析路由

# 导入工具模块
from utils.redis_cache import redis_cache
from utils.db_utils import db_utils
from db.mysql_config import get_db
from models.mysql_models import Opinion, HotTopic, TrendData
from sqlalchemy import func

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 自定义JSONResponse，确保中文正确显示
class CustomJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return json.dumps(content, ensure_ascii=False, allow_nan=False, indent=None, separators=(",", ":")).encode("utf-8")

app = FastAPI(
    title="校园舆情检测与热点话题分析系统",
    description="用于实时监控、分析和可视化校园相关舆情信息的平台",
    version="2.0.0",
    default_response_class=CustomJSONResponse
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(database_router)
app.include_router(sentiment_router)
app.include_router(cnn_sentiment_router)
app.include_router(hot_topic_router)
app.include_router(trend_router)

# 初始化缓存
@app.on_event("startup")
async def startup_event():
    """启动事件"""
    logger.info("系统启动中...")
    # 预热缓存
    try:
        # 使用模拟数据，不依赖数据库
        mock_hot_topics = [
            {
                "topic": "校园食堂改革",
                "count": 156,
                "sentiment": "neutral",
                "platforms": ["微博", "知乎"],
                "time_range": "最近7天"
            },
            {
                "topic": "期末考试安排",
                "count": 98,
                "sentiment": "negative",
                "platforms": ["微信", "QQ"],
                "time_range": "最近7天"
            }
        ]
        redis_cache.set("hot_topics:7days", mock_hot_topics, expire=3600)
        logger.info("缓存预热完成（使用模拟数据）")
    except Exception as e:
        logger.warning(f"缓存预热失败: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """关闭事件"""
    logger.info("系统关闭中...")

@app.get("/api/ping", tags=["基础接口"])
async def ping():
    return {"status": "ok", "message": "服务运行正常", "timestamp": datetime.now().isoformat()}

@app.get("/api/auth/me", tags=["认证"])
async def get_current_user():
    """获取当前用户信息（模拟数据）"""
    mock_user = {
        "id": "1",
        "username": "admin",
        "email": "admin@example.com",
        "name": "管理员",
        "avatar": "/api/avatar/admin.png",
        "role": "admin",
        "department": "管理部门",
        "position": "超级管理员",
        "phone_number": "13800138000",
        "status": "active",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "last_login_at": datetime.now().isoformat(),
        "permissions": ["read", "write", "edit", "delete", "admin"]
    }
    return mock_user

@app.get("/api/opinion/statistics", tags=["统计数据"])
@app.get("/api/opinions/statistics", tags=["统计数据"])
async def get_opinion_statistics(
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    db = Depends(get_db)
):
    try:
        # 从MySQL数据库获取真实数据
        total_count = db.query(Opinion).count()
        hot_topics_count = db.query(HotTopic).count()
        
        # 获取情感分布
        sentiment_stats = db.query(
            Opinion.sentiment,
            func.count(Opinion.id).label('count')
        ).group_by(Opinion.sentiment).all()
        
        sentiment_distribution = {
            "positive": 0,
            "negative": 0,
            "neutral": 0
        }
        
        for sentiment, count in sentiment_stats:
            if sentiment in sentiment_distribution:
                sentiment_distribution[sentiment] = count
        
        # 获取平台分布
        platform_stats = db.query(
            Opinion.source_platform,
            func.count(Opinion.id).label('count')
        ).group_by(Opinion.source_platform).all()
        
        platform_distribution = []
        for platform, count in platform_stats:
            percentage = (count / total_count * 100) if total_count > 0 else 0
            platform_name = platform
            if platform == "weibo":
                platform_name = "微博"
            elif platform == "wechat":
                platform_name = "微信"
            elif platform == "zhihu":
                platform_name = "知乎"
            else:
                platform_name = "其他"
                
            platform_distribution.append({
                "platform": platform_name,
                "count": count,
                "percentage": round(percentage, 1)
            })
        
        # 获取总阅读数
        views_count = db.query(func.sum(Opinion.read_count)).scalar() or 0
        
        statistics = {
            "total_count": total_count,
            "hot_topics_count": hot_topics_count,
            "views_count": views_count,
            "sentiment_distribution": sentiment_distribution,
            "platform_distribution": platform_distribution,
            "time_range": "最近7天"
        }
        return statistics
    except Exception as e:
        logger.error(f"获取统计数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")

@app.get("/api/opinion/list", tags=["舆情数据"])
async def get_opinion_list(
    page: int = 1,
    pageSize: int = 10,
    keyword: Optional[str] = None,
    source: Optional[str] = None,
    sentiment_type: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    is_sensitive: Optional[bool] = None,
    category: Optional[str] = None,
    db = Depends(get_db)
):
    try:
        # 构建查询
        query = db.query(Opinion)
        
        # 应用过滤条件
        if keyword:
            query = query.filter(Opinion.title.contains(keyword) | Opinion.content.contains(keyword))
        
        if source:
            source_map = {
                "微博": "weibo",
                "微信": "wechat",
                "知乎": "zhihu",
                "其他": "other"
            }
            query = query.filter(Opinion.source_platform == source_map.get(source, source))
        
        if sentiment_type:
            query = query.filter(Opinion.sentiment == sentiment_type)
        
        if is_sensitive is not None:
            query = query.filter(Opinion.is_hot == is_sensitive)
        
        # 获取总数
        total = query.count()
        
        # 分页
        offset = (page - 1) * pageSize
        opinions = query.offset(offset).limit(pageSize).all()
        
        # 转换为前端需要的格式
        items = []
        for opinion in opinions:
            platform_name = opinion.source_platform
            if platform_name == "weibo":
                platform_name = "微博"
            elif platform_name == "wechat":
                platform_name = "微信"
            elif platform_name == "zhihu":
                platform_name = "知乎"
            else:
                platform_name = "其他"
            
            items.append({
                "id": f"opinion_{opinion.id}",
                "content": opinion.content or opinion.title,
                "platform": platform_name,
                "sentiment": opinion.sentiment,
                "published_at": opinion.publish_time.isoformat() if opinion.publish_time else None,
                "url": opinion.source_url,
                "author": opinion.author,
                "is_sensitive": opinion.is_hot
            })
        
        result = {
            "items": items,
            "total": total,
            "page": page,
            "page_size": pageSize
        }
        return result
    except Exception as e:
        logger.error(f"获取舆情列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取舆情列表失败: {str(e)}")

@app.get("/api/hot-topic/list", tags=["热点分析"])
async def get_hot_topics(
    days: int = 7,
    limit: int = 10,
    db = Depends(get_db)
):
    try:
        # 从MySQL数据库获取热点话题数据
        hot_topics = db.query(HotTopic).order_by(HotTopic.mention_count.desc()).limit(limit).all()
        
        result = []
        for topic in hot_topics:
            # 获取相关的舆情数量
            related_opinions_count = db.query(Opinion).filter(
                Opinion.title.contains(topic.topic) | 
                Opinion.content.contains(topic.topic)
            ).count()
            
            # 获取涉及的平台
            platforms = db.query(Opinion.source_platform).filter(
                Opinion.title.contains(topic.topic) | 
                Opinion.content.contains(topic.topic)
            ).distinct().all()
            
            platform_names = []
            for (platform,) in platforms:
                if platform == "weibo":
                    platform_names.append("微博")
                elif platform == "wechat":
                    platform_names.append("微信")
                elif platform == "zhihu":
                    platform_names.append("知乎")
                else:
                    platform_names.append("其他")
            
            result.append({
                "topic": topic.topic,
                "count": topic.mention_count,
                "sentiment": topic.trend,
                "platforms": platform_names,
                "time_range": f"最近{days}天",
                "related_opinions": related_opinions_count
            })
        
        return result
    except Exception as e:
        logger.error(f"获取热点话题失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取热点话题失败: {str(e)}")

@app.get("/api/trend/opinion", tags=["趋势分析"])
async def get_trend_opinion(
    days: str = "7",
    platform: Optional[str] = None,
    db = Depends(get_db)
):
    try:
        days_int = int(days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_int - 1)
        
        # 从MySQL数据库获取趋势数据
        trend_data = db.query(TrendData).filter(
            TrendData.date >= start_date,
            TrendData.date <= end_date
        ).order_by(TrendData.date).all()
        
        result = []
        for data in trend_data:
            result.append({
                "date": data.date.strftime("%Y-%m-%d"),
                "count": data.total_count,
                "platform": platform or "all"
            })
        
        # 如果数据库中没有足够的数据，生成补充数据
        if len(result) < days_int:
            for i in range(days_int - len(result)):
                date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
                result.append({
                    "date": date,
                    "count": 0,
                    "platform": platform or "all"
                })
        
        return result
    except Exception as e:
        logger.error(f"获取趋势数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取趋势数据失败: {str(e)}")

@app.get("/api/trend/sentiment", tags=["趋势分析"])
async def get_trend_sentiment(
    days: str = "7",
    platform: Optional[str] = None,
    db = Depends(get_db)
):
    try:
        days_int = int(days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_int - 1)
        
        # 从MySQL数据库获取情感趋势数据
        trend_data = db.query(TrendData).filter(
            TrendData.date >= start_date,
            TrendData.date <= end_date
        ).order_by(TrendData.date).all()
        
        result = []
        for data in trend_data:
            result.append({
                "date": data.date.strftime("%Y-%m-%d"),
                "positive": data.positive_count,
                "negative": data.negative_count,
                "neutral": data.neutral_count,
                "platform": platform or "all"
            })
        
        # 如果数据库中没有足够的数据，生成补充数据
        if len(result) < days_int:
            for i in range(days_int - len(result)):
                date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
                result.append({
                    "date": date,
                    "positive": 0,
                    "negative": 0,
                    "neutral": 0,
                    "platform": platform or "all"
                })
        
        return result
    except Exception as e:
        logger.error(f"获取情感趋势数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取情感趋势数据失败: {str(e)}")

@app.get("/api/trend/platform-distribution", tags=["趋势分析"])
async def get_trend_platform_distribution(
    days: str = "7",
    db = Depends(get_db)
):
    try:
        days_int = int(days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_int - 1)
        
        # 从MySQL数据库获取平台分布数据
        platform_stats = db.query(
            Opinion.source_platform,
            func.count(Opinion.id).label('count')
        ).filter(
            Opinion.publish_time >= start_date,
            Opinion.publish_time <= end_date
        ).group_by(Opinion.source_platform).all()
        
        total_count = sum(stat.count for stat in platform_stats)
        
        result = []
        for platform, count in platform_stats:
            percentage = (count / total_count * 100) if total_count > 0 else 0
            
            platform_name = platform
            if platform == "weibo":
                platform_name = "微博"
            elif platform == "wechat":
                platform_name = "微信"
            elif platform == "zhihu":
                platform_name = "知乎"
            else:
                platform_name = "其他"
            
            result.append({
                "platform": platform_name,
                "count": count,
                "percentage": round(percentage, 1),
                "time_range": f"最近{days}天"
            })
        
        return result
    except Exception as e:
        logger.error(f"获取平台分布数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取平台分布数据失败: {str(e)}")

if __name__ == "__main__":
    import sys
    port = 8000
    if len(sys.argv) > 2 and sys.argv[1] == "--port":
        port = int(sys.argv[2])
    uvicorn.run(app, host="0.0.0.0", port=port)
