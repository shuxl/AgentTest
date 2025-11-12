"""
Redis连接管理模块
提供Redis连接和会话管理功能
"""
import logging
import redis.asyncio as redis
from typing import Optional

from core.config import Settings
from .exceptions import ConnectionError, OperationError

logger = logging.getLogger(__name__)


class RedisManager:
    """Redis连接管理类"""
    
    def __init__(self, settings: Settings, decode_responses: bool = True):
        """
        初始化Redis连接管理器
        
        Args:
            settings: 配置实例
            decode_responses: 是否自动解码响应为字符串
        """
        self.settings = settings
        self.host = settings.redis_host
        self.port = settings.redis_port
        self.db = settings.redis_db
        self.decode_responses = decode_responses
        self._client: Optional[redis.Redis] = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """
        初始化Redis连接池
        
        Raises:
            ConnectionError: 当连接池初始化失败时抛出
        """
        try:
            if not self._initialized:
                # 创建Redis客户端（自动管理连接池）
                self._client = redis.Redis(
                    host=self.host,
                    port=self.port,
                    db=self.db,
                    decode_responses=self.decode_responses,
                    max_connections=50  # 最大连接数
                )
                
                # 测试连接
                await self._client.ping()
                
                self._initialized = True
                logger.info(f"Redis连接池初始化成功 (host={self.host}, port={self.port}, db={self.db})")
        except Exception as e:
            logger.error(f"Redis连接池初始化失败: {str(e)}")
            raise ConnectionError(f"Redis连接池初始化失败: {str(e)}", e)
    
    def get_client(self) -> redis.Redis:
        """
        获取Redis客户端实例（懒加载）
        
        Returns:
            redis.Redis: Redis客户端实例
            
        Raises:
            ConnectionError: 当客户端未初始化时抛出
        """
        if self._client is None:
            # 如果没有初始化，尝试初始化
            if not self._initialized:
                # 同步初始化（在异步环境中应该先调用initialize）
                logger.warning("Redis客户端未初始化，尝试懒加载初始化")
                # 创建Redis客户端（自动管理连接池）
                self._client = redis.Redis(
                    host=self.host,
                    port=self.port,
                    db=self.db,
                    decode_responses=self.decode_responses,
                    max_connections=50
                )
                self._initialized = True
        return self._client
    
    async def close(self):
        """关闭Redis连接"""
        if self._client:
            await self._client.close()
            self._client = None
            logger.info("Redis连接已关闭")
        
        self._initialized = False
    
    async def ping(self) -> bool:
        """
        测试Redis连接
        
        Returns:
            bool: 连接成功返回True，否则返回False
        """
        try:
            client = self.get_client()
            result = await client.ping()
            return result
        except Exception as e:
            logger.error(f"Redis连接测试失败: {str(e)}")
            return False
    
    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """
        设置键值对
        
        Args:
            key: 键名
            value: 值
            ex: 过期时间（秒），None表示不过期
            
        Returns:
            bool: 设置成功返回True
            
        Raises:
            OperationError: 当操作失败时抛出
        """
        try:
            client = self.get_client()
            result = await client.set(key, value, ex=ex)
            return result
        except Exception as e:
            logger.error(f"Redis SET操作失败: {str(e)}")
            raise OperationError(f"Redis SET操作失败: {str(e)}", e)
    
    async def get(self, key: str) -> Optional[str]:
        """
        获取键值
        
        Args:
            key: 键名
            
        Returns:
            Optional[str]: 键值，如果不存在则返回None
            
        Raises:
            OperationError: 当操作失败时抛出
        """
        try:
            client = self.get_client()
            result = await client.get(key)
            return result
        except Exception as e:
            logger.error(f"Redis GET操作失败: {str(e)}")
            raise OperationError(f"Redis GET操作失败: {str(e)}", e)
    
    async def delete(self, *keys: str) -> int:
        """
        删除键
        
        Args:
            *keys: 要删除的键名列表
            
        Returns:
            int: 删除的键数量
            
        Raises:
            OperationError: 当操作失败时抛出
        """
        try:
            client = self.get_client()
            result = await client.delete(*keys)
            return result
        except Exception as e:
            logger.error(f"Redis DELETE操作失败: {str(e)}")
            raise OperationError(f"Redis DELETE操作失败: {str(e)}", e)
    
    async def exists(self, key: str) -> bool:
        """
        检查键是否存在
        
        Args:
            key: 键名
            
        Returns:
            bool: 键存在返回True，否则返回False
            
        Raises:
            OperationError: 当操作失败时抛出
        """
        try:
            client = self.get_client()
            result = await client.exists(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis EXISTS操作失败: {str(e)}")
            raise OperationError(f"Redis EXISTS操作失败: {str(e)}", e)
    
    @property
    def client(self) -> Optional[redis.Redis]:
        """获取Redis客户端实例"""
        return self._client


# 全局Redis管理器实例
_redis_manager: Optional[RedisManager] = None


def get_redis_manager(settings: Settings = None) -> RedisManager:
    """
    获取全局Redis管理器实例（单例模式）
    
    Args:
        settings: 配置实例（可选，如果不提供则从get_settings获取）
    
    Returns:
        RedisManager: Redis管理器实例
    """
    global _redis_manager
    if _redis_manager is None:
        if settings is None:
            from core.config import get_settings
            settings = get_settings()
        _redis_manager = RedisManager(settings=settings)
    return _redis_manager

