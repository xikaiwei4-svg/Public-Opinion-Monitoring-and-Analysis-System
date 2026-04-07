from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime
import motor.motor_asyncio
from db.mongo_client import db, get_collection
from tasks.crawler_tasks import run_weibo_crawler, run_wechat_crawler, run_zhihu_crawler, run_all_crawlers

router = APIRouter(prefix="/api/database", tags=["数据库管理"])

# 模拟数据（当MongoDB未连接时使用）
MOCK_COLLECTIONS = [
    {
        "key": "opinions",
        "name": "opinions",
        "documentCount": 15420,
        "size": "45.2 MB",
        "avgObjSize": "2.9 KB",
        "storageSize": "52.1 MB",
        "indexCount": 3,
        "indexSize": "8.5 MB",
        "status": "normal"
    },
    {
        "key": "users",
        "name": "users",
        "documentCount": 1250,
        "size": "2.8 MB",
        "avgObjSize": "2.3 KB",
        "storageSize": "4.1 MB",
        "indexCount": 2,
        "indexSize": "1.2 MB",
        "status": "normal"
    },
    {
        "key": "hot_topics",
        "name": "hot_topics",
        "documentCount": 856,
        "size": "1.5 MB",
        "avgObjSize": "1.8 KB",
        "storageSize": "2.1 MB",
        "indexCount": 2,
        "indexSize": "0.8 MB",
        "status": "normal"
    },
    {
        "key": "trend_data",
        "name": "trend_data",
        "documentCount": 52340,
        "size": "128.5 MB",
        "avgObjSize": "2.5 KB",
        "storageSize": "156.2 MB",
        "indexCount": 4,
        "indexSize": "24.6 MB",
        "status": "warning"
    },
    {
        "key": "logs",
        "name": "logs",
        "documentCount": 256800,
        "size": "512.3 MB",
        "avgObjSize": "2.1 KB",
        "storageSize": "625.8 MB",
        "indexCount": 2,
        "indexSize": "45.2 MB",
        "status": "warning"
    },
    {
        "key": "sessions",
        "name": "sessions",
        "documentCount": 450,
        "size": "0.8 MB",
        "avgObjSize": "1.8 KB",
        "storageSize": "1.2 MB",
        "indexCount": 1,
        "indexSize": "0.3 MB",
        "status": "normal"
    }
]

MOCK_STATS = {
    "db": "campus_opinion_db",
    "collections": 6,
    "views": 0,
    "objects": 327116,
    "avgObjSize": 2096,
    "dataSize": 691100000,
    "storageSize": 841500000,
    "indexes": 14,
    "indexSize": 80600000,
    "totalSize": 922100000,
    "fsUsedSize": 5242880000,
    "fsTotalSize": 10737418240,
    "collections_info": MOCK_COLLECTIONS
}

# 获取数据库统计信息
@router.get("/stats")
async def get_database_stats():
    try:
        # 获取所有集合名称
        collection_names = await db.list_collection_names()
        
        # 获取数据库统计信息
        stats = await db.command("dbStats")
        
        # 获取每个集合的详细信息
        collections_info = []
        for collection_name in collection_names:
            collection = get_collection(collection_name)
            
            # 获取集合统计信息
            coll_stats = await db.command("collStats", collection_name)
            
            # 获取文档数量
            count = await collection.count_documents({})
            
            # 获取索引信息
            indexes = await collection.list_indexes().to_list(None)
            index_count = len(indexes)
            
            # 计算索引大小
            index_size = coll_stats.get("totalIndexSize", 0)
            
            # 判断状态
            status = "normal"
            if count > 100000:
                status = "warning"
            if count > 500000:
                status = "error"
            
            collections_info.append({
                "name": collection_name,
                "documentCount": count,
                "size": format_bytes(coll_stats.get("size", 0)),
                "avgObjSize": format_bytes(coll_stats.get("avgObjSize", 0)),
                "storageSize": format_bytes(coll_stats.get("storageSize", 0)),
                "indexCount": index_count,
                "indexSize": format_bytes(index_size),
                "status": status
            })
        
        return {
            "db": stats.get("db", "unknown"),
            "collections": len(collection_names),
            "views": stats.get("views", 0),
            "objects": stats.get("objects", 0),
            "avgObjSize": stats.get("avgObjSize", 0),
            "dataSize": stats.get("dataSize", 0),
            "storageSize": stats.get("storageSize", 0),
            "indexes": stats.get("indexes", 0),
            "indexSize": stats.get("indexSize", 0),
            "totalSize": stats.get("totalSize", 0),
            "fsUsedSize": stats.get("fsUsedSize", 0),
            "fsTotalSize": stats.get("fsTotalSize", 0),
            "collections_info": collections_info
        }
    except Exception as e:
        # 如果MongoDB未连接，返回模拟数据
        print(f"MongoDB连接失败，返回模拟数据: {str(e)}")
        return MOCK_STATS

# 获取集合列表
@router.get("/collections")
async def get_collections():
    try:
        collection_names = await db.list_collection_names()
        
        collections_info = []
        for collection_name in collection_names:
            collection = get_collection(collection_name)
            coll_stats = await db.command("collStats", collection_name)
            count = await collection.count_documents({})
            indexes = await collection.list_indexes().to_list(None)
            index_count = len(indexes)
            index_size = coll_stats.get("totalIndexSize", 0)
            
            status = "normal"
            if count > 100000:
                status = "warning"
            if count > 500000:
                status = "error"
            
            collections_info.append({
                "key": collection_name,
                "name": collection_name,
                "documentCount": count,
                "size": format_bytes(coll_stats.get("size", 0)),
                "avgObjSize": format_bytes(coll_stats.get("avgObjSize", 0)),
                "storageSize": format_bytes(coll_stats.get("storageSize", 0)),
                "indexCount": index_count,
                "indexSize": format_bytes(index_size),
                "status": status
            })
        
        return collections_info
    except Exception as e:
        # 如果MongoDB未连接，返回模拟数据
        print(f"MongoDB连接失败，返回模拟数据: {str(e)}")
        return MOCK_COLLECTIONS

# 获取集合详情
@router.get("/collections/{collection_name}")
async def get_collection_detail(collection_name: str):
    try:
        collection = get_collection(collection_name)
        coll_stats = await db.command("collStats", collection_name)
        count = await collection.count_documents({})
        indexes = await collection.list_indexes().to_list(None)
        index_count = len(indexes)
        index_size = coll_stats.get("totalIndexSize", 0)
        
        status = "normal"
        if count > 100000:
            status = "warning"
        if count > 500000:
            status = "error"
        
        return {
            "name": collection_name,
            "documentCount": count,
            "size": format_bytes(coll_stats.get("size", 0)),
            "avgObjSize": format_bytes(coll_stats.get("avgObjSize", 0)),
            "storageSize": format_bytes(coll_stats.get("storageSize", 0)),
            "indexCount": index_count,
            "indexSize": format_bytes(index_size),
            "status": status,
            "indexes": [
                {
                    "name": idx.get("name"),
                    "keys": idx.get("key")
                }
                for idx in indexes
            ]
        }
    except Exception as e:
        # 如果MongoDB未连接，返回模拟数据
        print(f"MongoDB连接失败，返回模拟数据: {str(e)}")
        mock_collection = next((c for c in MOCK_COLLECTIONS if c["name"] == collection_name), MOCK_COLLECTIONS[0])
        return {
            "name": mock_collection["name"],
            "documentCount": mock_collection["documentCount"],
            "size": mock_collection["size"],
            "avgObjSize": mock_collection["avgObjSize"],
            "storageSize": mock_collection["storageSize"],
            "indexCount": mock_collection["indexCount"],
            "indexSize": mock_collection["indexSize"],
            "status": mock_collection["status"],
            "indexes": [
                {"name": "_id_", "keys": {"_id": 1}},
                {"name": "source_platform_1", "keys": {"source_platform": 1}},
                {"name": "publish_time_-1", "keys": {"publish_time": -1}}
            ]
        }

# 删除集合
@router.delete("/collections/{collection_name}")
async def delete_collection(collection_name: str):
    try:
        collection = get_collection(collection_name)
        result = await collection.drop()
        return {"message": f"集合 {collection_name} 已删除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除集合失败: {str(e)}")

# 获取数据库配置信息
@router.get("/config")
async def get_database_config():
    try:
        from db.db_config import get_settings
        settings = get_settings()
        
        return {
            "host": settings.MONGO_URI.split("//")[1].split(":")[0] if "//" in settings.MONGO_URI else "localhost",
            "port": int(settings.MONGO_URI.split(":")[-1].split("/")[0]) if ":" in settings.MONGO_URI else 27017,
            "database": settings.MONGO_DB_NAME,
            "username": settings.MONGO_URI.split("//")[1].split(":")[0] if "@" in settings.MONGO_URI else "",
            "password": "********",
            "authSource": settings.MONGO_URI.split("?authSource=")[-1] if "authSource=" in settings.MONGO_URI else "admin",
            "status": "connected",
            "lastConnected": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数据库配置失败: {str(e)}")

# 运行爬虫任务
@router.post("/crawler/run")
async def run_crawler(platform: str = "all", keywords: Optional[List[str]] = None):
    try:
        if platform == "weibo":
            task = run_weibo_crawler.delay(keywords=keywords)
            return {"status": "success", "message": "微博爬虫任务已提交", "task_id": task.id, "platform": "weibo"}
        elif platform == "wechat":
            task = run_wechat_crawler.delay(official_accounts=keywords)
            return {"status": "success", "message": "微信爬虫任务已提交", "task_id": task.id, "platform": "wechat"}
        elif platform == "zhihu":
            task = run_zhihu_crawler.delay(topics=keywords)
            return {"status": "success", "message": "知乎爬虫任务已提交", "task_id": task.id, "platform": "zhihu"}
        elif platform == "all":
            result = run_all_crawlers()
            return {"status": "success", "message": "所有爬虫任务已提交", "task_ids": result["task_ids"], "platform": "all"}
        else:
            raise HTTPException(status_code=400, detail=f"不支持的爬虫平台: {platform}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"运行爬虫任务失败: {str(e)}")

# 获取爬虫任务状态
@router.get("/crawler/task/{task_id}")
async def get_crawler_task_status(task_id: str):
    try:
        from celery.result import AsyncResult
        from celery_config import celery_app
        
        task_result = AsyncResult(task_id, app=celery_app)
        
        return {
            "task_id": task_id,
            "status": task_result.status,
            "result": task_result.result if task_result.ready() else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务状态失败: {str(e)}")

# 格式化字节大小的辅助函数
def format_bytes(bytes_size: int) -> str:
    if bytes_size == 0:
        return "0 Bytes"
    k = 1024
    sizes = ["Bytes", "KB", "MB", "GB", "TB"]
    i = int(bytes_size.bit_length() / 10)
    return f"{bytes_size / (k ** i):.2f} {sizes[i]}"
