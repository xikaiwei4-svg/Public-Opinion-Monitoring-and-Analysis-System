#!/usr/bin/env python3
# 定时爬虫任务脚本

import sys
import os
import logging
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs', 'crawler_schedule.log'),
    filemode='a'
)
logger = logging.getLogger(__name__)

try:
    # 导入爬虫任务
    from tasks.crawler_tasks import run_all_crawlers
    from tasks.crawler_tasks import run_weibo_crawler, run_wechat_crawler, run_zhihu_crawler
except ImportError as e:
    logger.error(f"导入爬虫任务失败: {str(e)}")
    sys.exit(1)

def run_crawlers_job():
    """
    运行所有爬虫任务的定时任务
    """
    try:
        logger.info(f"开始执行定时爬虫任务，时间: {datetime.now()}")
        
        # 运行所有爬虫
        result = run_all_crawlers()
        
        logger.info(f"定时爬虫任务执行完成，结果: {result}")
    except Exception as e:
        logger.error(f"定时爬虫任务执行失败: {str(e)}")

def run_weibo_crawler_job():
    """
    运行微博爬虫任务的定时任务
    """
    try:
        logger.info(f"开始执行定时微博爬虫任务，时间: {datetime.now()}")
        
        # 运行微博爬虫
        result = run_weibo_crawler()
        
        logger.info(f"定时微博爬虫任务执行完成，结果: {result}")
    except Exception as e:
        logger.error(f"定时微博爬虫任务执行失败: {str(e)}")

def run_wechat_crawler_job():
    """
    运行微信爬虫任务的定时任务
    """
    try:
        logger.info(f"开始执行定时微信爬虫任务，时间: {datetime.now()}")
        
        # 运行微信爬虫
        result = run_wechat_crawler()
        
        logger.info(f"定时微信爬虫任务执行完成，结果: {result}")
    except Exception as e:
        logger.error(f"定时微信爬虫任务执行失败: {str(e)}")

def run_zhihu_crawler_job():
    """
    运行知乎爬虫任务的定时任务
    """
    try:
        logger.info(f"开始执行定时知乎爬虫任务，时间: {datetime.now()}")
        
        # 运行知乎爬虫
        result = run_zhihu_crawler()
        
        logger.info(f"定时知乎爬虫任务执行完成，结果: {result}")
    except Exception as e:
        logger.error(f"定时知乎爬虫任务执行失败: {str(e)}")

def main():
    """
    主函数
    """
    try:
        # 创建调度器
        scheduler = BlockingScheduler()
        
        # 配置定时任务
        # 每天早上8点运行所有爬虫
        scheduler.add_job(
            run_crawlers_job,
            CronTrigger(hour=8, minute=0),
            id='run_all_crawlers',
            name='运行所有爬虫任务',
            replace_existing=True
        )
        
        # 每天中午12点运行微博爬虫
        scheduler.add_job(
            run_weibo_crawler_job,
            CronTrigger(hour=12, minute=0),
            id='run_weibo_crawler',
            name='运行微博爬虫任务',
            replace_existing=True
        )
        
        # 每天下午3点运行微信爬虫
        scheduler.add_job(
            run_wechat_crawler_job,
            CronTrigger(hour=15, minute=0),
            id='run_wechat_crawler',
            name='运行微信爬虫任务',
            replace_existing=True
        )
        
        # 每天晚上7点运行知乎爬虫
        scheduler.add_job(
            run_zhihu_crawler_job,
            CronTrigger(hour=19, minute=0),
            id='run_zhihu_crawler',
            name='运行知乎爬虫任务',
            replace_existing=True
        )
        
        logger.info("定时爬虫任务调度器已启动")
        logger.info("调度任务列表:")
        for job in scheduler.get_jobs():
            logger.info(f"  - {job.name} (ID: {job.id}) - {job.trigger}")
        
        # 启动调度器
        scheduler.start()
        
    except KeyboardInterrupt:
        logger.info("定时爬虫任务调度器已手动停止")
    except Exception as e:
        logger.error(f"定时爬虫任务调度器启动失败: {str(e)}")

if __name__ == "__main__":
    main()
