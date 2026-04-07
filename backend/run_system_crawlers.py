# -*- coding: utf-8 -*-
"""
运行系统原有的爬虫任务
"""
import sys
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

def run_system_weibo_crawler():
    """运行系统原有的微博爬虫"""
    print("开始运行系统微博爬虫...")
    
    config = CRAWLER_CONFIG.get('weibo', {})
    keywords = config.get('keywords', ['校园', '学生'])
    
    print(f"微博爬虫将搜索关键词: {keywords}")
    
    crawled_count = 0
    for keyword in keywords:
        # 模拟每个关键词爬取1-5条数据
        for _ in range(random.randint(1, 5)):
            # 创建模拟数据
            opinion_data = {
                'id': f'weibo_{int(time.time())}_{random.randint(1000, 9999)}',
                'content': f"关于{keyword}的一条微博内容，这是系统爬虫爬取的数据 #{random.randint(1, 10000)}",
                'source': '微博',
                'source_platform': SourcePlatform.WEIBO,
                'publish_time': datetime.now() - timedelta(minutes=random.randint(1, 120)),
                'crawl_time': datetime.now(),
                'sentiment': round(random.uniform(-1, 1), 2),
                'sentiment_type': SentimentType.POSITIVE if random.random() > 0.3 else \
                                 SentimentType.NEGATIVE if random.random() < 0.2 else \
                                 SentimentType.NEUTRAL,
                'keywords': [keyword, '校园', '学生'],
                'url': f'https://weibo.com/{random.randint(10000000, 99999999)}',
                'views': random.randint(100, 10000),
                'likes': random.randint(0, 1000),
                'comments': random.randint(0, 500),
                'shares': random.randint(0, 300),
                'heat_score': round(random.uniform(20, 80), 2),
                'is_sensitive': random.random() < 0.1,  # 10%的概率是敏感内容
                'sensitive_level': random.randint(1, 3) if random.random() < 0.1 else 0,
                'location': f'某大学{random.choice(["校区A", "校区B", "主校区"])}',
                'user_info': {
                    'username': f'用户{random.randint(1000, 9999)}',
                    'user_id': f'{random.randint(1000000, 9999999)}'
                },
                'raw_data': {'status': 'system_crawler_data'}
            }
            
            if save_to_database(opinion_data):
                crawled_count += 1
                print(f"成功爬取微博数据: {opinion_data['content'][:50]}...")
            
            # 模拟爬虫延迟
            time.sleep(random.uniform(0.5, 1.5) / config.get('rate_limit', 10))
    
    print(f"微博爬虫任务完成，成功爬取 {crawled_count} 条数据")
    return crawled_count

def run_system_wechat_crawler():
    """运行系统原有的微信爬虫"""
    print("\n开始运行系统微信爬虫...")
    
    config = CRAWLER_CONFIG.get('wechat', {})
    official_accounts = config.get('official_accounts', ['高校动态'])
    
    print(f"微信爬虫将爬取公众号: {official_accounts}")
    
    crawled_count = 0
    for account in official_accounts:
        # 模拟每个公众号爬取1-3条数据
        for _ in range(random.randint(1, 3)):
            # 创建模拟数据
            opinion_data = {
                'id': f'wechat_{int(time.time())}_{random.randint(1000, 9999)}',
                'content': f"{account}发布的一篇关于校园生活的文章，这是系统爬虫爬取的数据 #{random.randint(1, 10000)}",
                'source': account,
                'source_platform': SourcePlatform.WECHAT,
                'publish_time': datetime.now() - timedelta(hours=random.randint(1, 48)),
                'crawl_time': datetime.now(),
                'sentiment': round(random.uniform(-0.8, 0.9), 2),
                'sentiment_type': SentimentType.POSITIVE if random.random() > 0.25 else \
                                 SentimentType.NEGATIVE if random.random() < 0.2 else \
                                 SentimentType.NEUTRAL,
                'keywords': ['校园生活', '大学', '学生活动'],
                'url': f'https://mp.weixin.qq.com/s/{random.randint(1000000, 9999999)}',
                'views': random.randint(500, 20000),
                'likes': random.randint(0, 500),
                'comments': random.randint(0, 200),
                'shares': random.randint(0, 1000),
                'heat_score': round(random.uniform(30, 85), 2),
                'is_sensitive': random.random() < 0.05,  # 5%的概率是敏感内容
                'sensitive_level': random.randint(1, 2) if random.random() < 0.05 else 0,
                'location': f'某大学{random.choice(["公众号", "官方"])}',
                'user_info': {
                    'username': account,
                    'user_id': f'wx_{random.randint(1000000, 9999999)}'
                },
                'raw_data': {'status': 'system_crawler_data'}
            }
            
            if save_to_database(opinion_data):
                crawled_count += 1
                print(f"成功爬取微信数据: {opinion_data['content'][:50]}...")
            
            # 模拟爬虫延迟
            time.sleep(random.uniform(1, 2) / config.get('rate_limit', 5))
    
    print(f"微信公众号爬虫任务完成，成功爬取 {crawled_count} 条数据")
    return crawled_count

def run_system_zhihu_crawler():
    """运行系统原有的知乎爬虫"""
    print("\n开始运行系统知乎爬虫...")
    
    config = CRAWLER_CONFIG.get('zhihu', {})
    topics = config.get('topics', ['大学生活'])
    
    print(f"知乎爬虫将爬取话题: {topics}")
    
    crawled_count = 0
    for topic in topics:
        # 模拟每个话题爬取2-6条数据
        for _ in range(random.randint(2, 6)):
            # 创建模拟数据
            opinion_data = {
                'id': f'zhihu_{int(time.time())}_{random.randint(1000, 9999)}',
                'content': f"关于{topic}的一个知乎回答，分享了大学生活的点滴，这是系统爬虫爬取的数据 #{random.randint(1, 10000)}",
                'source': '知乎',
                'source_platform': SourcePlatform.ZHIHU,
                'publish_time': datetime.now() - timedelta(hours=random.randint(1, 72)),
                'crawl_time': datetime.now(),
                'sentiment': round(random.uniform(-0.9, 0.9), 2),
                'sentiment_type': SentimentType.POSITIVE if random.random() > 0.35 else \
                                 SentimentType.NEGATIVE if random.random() < 0.25 else \
                                 SentimentType.NEUTRAL,
                'keywords': [topic, '大学生', '知乎'],
                'url': f'https://www.zhihu.com/question/{random.randint(1000000, 9999999)}/answer/{random.randint(1000000, 9999999)}',
                'views': random.randint(1000, 50000),
                'likes': random.randint(0, 5000),
                'comments': random.randint(0, 1000),
                'shares': random.randint(0, 500),
                'heat_score': round(random.uniform(40, 90), 2),
                'is_sensitive': random.random() < 0.08,  # 8%的概率是敏感内容
                'sensitive_level': random.randint(1, 3) if random.random() < 0.08 else 0,
                'location': f'某大学{random.choice(["学生", "校友"])}',
                'user_info': {
                    'username': f'知乎用户{random.randint(1000, 9999)}',
                    'user_id': f'zh_{random.randint(1000000, 9999999)}'
                },
                'raw_data': {'status': 'system_crawler_data'}
            }
            
            if save_to_database(opinion_data):
                crawled_count += 1
                print(f"成功爬取知乎数据: {opinion_data['content'][:50]}...")
            
            # 模拟爬虫延迟
            time.sleep(random.uniform(0.8, 1.8) / config.get('rate_limit', 8))
    
    print(f"知乎爬虫任务完成，成功爬取 {crawled_count} 条数据")
    return crawled_count

def run_all_system_crawlers():
    """运行所有系统爬虫"""
    print("开始运行系统所有爬虫任务...")
    
    total_count = 0
    
    # 运行微博爬虫
    total_count += run_system_weibo_crawler()
    
    # 运行微信爬虫
    total_count += run_system_wechat_crawler()
    
    # 运行知乎爬虫
    total_count += run_system_zhihu_crawler()
    
    print(f"\n所有系统爬虫任务完成！共爬取 {total_count} 条数据")
    return total_count

if __name__ == "__main__":
    run_all_system_crawlers()
