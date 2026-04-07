from celery import Celery
from celery_config import CELERY_CONFIG

# 创建Celery应用实例
celery_app = Celery('campus_opinion_tasks')

# 加载配置
celery_app.config_from_object(CELERY_CONFIG)

# 注释掉自动发现任务，因为在运行main.py时不需要
# celery_app.autodiscover_tasks(['backend.tasks'], force=True)

# 启动命令示例:
# celery -A backend.tasks worker --loglevel=info -Q crawler,analyzer,notification
# celery -A backend.tasks beat --loglevel=info

# 检查任务状态命令示例:
# celery -A backend.tasks inspect registered
# celery -A backend.tasks inspect active
# celery -A backend.tasks inspect scheduled

# 任务监控命令:
# celery flower -A backend.tasks --port=5555