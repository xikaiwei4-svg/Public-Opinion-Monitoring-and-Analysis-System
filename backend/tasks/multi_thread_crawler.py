#!/usr/bin/env python3
# 多线程爬虫任务脚本

import threading
import logging
import sys
import os
from datetime import datetime
from typing import Dict, Any

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs', 'multi_thread_crawler.log'),
    filemode='a'
)
logger = logging.getLogger(__name__)

try:
    # 导入爬虫任务
    from tasks.crawler_tasks import run_weibo_crawler, run_wechat_crawler, run_zhihu_crawler
except ImportError as e:
    logger.error(f"导入爬虫任务失败: {str(e)}")
    raise

def run_crawler_task(task_func, task_name: str, results: Dict[str, Any]):
    """
    运行单个爬虫任务的线程函数
    """
    try:
        logger.info(f"开始运行{task_name}爬虫任务，时间: {datetime.now()}")
        result = task_func()
        results[task_name] = result
        logger.info(f"{task_name}爬虫任务执行完成，结果: {result}")
    except Exception as e:
        logger.error(f"{task_name}爬虫任务执行失败: {str(e)}")
        results[task_name] = {
            "status": "error",
            "message": f"{task_name}爬虫任务执行失败: {str(e)}"
        }

def run_all_crawlers_multi_thread():
    """
    使用多线程并行运行所有爬虫任务
    """
    logger.info(f"开始并行运行所有爬虫任务，时间: {datetime.now()}")
    
    # 存储任务结果
    results = {}
    
    # 创建线程
    threads = [
        threading.Thread(
            target=run_crawler_task,
            args=(run_weibo_crawler, "微博", results)
        ),
        threading.Thread(
            target=run_crawler_task,
            args=(run_wechat_crawler, "微信", results)
        ),
        threading.Thread(
            target=run_crawler_task,
            args=(run_zhihu_crawler, "知乎", results)
        )
    ]
    
    # 启动所有线程
    for thread in threads:
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    # 检查是否所有任务都失败
    all_failed = all(result.get('status') == 'error' for result in results.values())
    
    if all_failed:
        logger.error("所有爬虫任务执行失败")
        return {
            "status": "error",
            "message": "所有爬虫任务执行失败",
            "results": results
        }
    
    logger.info("所有爬虫任务执行完成")
    return {
        "status": "success",
        "message": "所有爬虫任务执行完成",
        "results": results
    }

if __name__ == "__main__":
    # 运行多线程爬虫任务
    result = run_all_crawlers_multi_thread()
    logger.info(f"多线程爬虫任务执行结果: {result}")
    print(result)
