"""数据库工具模块"""
import logging
from typing import Dict, List, Any, Optional
from pymongo import ASCENDING, DESCENDING
from db.mongo_client import opinion_collection, hot_topics_collection

logger = logging.getLogger(__name__)

class DBUtils:
    """数据库工具类"""
    
    @staticmethod
    async def get_opinion_statistics(start_time=None, end_time=None) -> Dict[str, Any]:
        """获取舆情统计数据"""
        try:
            # 构建查询条件
            query = {}
            if start_time:
                query["publish_time"] = {"$gte": start_time}
            if end_time:
                if "publish_time" in query:
                    query["publish_time"]["$lte"] = end_time
                else:
                    query["publish_time"] = {"$lte": end_time}
            
            # 获取总数
            total_opinions = await opinion_collection.count_documents(query)
            
            # 按情感类型统计
            sentiment_pipeline = [
                {"$match": query},
                {"$group": {"_id": "$sentiment_type", "count": {"$sum": 1}}}
            ]
            sentiment_result = await opinion_collection.aggregate(sentiment_pipeline).to_list(length=10)
            
            sentiment_counts = {
                "positive": 0,
                "negative": 0,
                "neutral": 0
            }
            for item in sentiment_result:
                if item["_id"] in sentiment_counts:
                    sentiment_counts[item["_id"]] = item["count"]
            
            # 获取平台分布
            platform_pipeline = [
                {"$match": query},
                {"$group": {"_id": "$source_platform", "count": {"$sum": 1}}},
                {"$sort": {"count": DESCENDING}}
            ]
            platform_result = await opinion_collection.aggregate(platform_pipeline).to_list(length=20)
            
            platform_distribution = []
            for item in platform_result:
                percentage = (item["count"] / total_opinions * 100) if total_opinions > 0 else 0
                platform_distribution.append({
                    "platform": item["_id"],
                    "count": item["count"],
                    "percentage": round(percentage, 2)
                })
            
            return {
                "total_opinions": total_opinions,
                "positive_count": sentiment_counts["positive"],
                "negative_count": sentiment_counts["negative"],
                "neutral_count": sentiment_counts["neutral"],
                "platform_distribution": platform_distribution
            }
            
        except Exception as e:
            logger.error(f"获取舆情统计数据失败: {e}")
            raise
    
    @staticmethod
    async def get_opinion_list(
        page: int = 1,
        page_size: int = 10,
        keyword: Optional[str] = None,
        source: Optional[str] = None,
        sentiment_type: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        is_sensitive: Optional[bool] = None
    ) -> Dict[str, Any]:
        """获取舆情列表"""
        try:
            # 构建查询条件
            query = {}
            
            if keyword:
                query["$or"] = [
                    {"content": {"$regex": keyword, "$options": "i"}},
                    {"keywords": {"$in": [keyword]}}
                ]
            
            if source:
                query["source_platform"] = source
            
            if sentiment_type:
                query["sentiment_type"] = sentiment_type
            
            if start_time:
                query["publish_time"] = {"$gte": start_time}
            if end_time:
                if "publish_time" in query:
                    query["publish_time"]["$lte"] = end_time
                else:
                    query["publish_time"] = {"$lte": end_time}
            
            if is_sensitive is not None:
                query["is_sensitive"] = is_sensitive
            
            # 获取总数
            total = await opinion_collection.count_documents(query)
            
            # 分页查询
            skip = (page - 1) * page_size
            cursor = opinion_collection.find(query).sort("publish_time", DESCENDING).skip(skip).limit(page_size)
            items = await cursor.to_list(length=page_size)
            
            return {
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size
            }
            
        except Exception as e:
            logger.error(f"获取舆情列表失败: {e}")
            raise
    
    @staticmethod
    async def get_hot_topics(days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
        """获取热点话题"""
        try:
            from datetime import datetime, timedelta
            
            # 计算时间范围
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            # 查询热点话题
            query = {
                "start_time": {"$gte": start_time},
                "end_time": {"$lte": end_time}
            }
            
            cursor = hot_topics_collection.find(query).sort("heat_score", DESCENDING).limit(limit)
            hot_topics = await cursor.to_list(length=limit)
            
            return hot_topics
            
        except Exception as e:
            logger.error(f"获取热点话题失败: {e}")
            raise
    
    @staticmethod
    async def get_trend_data(days: int = 7, platform: Optional[str] = None) -> Dict[str, Any]:
        """获取趋势数据"""
        try:
            from datetime import datetime, timedelta
            
            # 计算时间范围
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            # 构建查询条件
            query = {
                "publish_time": {"$gte": start_time, "$lte": end_time}
            }
            
            if platform:
                query["source_platform"] = platform
            
            # 按日期分组统计
            pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": {
                            "$dateToString": {
                                "format": "%Y-%m-%d",
                                "date": "$publish_time"
                            }
                        },
                        "count": {"$sum": 1},
                        "total_heat": {"$sum": "$heat_score"},
                        "positive": {"$sum": {"$cond": [{"$eq": ["$sentiment_type", "positive"]}, 1, 0]}},
                        "negative": {"$sum": {"$cond": [{"$eq": ["$sentiment_type", "negative"]}, 1, 0]}},
                        "neutral": {"$sum": {"$cond": [{"$eq": ["$sentiment_type", "neutral"]}, 1, 0]}}
                    }
                },
                {"$sort": {"_id": ASCENDING}}
            ]
            
            result = await opinion_collection.aggregate(pipeline).to_list(length=days)
            
            # 转换结果格式
            trend_data = []
            sentiment_data = []
            
            for item in result:
                date = item["_id"]
                count = item["count"]
                avg_heat = round(item["total_heat"] / count, 2) if count > 0 else 0
                
                trend_data.append({
                    "date": date,
                    "count": count,
                    "heat": avg_heat
                })
                
                sentiment_data.append({
                    "date": date,
                    "positive": item["positive"],
                    "negative": item["negative"],
                    "neutral": item["neutral"]
                })
            
            # 获取平台分布
            platform_pipeline = [
                {"$match": query},
                {"$group": {"_id": "$source_platform", "count": {"$sum": 1}}},
                {"$sort": {"count": DESCENDING}}
            ]
            
            platform_result = await opinion_collection.aggregate(platform_pipeline).to_list(length=20)
            total_count = sum(item["count"] for item in platform_result)
            
            platform_distribution = []
            for item in platform_result:
                percentage = (item["count"] / total_count * 100) if total_count > 0 else 0
                platform_distribution.append({
                    "platform": item["_id"],
                    "count": item["count"],
                    "percentage": round(percentage, 2)
                })
            
            return {
                "trend_data": trend_data,
                "sentiment_data": sentiment_data,
                "platform_distribution": platform_distribution
            }
            
        except Exception as e:
            logger.error(f"获取趋势数据失败: {e}")
            raise

# 创建全局实例
db_utils = DBUtils()
