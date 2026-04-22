#!/usr/bin/env python3
# 热点话题数据同步脚本

import sys
import os
import re
from datetime import datetime, timedelta
from collections import Counter

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.mysql_config import get_db
from models.mysql_models import HotTopic, Opinion
from sqlalchemy.orm import Session
from sqlalchemy import func

def extract_keywords(content: str) -> list:
    """
    从文本中提取关键词
    """
    # 简单的关键词提取，实际应用中可以使用更复杂的NLP方法
    keywords = []
    
    # 常见的校园相关关键词
    campus_keywords = [
        '校园', '学校', '学生', '教师', '教育', '考试', '课程', '活动',
        '宿舍', '食堂', '图书馆', '操场', '实验室', '社团', '学生会',
        '奖学金', '助学金', '就业', '实习', '留学', '考研', '保研'
    ]
    
    # 提取关键词
    for keyword in campus_keywords:
        if keyword in content:
            keywords.append(keyword)
    
    return keywords

def sync_hot_topics(days: int = 365) -> dict:
    """
    同步热点话题数据
    """
    try:
        # 获取数据库会话
        db = next(get_db())
        
        # 计算时间范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 检查是否有舆情数据
        earliest_date = db.query(func.min(Opinion.publish_time)).scalar()
        if earliest_date:
            start_date = earliest_date
        
        print(f"开始同步热点话题数据，时间范围：{start_date} 至 {end_date}")
        
        # 获取时间范围内的舆情数据
        opinions = db.query(Opinion).filter(
            Opinion.publish_time >= start_date,
            Opinion.publish_time <= end_date
        ).all()
        
        print(f"获取到 {len(opinions)} 条舆情数据")
        
        # 提取关键词
        all_keywords = []
        for opinion in opinions:
            if opinion.keywords:
                # 如果舆情数据已经有关键词，直接使用
                keywords = opinion.keywords.split(',')
                all_keywords.extend(keywords)
            else:
                # 否则从内容中提取
                if opinion.content:
                    keywords = extract_keywords(opinion.content)
                    all_keywords.extend(keywords)
        
        print(f"提取到 {len(all_keywords)} 个关键词")
        
        # 统计关键词出现次数
        keyword_counter = Counter(all_keywords)
        print(f"统计到 {len(keyword_counter)} 个不同的关键词")
        
        # 筛选热点话题（出现次数大于等于10）
        hot_keywords = [(keyword, count) for keyword, count in keyword_counter.items() if count >= 10]
        hot_keywords.sort(key=lambda x: x[1], reverse=True)
        
        print(f"筛选出 {len(hot_keywords)} 个热点话题")
        
        # 更新或创建热点话题记录
        updated_topics = []
        created_topics = []
        
        for keyword, mention_count in hot_keywords:
            # 检查是否已存在该热点话题
            existing_topic = db.query(HotTopic).filter(
                HotTopic.keyword == keyword
            ).first()
            
            if existing_topic:
                # 更新现有热点话题
                existing_topic.mention_count = mention_count
                existing_topic.last_seen = end_date
                existing_topic.trend = "rising" if mention_count > existing_topic.mention_count else "stable"
                updated_topics.append(keyword)
            else:
                # 创建新热点话题
                new_topic = HotTopic(
                    topic=keyword + "相关话题",
                    keyword=keyword,
                    mention_count=mention_count,
                    first_seen=start_date,
                    last_seen=end_date,
                    trend="rising"
                )
                db.add(new_topic)
                created_topics.append(keyword)
        
        # 提交更改
        db.commit()
        
        print(f"更新了 {len(updated_topics)} 个热点话题")
        print(f"创建了 {len(created_topics)} 个新热点话题")
        
        # 获取更新后的热点话题总数
        total_topics = db.query(HotTopic).count()
        print(f"当前热点话题总数：{total_topics}")
        
        return {
            "status": "success",
            "message": "热点话题数据同步完成",
            "statistics": {
                "total_opinions": len(opinions),
                "total_keywords": len(keyword_counter),
                "hot_topics": len(hot_keywords),
                "updated_topics": len(updated_topics),
                "created_topics": len(created_topics),
                "total_topics": total_topics
            }
        }
        
    except Exception as e:
        print(f"同步热点话题数据失败：{str(e)}")
        return {
            "status": "error",
            "message": f"同步热点话题数据失败：{str(e)}"
        }

if __name__ == "__main__":
    # 同步最近7天的热点话题
    result = sync_hot_topics(7)
    print(result)
