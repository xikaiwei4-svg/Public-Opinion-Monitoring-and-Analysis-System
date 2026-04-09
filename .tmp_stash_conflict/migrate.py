#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本
用于初始化MySQL数据库并插入示例数据
"""

import os
import sys
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.mysql_config import engine, Base, SessionLocal
from models.mysql_models import Opinion, User, HotTopic, TrendData, CrawlerLog
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_database():
    """初始化数据库，创建所有表"""
    logger.info("开始初始化数据库...")
    try:
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建成功")
        return True
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        return False

def insert_sample_data():
    """插入示例数据"""
    logger.info("开始插入示例数据...")
    db = SessionLocal()
    try:
        # 检查是否已有数据
        if db.query(Opinion).count() > 0:
            logger.info("数据库已有数据，跳过插入示例数据")
            return True
        
        # 插入用户数据
        users = [
            User(
                username="admin",
                email="admin@example.com",
                password_hash="$2b$12$LQvQp4Y4K5K5K5K5K5K5eK5K5K5K5K5K5K5K5K5K5K5K5K5",
                role="admin",
                is_active=True
            ),
            User(
                username="user",
                email="user@example.com",
                password_hash="$2b$12$LQvQp4Y4K5K5K5K5K5eK5K5K5K5K5K5K5K5K5K5K5K5K5",
                role="user",
                is_active=True
            )
        ]
        db.add_all(users)
        db.commit()
        logger.info("用户数据插入成功")
        
        # 插入舆情数据
        opinions = []
        platforms = ["weibo", "wechat", "zhihu", "other"]
        sentiments = ["positive", "negative", "neutral"]
        
        for i in range(50):
            opinion = Opinion(
                title=f"校园舆情话题示例{i+1}",
                content=f"这是第{i+1}条校园舆情数据，内容涉及校园生活、学习环境、食堂服务等方面的讨论。",
                source_platform=platforms[i % len(platforms)],
                source_url=f"https://example.com/opinion/{i+1}",
                author=f"用户{i+1}",
                publish_time=datetime.now() - timedelta(days=i % 30),
                sentiment=sentiments[i % len(sentiments)],
                sentiment_score=(i % 10) / 10.0,
                keywords=f"校园,舆情,话题{i+1}",
                read_count=100 + i * 10,
                like_count=10 + i,
                comment_count=5 + i // 5,
                share_count=3 + i // 10,
                is_hot=i < 10,
                hot_score=(i % 10) / 10.0
            )
            opinions.append(opinion)
        
        db.add_all(opinions)
        db.commit()
        logger.info("舆情数据插入成功")
        
        # 插入热点话题数据
        hot_topics = [
            HotTopic(
                topic="校园食堂改革",
                keyword="食堂,改革",
                mention_count=156,
                sentiment_distribution='{"positive": 52, "negative": 34, "neutral": 70}',
                trend="rising",
                first_seen=datetime.now() - timedelta(days=7),
                last_seen=datetime.now()
            ),
            HotTopic(
                topic="期末考试安排",
                keyword="考试,安排",
                mention_count=98,
                sentiment_distribution='{"positive": 23, "negative": 65, "neutral": 10}',
                trend="stable",
                first_seen=datetime.now() - timedelta(days=5),
                last_seen=datetime.now()
            ),
            HotTopic(
                topic="校园网络升级",
                keyword="网络,升级",
                mention_count=78,
                sentiment_distribution='{"positive": 65, "negative": 10, "neutral": 3}',
                trend="rising",
                first_seen=datetime.now() - timedelta(days=3),
                last_seen=datetime.now()
            ),
            HotTopic(
                topic="宿舍环境改善",
                keyword="宿舍,环境",
                mention_count=65,
                sentiment_distribution='{"positive": 45, "negative": 10, "neutral": 10}',
                trend="stable",
                first_seen=datetime.now() - timedelta(days=10),
                last_seen=datetime.now()
            ),
            HotTopic(
                topic="校园活动安排",
                keyword="活动,安排",
                mention_count=45,
                sentiment_distribution='{"positive": 30, "negative": 5, "neutral": 10}',
                trend="declining",
                first_seen=datetime.now() - timedelta(days=15),
                last_seen=datetime.now()
            )
        ]
        
        db.add_all(hot_topics)
        db.commit()
        logger.info("热点话题数据插入成功")
        
        # 插入趋势数据
        trend_data = []
        for i in range(30):
            date = datetime.now() - timedelta(days=29 - i)
            trend = TrendData(
                date=date,
                platform="all",
                total_count=50 + i * 5,
                positive_count=20 + i * 2,
                negative_count=15 + i,
                neutral_count=15 + i * 2,
                hot_topics="校园食堂改革,期末考试安排"
            )
            trend_data.append(trend)
        
        db.add_all(trend_data)
        db.commit()
        logger.info("趋势数据插入成功")
        
        # 插入爬虫日志
        crawler_log = CrawlerLog(
            platform="all",
            status="success",
            start_time=datetime.now() - timedelta(hours=2),
            end_time=datetime.now() - timedelta(hours=1),
            total_count=50,
            success_count=50,
            error_count=0,
            error_message=""
        )
        db.add(crawler_log)
        db.commit()
        logger.info("爬虫日志插入成功")
        
        logger.info("所有示例数据插入完成")
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"插入示例数据失败: {e}")
        return False
    finally:
        db.close()

def main():
    """主函数"""
    logger.info("开始数据库迁移...")
    
    # 初始化数据库
    if not init_database():
        logger.error("数据库初始化失败，退出")
        return 1
    
    # 插入示例数据
    if not insert_sample_data():
        logger.error("插入示例数据失败")
        return 1
    
    logger.info("数据库迁移完成")
    return 0

if __name__ == "__main__":
    sys.exit(main())
