# -*- coding: utf-8 -*-
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime, timedelta
import uvicorn
from dateutil import parser
import json

from auth.auth_router import auth_router
# from routers.database_router import router as database_router  # MongoDB路由
from routers.mysql_database_router import router as database_router  # MySQL路由
from routers.sentiment_router import router as sentiment_router  # 情感分析路由
from routers.cnn_sentiment_router import router as cnn_sentiment_router  # CNN情感分析路由

# 自定义JSONResponse，确保中文正确显示
class CustomJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return json.dumps(content, ensure_ascii=False, allow_nan=False, indent=None, separators=(",", ":")).encode("utf-8")

app = FastAPI(
    title="校园舆情检测与热点话题分析系统",
    description="用于实时监控、分析和可视化校园相关舆情信息的平台",
    version="1.0.0",
    default_response_class=CustomJSONResponse
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(database_router)
app.include_router(sentiment_router)
app.include_router(cnn_sentiment_router)

sample_opinions = [
    {
        "id": "1",
        "content": "教育部近日发布新政策，将加大对乡村教师的支持力度，提高乡村教师待遇，改善乡村学校办学条件。这一政策的出台，将有助于促进教育公平，推动乡村教育振兴。",
        "source": "中国教育报",
        "source_platform": "微博",
        "publish_time": datetime.now().isoformat(),
        "crawl_time": datetime.now().isoformat(),
        "sentiment": 0.8,
        "sentiment_type": "positive",
        "keywords": ["教育部", "政策", "教育公平", "振兴乡村"],
        "url": "https://example.com/news/1",
        "views": 12543,
        "likes": 892,
        "comments": 235,
        "shares": 578,
        "heat_score": 92,
        "is_sensitive": False,
        "sensitive_level": 0
    },
    {
        "id": "2",
        "content": "据最新调查数据显示，今年高校毕业生就业形势总体平稳，但结构性矛盾依然存在。IT、人工智能、医疗健康等行业需求旺盛，而传统制造业、服务业就业压力较大。专家建议，高校应加强专业设置与市场需求的对接，提高学生实践能力。",
        "source": "中国青年报",
        "source_platform": "微信",
        "publish_time": datetime.now().isoformat(),
        "crawl_time": datetime.now().isoformat(),
        "sentiment": 0.5,
        "sentiment_type": "neutral",
        "keywords": ["高校毕业生", "就业形势", "人工智能", "医疗健康"],
        "url": "https://example.com/news/2",
        "views": 9870,
        "likes": 654,
        "comments": 189,
        "shares": 132,
        "heat_score": 78,
        "is_sensitive": False,
        "sensitive_level": 0
    },
    {
        "id": "3",
        "content": "近期，多所高校发生网络安全事件，导致部分学生信息泄露。专家提醒，学校应加强网络安全防护措施，定期进行安全漏洞扫描，同时提高师生网络安全意识，避免点击可疑链接、下载不明软件。",
        "source": "科技日报",
        "source_platform": "知乎",
        "publish_time": datetime.now().isoformat(),
        "crawl_time": datetime.now().isoformat(),
        "sentiment": 0.2,
        "sentiment_type": "negative",
        "keywords": ["网络安全", "校园安全", "信息泄露"],
        "url": "https://example.com/news/3",
        "views": 15680,
        "likes": 1234,
        "comments": 342,
        "shares": 215,
        "heat_score": 92,
        "is_sensitive": True,
        "sensitive_level": 7
    },
    {
        "id": "4",
        "content": "为鼓励大学生创业创新，国家近日升级了大学生创业扶持政策，符合条件的创业项目最高可获得50万元补贴。此外，还将提供创业培训、导师指导、场地支持等一站式服务。这一政策的出台，将继续激发大学生创业热情。",
        "source": "经济参考报",
        "source_platform": "校园论坛",
        "publish_time": datetime.now().isoformat(),
        "crawl_time": datetime.now().isoformat(),
        "sentiment": 0.9,
        "sentiment_type": "positive",
        "keywords": ["大学生创业", "扶持政策", "补贴"],
        "url": "https://example.com/news/4",
        "views": 8960,
        "likes": 789,
        "comments": 175,
        "shares": 128,
        "heat_score": 76,
        "is_sensitive": False,
        "sensitive_level": 0
    },
    {
        "id": "5",
        "content": "据教育部公布的数据，今年全国硕士研究生招生考试报名人数突破500万，创历史新高。专家分析，就业压力、学历提升需求是报名人数增长主要原因。面对激烈的竞争，考生应提前做好复习规划，理性选择报考院校和专业。",
        "source": "新华社",
        "source_platform": "微博",
        "publish_time": datetime.now().isoformat(),
        "crawl_time": datetime.now().isoformat(),
        "sentiment": 0.5,
        "sentiment_type": "neutral",
        "keywords": ["研究生考试", "报名人数", "竞争"],
        "url": "https://example.com/news/5",
        "views": 14530,
        "likes": 987,
        "comments": 321,
        "shares": 198,
        "heat_score": 88,
        "is_sensitive": False,
        "sensitive_level": 0
    }
]

@app.get("/api/ping", tags=["基础接口"])
async def ping():
    return {"status": "ok", "message": "服务运行正常"}

@app.get("/api/opinion/statistics", tags=["统计数据"])
@app.get("/api/opinions/statistics", tags=["统计数据"])
async def get_opinion_statistics(
    start_time: Optional[str] = None,
    end_time: Optional[str] = None
):
    try:
        total_opinions = 1256
        positive_count = 523
        negative_count = 312
        neutral_count = 421
        
        today = datetime.now()
        daily_trend = []
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            date_str = f"{date.month}月{date.day}日"
            count = 150 + (6 - i) * 10 + (i % 2) * 20
            daily_trend.append({"date": date_str, "count": count})
        
        platform_distribution = [
            {"platform": "微博", "count": 567, "percentage": 45.1},
            {"platform": "微信", "count": 342, "percentage": 27.2},
            {"platform": "知乎", "count": 189, "percentage": 15.0},
            {"platform": "校园论坛", "count": 158, "percentage": 12.6}
        ]
        
        category_distribution = [
            {"category": "政策解读", "count": 321},
            {"category": "就业情况", "count": 289},
            {"category": "科技创新", "count": 256},
            {"category": "校园安全", "count": 189},
            {"category": "教育改革", "count": 201}
        ]
        
        return {
            "total_opinions": total_opinions,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "neutral_count": neutral_count,
            "daily_trend": daily_trend,
            "platform_distribution": platform_distribution,
            "category_distribution": category_distribution
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

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
        filtered_data = sample_opinions.copy()
        
        if keyword:
            filtered_data = [item for item in filtered_data if keyword in item["content"] or any(keyword in kw for kw in item["keywords"])]
        
        if source:
            filtered_data = [item for item in filtered_data if item["source_platform"] == source]
        
        if sentiment_type:
            filtered_data = [item for item in filtered_data if item["sentiment_type"] == sentiment_type]
        
        if start_time:
            try:
                start_dt = parser.parse(start_time)
                filtered_data = [item for item in filtered_data if parser.parse(item["publish_time"]) >= start_dt]
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_time format")
        
        if end_time:
            try:
                end_dt = parser.parse(end_time)
                filtered_data = [item for item in filtered_data if parser.parse(item["publish_time"]) <= end_dt]
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_time format")
        
        if is_sensitive is not None:
            filtered_data = [item for item in filtered_data if item["is_sensitive"] == is_sensitive]
        
        start_idx = (page - 1) * pageSize
        end_idx = start_idx + pageSize
        paginated_data = filtered_data[start_idx:end_idx]
        
        return {
            "items": paginated_data,
            "total": len(filtered_data),
            "page": page,
            "page_size": pageSize
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/opinion/{id}", tags=["舆情数据"])
async def get_opinion_detail(id: str):
    try:
        for item in sample_opinions:
            if item["id"] == id:
                return item
        raise HTTPException(status_code=404, detail="舆情数据不存在")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/hot-topic/list", tags=["热点分析"])
async def get_hot_topics(
    days: int = 7,
    limit: int = 10
):
    try:
        hot_topics = [
            {"id": "1", "topic": "食堂饭菜质量提升", "heat_score": 95, "sentiment": 0.7},
            {"id": "2", "topic": "图书馆座位紧张", "heat_score": 88, "sentiment": -0.4},
            {"id": "3", "topic": "校园安全管理", "heat_score": 76, "sentiment": 0.2},
            {"id": "4", "topic": "考研报名人数创新高", "heat_score": 90, "sentiment": 0.1},
            {"id": "5", "topic": "大学生创业扶持政策", "heat_score": 85, "sentiment": 0.8}
        ]
        
        return hot_topics[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/trend/opinion", tags=["趋势分析"])
async def get_trend_opinion(
    days: str = "7",
    platform: Optional[str] = None
):
    try:
        today = datetime.now()
        mock_trend_data = []
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            date_str = f"{date.month}月{date.day}日"
            count = 80 + (6 - i) * 8 + (i % 2) * 15
            heat = 60 + (6 - i) * 5 + (i % 3) * 10
            mock_trend_data.append({"date": date_str, "count": count, "heat": heat})
        
        return mock_trend_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/trend/sentiment", tags=["趋势分析"])
async def get_trend_sentiment(
    days: str = "7",
    platform: Optional[str] = None
):
    try:
        today = datetime.now()
        mock_sentiment_data = []
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            date_str = f"{date.month}月{date.day}日"
            positive = 30 + (6 - i) * 4 + (i % 2) * 8
            negative = 20 + (i % 3) * 6
            neutral = 25 + (6 - i) * 3 + (i % 2) * 5
            mock_sentiment_data.append({
                "date": date_str,
                "positive": positive,
                "negative": negative,
                "neutral": neutral
            })
        
        return mock_sentiment_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/trend/platform-distribution", tags=["趋势分析"])
async def get_trend_platform_distribution(
    days: str = "7"
):
    try:
        mock_platform_data = [
            {"platform": "微博", "count": 420, "percentage": 35.7, "color": "#E6162D"},
            {"platform": "微信", "count": 350, "percentage": 29.8, "color": "#07C160"},
            {"platform": "知乎", "count": 210, "percentage": 17.9, "color": "#0066FF"},
            {"platform": "校园论坛", "count": 120, "percentage": 10.2, "color": "#FF9500"},
            {"platform": "其他", "count": 75, "percentage": 6.4, "color": "#5856D6"}
        ]
        
        return mock_platform_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
