from celery import shared_task
from celery.utils.log import get_task_logger
from datetime import datetime, timedelta
import time
import random
import pymysql
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

# 创建日志记录器
logger = get_task_logger(__name__)

@shared_task(name='backend.tasks.crawler.run_weibo_crawler', queue='crawler')
def run_weibo_crawler(keywords=None):
    """
    运行微博爬虫任务
    """
    logger.info(f"开始运行微博爬虫任务，时间: {datetime.now()}")
    
    try:
        # 获取配置
        config = CRAWLER_CONFIG.get('weibo', {})
        
        # 如果未提供关键词，使用配置中的关键词
        if keywords is None:
            keywords = config.get('keywords', ['校园', '学生'])
        
        # 模拟爬虫运行
        # 在实际应用中，这里应该调用真正的微博爬虫逻辑
        logger.info(f"微博爬虫将搜索关键词: {keywords}")
        
        # 模拟爬取数据（实际应用中应该是真实的爬取逻辑）
        crawled_count = 0
        for keyword in keywords:
            # 模拟每个关键词爬取1-5条数据
            for _ in range(random.randint(1, 5)):
                # 创建模拟数据
                unique_id = f"{int(time.time())}_{random.randint(1000, 9999)}"
                content = f"关于{keyword}的一条微博内容，这是系统爬虫在{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}爬取的数据 #{unique_id}"
                
                opinion_data = {
                    'id': f'weibo_{unique_id}',
                    'content': content,
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
                    'raw_data': {'status': 'simulated_data'}
                }
                
                # 保存到数据库
                # 检查数据是否已存在（基于content字段）
                connection = pymysql.connect(**DB_CONFIG)
                cursor = connection.cursor()
                try:
                    cursor.execute("SELECT COUNT(*) FROM opinions WHERE content = %s", (content,))
                    if cursor.fetchone()[0] == 0:
                        cursor.execute(
                            "INSERT INTO opinions (title, content, source_platform, publish_time, crawl_time, sentiment, sentiment_score, keywords, read_count, like_count, comment_count, share_count, hot_score) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                            (
                                f"微博舆情{unique_id}", 
                                content, 
                                opinion_data['source_platform'],
                                opinion_data['publish_time'], 
                                opinion_data['crawl_time'],
                                opinion_data['sentiment_type'], 
                                opinion_data['sentiment'],
                                ','.join(opinion_data['keywords']),
                                opinion_data['views'],
                                opinion_data['likes'],
                                opinion_data['comments'],
                                opinion_data['shares'],
                                opinion_data['heat_score']
                            )
                        )
                        connection.commit()
                        crawled_count += 1
                        print(f"成功插入数据: {content[:50]}...")
                except Exception as e:
                    logger.error(f"保存数据失败: {str(e)}")
                    connection.rollback()
                finally:
                    cursor.close()
                    connection.close()
                
                # 模拟爬虫延迟
                time.sleep(random.uniform(0.5, 1.5) / config.get('rate_limit', 10))
        
        logger.info(f"微博爬虫任务完成，成功爬取 {crawled_count} 条数据")
        return {"status": "success", "message": f"微博爬虫成功爬取{crawled_count}条数据"}
    except Exception as e:
        logger.error(f"微博爬虫任务失败: {str(e)}")
        return {"status": "error", "message": str(e)}

@shared_task(name='backend.tasks.crawler.run_wechat_crawler', queue='crawler')
def run_wechat_crawler(official_accounts=None):
    """
    运行微信公众号爬虫任务
    """
    logger.info(f"开始运行微信公众号爬虫任务，时间: {datetime.now()}")
    
    try:
        # 获取配置
        config = CRAWLER_CONFIG.get('wechat', {})
        
        # 如果未提供公众号，使用配置中的公众号
        if official_accounts is None:
            official_accounts = config.get('official_accounts', ['高校动态'])
        
        # 模拟爬虫运行
        logger.info(f"微信爬虫将爬取公众号: {official_accounts}")
        
        # 模拟爬取数据
        crawled_count = 0
        for account in official_accounts:
            # 模拟每个公众号爬取1-3条数据
            for _ in range(random.randint(1, 3)):
                # 创建模拟数据
                unique_id = f"{int(time.time())}_{random.randint(1000, 9999)}"
                content = f"{account}发布的一篇关于校园生活的文章，这是系统爬虫在{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}爬取的数据 #{unique_id}"
                
                opinion_data = {
                    'id': f'wechat_{unique_id}',
                    'content': content,
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
                    'raw_data': {'status': 'simulated_data'}
                }
                
                # 保存到数据库
                # 检查数据是否已存在（基于content字段）
                connection = pymysql.connect(**DB_CONFIG)
                cursor = connection.cursor()
                try:
                    cursor.execute("SELECT COUNT(*) FROM opinions WHERE content = %s", (content,))
                    if cursor.fetchone()[0] == 0:
                        cursor.execute(
                            "INSERT INTO opinions (title, content, source_platform, publish_time, crawl_time, sentiment, sentiment_score, keywords, read_count, like_count, comment_count, share_count, hot_score) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                            (
                                f"{account}舆情{unique_id}", 
                                content, 
                                opinion_data['source_platform'],
                                opinion_data['publish_time'], 
                                opinion_data['crawl_time'],
                                opinion_data['sentiment_type'], 
                                opinion_data['sentiment'],
                                ','.join(opinion_data['keywords']),
                                opinion_data['views'],
                                opinion_data['likes'],
                                opinion_data['comments'],
                                opinion_data['shares'],
                                opinion_data['heat_score']
                            )
                        )
                        connection.commit()
                        crawled_count += 1
                        print(f"成功插入数据: {content[:50]}...")
                except Exception as e:
                    logger.error(f"保存数据失败: {str(e)}")
                    connection.rollback()
                finally:
                    cursor.close()
                    connection.close()
                
                # 模拟爬虫延迟
                time.sleep(random.uniform(1, 2) / config.get('rate_limit', 5))
        
        logger.info(f"微信公众号爬虫任务完成，成功爬取 {crawled_count} 条数据")
        return {"status": "success", "message": f"微信爬虫成功爬取{crawled_count}条数据"}
    except Exception as e:
        logger.error(f"微信公众号爬虫任务失败: {str(e)}")
        return {"status": "error", "message": str(e)}

@shared_task(name='backend.tasks.crawler.run_zhihu_crawler', queue='crawler')
def run_zhihu_crawler(topics=None):
    """
    运行知乎爬虫任务
    """
    logger.info(f"开始运行知乎爬虫任务，时间: {datetime.now()}")
    
    try:
        # 获取配置
        config = CRAWLER_CONFIG.get('zhihu', {})
        
        # 如果未提供话题，使用配置中的话题
        if topics is None:
            topics = config.get('topics', ['大学生活'])
        
        # 模拟爬虫运行
        logger.info(f"知乎爬虫将爬取话题: {topics}")
        
        # 模拟爬取数据
        crawled_count = 0
        for topic in topics:
            # 模拟每个话题爬取2-6条数据
            for _ in range(random.randint(2, 6)):
                # 创建模拟数据
                unique_id = f"{int(time.time())}_{random.randint(1000, 9999)}"
                content = f"关于{topic}的一个知乎回答，分享了大学生活的点滴，这是系统爬虫在{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}爬取的数据 #{unique_id}"
                
                opinion_data = {
                    'id': f'zhihu_{unique_id}',
                    'content': content,
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
                    'raw_data': {'status': 'simulated_data'}
                }
                
                # 保存到数据库
                # 检查数据是否已存在（基于content字段）
                connection = pymysql.connect(**DB_CONFIG)
                cursor = connection.cursor()
                try:
                    cursor.execute("SELECT COUNT(*) FROM opinions WHERE content = %s", (content,))
                    if cursor.fetchone()[0] == 0:
                        cursor.execute(
                            "INSERT INTO opinions (title, content, source_platform, publish_time, crawl_time, sentiment, sentiment_score, keywords, read_count, like_count, comment_count, share_count, hot_score) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                            (
                                f"知乎舆情{unique_id}", 
                                content, 
                                opinion_data['source_platform'],
                                opinion_data['publish_time'], 
                                opinion_data['crawl_time'],
                                opinion_data['sentiment_type'], 
                                opinion_data['sentiment'],
                                ','.join(opinion_data['keywords']),
                                opinion_data['views'],
                                opinion_data['likes'],
                                opinion_data['comments'],
                                opinion_data['shares'],
                                opinion_data['heat_score']
                            )
                        )
                        connection.commit()
                        crawled_count += 1
                        print(f"成功插入数据: {content[:50]}...")
                except Exception as e:
                    logger.error(f"保存数据失败: {str(e)}")
                    connection.rollback()
                finally:
                    cursor.close()
                    connection.close()
                
                # 模拟爬虫延迟
                time.sleep(random.uniform(0.8, 1.8) / config.get('rate_limit', 8))
        
        logger.info(f"知乎爬虫任务完成，成功爬取 {crawled_count} 条数据")
        return {"status": "success", "message": f"知乎爬虫成功爬取{crawled_count}条数据"}
    except Exception as e:
        logger.error(f"知乎爬虫任务失败: {str(e)}")
        return {"status": "error", "message": str(e)}

@shared_task(name='backend.tasks.crawler.run_all_crawlers', queue='crawler')
def run_all_crawlers():
    """
    运行所有爬虫任务
    """
    logger.info(f"开始运行所有爬虫任务，时间: {datetime.now()}")
    
    # 异步调用各个爬虫任务
    weibo_task = run_weibo_crawler.delay()
    wechat_task = run_wechat_crawler.delay()
    zhihu_task = run_zhihu_crawler.delay()
    
    logger.info(f"所有爬虫任务已提交，任务ID: weibo={weibo_task.id}, wechat={wechat_task.id}, zhihu={zhihu_task.id}")
    
    return {
        "status": "success",
        "message": "所有爬虫任务已提交",
        "task_ids": {
            "weibo": weibo_task.id,
            "wechat": wechat_task.id,
            "zhihu": zhihu_task.id
        }
    }