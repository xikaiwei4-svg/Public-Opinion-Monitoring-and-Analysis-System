from celery import Celery
import os
from db.db_config import get_settings

settings = get_settings()

# 创建Celery应用
celery_app = Celery(
    "campus_opinion_system",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "tasks.analyzer_tasks",
        "tasks.crawler_tasks"
    ]
)

# 配置Celery
celery_app.conf.update(
    result_expires=3600,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Shanghai",
    enable_utc=False,
    # 任务路由配置
    task_routes={
        "tasks.analyzer_tasks.*": {"queue": "analyzer"},
        "tasks.crawler_tasks.*": {"queue": "crawler"}
    },
    # 任务执行配置
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    # 任务重试配置
    task_retry_delay=30,
    task_retry_max=3,
    task_acks_late=True,
)

# 如果是作为主程序运行，则启动worker
if __name__ == "__main__":
    celery_app.start()