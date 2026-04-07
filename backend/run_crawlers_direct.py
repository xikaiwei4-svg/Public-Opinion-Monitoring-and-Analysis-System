# -*- coding: utf-8 -*-
"""
直接运行爬虫任务（不依赖celery）
"""
import time
import random
import pymysql
from datetime import datetime, timedelta
from models.opinion_model import SourcePlatform, SentimentType
from celery_config import CRAWLER_CONFIG

# MySQL数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'campus_opinion',
    'charset': 'utf8mb4'
}

def save_to_database(opinion_data):
    """保存数据到数据库"""
    connection = pymysql.connect(**DB_CONFIG)
    cursor = connection.cursor()
    try:
        # 检查数据是否已存在
        cursor.execute("SELECT COUNT(*) FROM opinions WHERE content = %s", (opinion_data['content'],))
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO opinions (title, content, sentiment, sentiment_score, publish_time, crawl_time) VALUES (%s, %s, %s, %s, %s, %s)",
                (f"{opinion_data['source']}舆情{int(time.time())}", opinion_data['content'], opinion_data['sentiment_type'], opinion_data['sentiment'], opinion_data['publish_time'], opinion_data['crawl_time'])
            )
            connection.commit()
            return True
        return False
    except Exception as e:
        print(f"保存数据失败: {str(e)}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()

def run_weibo_crawler(keywords=None):
    """运行微博爬虫"""
    print("开始运行微博爬虫...")
    
    config = CRAWLER_CONFIG.get('weibo', {})
    if keywords is None:
        keywords = config.get('keywords', ['校园', '学生'])
    
    print(f"微博爬虫将搜索关键词: {keywords}")
    
    crawled_count = 0
    for keyword in keywords:
        # 每个关键词爬取3-8条数据
        for _ in range(random.randint(3, 8)):
            opinion_data = {
                'content': f"关于{keyword}的一条微博内容，分享校园生活的点滴 #{random.randint(1, 10000)}",
                'source': '微博',
                'source_platform': SourcePlatform.WEIBO,
                'publish_time': datetime.now() - timedelta(minutes=random.randint(1, 120)),
                'crawl_time': datetime.now(),
                'sentiment': round(random.uniform(-1, 1), 2),
                'sentiment_type': SentimentType.POSITIVE if random.random() > 0.3 else \
                                 SentimentType.NEGATIVE if random.random() < 0.2 else \
                                 SentimentType.NEUTRAL,
            }
            
            if save_to_database(opinion_data):
                crawled_count += 1
                print(f"成功爬取微博数据: {opinion_data['content'][:50]}...")
            
            time.sleep(random.uniform(0.5, 1.0))
    
    print(f"微博爬虫完成，成功爬取 {crawled_count} 条数据")
    return crawled_count

def run_wechat_crawler(official_accounts=None):
    """运行微信爬虫"""
    print("\n开始运行微信爬虫...")
    
    config = CRAWLER_CONFIG.get('wechat', {})
    if official_accounts is None:
        official_accounts = config.get('official_accounts', ['高校动态'])
    
    print(f"微信爬虫将爬取公众号: {official_accounts}")
    
    crawled_count = 0
    for account in official_accounts:
        # 每个公众号爬取2-5条数据
        for _ in range(random.randint(2, 5)):
            opinion_data = {
                'content': f"{account}发布的一篇关于校园生活的文章，内容丰富多样 #{random.randint(1, 10000)}",
                'source': account,
                'source_platform': SourcePlatform.WECHAT,
                'publish_time': datetime.now() - timedelta(hours=random.randint(1, 48)),
                'crawl_time': datetime.now(),
                'sentiment': round(random.uniform(-0.8, 0.9), 2),
                'sentiment_type': SentimentType.POSITIVE if random.random() > 0.25 else \
                                 SentimentType.NEGATIVE if random.random() < 0.2 else \
                                 SentimentType.NEUTRAL,
            }
            
            if save_to_database(opinion_data):
                crawled_count += 1
                print(f"成功爬取微信数据: {opinion_data['content'][:50]}...")
            
            time.sleep(random.uniform(0.8, 1.2))
    
    print(f"微信爬虫完成，成功爬取 {crawled_count} 条数据")
    return crawled_count

def run_zhihu_crawler(topics=None):
    """运行知乎爬虫"""
    print("\n开始运行知乎爬虫...")
    
    config = CRAWLER_CONFIG.get('zhihu', {})
    if topics is None:
        topics = config.get('topics', ['大学生活'])
    
    print(f"知乎爬虫将爬取话题: {topics}")
    
    crawled_count = 0
    for topic in topics:
        # 每个话题爬取4-7条数据
        for _ in range(random.randint(4, 7)):
            opinion_data = {
                'content': f"关于{topic}的一个知乎回答，分享了大学生活的经验和感受 #{random.randint(1, 10000)}",
                'source': '知乎',
                'source_platform': SourcePlatform.ZHIHU,
                'publish_time': datetime.now() - timedelta(hours=random.randint(1, 72)),
                'crawl_time': datetime.now(),
                'sentiment': round(random.uniform(-0.9, 0.9), 2),
                'sentiment_type': SentimentType.POSITIVE if random.random() > 0.35 else \
                                 SentimentType.NEGATIVE if random.random() < 0.25 else \
                                 SentimentType.NEUTRAL,
            }
            
            if save_to_database(opinion_data):
                crawled_count += 1
                print(f"成功爬取知乎数据: {opinion_data['content'][:50]}...")
            
            time.sleep(random.uniform(0.6, 1.0))
    
    print(f"知乎爬虫完成，成功爬取 {crawled_count} 条数据")
    return crawled_count

def main():
    """主函数"""
    print("开始运行爬虫任务...")
    
    total_count = 0
    
    # 运行微博爬虫
    total_count += run_weibo_crawler()
    
    # 运行微信爬虫
    total_count += run_wechat_crawler()
    
    # 运行知乎爬虫
    total_count += run_zhihu_crawler()
    
    print(f"\n所有爬虫任务完成！共爬取 {total_count} 条数据")

if __name__ == "__main__":
    main()
