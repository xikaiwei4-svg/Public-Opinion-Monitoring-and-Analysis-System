from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
import pandas as pd
from ..db.mongo_client import opinion_collection, trend_analysis_collection
from ..models.opinion_model import TrendAnalysisModel, TrendDataPoint, SentimentType, SourcePlatform

# 创建路由实例
router = APIRouter(
    prefix="/api/趋势",
    tags=["趋势分析"],
    responses={404: {"description": "未找到"}},
)

@router.get("/analysis", response_model=dict)
async def get_trend_analysis(
    keyword: Optional[str] = Query(None, description="分析关键词"),
    start_date: str = Query(..., description="开始日期，格式：YYYY-MM-DD"),
    end_date: str = Query(..., description="结束日期，格式：YYYY-MM-DD"),
    frequency: str = Query("daily", description="时间频率：daily, weekly, monthly"),
    source: Optional[SourcePlatform] = Query(None, description="来源平台"),
    sentiment_type: Optional[SentimentType] = Query(None, description="情感类型")
):
    """
    获取舆情趋势分析数据
    """
    try:
        # 解析日期
        try:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式错误，应为YYYY-MM-DD")
        
        # 验证日期范围
        if start_datetime > end_datetime:
            raise HTTPException(status_code=400, detail="开始日期不能晚于结束日期")
        
        # 构建查询条件
        query = {"publish_time": {"$gte": start_datetime, "$lte": end_datetime}}
        
        if keyword:
            query["$or"] = [
                {"content": {"$regex": keyword, "$options": "i"}},
                {"keywords": {"$regex": keyword, "$options": "i"}}
            ]
        
        if source:
            query["source_platform"] = source
        
        if sentiment_type:
            query["sentiment_type"] = sentiment_type
        
        # 查询所有符合条件的舆情数据
        cursor = opinion_collection.find(query, {"publish_time": 1, "sentiment_type": 1, "_id": 0})
        opinions = await cursor.to_list(length=None)
        
        if not opinions:
            return {
                "code": 200,
                "data": {
                    "trend_data": [],
                    "keyword": keyword,
                    "time_range": f"{start_date} 至 {end_date}",
                    "total_count": 0
                },
                "message": "未找到匹配的舆情数据"
            }
        
        # 转换为DataFrame进行时间序列分析
        df = pd.DataFrame(opinions)
        
        # 将publish_time转换为日期类型
        df['publish_time'] = pd.to_datetime(df['publish_time'])
        df['date'] = df['publish_time'].dt.date
        
        # 按日期和情感类型分组计数
        grouped = df.groupby(['date', 'sentiment_type']).size().unstack(fill_value=0)
        
        # 确保所有情感类型都存在
        for sentiment in SentimentType:
            if sentiment not in grouped.columns:
                grouped[sentiment] = 0
        
        # 计算每日总数
        grouped['total_count'] = grouped.sum(axis=1)
        
        # 生成趋势数据
        trend_data = []
        for date, row in grouped.iterrows():
            trend_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "positive_count": row.get(SentimentType.POSITIVE, 0),
                "negative_count": row.get(SentimentType.NEGATIVE, 0),
                "neutral_count": row.get(SentimentType.NEUTRAL, 0),
                "total_count": row['total_count']
            })
        
        # 按日期排序
        trend_data.sort(key=lambda x: x["date"])
        
        return {
            "code": 200,
            "data": {
                "trend_data": trend_data,
                "keyword": keyword,
                "time_range": f"{start_date} 至 {end_date}",
                "total_count": sum(item["total_count"] for item in trend_data)
            },
            "message": "分析成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误：{str(e)}")

@router.get("/analysis/sentiment", response_model=dict)
async def get_sentiment_trend(
    start_date: str = Query(..., description="开始日期，格式：YYYY-MM-DD"),
    end_date: str = Query(..., description="结束日期，格式：YYYY-MM-DD"),
    keyword: Optional[str] = Query(None, description="分析关键词")
):
    """
    获取情感倾向趋势分析
    """
    try:
        # 解析日期
        try:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式错误，应为YYYY-MM-DD")
        
        # 构建查询条件
        query = {"publish_time": {"$gte": start_datetime, "$lte": end_datetime}}
        
        if keyword:
            query["$or"] = [
                {"content": {"$regex": keyword, "$options": "i"}},
                {"keywords": {"$regex": keyword, "$options": "i"}}
            ]
        
        # 查询所有符合条件的舆情数据
        cursor = opinion_collection.find(query, {"publish_time": 1, "sentiment": 1, "_id": 0})
        opinions = await cursor.to_list(length=None)
        
        if not opinions:
            return {
                "code": 200,
                "data": {
                    "sentiment_trend": [],
                    "average_sentiment": 0,
                    "keyword": keyword
                },
                "message": "未找到匹配的舆情数据"
            }
        
        # 转换为DataFrame进行分析
        df = pd.DataFrame(opinions)
        df['publish_time'] = pd.to_datetime(df['publish_time'])
        df['date'] = df['publish_time'].dt.date
        
        # 按日期分组计算平均情感值
        daily_sentiment = df.groupby('date')['sentiment'].mean().reset_index()
        daily_sentiment.columns = ['date', 'avg_sentiment']
        
        # 计算总体平均情感值
        avg_sentiment = df['sentiment'].mean()
        
        # 生成趋势数据
        sentiment_trend = []
        for _, row in daily_sentiment.iterrows():
            sentiment_trend.append({
                "date": row['date'].strftime("%Y-%m-%d"),
                "avg_sentiment": round(row['avg_sentiment'], 4)
            })
        
        # 按日期排序
        sentiment_trend.sort(key=lambda x: x["date"])
        
        return {
            "code": 200,
            "data": {
                "sentiment_trend": sentiment_trend,
                "average_sentiment": round(avg_sentiment, 4),
                "keyword": keyword,
                "time_range": f"{start_date} 至 {end_date}"
            },
            "message": "情感趋势分析成功"
        }
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
    """
    获取各平台舆情分布数据
    """
    try:
        # 解析日期
        try:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式错误，应为YYYY-MM-DD")
        
        # 构建查询条件
        query = {"publish_time": {"$gte": start_datetime, "$lte": end_datetime}}
        
        if keyword:
            query["$or"] = [
                {"content": {"$regex": keyword, "$options": "i"}},
                {"keywords": {"$regex": keyword, "$options": "i"}}
            ]
        
        # 按平台分组统计
        pipeline = [
            {"$match": query},
            {"$group": {"_id": "$source_platform", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        platform_stats = await opinion_collection.aggregate(pipeline).to_list(length=None)
        
        # 计算总数
        total_count = sum(stat["count"] for stat in platform_stats)
        
        # 格式化结果
        distribution_data = []
        for stat in platform_stats:
            distribution_data.append({
                "platform": stat["_id"],
                "count": stat["count"],
                "percentage": round((stat["count"] / total_count) * 100, 2) if total_count > 0 else 0
            })
        
        return {
            "code": 200,
            "data": {
                "distribution_data": distribution_data,
                "total_count": total_count,
                "keyword": keyword,
                "time_range": f"{start_date} 至 {end_date}"
            },
            "message": "平台分布分析成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误：{str(e)}")