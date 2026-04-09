"""Redis缓存模块"""
import json
import redis
from typing import Optional, Any, Dict, List
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class RedisCache:
    """Redis缓存管理器"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """初始化Redis连接"""
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            logger.info("Redis连接成功")
        except Exception as e:
            logger.warning(f"Redis连接失败: {e}，将使用内存缓存作为后备")
            self.redis_client = None
            self.memory_cache = {}
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            else:
                # 使用内存缓存作为后备
                return self.memory_cache.get(key)
        except Exception as e:
            logger.error(f"获取缓存失败: {e}")
        return None
    
    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """设置缓存值"""
        try:
            serialized_value = json.dumps(value, ensure_ascii=False)
            
            if self.redis_client:
                self.redis_client.setex(key, expire, serialized_value)
            else:
                # 使用内存缓存作为后备
                self.memory_cache[key] = value
            
            return True
        except Exception as e:
            logger.error(f"设置缓存失败: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """删除缓存值"""
        try:
            if self.redis_client:
                self.redis_client.delete(key)
            else:
                # 使用内存缓存作为后备
                if key in self.memory_cache:
                    del self.memory_cache[key]
            return True
        except Exception as e:
            logger.error(f"删除缓存失败: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        try:
            if self.redis_client:
                return self.redis_client.exists(key) > 0
            else:
                # 使用内存缓存作为后备
                return key in self.memory_cache
        except Exception as e:
            logger.error(f"检查缓存失败: {e}")
            return False
    
    def get_pattern(self, pattern: str) -> List[str]:
        """获取匹配模式的所有键"""
        try:
            if self.redis_client:
                return self.redis_client.keys(pattern)
            else:
                # 使用内存缓存作为后备
                return [key for key in self.memory_cache.keys() if pattern.replace('*', '') in key]
        except Exception as e:
            logger.error(f"获取匹配键失败: {e}")
            return []
    
    def clear_pattern(self, pattern: str) -> int:
        """清除匹配模式的所有缓存"""
        try:
            keys = self.get_pattern(pattern)
            if keys:
                if self.redis_client:
                    return self.redis_client.delete(*keys)
                else:
                    # 使用内存缓存作为后备
                    for key in keys:
                        if key in self.memory_cache:
                            del self.memory_cache[key]
                    return len(keys)
            return 0
        except Exception as e:
            logger.error(f"清除缓存失败: {e}")
            return 0

# 创建全局缓存实例
redis_cache = RedisCache()

# 缓存装饰器
def cache(expire: int = 3600):
    """缓存装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{func.__module__}:{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # 尝试从缓存获取
            cached_result = redis_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 缓存结果
            redis_cache.set(cache_key, result, expire)
            
            return result
        return wrapper
    return decorator
