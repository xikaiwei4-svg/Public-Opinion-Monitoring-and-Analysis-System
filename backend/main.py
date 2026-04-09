# -*- coding: utf-8 -*-
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
    end_time: Optional[str] = None
):
    try:
        # 返回模拟数据，不依赖数据库
        mock_statistics = {
            "total_count": 1256,
            "hot_topics_count": 28,
            "views_count": 3567,
            "sentiment_distribution": {
                "positive": 523,
                "negative": 345,
                "neutral": 388
            },
            "platform_distribution": [
                {"platform": "微博", "count": 456, "percentage": 36.3},
                {"platform": "知乎", "count": 321, "percentage": 25.6},
                {"platform": "微信", "count": 289, "percentage": 23.0},
                {"platform": "其他", "count": 190, "percentage": 15.1}
            ],
            "time_range": "最近7天"
        }
        return mock_statistics
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
    category: Optional[str] = None
):
    try:
        # 返回模拟数据，不依赖数据库
        mock_opinions = []
        for i in range(pageSize):
            mock_opinions.append({
                "id": f"opinion_{(page-1)*pageSize + i + 1}",
                "content": f"这是一条模拟舆情数据 {i+1}：关于校园生活的讨论...",
                "platform": ["微博", "知乎", "微信"][i % 3],
                "sentiment": ["positive", "negative", "neutral"][i % 3],
                "published_at": f"2026-04-{str(9 - i % 7).zfill(2)}T10:00:00Z",
                "url": f"https://example.com/opinion/{i+1}",
                "author": f"用户{i+1}",
                "is_sensitive": i % 5 == 0
            })
        
        mock_result = {
            "items": mock_opinions,
            "total": 1256,
            "page": page,
            "page_size": pageSize
        }
        return mock_result
    except Exception as e:
        logger.error(f"获取舆情列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取舆情列表失败: {str(e)}")

@app.get("/api/hot-topic/list", tags=["热点分析"])
async def get_hot_topics(
    days: int = 7,
    limit: int = 10
):
    try:
        # 返回模拟数据，不依赖数据库
        mock_hot_topics = [
            {
                "topic": "校园食堂改革",
                "count": 156,
                "sentiment": "neutral",
                "platforms": ["微博", "知乎"],
                "time_range": f"最近{days}天",
                "related_opinions": 89
            },
            {
                "topic": "期末考试安排",
                "count": 98,
                "sentiment": "negative",
                "platforms": ["微信", "QQ"],
                "time_range": f"最近{days}天",
                "related_opinions": 56
            },
            {
                "topic": "校园网络升级",
                "count": 78,
                "sentiment": "positive",
                "platforms": ["微博", "知乎", "微信"],
                "time_range": f"最近{days}天",
                "related_opinions": 42
            },
            {
                "topic": "宿舍环境改善",
                "count": 65,
                "sentiment": "positive",
                "platforms": ["微信"],
                "time_range": f"最近{days}天",
                "related_opinions": 38
            },
            {
                "topic": "校园活动安排",
                "count": 45,
                "sentiment": "neutral",
                "platforms": ["微博", "QQ"],
                "time_range": f"最近{days}天",
                "related_opinions": 29
            }
        ]
        return mock_hot_topics[:limit]
    except Exception as e:
        logger.error(f"获取热点话题失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取热点话题失败: {str(e)}")

@app.get("/api/trend/opinion", tags=["趋势分析"])
async def get_trend_opinion(
    days: str = "7",
    platform: Optional[str] = None
):
    try:
        # 返回模拟数据，不依赖数据库
        days_int = int(days)
        mock_trend_data = []
        
        for i in range(days_int):
            date = (datetime.now() - timedelta(days=days_int - i - 1)).strftime("%Y-%m-%d")
            mock_trend_data.append({
                "date": date,
                "count": 50 + i * 10,
                "platform": platform or "all"
            })
        
        return mock_trend_data
    except Exception as e:
        logger.error(f"获取趋势数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取趋势数据失败: {str(e)}")

@app.get("/api/trend/sentiment", tags=["趋势分析"])
async def get_trend_sentiment(
    days: str = "7",
    platform: Optional[str] = None
):
    try:
        # 返回模拟数据，不依赖数据库
        days_int = int(days)
        mock_sentiment_data = []
        
        for i in range(days_int):
            date = (datetime.now() - timedelta(days=days_int - i - 1)).strftime("%Y-%m-%d")
            mock_sentiment_data.append({
                "date": date,
                "positive": 30 + i * 5,
                "negative": 20 + i * 2,
                "neutral": 40 + i * 3,
                "platform": platform or "all"
            })
        
        return mock_sentiment_data
    except Exception as e:
        logger.error(f"获取情感趋势数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取情感趋势数据失败: {str(e)}")

@app.get("/api/trend/platform-distribution", tags=["趋势分析"])
async def get_trend_platform_distribution(
    days: str = "7"
):
    try:
        # 返回模拟数据，不依赖数据库
        mock_platform_distribution = [
            {
                "platform": "微博",
                "count": 456,
                "percentage": 36.3,
                "time_range": f"最近{days}天"
            },
            {
                "platform": "知乎",
                "count": 321,
                "percentage": 25.6,
                "time_range": f"最近{days}天"
            },
            {
                "platform": "微信",
                "count": 289,
                "percentage": 23.0,
                "time_range": f"最近{days}天"
            },
            {
                "platform": "其他",
                "count": 190,
                "percentage": 15.1,
                "time_range": f"最近{days}天"
            }
        ]
        
        return mock_platform_distribution
    except Exception as e:
        logger.error(f"获取平台分布数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取平台分布数据失败: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
