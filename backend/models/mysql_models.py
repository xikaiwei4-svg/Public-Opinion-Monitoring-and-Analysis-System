from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from db.mysql_config import Base
import enum


class SentimentType(str, enum.Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(200), unique=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime)


class Opinion(Base):
    __tablename__ = "opinions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500))
    content = Column(Text)
    source_platform = Column(String(50))
    source_url = Column(String(1000))
    author = Column(String(200))
    author_id = Column(String(200))
    publish_time = Column(DateTime)
    crawl_time = Column(DateTime)
    sentiment = Column(String(20))
    sentiment_score = Column(Float)
    keywords = Column(String(500))
    read_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    is_hot = Column(Boolean, default=False)
    hot_score = Column(Float, default=0.0)

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
            "hot_score": self.hot_score,
        }


class HotTopic(Base):
    __tablename__ = "hot_topics"
    id = Column(Integer, primary_key=True, autoincrement=True)
    topic = Column(String(500), nullable=False)
    keyword = Column(String(200))
    mention_count = Column(Integer, default=0)
    sentiment_distribution = Column(String(500))
    trend = Column(String(50))
    first_seen = Column(DateTime)
    last_seen = Column(DateTime)
    related_opinions = Column(String(1000))


class TrendData(Base):
    __tablename__ = "trend_data"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False)
    platform = Column(String(50))
    total_count = Column(Integer, default=0)
    positive_count = Column(Integer, default=0)
    negative_count = Column(Integer, default=0)
    neutral_count = Column(Integer, default=0)
    hot_topics = Column(String(1000))


class CrawlerLog(Base):
    __tablename__ = "crawler_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(100))
    platform = Column(String(50), nullable=False)
    status = Column(String(50))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    total_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    error_message = Column(Text)


class AlertRecord(Base):
    __tablename__ = "alert_records"
    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_type = Column(String(50), nullable=False)
    alert_level = Column(String(20))
    title = Column(String(500), nullable=False)
    description = Column(Text)
    opinion_id = Column(Integer, ForeignKey("opinions.id"))
    hot_topic_id = Column(Integer, ForeignKey("hot_topics.id"))
    trigger_condition = Column(String(500))
    created_at = Column(DateTime, default=datetime.now)
    processed = Column(Boolean, default=False)
    processed_at = Column(DateTime)
    processed_by = Column(Integer)
    processing_note = Column(Text)
