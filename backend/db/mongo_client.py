from motor.motor_asyncio import AsyncIOMotorClient
from .db_config import get_settings

# 获取配置
settings = get_settings()

# 创建MongoDB客户端
client = AsyncIOMotorClient(settings.MONGO_URI)

# 获取数据库
db = client[settings.MONGO_DB_NAME]

# 集合引用
def get_collection(collection_name: str):
    """获取指定名称的集合"""
    return db[collection_name]

# 示例集合引用
# 舆情数据集合
opinion_collection = get_collection("opinions")
# 热点话题集合
hot_topics_collection = get_collection("hot_topics")
# 趋势分析结果集合
trend_analysis_collection = get_collection("trend_analysis")