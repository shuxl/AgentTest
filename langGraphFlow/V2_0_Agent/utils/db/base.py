"""
SQLAlchemy Base 类和数据库引擎管理
提供异步数据库会话和引擎的创建与管理
使用统一的数据库连接池管理（通过 utils.database）
"""
import logging
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
)
from sqlalchemy.orm import declarative_base
from ..database import get_db_pool

logger = logging.getLogger(__name__)

# 创建 Base 类，用于定义数据模型
Base = declarative_base()

# 全局会话工厂（使用统一管理的引擎）
_async_session_maker: Optional[async_sessionmaker[AsyncSession]] = None


def get_async_engine() -> AsyncEngine:
    """
    获取 SQLAlchemy 异步引擎（从统一的数据库连接池管理器获取）
    
    Returns:
        AsyncEngine: SQLAlchemy 异步引擎实例
        
    Note:
        - 引擎由 utils.database.DatabasePool 统一管理
        - 确保与 LangGraph 连接池配置一致
    """
    db_pool = get_db_pool()
    engine = db_pool.sqlalchemy_engine
    
    if engine is None:
        raise RuntimeError(
            "SQLAlchemy 引擎未初始化。请先调用 database.get_db_pool().create_pool() 初始化连接池。"
        )
    
    return engine


def get_async_session() -> async_sessionmaker[AsyncSession]:
    """
    获取或创建异步会话工厂（单例模式）
    
    Returns:
        async_sessionmaker[AsyncSession]: 异步会话工厂
    """
    global _async_session_maker
    
    if _async_session_maker is None:
        engine = get_async_engine()
        _async_session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,  # 提交后不过期对象，允许访问已提交的数据
        )
        logger.info("异步会话工厂创建成功（使用统一管理的引擎）")
    
    return _async_session_maker


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话的依赖注入函数（用于 FastAPI 等框架）
    
    Yields:
        AsyncSession: 数据库会话实例
        
    Example:
        ```python
        async with get_db_session() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
        ```
    """
    async_session_maker = get_async_session()
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_engine():
    """
    关闭数据库引擎（应用关闭时调用）
    注意：实际关闭操作由 utils.database.DatabasePool.close() 统一管理
    """
    global _async_session_maker
    
    # 重置会话工厂（引擎关闭由 DatabasePool 统一管理）
    _async_session_maker = None
    logger.info("SQLAlchemy 会话工厂已重置（引擎关闭由 DatabasePool 统一管理）")

