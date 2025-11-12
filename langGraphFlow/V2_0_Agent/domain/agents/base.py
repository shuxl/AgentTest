"""
智能体基类
定义智能体的统一接口和通用方法
"""
from abc import ABC, abstractmethod
from typing import Optional
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.postgres import AsyncPostgresStore
from psycopg_pool import AsyncConnectionPool
from domain.router import RouterState


class BaseAgent(ABC):
    """智能体基类（可选，用于定义统一接口）"""
    
    def __init__(
        self,
        pool: AsyncConnectionPool,
        checkpointer: Optional[AsyncPostgresSaver] = None,
        store: Optional[AsyncPostgresStore] = None
    ):
        """
        初始化智能体
        
        Args:
            pool: PostgreSQL数据库连接池实例
            checkpointer: PostgreSQL Checkpointer实例
            store: PostgreSQL Store实例（可选）
        """
        self.pool = pool
        self.checkpointer = checkpointer
        self.store = store
    
    @abstractmethod
    async def process(self, state: RouterState) -> RouterState:
        """
        处理路由状态
        
        Args:
            state: 路由状态
            
        Returns:
            RouterState: 更新后的路由状态
        """
        pass
    
    def get_system_prompt(self) -> str:
        """
        获取系统提示词
        
        Returns:
            str: 系统提示词
        """
        return ""

