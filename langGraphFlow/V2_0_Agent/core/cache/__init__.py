"""
缓存管理模块
提供Redis连接管理和异常处理
"""
from .redis import RedisManager, get_redis_manager
from .exceptions import (
    CacheError,
    ConnectionError,
    OperationError,
)

__all__ = [
    "RedisManager",
    "get_redis_manager",
    "CacheError",
    "ConnectionError",
    "OperationError",
]

