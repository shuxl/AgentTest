"""
数据库连接池管理模块
提供PostgreSQL数据库连接池的创建和管理功能
使用psycopg_pool的AsyncConnectionPool，与LangGraph兼容
"""
import logging
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row
from typing import Optional
from .config import Config

logger = logging.getLogger(__name__)


class DatabasePool:
    """数据库连接池管理类"""
    
    def __init__(self, db_uri: str, min_size: int = 5, max_size: int = 10):
        """
        初始化数据库连接池
        
        Args:
            db_uri: PostgreSQL数据库连接URI
            min_size: 连接池最小连接数
            max_size: 连接池最大连接数
        """
        self.db_uri = db_uri
        self.min_size = min_size
        self.max_size = max_size
        self._pool: Optional[AsyncConnectionPool] = None
    
    async def create_pool(self) -> AsyncConnectionPool:
        """
        创建数据库连接池
        
        Returns:
            AsyncConnectionPool: 数据库连接池实例
            
        Raises:
            Exception: 当连接池创建失败时抛出
        """
        try:
            from .config import Config
            # 设置连接工厂，在每次创建连接时设置时区
            async def configure_connection(conn):
                async with conn.cursor() as cur:
                    await cur.execute(f"SET timezone = '{Config.DB_TIMEZONE}';")
            
            self._pool = AsyncConnectionPool(
                conninfo=self.db_uri,
                min_size=self.min_size,
                max_size=self.max_size,
                kwargs={"autocommit": True, "prepare_threshold": 0, "row_factory": dict_row},
                # 使用连接工厂配置时区
                configure=configure_connection
            )
            await self._pool.open()
            logger.info(f"数据库连接池创建成功 (min_size={self.min_size}, max_size={self.max_size}, timezone={Config.DB_TIMEZONE})")
            return self._pool
        except Exception as e:
            logger.error(f"数据库连接池创建失败: {str(e)}")
            raise
    
    async def close(self):
        """关闭数据库连接池"""
        if self._pool:
            await self._pool.close()
            logger.info("数据库连接池已关闭")
    
    @property
    def pool(self) -> Optional[AsyncConnectionPool]:
        """获取连接池实例"""
        return self._pool


# 全局数据库连接池实例
_db_pool: Optional[DatabasePool] = None


def get_db_pool() -> DatabasePool:
    """
    获取全局数据库连接池实例（单例模式）
    
    Returns:
        DatabasePool: 数据库连接池实例
    """
    global _db_pool
    if _db_pool is None:
        _db_pool = DatabasePool(
            db_uri=Config.DB_URI,
            min_size=Config.MIN_SIZE,
            max_size=Config.MAX_SIZE
        )
    return _db_pool

