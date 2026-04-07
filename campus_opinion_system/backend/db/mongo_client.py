from motor.motor_asyncio import AsyncIOMotorClient
from .db_config import get_settings

settings = get_settings()

# 创建MongoDB客户端
client = AsyncIOMotorClient(settings.MONGO_URI)

# 获取数据库
mongo_db = client[settings.MONGO_DB_NAME]

# 获取集合
opinions_collection = mongo_db.opinions
hot_topics_collection = mongo_db.hot_topics
trend_analysis_collection = mongo_db.trend_analysis

async def get_mongo_db():
    """依赖注入函数，返回MongoDB数据库实例"""
    return mongo_db

async def close_mongo_connection():
    """关闭MongoDB连接"""
    client.close()

# MongoDB查询助手函数
async def find_all(collection, query=None, projection=None, sort=None, limit=None):
    """查找集合中的所有文档"""
    query = query or {}
    projection = projection or {}
    cursor = collection.find(query, projection)
    if sort:
        cursor = cursor.sort(sort)
    if limit:
        cursor = cursor.limit(limit)
    return await cursor.to_list(length=limit)

async def find_one(collection, query=None, projection=None):
    """查找集合中的单个文档"""
    query = query or {}
    projection = projection or {}
    return await collection.find_one(query, projection)

async def insert_one(collection, document):
    """插入单个文档"""
    result = await collection.insert_one(document)
    return result.inserted_id

async def insert_many(collection, documents):
    """插入多个文档"""
    result = await collection.insert_many(documents)
    return result.inserted_ids

async def update_one(collection, query, update):
    """更新单个文档"""
    result = await collection.update_one(query, update)
    return result.modified_count

async def delete_one(collection, query):
    """删除单个文档"""
    result = await collection.delete_one(query)
    return result.deleted_count