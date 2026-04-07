from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class SentimentType(str, Enum):
    """情感类型枚举"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class SourcePlatform(str, Enum):
    """数据源平台枚举"""
    WEIBO = "weibo"
    WECHAT = "wechat"
    ZHIHU = "zhihu"
    FORUM = "forum"
    OTHER = "other"

class OpinionModel(BaseModel):
    """舆情数据模型"""
    id: str = Field(..., description="舆情ID")
    content: str = Field(..., description="舆情内容")
    source: str = Field(..., description="数据来源")
    source_platform: SourcePlatform = Field(..., description="来源平台")
    publish_time: datetime = Field(..., description="发布时间")
    crawl_time: datetime = Field(default_factory=datetime.now, description="抓取时间")
    sentiment: float = Field(..., ge=-1.0, le=1.0, description="情感分数[-1,1]")
    sentiment_type: SentimentType = Field(..., description="情感类型")
    keywords: List[str] = Field(default_factory=list, description="关键词列表")
    url: Optional[str] = Field(None, description="原文链接")
    views: Optional[int] = Field(0, ge=0, description="浏览量")
    likes: Optional[int] = Field(0, ge=0, description="点赞数")
    comments: Optional[int] = Field(0, ge=0, description="评论数")
    shares: Optional[int] = Field(0, ge=0, description="分享数")
    heat_score: Optional[float] = Field(0.0, ge=0.0, le=100.0, description="热度分数[0,100]")
    is_sensitive: Optional[bool] = Field(False, description="是否敏感内容")
    sensitive_level: Optional[int] = Field(0, ge=0, le=5, description="敏感级别[0-5]")
    location: Optional[str] = Field(None, description="地点信息")
    user_info: Optional[Dict] = Field(None, description="用户信息")
    raw_data: Optional[Dict] = Field(None, description="原始数据")
    
    @validator('sentiment_type', pre=True, always=True)
    def set_sentiment_type(cls, v, values):
        """根据情感分数自动设置情感类型"""
        if 'sentiment' in values:
            if values['sentiment'] > 0.2:
                return SentimentType.POSITIVE
            elif values['sentiment'] < -0.2:
                return SentimentType.NEGATIVE
            else:
                return SentimentType.NEUTRAL
        return v

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S')
        }

class HotTopicModel(BaseModel):
    """热点话题模型"""
    id: str = Field(..., description="热点ID")
    topic: str = Field(..., description="话题名称")
    keywords: List[str] = Field(default_factory=list, description="相关关键词")
    heat_score: float = Field(..., ge=0.0, le=100.0, description="热度分数")
    sentiment: float = Field(..., ge=-1.0, le=1.0, description="情感分数")
    related_opinions_count: int = Field(..., ge=0, description="相关舆情数量")
    start_time: datetime = Field(..., description="话题起始时间")
    end_time: datetime = Field(..., description="话题结束时间")
    trend: str = Field(..., description="发展趋势: rising, stable, falling")
    platforms: List[SourcePlatform] = Field(default_factory=list, description="涉及平台")
    details: Optional[Dict] = Field(None, description="详细信息")

class TrendDataPoint(BaseModel):
    """趋势数据点"""
    date: str = Field(..., description="日期")
    positive_count: int = Field(..., ge=0, description="正面舆情数量")
    negative_count: int = Field(..., ge=0, description="负面舆情数量")
    neutral_count: int = Field(..., ge=0, description="中性舆情数量")
    total_count: int = Field(..., ge=0, description="总舆情数量")

class TrendAnalysisModel(BaseModel):
    """趋势分析结果模型"""
    id: str = Field(..., description="分析ID")
    keyword: Optional[str] = Field(None, description="分析关键词")
    start_date: str = Field(..., description="开始日期")
    end_date: str = Field(..., description="结束日期")
    trend_data: List[TrendDataPoint] = Field(default_factory=list, description="趋势数据")
    analysis_time: datetime = Field(default_factory=datetime.now, description="分析时间")
    summary: Optional[str] = Field(None, description="分析总结")