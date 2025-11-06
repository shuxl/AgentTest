"""
Redis连接管理模块
提供Redis连接和会话管理功能
"""
import logging
import redis.asyncio as redis
from typing import Optional
from .config import Config

logger = logging.getLogger(__name__)


class RedisManager:
    """Redis连接管理类"""
    
    def __init__(self, host: str, port: int, db: int, decode_responses: bool = True):
        """
        初始化Redis连接管理器
        
        Args:
            host: Redis服务器地址
            port: Redis服务器端口
            db: Redis数据库编号
            decode_responses: 是否自动解码响应为字符串
        """
        self.host = host
        self.port = port
        self.db = db
        self.decode_responses = decode_responses
        self._client: Optional[redis.Redis] = None
    
    def get_client(self) -> redis.Redis:
        """
        获取Redis客户端实例（懒加载）
        
        Returns:
            redis.Redis: Redis客户端实例
        """
        if self._client is None:
            self._client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=self.decode_responses
            )
            logger.info(f"Redis连接创建成功 (host={self.host}, port={self.port}, db={self.db})")
        return self._client
    
    async def close(self):
        """关闭Redis连接"""
        if self._client:
            await self._client.close()
            logger.info("Redis连接已关闭")
    
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
        """
        try:
            client = self.get_client()
            result = await client.set(key, value, ex=ex)
            return result
        except Exception as e:
            logger.error(f"Redis SET操作失败: {str(e)}")
            raise
    
    async def get(self, key: str) -> Optional[str]:
        """
        获取键值
        
        Args:
            key: 键名
            
        Returns:
            Optional[str]: 键值，如果不存在则返回None
        """
        try:
            client = self.get_client()
            result = await client.get(key)
            return result
        except Exception as e:
            logger.error(f"Redis GET操作失败: {str(e)}")
            raise
    
    async def delete(self, *keys: str) -> int:
        """
        删除键
        
        Args:
            *keys: 要删除的键名列表
            
        Returns:
            int: 删除的键数量
        """
        try:
            client = self.get_client()
            result = await client.delete(*keys)
            return result
        except Exception as e:
            logger.error(f"Redis DELETE操作失败: {str(e)}")
            raise
    
    async def exists(self, key: str) -> bool:
        """
        检查键是否存在
        
        Args:
            key: 键名
            
        Returns:
            bool: 键存在返回True，否则返回False
        """
        try:
            client = self.get_client()
            result = await client.exists(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis EXISTS操作失败: {str(e)}")
            raise
    
    @property
    def client(self) -> Optional[redis.Redis]:
        """获取Redis客户端实例"""
        return self._client


# 全局Redis管理器实例
_redis_manager: Optional[RedisManager] = None


def get_redis_manager() -> RedisManager:
    """
    获取全局Redis管理器实例（单例模式）
    
    Returns:
        RedisManager: Redis管理器实例
    """
    global _redis_manager
    if _redis_manager is None:
        _redis_manager = RedisManager(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            db=Config.REDIS_DB
        )
    return _redis_manager

