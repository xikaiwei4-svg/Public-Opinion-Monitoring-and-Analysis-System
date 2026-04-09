# MySQL数据模型
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, Float, Boolean
from sqlalchemy.sql import func
from db.mysql_config import Base
import enum

# 枚举类型
class SourcePlatform(str, enum.Enum):
    WEIBO = "weibo"
    WECHAT = "wechat"
    ZHIHU = "zhihu"
    OTHER = "other"

class SentimentType(str, enum.Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

# 舆情数据模型
class Opinion(Base):
    __tablename__ = "opinions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(500), nullable=True, comment="标题")
    content = Column(Text, nullable=True, comment="内容")
    source_platform = Column(String(50), nullable=True, comment="来源平台")
    source_url = Column(String(1000), nullable=True, comment="来源链接")
    author = Column(String(200), nullable=True, comment="作者")
    author_id = Column(String(200), nullable=True, comment="作者ID")
    publish_time = Column(DateTime, nullable=True, comment="发布时间")
    crawl_time = Column(DateTime, default=func.now(), comment="抓取时间")
    sentiment = Column(String(20), default="neutral", comment="情感倾向")
    sentiment_score = Column(Float, default=0.0, comment="情感分数")
    keywords = Column(String(500), nullable=True, comment="关键词")
    read_count = Column(Integer, default=0, comment="阅读数")
    like_count = Column(Integer, default=0, comment="点赞数")
    comment_count = Column(Integer, default=0, comment="评论数")
    share_count = Column(Integer, default=0, comment="分享数")
    is_hot = Column(Boolean, default=False, comment="是否热点")
    hot_score = Column(Float, default=0.0, comment="热度分数")
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "source_platform": self.source_platform,
            "source_url": self.source_url,
            "author": self.author,
            "author_id": self.author_id,
            "publish_time": self.publish_time.isoformat() if self.publish_time else None,
            "crawl_time": self.crawl_time.isoformat() if self.crawl_time else None,
            "sentiment": self.sentiment,
            "sentiment_score": self.sentiment_score,
            "keywords": self.keywords,
            "read_count": self.read_count,
            "like_count": self.like_count,
            "comment_count": self.comment_count,
            "share_count": self.share_count,
            "is_hot": self.is_hot,
            "hot_score": self.hot_score
        }

# 用户模型
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, comment="用户名")
    email = Column(String(200), unique=True, nullable=True, comment="邮箱")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    role = Column(String(50), default="user", comment="角色")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    last_login = Column(DateTime, nullable=True, comment="最后登录时间")

# 热点话题模型
class HotTopic(Base):
    __tablename__ = "hot_topics"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    topic = Column(String(500), nullable=False, comment="话题")
    keyword = Column(String(200), nullable=True, comment="关键词")
    mention_count = Column(Integer, default=0, comment="提及次数")
    sentiment_distribution = Column(String(500), nullable=True, comment="情感分布")
    trend = Column(String(50), default="stable", comment="趋势")
    first_seen = Column(DateTime, nullable=True, comment="首次出现")
    last_seen = Column(DateTime, default=func.now(), comment="最后出现")
    related_opinions = Column(String(1000), nullable=True, comment="相关舆情ID")

# 趋势数据模型
class TrendData(Base):
    __tablename__ = "trend_data"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date = Column(DateTime, nullable=False, comment="日期")
    platform = Column(String(50), nullable=True, comment="平台")
    total_count = Column(Integer, default=0, comment="总数")
    positive_count = Column(Integer, default=0, comment="正面数")
    negative_count = Column(Integer, default=0, comment="负面数")
    neutral_count = Column(Integer, default=0, comment="中性数")
    hot_topics = Column(String(1000), nullable=True, comment="热门话题")

# 爬虫任务日志模型
class CrawlerLog(Base):
    __tablename__ = "crawler_logs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_id = Column(String(100), nullable=True, comment="任务ID")
    platform = Column(String(50), nullable=False, comment="平台")
    status = Column(String(50), default="pending", comment="状态")
    start_time = Column(DateTime, default=func.now(), comment="开始时间")
    end_time = Column(DateTime, nullable=True, comment="结束时间")
    total_count = Column(Integer, default=0, comment="抓取总数")
    success_count = Column(Integer, default=0, comment="成功数")
    error_count = Column(Integer, default=0, comment="失败数")
    error_message = Column(Text, nullable=True, comment="错误信息")

# 预警记录模型
class AlertRecord(Base):
    __tablename__ = "alert_records"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    alert_type = Column(String(50), nullable=False, comment="预警类型")
    alert_level = Column(String(20), default="medium", comment="预警级别")
    title = Column(String(500), nullable=False, comment="预警标题")
    description = Column(Text, nullable=True, comment="预警描述")
    opinion_id = Column(Integer, nullable=True, comment="关联舆情ID")
    hot_topic_id = Column(Integer, nullable=True, comment="关联热点话题ID")
    trigger_condition = Column(String(500), nullable=True, comment="触发条件")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    processed = Column(Boolean, default=False, comment="是否已处理")
    processed_at = Column(DateTime, nullable=True, comment="处理时间")
    processed_by = Column(Integer, nullable=True, comment="处理人ID")
    processing_note = Column(Text, nullable=True, comment="处理备注")
