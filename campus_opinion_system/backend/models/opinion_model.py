from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

# Pydantic模型配置
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class OpinionData(BaseModel):
    """舆情数据模型"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    content: str = Field(..., description="舆情内容")
    source: str = Field(..., description="舆情来源")
    publish_time: datetime = Field(..., description="发布时间")
    sentiment: float = Field(..., ge=-1.0, le=1.0, description="情感得分，-1.0到1.0之间")
    keywords: List[str] = Field(..., description="关键词列表")
    url: Optional[str] = Field(None, description="原始链接")
    views: Optional[int] = Field(0, ge=0, description="浏览量")
    likes: Optional[int] = Field(0, ge=0, description="点赞量")
    comments: Optional[int] = Field(0, ge=0, description="评论量")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class HotTopic(BaseModel):
    """热点话题模型"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    topic: str = Field(..., description="话题名称")
    heat_score: float = Field(..., ge=0, description="热度得分")
    sentiment: float = Field(..., ge=-1.0, le=1.0, description="情感得分")
    keywords: List[str] = Field(..., description="相关关键词")
    occurrence_count: int = Field(..., ge=0, description="出现次数")
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime = Field(..., description="结束日期")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class TrendData(BaseModel):
    """趋势数据模型"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    date: datetime = Field(..., description="日期")
    positive_count: int = Field(..., ge=0, description="正面舆情数量")
    negative_count: int = Field(..., ge=0, description="负面舆情数量")
    neutral_count: int = Field(..., ge=0, description="中性舆情数量")
    keyword: Optional[str] = Field(None, description="关键词")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}