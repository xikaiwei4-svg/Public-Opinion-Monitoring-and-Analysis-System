from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
import pandas as pd
from db.mysql_config import get_db
from models.mysql_models import Opinion, TrendData
from sqlalchemy.orm import Session
from sqlalchemy import func

# 创建路由实例
router = APIRouter(
    prefix="/api/trend",
    tags=["趋势分析"],
    responses={404: {"description": "未找到"}},
)

@router.get("/analysis", response_model=dict)
async def get_trend_analysis(
    keyword: Optional[str] = Query(None, description="分析关键词"),
    start_date: str = Query(..., description="开始日期，格式：YYYY-MM-DD"),
    end_date: str = Query(..., description="结束日期，格式：YYYY-MM-DD"),
    frequency: str = Query("daily", description="时间频率：daily, weekly, monthly"),
    source: Optional[str] = Query(None, description="来源平台"),
    sentiment_type: Optional[str] = Query(None, description="情感类型")
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
        
        # 获取数据库会话
        db = next(get_db())
        
        # 构建查询
        query = db.query(
            func.date(Opinion.publish_time).label('date'),
            Opinion.sentiment,
            func.count(Opinion.id).label('count')
        ).filter(
            Opinion.publish_time >= start_datetime,
            Opinion.publish_time <= end_datetime
        )
        
        if keyword:
            query = query.filter(
                func.or_(
                    Opinion.content.like(f"%{keyword}%"),
                    Opinion.keywords.like(f"%{keyword}%")
                )
            )
        
        if source:
            query = query.filter(Opinion.source_platform == source)
        
        if sentiment_type:
            query = query.filter(Opinion.sentiment == sentiment_type)
        
        # 按日期和情感类型分组
        results = query.group_by(
            func.date(Opinion.publish_time),
            Opinion.sentiment
        ).all()
        
        # 转换为DataFrame进行分析
        df = pd.DataFrame([
            {
                'date': str(result.date),
                'sentiment': result.sentiment,
                'count': result.count
            }
            for result in results
        ])
        
        # 确保所有情感类型都存在
        if not df.empty:
            # 按日期分组
            grouped = df.groupby('date').agg({
                'count': 'sum',
                'sentiment': lambda x: list(x)
            }).reset_index()
            
            # 生成趋势数据
            trend_data = []
            for _, row in grouped.iterrows():
                # 计算各情感类型的数量
                positive_count = df[(df['date'] == row['date']) & (df['sentiment'] == 'positive')]['count'].sum()
                negative_count = df[(df['date'] == row['date']) & (df['sentiment'] == 'negative')]['count'].sum()
                neutral_count = df[(df['date'] == row['date']) & (df['sentiment'] == 'neutral')]['count'].sum()
                
                trend_data.append({
                    "date": row['date'],
                    "positive_count": int(positive_count),
                    "negative_count": int(negative_count),
                    "neutral_count": int(neutral_count),
                    "total_count": int(row['count'])
                })
            
            # 按日期排序
            trend_data.sort(key=lambda x: x["date"])
        else:
            trend_data = []
        
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
        
        # 获取数据库会话
        db = next(get_db())
        
        # 构建查询
        query = db.query(
            Opinion.source_platform,
            func.count(Opinion.id).label('count')
        ).filter(
            Opinion.publish_time >= start_datetime,
            Opinion.publish_time <= end_datetime
        )
        
        if keyword:
            query = query.filter(
                func.or_(
                    Opinion.content.like(f"%{keyword}%"),
                    Opinion.keywords.like(f"%{keyword}%")
                )
            )
        
        # 按平台分组
        results = query.group_by(Opinion.source_platform).all()
        
        # 计算总数
        total_count = sum(result.count for result in results)
        
        # 格式化结果
        distribution_data = []
        for result in results:
            percentage = round((result.count / total_count) * 100, 2) if total_count > 0 else 0
            # 过滤掉数量为0和占比小于1%的平台
            if result.count > 0 and percentage >= 1:
                distribution_data.append({
                    "platform": result.source_platform,
                    "count": result.count,
                    "percentage": percentage
                })
        
        # 按数量排序
        distribution_data.sort(key=lambda x: x["count"], reverse=True)
        
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