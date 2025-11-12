"""
数据库管理模块
提供数据库连接池管理、健康检查和异常处理
"""
from .pool import DatabasePool, get_db_pool
from .health import HealthChecker
from .exceptions import (
    DatabaseError,
    ConnectionPoolError,
    QueryError,
)

__all__ = [
    "DatabasePool",
    "get_db_pool",
    "HealthChecker",
    "DatabaseError",
    "ConnectionPoolError",
    "QueryError",
]

