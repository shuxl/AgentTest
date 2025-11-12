"""
数据库连接池管理模块
提供PostgreSQL数据库连接池的创建和管理功能
统一管理 psycopg_pool（LangGraph）和 SQLAlchemy 的连接池
"""
import logging
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from core.config import Settings
from .health import HealthChecker
from .exceptions import ConnectionPoolError, DatabaseError

logger = logging.getLogger(__name__)


class DatabasePool:
    """数据库连接池管理类（统一管理 LangGraph 和 SQLAlchemy 连接池）"""
    
    def __init__(self, settings: Settings):
        """
        初始化数据库连接池
        
        Args:
            settings: 配置实例
        """
        self.settings = settings
        self.db_uri = settings.db_uri
        self.min_size = settings.db_min_size
        self.max_size = settings.db_max_size
        self.timezone = settings.db_timezone
        self._pool: Optional[AsyncConnectionPool] = None  # LangGraph 使用的连接池
        self._sqlalchemy_engine: Optional[AsyncEngine] = None  # SQLAlchemy 使用的引擎
        self._initialized = False
    
    async def initialize(self) -> None:
        """
        初始化连接池和引擎
        
        Raises:
            ConnectionPoolError: 当连接池初始化失败时抛出
        """
        try:
            if not self._initialized:
                # 初始化LangGraph连接池
                await self._init_langgraph_pool()
                # 初始化SQLAlchemy引擎
                await self._init_sqlalchemy_engine()
                self._initialized = True
                logger.info("数据库连接池初始化成功")
        except Exception as e:
            logger.error(f"数据库连接池初始化失败: {str(e)}")
            raise ConnectionPoolError(f"数据库连接池初始化失败: {str(e)}", e)
    
    async def _init_langgraph_pool(self) -> None:
        """初始化LangGraph连接池"""
        if self._pool is None:
            # 设置连接工厂，在每次创建连接时设置时区
            async def configure_connection(conn):
                async with conn.cursor() as cur:
                    await cur.execute(f"SET timezone = '{self.timezone}';")
            
            self._pool = AsyncConnectionPool(
                conninfo=self.db_uri,
                min_size=self.min_size,
                max_size=self.max_size,
                kwargs={"autocommit": True, "prepare_threshold": 0, "row_factory": dict_row},
                # 使用连接工厂配置时区
                configure=configure_connection
            )
            await self._pool.open()
            logger.info(
                f"LangGraph 数据库连接池创建成功 "
                f"(min_size={self.min_size}, max_size={self.max_size}, timezone={self.timezone})"
            )
    
    async def _init_sqlalchemy_engine(self) -> None:
        """初始化 SQLAlchemy 引擎（确保与 LangGraph 连接池配置一致）"""
        if self._sqlalchemy_engine is None:
            # 转换连接字符串：postgresql:// -> postgresql+psycopg://
            if self.db_uri.startswith("postgresql://"):
                sqlalchemy_uri = self.db_uri.replace("postgresql://", "postgresql+psycopg://", 1)
            elif self.db_uri.startswith("postgresql+psycopg://"):
                sqlalchemy_uri = self.db_uri
            else:
                raise ValueError(f"不支持的数据库URI格式: {self.db_uri}")
            
            # 创建异步引擎，配置与 LangGraph 连接池一致
            self._sqlalchemy_engine = create_async_engine(
                sqlalchemy_uri,
                echo=False,  # 设置为 True 可以看到 SQL 日志（调试用）
                pool_pre_ping=True,  # 连接前ping，确保连接有效
                pool_size=self.min_size,  # 连接池最小连接数（与 LangGraph 一致）
                max_overflow=self.max_size - self.min_size,  # 最大溢出连接数
                # 连接工厂：设置时区（与 LangGraph 一致）
                connect_args={
                    "options": f"-c timezone={self.timezone}"
                }
            )
            logger.info(
                f"SQLAlchemy 异步引擎创建成功 "
                f"(pool_size={self.min_size}, max_overflow={self.max_size - self.min_size}, "
                f"timezone={self.timezone})"
            )
    
    async def create_pool(self) -> AsyncConnectionPool:
        """
        创建数据库连接池（供 LangGraph 使用）
        
        Returns:
            AsyncConnectionPool: 数据库连接池实例
            
        Raises:
            ConnectionPoolError: 当连接池创建失败时抛出
        """
        try:
            if not self._initialized:
                await self.initialize()
            return self._pool
        except Exception as e:
            logger.error(f"数据库连接池创建失败: {str(e)}")
            raise ConnectionPoolError(f"数据库连接池创建失败: {str(e)}", e)
    
    async def close(self):
        """关闭所有数据库连接池"""
        # 关闭 SQLAlchemy 引擎
        if self._sqlalchemy_engine:
            await self._sqlalchemy_engine.dispose()
            self._sqlalchemy_engine = None
            logger.info("SQLAlchemy 引擎已关闭")
        
        # 关闭 LangGraph 连接池
        if self._pool:
            await self._pool.close()
            self._pool = None
            logger.info("LangGraph 数据库连接池已关闭")
        
        self._initialized = False
    
    async def health_check(self) -> dict:
        """
        执行健康检查
        
        Returns:
            dict: 健康检查结果
        """
        checker = HealthChecker(pool=self._pool, engine=self._sqlalchemy_engine)
        return await checker.check()
    
    @property
    def pool(self) -> Optional[AsyncConnectionPool]:
        """获取 LangGraph 连接池实例"""
        return self._pool
    
    @property
    def sqlalchemy_engine(self) -> Optional[AsyncEngine]:
        """获取 SQLAlchemy 引擎实例"""
        return self._sqlalchemy_engine
    
    def get_pool_stats(self) -> dict:
        """
        获取连接池统计信息
        
        Returns:
            dict: 包含连接池统计信息的字典
        """
        stats = {
            "langgraph_pool": None,
            "sqlalchemy_engine": None
        }
        
        if self._pool:
            try:
                # psycopg_pool 的统计信息
                stats["langgraph_pool"] = {
                    "min_size": self.min_size,
                    "max_size": self.max_size,
                    "pool_size": getattr(self._pool, "pool_size", None),
                    "available": getattr(self._pool, "available", None),
                    "waiting": getattr(self._pool, "waiting", None),
                }
            except Exception as e:
                logger.warning(f"获取 LangGraph 连接池统计信息失败: {str(e)}")
        
        if self._sqlalchemy_engine:
            try:
                # SQLAlchemy 的统计信息
                pool = self._sqlalchemy_engine.pool
                # size 和 overflow 是方法，需要调用
                size = pool.size() if hasattr(pool, "size") and callable(pool.size) else None
                overflow = pool.overflow() if hasattr(pool, "overflow") and callable(pool.overflow) else None
                
                stats["sqlalchemy_engine"] = {
                    "size": size,
                    "checked_in": getattr(pool, "checked_in", None),
                    "checked_out": getattr(pool, "checked_out", None),
                    "overflow": overflow,
                    "invalid": getattr(pool, "invalid", None),
                }
            except Exception as e:
                logger.warning(f"获取 SQLAlchemy 连接池统计信息失败: {str(e)}")
        
        return stats


# 全局数据库连接池实例
_db_pool: Optional[DatabasePool] = None


def get_db_pool(settings: Settings = None) -> DatabasePool:
    """
    获取全局数据库连接池实例（单例模式）
    
    Args:
        settings: 配置实例（可选，如果不提供则从get_settings获取）
    
    Returns:
        DatabasePool: 数据库连接池实例
    """
    global _db_pool
    if _db_pool is None:
        if settings is None:
            from core.config import get_settings
            settings = get_settings()
        _db_pool = DatabasePool(settings=settings)
    return _db_pool

