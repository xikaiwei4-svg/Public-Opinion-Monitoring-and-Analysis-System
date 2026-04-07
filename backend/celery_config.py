import os
from datetime import timedelta
from db.db_config import get_settings

# 获取配置
settings = get_settings()

# Celery配置
CELERY_CONFIG = {
    # 消息代理配置
    'broker_url': settings.REDIS_URL,
    
    # 结果后端配置
    'result_backend': settings.REDIS_URL,
    
    # 任务序列化配置
    'task_serializer': 'json',
    'result_serializer': 'json',
    'accept_content': ['json'],
    
    # 时区配置
    'timezone': 'Asia/Shanghai',
    'enable_utc': True,
    
    # 任务过期时间
    'result_expires': 3600,  # 1小时
    
    # 任务路由配置
    'task_routes': {
        'backend.tasks.crawler.*': {'queue': 'crawler'},
        'backend.tasks.analyzer.*': {'queue': 'analyzer'},
        'backend.tasks.notification.*': {'queue': 'notification'}
    },
    
    # 任务调度配置
    'beat_schedule': {
        # 定时爬虫任务
        'run-weibo-crawler-every-30-minutes': {
            'task': 'backend.tasks.crawler.run_weibo_crawler',
            'schedule': timedelta(minutes=30),
        },
        'run-wechat-crawler-every-60-minutes': {
            'task': 'backend.tasks.crawler.run_wechat_crawler',
            'schedule': timedelta(hours=1),
        },
        'run-zhihu-crawler-every-45-minutes': {
            'task': 'backend.tasks.crawler.run_zhihu_crawler',
            'schedule': timedelta(minutes=45),
        },
        
        # 定时分析任务
        'run-sentiment-analysis-every-hour': {
            'task': 'backend.tasks.analyzer.run_sentiment_analysis',
            'schedule': timedelta(hours=1),
        },
        'run-hot-topics-detection-every-2-hours': {
            'task': 'backend.tasks.analyzer.run_hot_topics_detection',
            'schedule': timedelta(hours=2),
        },
        'run-daily-summary-every-day': {
            'task': 'backend.tasks.analyzer.generate_daily_summary',
            'schedule': timedelta(days=1),
            'kwargs': {'time': '00:00'}
        },
    },
    
    # 工作池配置
    'worker_prefetch_multiplier': 1,
    'worker_concurrency': os.cpu_count() or 4,
    
    # 日志配置
    'worker_log_format': '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    'worker_task_log_format': '[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s',
}

# 任务优先级配置
TASK_PRIORITIES = {
    'critical': 10,
    'high': 8,
    'medium': 5,
    'low': 3,
    'background': 1
}

# 爬虫配置
CRAWLER_CONFIG = {
    # 各平台爬虫配置
    'weibo': {
        'enabled': True,
        'rate_limit': 10,  # 每秒请求数
        'timeout': 30,  # 超时时间（秒）
        'max_retries': 3,
        'keywords': ['校园', '学生', '食堂', '宿舍', '图书馆', '考试', '就业', '活动']  # 监控关键词
    },
    'wechat': {
        'enabled': True,
        'rate_limit': 5,
        'timeout': 60,
        'max_retries': 3,
        'official_accounts': ['高校动态', '校园生活', '大学新鲜事']  # 监控公众号
    },
    'zhihu': {
        'enabled': True,
        'rate_limit': 8,
        'timeout': 45,
        'max_retries': 3,
        'topics': ['大学生活', '校园话题']  # 监控话题
    },
    'forum': {
        'enabled': True,
        'rate_limit': 15,
        'timeout': 30,
        'max_retries': 3,
        'forums': ['学校论坛', '贴吧']  # 监控论坛
    }
}

# 分析配置
ANALYZER_CONFIG = {
    # 情感分析配置
    'sentiment': {
        'model': 'hfl/chinese-roberta-wwm-ext-sentiment',  # 使用的模型
        'batch_size': 32,
        'thresholds': {
            'positive': 0.6,  # 正面阈值
            'negative': 0.4   # 负面阈值
        }
    },
    # 热点话题检测配置
    'hot_topics': {
        'min_occurrences': 5,  # 最小出现次数
        'window_size': 24,  # 时间窗口（小时）
        'top_n': 20,  # 每次检测的热点数量
        'keywords_limit': 10  # 每个热点提取的关键词数量
    },
    # 文本预处理配置
    'preprocessing': {
        'remove_stopwords': True,
        'stemming': False,
        'lemmatization': False,
        'min_length': 10  # 最小文本长度
    }
}