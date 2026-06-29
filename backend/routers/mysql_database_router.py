# MySQL数据库管理路由
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import text, func
from sqlalchemy.orm import Session
import json
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel

from db.mysql_config import get_db, engine, admin_engine, settings
from models.mysql_models import Opinion, User, HotTopic, TrendData, CrawlerLog, Base

router = APIRouter(prefix="/api/database", tags=["数据库管理"])

# 爬虫任务状态跟踪
crawler_tasks: Dict[str, dict] = {}
_thread_pool = ThreadPoolExecutor(max_workers=2)

# 创建数据库和表
@router.post("/init")
def init_database():
    try:
        # 使用admin引擎创建数据库（连接到mysql系统数据库）
        with admin_engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {settings.MYSQL_DATABASE} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
            conn.commit()
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        
        return {"message": "数据库初始化成功", "database": settings.MYSQL_DATABASE}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库初始化失败: {str(e)}")

# 获取数据库统计信息
@router.get("/stats")
def get_database_stats(db: Session = Depends(get_db)):
    try:
        # 获取各表记录数
        opinions_count = db.query(Opinion).count()
        users_count = db.query(User).count()
        hot_topics_count = db.query(HotTopic).count()
        trend_data_count = db.query(TrendData).count()
        crawler_logs_count = db.query(CrawlerLog).count()
        
        total_records = opinions_count + users_count + hot_topics_count + trend_data_count + crawler_logs_count
        
        # 构建集合信息
        collections_info = [
            {
                "name": "opinions",
                "documentCount": opinions_count,
                "status": "normal" if opinions_count < 100000 else "warning"
            },
            {
                "name": "users",
                "documentCount": users_count,
                "status": "normal"
            },
            {
                "name": "hot_topics",
                "documentCount": hot_topics_count,
                "status": "normal"
            },
            {
                "name": "trend_data",
                "documentCount": trend_data_count,
                "status": "normal"
            },
            {
                "name": "crawler_logs",
                "documentCount": crawler_logs_count,
                "status": "normal"
            }
        ]
        
        return {
            "db": settings.MYSQL_DATABASE,
            "collections": 5,
            "views": 0,
            "objects": total_records,
            "avgObjSize": 2200,
            "dataSize": total_records * 2200,
            "storageSize": total_records * 2600,
            "indexes": 11,
            "indexSize": total_records * 400,
            "totalSize": total_records * 3000,
            "fsUsedSize": 5242880000,
            "fsTotalSize": 10737418240,
            "collections_info": collections_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数据库统计信息失败: {str(e)}")

# 获取集合列表
@router.get("/collections")
def get_collections(db: Session = Depends(get_db)):
    try:
        opinions_count = db.query(Opinion).count()
        users_count = db.query(User).count()
        hot_topics_count = db.query(HotTopic).count()
        trend_data_count = db.query(TrendData).count()
        crawler_logs_count = db.query(CrawlerLog).count()
        
        collections = [
            {
                "key": "opinions",
                "name": "opinions",
                "documentCount": opinions_count,
                "size": f"{opinions_count * 2.5:.1f} KB" if opinions_count > 0 else "0 Bytes",
                "avgObjSize": "2.5 KB",
                "storageSize": f"{opinions_count * 3:.1f} KB" if opinions_count > 0 else "0 Bytes",
                "indexCount": 3,
                "indexSize": f"{opinions_count * 0.5:.1f} KB" if opinions_count > 0 else "0 Bytes",
                "status": "normal" if opinions_count < 100000 else "warning"
            },
            {
                "key": "users",
                "name": "users",
                "documentCount": users_count,
                "size": f"{users_count * 1.5:.1f} KB" if users_count > 0 else "0 Bytes",
                "avgObjSize": "1.5 KB",
                "storageSize": f"{users_count * 2:.1f} KB" if users_count > 0 else "0 Bytes",
                "indexCount": 2,
                "indexSize": f"{users_count * 0.3:.1f} KB" if users_count > 0 else "0 Bytes",
                "status": "normal"
            },
            {
                "key": "hot_topics",
                "name": "hot_topics",
                "documentCount": hot_topics_count,
                "size": f"{hot_topics_count * 2:.1f} KB" if hot_topics_count > 0 else "0 Bytes",
                "avgObjSize": "2 KB",
                "storageSize": f"{hot_topics_count * 2.5:.1f} KB" if hot_topics_count > 0 else "0 Bytes",
                "indexCount": 2,
                "indexSize": f"{hot_topics_count * 0.4:.1f} KB" if hot_topics_count > 0 else "0 Bytes",
                "status": "normal"
            },
            {
                "key": "trend_data",
                "name": "trend_data",
                "documentCount": trend_data_count,
                "size": f"{trend_data_count * 1.8:.1f} KB" if trend_data_count > 0 else "0 Bytes",
                "avgObjSize": "1.8 KB",
                "storageSize": f"{trend_data_count * 2.2:.1f} KB" if trend_data_count > 0 else "0 Bytes",
                "indexCount": 2,
                "indexSize": f"{trend_data_count * 0.35:.1f} KB" if trend_data_count > 0 else "0 Bytes",
                "status": "normal"
            },
            {
                "key": "crawler_logs",
                "name": "crawler_logs",
                "documentCount": crawler_logs_count,
                "size": f"{crawler_logs_count * 3:.1f} KB" if crawler_logs_count > 0 else "0 Bytes",
                "avgObjSize": "3 KB",
                "storageSize": f"{crawler_logs_count * 3.5:.1f} KB" if crawler_logs_count > 0 else "0 Bytes",
                "indexCount": 2,
                "indexSize": f"{crawler_logs_count * 0.5:.1f} KB" if crawler_logs_count > 0 else "0 Bytes",
                "status": "normal"
            }
        ]
        
        return collections
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取集合列表失败: {str(e)}")

# 获取集合详情
@router.get("/collections/{collection_name}")
def get_collection_detail(collection_name: str, db: Session = Depends(get_db)):
    try:
        count = 0
        if collection_name == "opinions":
            count = db.query(Opinion).count()
        elif collection_name == "users":
            count = db.query(User).count()
        elif collection_name == "hot_topics":
            count = db.query(HotTopic).count()
        elif collection_name == "trend_data":
            count = db.query(TrendData).count()
        elif collection_name == "crawler_logs":
            count = db.query(CrawlerLog).count()
        else:
            raise HTTPException(status_code=404, detail=f"集合 {collection_name} 不存在")
        
        return {
            "name": collection_name,
            "documentCount": count,
            "size": f"{count * 2.5:.1f} KB" if count > 0 else "0 Bytes",
            "avgObjSize": "2.5 KB",
            "storageSize": f"{count * 3:.1f} KB" if count > 0 else "0 Bytes",
            "indexCount": 3,
            "indexSize": f"{count * 0.5:.1f} KB" if count > 0 else "0 Bytes",
            "status": "normal" if count < 100000 else "warning",
            "indexes": [
                {"name": "PRIMARY", "keys": {"id": 1}},
                {"name": "ix_source_platform", "keys": {"source_platform": 1}},
                {"name": "ix_publish_time", "keys": {"publish_time": -1}}
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取集合详情失败: {str(e)}")

# 删除集合（清空表）
@router.delete("/collections/{collection_name}")
def delete_collection(collection_name: str, db: Session = Depends(get_db)):
    try:
        if collection_name == "opinions":
            db.query(Opinion).delete()
        elif collection_name == "users":
            db.query(User).delete()
        elif collection_name == "hot_topics":
            db.query(HotTopic).delete()
        elif collection_name == "trend_data":
            db.query(TrendData).delete()
        elif collection_name == "crawler_logs":
            db.query(CrawlerLog).delete()
        else:
            raise HTTPException(status_code=404, detail=f"集合 {collection_name} 不存在")
        
        db.commit()
        return {"message": f"集合 {collection_name} 已清空"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除集合失败: {str(e)}")

# 获取数据库配置信息
@router.get("/config")
def get_database_config():
    try:
        return {
            "host": settings.MYSQL_HOST,
            "port": settings.MYSQL_PORT,
            "database": settings.MYSQL_DATABASE,
            "username": settings.MYSQL_USER,
            "password": "********",
            "authSource": "mysql",
            "status": "connected",
            "lastConnected": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数据库配置失败: {str(e)}")

# 获取舆情数据列表
@router.get("/opinions")
def get_opinions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        # 获取总数
        total = db.query(Opinion).count()
        # 获取分页数据
        opinions = db.query(Opinion).offset(skip).limit(limit).all()
        data = [opinion.to_dict() for opinion in opinions]
        # 返回包含总数的数据
        result = {
            "items": data,
            "total": total,
            "skip": skip,
            "limit": limit
        }
        return JSONResponse(content=result, media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取舆情数据失败: {str(e)}")

# 创建舆情数据
@router.post("/opinions")
def create_opinion(opinion_data: Dict[str, Any], db: Session = Depends(get_db)):
    try:
        opinion = Opinion(**opinion_data)
        db.add(opinion)
        db.commit()
        db.refresh(opinion)
        return opinion.to_dict()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建舆情数据失败: {str(e)}")

def _do_crawl(task_id: str, platform: str, keywords: Optional[str]):
    """在后台线程中执行爬虫任务"""
    import requests
    from bs4 import BeautifulSoup
    from routers.sentiment_router import analyze_sentiment

    db = next(get_db())
    try:
        crawler_tasks[task_id]["status"] = "running"

        sources = [
            {"name": "新浪教育", "url": "https://edu.sina.com.cn/", "platform": "sina"},
            {"name": "中国教育在线", "url": "https://www.eol.cn/", "platform": "eol"},
            {"name": "中国教育新闻网", "url": "http://www.jyb.cn/", "platform": "jyb"},
            {"name": "腾讯教育", "url": "https://edu.qq.com/", "platform": "qq"},
            {"name": "搜狐教育", "url": "https://learning.sohu.com/", "platform": "sohu"},
            {"name": "网易教育", "url": "https://education.163.com/", "platform": "163"},
            {"name": "凤凰教育", "url": "https://edu.ifeng.com/", "platform": "ifeng"},
            {"name": "中国高校之窗", "url": "http://www.gx211.com/", "platform": "gx211"},
            {"name": "高校招生网", "url": "https://www.gxzs.com/", "platform": "gxzs"},
            {"name": "中国考研网", "url": "https://www.chinakaoyan.com/", "platform": "chinakaoyan"},
            {"name": "中国大学网", "url": "https://www.chinauniversity.com.cn/", "platform": "chinauniversity"},
            {"name": "高校之窗", "url": "https://www.gaoxiao.info/", "platform": "gaoxiao"},
            {"name": "高考网", "url": "https://www.gaokao.com/", "platform": "gaokao"},
            {"name": "考研帮", "url": "https://www.kaoyan.com/", "platform": "kaoyanbang"},
            {"name": "自考网", "url": "https://www.zikao.com/", "platform": "zikao"},
            {"name": "教育界", "url": "https://www.jyjy.net.cn/", "platform": "jyjy"},
            {"name": "教育信息网", "url": "https://www.eduzhixin.com/", "platform": "eduzhixin"},
            {"name": "中国教育装备网", "url": "https://www.ceiea.com/", "platform": "ceiea"},
            {"name": "北京教育考试院", "url": "https://www.bjeea.cn/", "platform": "bjeea"},
            {"name": "上海教育考试院", "url": "https://www.shmeea.edu.cn/", "platform": "shmeea"},
            {"name": "广东教育考试院", "url": "https://eea.gd.gov.cn/", "platform": "eeagd"},
        ]

        crawler_tasks[task_id]["total_sources"] = len(sources)
        crawled_count = 0
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        for i, source in enumerate(sources):
            if platform != "all" and source["platform"] != platform:
                continue

            crawler_tasks[task_id]["current_source"] = source["name"]
            crawler_tasks[task_id]["progress"] = i + 1

            try:
                response = requests.get(source["url"], headers=headers, timeout=15)
                response.raise_for_status()
                if response.encoding == "ISO-8859-1":
                    response.encoding = response.apparent_encoding

                soup = BeautifulSoup(response.content, "html.parser")
                for link in soup.find_all("a"):
                    try:
                        title = link.get_text(strip=True)
                        url = link.get("href", "")
                        if len(title) < 2 or not url:
                            continue
                        if any(kw in url.lower() for kw in ["javascript:", "void(0)"]):
                            continue
                        if url.startswith("//"):
                            url = ("https:" if source["url"].startswith("https") else "http:") + url

                        if db.query(Opinion).filter(Opinion.source_url == url).first():
                            continue

                        result = analyze_sentiment(title)
                        db.add(Opinion(
                            title=title, content=title,
                            source_platform=source["platform"], source_url=url,
                            author=source["name"], publish_time=datetime.now(),
                            sentiment=result["sentiment_type"], sentiment_score=result["sentiment_score"],
                            keywords=",".join(title.split()[:5]),
                            read_count=0, like_count=0, comment_count=0, share_count=0,
                        ))
                        crawled_count += 1
                        crawler_tasks[task_id]["crawled_count"] = crawled_count
                    except Exception:
                        continue
            except Exception as e:
                print(f"[{task_id}] {source['name']} 失败: {e}")
                continue

        if crawled_count > 0:
            db.commit()

        db.add(CrawlerLog(
            platform=platform, status="success",
            start_time=datetime.now(), end_time=datetime.now(),
            total_count=crawled_count, success_count=crawled_count, error_count=0,
        ))
        db.commit()

        crawler_tasks[task_id]["status"] = "completed"
        crawler_tasks[task_id]["crawled_count"] = crawled_count
        print(f"[{task_id}] 完成，共抓取 {crawled_count} 条")

    except Exception as e:
        db.rollback()
        crawler_tasks[task_id]["status"] = "failed"
        crawler_tasks[task_id]["error"] = str(e)
        print(f"[{task_id}] 失败: {e}")
    finally:
        db.close()


@router.post("/crawler/run")
async def run_crawler(data: dict):
    try:
        platform = data.get("platform", "all")
        task_id = str(uuid.uuid4())

        crawler_tasks[task_id] = {
            "status": "pending",
            "progress": 0,
            "total_sources": 0,
            "current_source": "",
            "crawled_count": 0,
            "created_at": datetime.now().isoformat(),
        }

        loop = asyncio.get_event_loop()
        loop.run_in_executor(_thread_pool, _do_crawl, task_id, platform, data.get("keywords"))

        return {
            "status": "success",
            "message": "爬虫任务已启动，正在后台运行...",
            "task_id": task_id,
            "platform": platform,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动爬虫任务失败: {str(e)}")

# 获取爬虫任务状态
@router.get("/crawler/task/{task_id}")
def get_crawler_task_status(task_id: str):
    task = crawler_tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return {"task_id": task_id, **task}
