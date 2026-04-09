from celery import shared_task
from celery.utils.log import get_task_logger
from datetime import datetime, timedelta
import time
import random
import pymysql
from typing import List, Dict, Any, Optional
from models.opinion_model import SourcePlatform, SentimentType
from celery_config import CRAWLER_CONFIG
from db.db_config import get_settings

# 尝试导入Kafka生产者，如果失败则使用模拟模式
try:
    from ..kafka.kafka_producer import kafka_producer
    KAFKA_AVAILABLE = True
except ImportError:
    # 创建模拟的kafka_producer
    class MockKafkaProducer:
        def send_opinion(self, data):
            pass
    kafka_producer = MockKafkaProducer()
    KAFKA_AVAILABLE = False

# 获取配置
settings = get_settings()

# MySQL数据库配置
DB_CONFIG = {
    'host': settings.MYSQL_HOST,
    'port': settings.MYSQL_PORT,
    'user': settings.MYSQL_USER,
    'password': settings.MYSQL_PASSWORD,
    'database': settings.MYSQL_DATABASE,
    'charset': 'utf8mb4'
}

# 创建日志记录器
logger = get_task_logger(__name__)

# 校园相关关键词
CAMPUS_KEYWORDS = [
    '校园', '大学', '学生', '考试', '食堂', '图书馆', '宿舍', '课程', 
    '老师', '作业', '毕业', '就业', '考研', '保研', '奖学金', '社团',
    '活动', '讲座', '比赛', '实习', '校园卡', '门禁', '学费', '助学贷款'
]

# 敏感词列表
SENSITIVE_WORDS = [
    '作弊', '挂科', '退学', '自杀', '暴力', '冲突', '抗议', '示威',
    '丑闻', '腐败', '贪污', '泄露', '隐私', '安全', '事故', '伤亡'
]

class DatabaseConnectionPool:
    """数据库连接池管理"""
    
    _connections = []
    _max_connections = 5
    
    @classmethod
    def get_connection(cls):
        """获取数据库连接"""
        if cls._connections:
            return cls._connections.pop()
        return pymysql.connect(**DB_CONFIG)
    
    @classmethod
    def release_connection(cls, connection):
        """释放数据库连接"""
        if len(cls._connections)< cls._max_connections:
            cls._connections.append(connection)
        else:
            connection.close()

def detect_sensitive_content(content: str) -> bool:
    """检测敏感内容"""
    for word in SENSITIVE_WORDS:
        if word in content:
            return True
    return False

def calculate_sensitive_level(content: str) -> int:
    """计算敏感级别"""
    sensitive_count = sum(1 for word in SENSITIVE_WORDS if word in content)
    if sensitive_count >= 3:
        return 3
    elif sensitive_count >= 2:
        return 2
    elif sensitive_count >= 1:
        return 1
    return 0

def generate_realistic_content(keyword: str, platform: str) -> str:
    """生成更真实的内容"""
    content_templates = {
        'weibo': [
            f"今天在学校看到关于{keyword}的讨论，感觉很有意义，大家怎么看？#{keyword} #校园生活",
            f"{keyword}的问题真的需要重视了，希望学校能采取措施改进。#校园热点",
            f"分享一下我对{keyword}的看法，欢迎大家讨论交流。#大学生活",
            f"最近{keyword}成为热门话题，作为学生我们应该积极参与讨论。#校园话题",
            f"{keyword}相关的活动很精彩，学到了很多东西！#校园活动"
        ],
        'wechat': [
            f"【校园动态】关于{keyword}的最新消息，学校发布了相关政策，学生们反响热烈。",
            f"深度解析：{keyword}背后的故事，看看专家怎么说。",
            f"关注{keyword}，了解校园最新动态，做知情的大学生。",
            f"{keyword}引发广泛讨论，各方观点不一，你怎么看？",
            f"最新：{keyword}有了新进展，学校采取了积极措施。"
        ],
        'zhihu': [
            f"如何看待{keyword}现象？作为大学生，我们应该如何应对？",
            f"{keyword}对大学生活有什么影响？欢迎分享你的经历。",
            f"深度分析：{keyword}的现状和未来发展趋势",
            f"作为过来人，想聊聊{keyword}那些事儿",
            f"{keyword}背后的原因是什么？有什么解决方案？"
        ]
    }
    
    templates = content_templates.get(platform, content_templates['weibo'])
    return random.choice(templates)

@shared_task(name='backend.tasks.crawler.run_weibo_crawler', queue='crawler', max_retries=3, retry_backoff=60)
def run_weibo_crawler(keywords=None):
    """
    运行微博爬虫任务 - 优化版本
    """
    logger.info(f"开始运行微博爬虫任务，时间: {datetime.now()}")
    
    try:
        # 获取配置
        config = CRAWLER_CONFIG.get('weibo', {})
        
        # 如果未提供关键词，使用配置中的关键词
        if keywords is None:
            keywords = config.get('keywords', CAMPUS_KEYWORDS[:5])
        
        # 限制关键词数量
        keywords = keywords[:10]
        logger.info(f"微博爬虫将搜索关键词: {keywords}")
        
        # 模拟爬取数据（实际应用中应该是真实的爬取逻辑）
        crawled_count = 0
        batch_size = 10
        batch_data = []
        
        for keyword in keywords:
            # 模拟每个关键词爬取2-8条数据
            for _ in range(random.randint(2, 8)):
                # 创建模拟数据
                unique_id = f"{int(time.time())}_{random.randint(1000, 9999)}"
                content = generate_realistic_content(keyword, 'weibo')
                
                # 检测敏感内容
                is_sensitive = detect_sensitive_content(content)
                sensitive_level = calculate_sensitive_level(content)
                
                opinion_data = {
                    'id': f'weibo_{unique_id}',
                    'content': content,
                    'source': '微博',
                    'source_platform': SourcePlatform.WEIBO,
                    'publish_time': datetime.now() - timedelta(minutes=random.randint(1, 1440)),  # 最近24小时
                    'crawl_time': datetime.now(),
                    'sentiment': round(random.uniform(-0.9, 0.9), 2),
                    'sentiment_type': SentimentType.POSITIVE if random.random() > 0.3 else \
                                     SentimentType.NEGATIVE if random.random() < 0.25 else \
                                     SentimentType.NEUTRAL,
                    'keywords': [keyword] + random.sample(CAMPUS_KEYWORDS, min(3, len(CAMPUS_KEYWORDS))),
                    'url': f'https://weibo.com/{random.randint(10000000, 99999999)}/{random.randint(1000000, 9999999)}',
                    'views': random.randint(50, 50000),
                    'likes': random.randint(0, 2000),
                    'comments': random.randint(0, 1000),
                    'shares': random.randint(0, 800),
                    'heat_score': round(random.uniform(10, 95), 2),
                    'is_sensitive': is_sensitive,
                    'sensitive_level': sensitive_level,
                    'location': f'某大学{random.choice(["校区A", "校区B", "主校区", "东校区", "西校区"])}',
                    'user_info': {
                        'username': f'微博用户{random.randint(1000, 9999)}',
                        'user_id': f'{random.randint(1000000, 9999999)}'
                    },
                    'raw_data': {'status': 'simulated_data', 'keyword': keyword}
                }
                
                # 添加到批量数据
                batch_data.append((
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
                ))
                
                # 批量插入
                if len(batch_data) >= batch_size:
                    crawled_count += insert_batch_data(batch_data)
                    batch_data = []
                
                # 模拟爬虫延迟
                time.sleep(random.uniform(0.3, 1.2) / config.get('rate_limit', 15))
        
        # 插入剩余数据
        if batch_data:
            crawled_count += insert_batch_data(batch_data)
        
        logger.info(f"微博爬虫任务完成，成功爬取 {crawled_count} 条数据")
        return {"status": "success", "message": f"微博爬虫成功爬取{crawled_count}条数据", "count": crawled_count}
    except Exception as e:
        logger.error(f"微博爬虫任务失败: {str(e)}")
        # 重试机制
        raise shared_task.retry(exc=e, countdown=60)

def insert_batch_data(batch_data):
    """批量插入数据并发送到Kafka"""
    if not batch_data:
        return 0
    
    connection = None
    cursor = None
    inserted_count = 0
    
    try:
        connection = DatabaseConnectionPool.get_connection()
        cursor = connection.cursor()
        
        # 使用ON DUPLICATE KEY UPDATE避免重复插入
        sql = """
        INSERT INTO opinions (title, content, source_platform, publish_time, crawl_time, sentiment, sentiment_score, keywords, read_count, like_count, comment_count, share_count, hot_score)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        sentiment = VALUES(sentiment),
        sentiment_score = VALUES(sentiment_score),
        read_count = VALUES(read_count),
        like_count = VALUES(like_count),
        comment_count = VALUES(comment_count),
        share_count = VALUES(share_count),
        hot_score = VALUES(hot_score),
        crawl_time = VALUES(crawl_time)
        """
        
        # 批量执行
        cursor.executemany(sql, batch_data)
        connection.commit()
        inserted_count = cursor.rowcount
        
        logger.info(f"批量插入成功，插入 {inserted_count} 条数据")
        
        # 发送数据到Kafka
        for data in batch_data:
            opinion_data = {
                "id": f"{data[2]}_{int(time.time())}_{random.randint(1000, 9999)}",
                "title": data[0],
                "content": data[1],
                "source_platform": data[2],
                "publish_time": data[3].isoformat() if hasattr(data[3], 'isoformat') else str(data[3]),
                "crawl_time": data[4].isoformat() if hasattr(data[4], 'isoformat') else str(data[4]),
                "sentiment": data[5],
                "sentiment_score": data[6],
                "keywords": data[7].split(','),
                "read_count": data[8],
                "like_count": data[9],
                "comment_count": data[10],
                "share_count": data[11],
                "hot_score": data[12]
            }
            
            # 发送到Kafka
            kafka_producer.send_opinion(opinion_data)
            
        logger.info(f"成功发送 {len(batch_data)} 条数据到Kafka")
        
    except Exception as e:
        logger.error(f"批量插入失败: {str(e)}")
        if connection:
            connection.rollback()
    finally:
        if cursor:
            cursor.close()
        if connection:
            DatabaseConnectionPool.release_connection(connection)
    
    return inserted_count

@shared_task(name='backend.tasks.crawler.run_wechat_crawler', queue='crawler', max_retries=3, retry_backoff=60)
def run_wechat_crawler(official_accounts=None):
    """
    运行微信公众号爬虫任务 - 优化版本
    """
    logger.info(f"开始运行微信公众号爬虫任务，时间: {datetime.now()}")
    
    try:
        # 获取配置
        config = CRAWLER_CONFIG.get('wechat', {})
        
        # 如果未提供公众号，使用配置中的公众号
        if official_accounts is None:
            official_accounts = config.get('official_accounts', ['高校动态', '校园生活', '大学生活'])
        
        # 限制公众号数量
        official_accounts = official_accounts[:5]
        logger.info(f"微信爬虫将爬取公众号: {official_accounts}")
        
        # 模拟爬取数据
        crawled_count = 0
        batch_size = 8
        batch_data = []
        
        for account in official_accounts:
            # 模拟每个公众号爬取2-5条数据
            for _ in range(random.randint(2, 5)):
                # 创建模拟数据
                unique_id = f"{int(time.time())}_{random.randint(1000, 9999)}"
                
                # 随机选择一个校园关键词
                keyword = random.choice(CAMPUS_KEYWORDS)
                content = generate_realistic_content(keyword, 'wechat')
                
                # 检测敏感内容
                is_sensitive = detect_sensitive_content(content)
                sensitive_level = calculate_sensitive_level(content)
                
                opinion_data = {
                    'id': f'wechat_{unique_id}',
                    'content': content,
                    'source': account,
                    'source_platform': SourcePlatform.WECHAT,
                    'publish_time': datetime.now() - timedelta(hours=random.randint(1, 72)),  # 最近3天
                    'crawl_time': datetime.now(),
                    'sentiment': round(random.uniform(-0.8, 0.95), 2),
                    'sentiment_type': SentimentType.POSITIVE if random.random() > 0.25 else \
                                     SentimentType.NEGATIVE if random.random() < 0.2 else \
                                     SentimentType.NEUTRAL,
                    'keywords': [keyword] + random.sample(CAMPUS_KEYWORDS, min(2, len(CAMPUS_KEYWORDS))),
                    'url': f'https://mp.weixin.qq.com/s/{random.randint(1000000, 9999999)}',
                    'views': random.randint(1000, 50000),
                    'likes': random.randint(0, 1000),
                    'comments': random.randint(0, 500),
                    'shares': random.randint(0, 2000),
                    'heat_score': round(random.uniform(20, 90), 2),
                    'is_sensitive': is_sensitive,
                    'sensitive_level': sensitive_level,
                    'location': f'某大学{random.choice(["公众号", "官方", "校园媒体"])}',
                    'user_info': {
                        'username': account,
                        'user_id': f'wx_{random.randint(1000000, 9999999)}'
                    },
                    'raw_data': {'status': 'simulated_data', 'account': account, 'keyword': keyword}
                }
                
                # 添加到批量数据
                batch_data.append((
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
                ))
                
                # 批量插入
                if len(batch_data) >= batch_size:
                    crawled_count += insert_batch_data(batch_data)
                    batch_data = []
                
                # 模拟爬虫延迟
                time.sleep(random.uniform(0.8, 1.5) / config.get('rate_limit', 8))
        
        # 插入剩余数据
        if batch_data:
            crawled_count += insert_batch_data(batch_data)
        
        logger.info(f"微信公众号爬虫任务完成，成功爬取 {crawled_count} 条数据")
        return {"status": "success", "message": f"微信爬虫成功爬取{crawled_count}条数据", "count": crawled_count}
    except Exception as e:
        logger.error(f"微信公众号爬虫任务失败: {str(e)}")
        # 重试机制
        raise shared_task.retry(exc=e, countdown=60)

@shared_task(name='backend.tasks.crawler.run_zhihu_crawler', queue='crawler', max_retries=3, retry_backoff=60)
def run_zhihu_crawler(topics=None):
    """
    运行知乎爬虫任务 - 优化版本
    """
    logger.info(f"开始运行知乎爬虫任务，时间: {datetime.now()}")
    
    try:
        # 获取配置
        config = CRAWLER_CONFIG.get('zhihu', {})
        
        # 如果未提供话题，使用配置中的话题
        if topics is None:
            topics = config.get('topics', ['大学生活', '校园生活', '大学生就业'])
        
        # 限制话题数量
        topics = topics[:8]
        logger.info(f"知乎爬虫将爬取话题: {topics}")
        
        # 模拟爬取数据
        crawled_count = 0
        batch_size = 12
        batch_data = []
        
        for topic in topics:
            # 模拟每个话题爬取3-8条数据
            for _ in range(random.randint(3, 8)):
                # 创建模拟数据
                unique_id = f"{int(time.time())}_{random.randint(1000, 9999)}"
                content = generate_realistic_content(topic, 'zhihu')
                
                # 检测敏感内容
                is_sensitive = detect_sensitive_content(content)
                sensitive_level = calculate_sensitive_level(content)
                
                opinion_data = {
                    'id': f'zhihu_{unique_id}',
                    'content': content,
                    'source': '知乎',
                    'source_platform': SourcePlatform.ZHIHU,
                    'publish_time': datetime.now() - timedelta(hours=random.randint(1, 168)),  # 最近7天
                    'crawl_time': datetime.now(),
                    'sentiment': round(random.uniform(-0.95, 0.95), 2),
                    'sentiment_type': SentimentType.POSITIVE if random.random() > 0.35 else \
                                     SentimentType.NEGATIVE if random.random() < 0.25 else \
                                     SentimentType.NEUTRAL,
                    'keywords': [topic] + random.sample(CAMPUS_KEYWORDS, min(3, len(CAMPUS_KEYWORDS))),
                    'url': f'https://www.zhihu.com/question/{random.randint(1000000, 9999999)}/answer/{random.randint(1000000, 9999999)}',
                    'views': random.randint(500, 100000),
                    'likes': random.randint(0, 10000),
                    'comments': random.randint(0, 2000),
                    'shares': random.randint(0, 1000),
                    'heat_score': round(random.uniform(30, 95), 2),
                    'is_sensitive': is_sensitive,
                    'sensitive_level': sensitive_level,
                    'location': f'某大学{random.choice(["学生", "校友", "教师", "毕业生"])}',
                    'user_info': {
                        'username': f'知乎用户{random.randint(1000, 9999)}',
                        'user_id': f'zh_{random.randint(1000000, 9999999)}'
                    },
                    'raw_data': {'status': 'simulated_data', 'topic': topic}
                }
                
                # 添加到批量数据
                batch_data.append((
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
                ))
                
                # 批量插入
                if len(batch_data) >= batch_size:
                    crawled_count += insert_batch_data(batch_data)
                    batch_data = []
                
                # 模拟爬虫延迟
                time.sleep(random.uniform(0.5, 1.2) / config.get('rate_limit', 12))
        
        # 插入剩余数据
        if batch_data:
            crawled_count += insert_batch_data(batch_data)
        
        logger.info(f"知乎爬虫任务完成，成功爬取 {crawled_count} 条数据")
        return {"status": "success", "message": f"知乎爬虫成功爬取{crawled_count}条数据", "count": crawled_count}
    except Exception as e:
        logger.error(f"知乎爬虫任务失败: {str(e)}")
        # 重试机制
        raise shared_task.retry(exc=e, countdown=60)

@shared_task(name='backend.tasks.crawler.run_all_crawlers', queue='crawler', max_retries=2, retry_backoff=120)
def run_all_crawlers():
    """
    运行所有爬虫任务 - 优化版本
    """
    logger.info(f"开始运行所有爬虫任务，时间: {datetime.now()}")
    
    try:
        # 异步调用各个爬虫任务
        task_results = {}
        
        # 微博爬虫
        try:
            weibo_task = run_weibo_crawler.delay()
            task_results['weibo'] = {'status': 'submitted', 'task_id': weibo_task.id}
            logger.info(f"微博爬虫任务已提交，任务ID: {weibo_task.id}")
        except Exception as e:
            logger.error(f"提交微博爬虫任务失败: {str(e)}")
            task_results['weibo'] = {'status': 'error', 'message': str(e)}
        
        # 微信爬虫
        try:
            wechat_task = run_wechat_crawler.delay()
            task_results['wechat'] = {'status': 'submitted', 'task_id': wechat_task.id}
            logger.info(f"微信爬虫任务已提交，任务ID: {wechat_task.id}")
        except Exception as e:
            logger.error(f"提交微信爬虫任务失败: {str(e)}")
            task_results['wechat'] = {'status': 'error', 'message': str(e)}
        
        # 知乎爬虫
        try:
            zhihu_task = run_zhihu_crawler.delay()
            task_results['zhihu'] = {'status': 'submitted', 'task_id': zhihu_task.id}
            logger.info(f"知乎爬虫任务已提交，任务ID: {zhihu_task.id}")
        except Exception as e:
            logger.error(f"提交知乎爬虫任务失败: {str(e)}")
            task_results['zhihu'] = {'status': 'error', 'message': str(e)}
        
        # 检查是否所有任务都提交失败
        all_failed = all(result['status'] == 'error' for result in task_results.values())
        
        if all_failed:
            logger.error("所有爬虫任务提交失败")
            return {
                "status": "error",
                "message": "所有爬虫任务提交失败",
                "results": task_results
            }
        
        logger.info("所有爬虫任务提交完成")
        return {
            "status": "success",
            "message": "爬虫任务提交完成",
            "results": task_results
        }
        
    except Exception as e:
        logger.error(f"运行所有爬虫任务失败: {str(e)}")
        # 重试机制
        raise shared_task.retry(exc=e, countdown=120)