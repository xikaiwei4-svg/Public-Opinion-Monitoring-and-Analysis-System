"""Redis缓存模块 - 缓存优先策略 (Cache-Aside Pattern)"""

import json

import redis

import hashlib

from typing import Optional, Any, Callable

from datetime import timedelta

import logging

from functools import wraps

import os



logger = logging.getLogger(__name__)





class RedisCache:

    """Redis缓存管理器  缓存优先，MySQL兜底"""



    def __init__(self, redis_url: Optional[str] = None):

        self.redis_client = None

        self.memory_cache = {}

        # 优先使用环境变量 REDIS_URL，否则使用默认值

        url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")

        self._connect(url)



    def _connect(self, redis_url: str):

        try:

            self.redis_client = redis.from_url(redis_url, decode_responses=True, socket_connect_timeout=3)

            self.redis_client.ping()

            logger.info("Redis连接成功 - 缓存层就绪")

        except Exception as e:

            logger.warning(f"Redis连接失败: {e}，使用内存缓存作为后备")

            self.redis_client = None



    @property

    def available(self) -> bool:

        return self.redis_client is not None



    #  基础操作 



    def get(self, key: str) -> Optional[Any]:

        try:

            if self.redis_client:

                value = self.redis_client.get(key)

                return json.loads(value) if value else None

            return self.memory_cache.get(key)

        except Exception as e:

            logger.error(f"缓存读取失败 [{key}]: {e}")

            return None



    def set(self, key: str, value: Any, expire: int = 3600) -> bool:

        try:

            serialized = json.dumps(value, ensure_ascii=False, default=str)

            if self.redis_client:

                self.redis_client.setex(key, expire, serialized)

            else:

                self.memory_cache[key] = value

            return True

        except Exception as e:

            logger.error(f"缓存写入失败 [{key}]: {e}")

            return False



    def delete(self, key: str) -> bool:

        try:

            if self.redis_client:

                self.redis_client.delete(key)

            else:

                self.memory_cache.pop(key, None)

            return True

        except Exception as e:

            logger.error(f"缓存删除失败 [{key}]: {e}")

            return False



    def delete_pattern(self, pattern: str) -> int:

        try:

            if self.redis_client:

                keys = self.redis_client.keys(pattern)

                if keys:

                    return self.redis_client.delete(*keys)

                return 0

            keys = [k for k in self.memory_cache if pattern.replace("*", "") in k]

            for k in keys:

                del self.memory_cache[k]

            return len(keys)

        except Exception as e:

            logger.error(f"批量删除缓存失败 [{pattern}]: {e}")

            return 0



    #  缓存优先策略 (核心) 



    def cache_aside(

        self,

        cache_key: str,

        db_func: Callable,

        expire: int = 300,

        force_refresh: bool = False,

    ) -> Any:

        """

        缓存优先读取:

        1. 查 Redis  命中则返回

        2. 未命中  查 MySQL (db_func)

        3. 结果写入 Redis  返回



        Args:

            cache_key: 缓存键

            db_func: 数据库查询函数(无参数可调用对象)

            expire: 缓存过期时间(秒), 默认300

            force_refresh: 强制刷新缓存

        """

        if not force_refresh:

            cached = self.get(cache_key)

            if cached is not None:

                logger.debug(f"缓存命中: {cache_key}")

                return cached



        logger.debug(f"缓存未命中，查询数据库 {cache_key}")

        try:

            data = db_func()

            if data is not None and data != [] and data != {}:

                self.set(cache_key, data, expire)

            return data

        except Exception as e:

            logger.error(f"数据库查询失败 [{cache_key}]: {e}")

            raise



    def invalidate_on_write(self, *patterns: str):

        """写入数据后失效相关缓存"""

        for pattern in patterns:

            count = self.delete_pattern(pattern)

            if count > 0:

                logger.debug(f"缓存失效 [{pattern}]: {count} 个键已清除")



    #  热点数据预热 



    def warmup(self, warmup_funcs: dict):

        """

        系统启动时预热情热点缓存

        warmup_funcs: {"key": db_func, ...}

        """

        logger.info("开始缓存预热...")

        for key, func in warmup_funcs.items():

            try:

                data = func()

                if data is not None:

                    self.set(key, data, expire=600)

                    logger.info(f"预热完成: {key}")

            except Exception as e:

                logger.warning(f"预热失败 [{key}]: {e}")

        logger.info("缓存预热结束")





# 全局单例

redis_cache = RedisCache()





#  缓存键生成工具 



def make_cache_key(prefix: str, **params) -> str:

    """生成带参数的缓存键"""

    if not params:

        return prefix

    raw = json.dumps(params, sort_keys=True, ensure_ascii=False, default=str)

    digest = hashlib.md5(raw.encode()).hexdigest()[:10]

    return f"{prefix}:{digest}"





def cache_decorator(prefix: str, expire: int = 300):

    """缓存装饰器 - 自动缓存函数返回值为JSON"""

    def decorator(func):

        @wraps(func)

        def wrapper(*args, **kwargs):

            cache_key = make_cache_key(prefix)

            cached = redis_cache.get(cache_key)

            if cached is not None:

                return cached

            result = func(*args, **kwargs)

            if result is not None:

                redis_cache.set(cache_key, result, expire)

            return result

        return wrapper

    return decorator

