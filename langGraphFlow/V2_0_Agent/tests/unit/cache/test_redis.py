"""
Redis缓存管理模块测试
测试core.cache模块的功能
"""
import os
import sys
import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Optional

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from core.cache import RedisManager, get_redis_manager, ConnectionError, OperationError
from core.config import Settings


async def test_redis_initialization():
    """测试Redis连接初始化"""
    print("=" * 60)
    print("测试1：Redis连接初始化")
    print("=" * 60)
    
    settings = Settings()
    redis_manager = RedisManager(settings=settings)
    
    # 验证初始状态
    assert redis_manager._client is None
    assert redis_manager._initialized is False
    assert redis_manager.host == settings.redis_host
    assert redis_manager.port == settings.redis_port
    assert redis_manager.db == settings.redis_db
    
    print("✅ Redis管理器初始化测试通过")


async def test_redis_initialization_with_mock():
    """测试Redis连接初始化（使用Mock）"""
    print("=" * 60)
    print("测试2：Redis连接初始化（Mock测试）")
    print("=" * 60)
    
    settings = Settings()
    redis_manager = RedisManager(settings=settings)
    
    # Mock Redis客户端
    mock_client = AsyncMock()
    mock_client.ping = AsyncMock(return_value=True)
    
    with patch('core.cache.redis.redis.Redis', return_value=mock_client):
        await redis_manager.initialize()
        
        assert redis_manager._initialized is True
        assert redis_manager._client is not None
        mock_client.ping.assert_called_once()
    
    print("✅ Redis连接初始化（Mock）测试通过")


async def test_redis_get_client():
    """测试获取Redis客户端"""
    print("=" * 60)
    print("测试3：获取Redis客户端")
    print("=" * 60)
    
    settings = Settings()
    redis_manager = RedisManager(settings=settings)
    
    # Mock Redis客户端
    mock_client = AsyncMock()
    mock_client.ping = AsyncMock(return_value=True)
    
    with patch('core.cache.redis.redis.Redis', return_value=mock_client):
        # 测试懒加载
        client = redis_manager.get_client()
        assert client is not None
        assert redis_manager._initialized is True
    
    print("✅ 获取Redis客户端测试通过")


async def test_redis_set_operation():
    """测试Redis SET操作"""
    print("=" * 60)
    print("测试4：Redis SET操作")
    print("=" * 60)
    
    settings = Settings()
    redis_manager = RedisManager(settings=settings)
    
    # Mock Redis客户端
    mock_client = AsyncMock()
    mock_client.set = AsyncMock(return_value=True)
    mock_client.ping = AsyncMock(return_value=True)
    
    with patch('core.cache.redis.redis.Redis', return_value=mock_client):
        await redis_manager.initialize()
        
        # 测试SET操作
        result = await redis_manager.set("test_key", "test_value")
        assert result is True
        mock_client.set.assert_called_once_with("test_key", "test_value", ex=None)
        
        # 测试SET操作（带过期时间）
        result = await redis_manager.set("test_key", "test_value", ex=3600)
        assert result is True
        mock_client.set.assert_called_with("test_key", "test_value", ex=3600)
    
    print("✅ Redis SET操作测试通过")


async def test_redis_get_operation():
    """测试Redis GET操作"""
    print("=" * 60)
    print("测试5：Redis GET操作")
    print("=" * 60)
    
    settings = Settings()
    redis_manager = RedisManager(settings=settings)
    
    # Mock Redis客户端
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value="test_value")
    mock_client.ping = AsyncMock(return_value=True)
    
    with patch('core.cache.redis.redis.Redis', return_value=mock_client):
        await redis_manager.initialize()
        
        # 测试GET操作（存在）
        result = await redis_manager.get("test_key")
        assert result == "test_value"
        mock_client.get.assert_called_once_with("test_key")
        
        # 测试GET操作（不存在）
        mock_client.get = AsyncMock(return_value=None)
        result = await redis_manager.get("non_existent_key")
        assert result is None
    
    print("✅ Redis GET操作测试通过")


async def test_redis_delete_operation():
    """测试Redis DELETE操作"""
    print("=" * 60)
    print("测试6：Redis DELETE操作")
    print("=" * 60)
    
    settings = Settings()
    redis_manager = RedisManager(settings=settings)
    
    # Mock Redis客户端
    mock_client = AsyncMock()
    mock_client.delete = AsyncMock(return_value=1)
    mock_client.ping = AsyncMock(return_value=True)
    
    with patch('core.cache.redis.redis.Redis', return_value=mock_client):
        await redis_manager.initialize()
        
        # 测试DELETE操作（单个键）
        result = await redis_manager.delete("test_key")
        assert result == 1
        mock_client.delete.assert_called_once_with("test_key")
        
        # 测试DELETE操作（多个键）
        mock_client.delete = AsyncMock(return_value=2)
        result = await redis_manager.delete("key1", "key2")
        assert result == 2
        mock_client.delete.assert_called_with("key1", "key2")
    
    print("✅ Redis DELETE操作测试通过")


async def test_redis_exists_operation():
    """测试Redis EXISTS操作"""
    print("=" * 60)
    print("测试7：Redis EXISTS操作")
    print("=" * 60)
    
    settings = Settings()
    redis_manager = RedisManager(settings=settings)
    
    # Mock Redis客户端
    mock_client = AsyncMock()
    mock_client.exists = AsyncMock(return_value=1)  # 存在
    mock_client.ping = AsyncMock(return_value=True)
    
    with patch('core.cache.redis.redis.Redis', return_value=mock_client):
        await redis_manager.initialize()
        
        # 测试EXISTS操作（存在）
        result = await redis_manager.exists("test_key")
        assert result is True
        mock_client.exists.assert_called_once_with("test_key")
        
        # 测试EXISTS操作（不存在）
        mock_client.exists = AsyncMock(return_value=0)
        result = await redis_manager.exists("non_existent_key")
        assert result is False
    
    print("✅ Redis EXISTS操作测试通过")


async def test_redis_ping_operation():
    """测试Redis PING操作"""
    print("=" * 60)
    print("测试8：Redis PING操作")
    print("=" * 60)
    
    settings = Settings()
    redis_manager = RedisManager(settings=settings)
    
    # Mock Redis客户端
    mock_client = AsyncMock()
    mock_client.ping = AsyncMock(return_value=True)
    
    with patch('core.cache.redis.redis.Redis', return_value=mock_client):
        await redis_manager.initialize()
        
        # 测试PING操作
        result = await redis_manager.ping()
        assert result is True
        mock_client.ping.assert_called()
    
    print("✅ Redis PING操作测试通过")


async def test_redis_connection_error():
    """测试Redis连接错误异常处理"""
    print("=" * 60)
    print("测试9：Redis连接错误异常处理")
    print("=" * 60)
    
    settings = Settings()
    redis_manager = RedisManager(settings=settings)
    
    # Mock Redis客户端抛出连接错误
    mock_client = AsyncMock()
    mock_client.ping = AsyncMock(side_effect=Exception("Connection refused"))
    
    with patch('core.cache.redis.redis.Redis', return_value=mock_client):
        try:
            await redis_manager.initialize()
            assert False, "应该抛出ConnectionError"
        except ConnectionError as e:
            assert "Redis连接池初始化失败" in str(e)
            print("✅ ConnectionError异常处理测试通过")


async def test_redis_operation_error():
    """测试Redis操作错误异常处理"""
    print("=" * 60)
    print("测试10：Redis操作错误异常处理")
    print("=" * 60)
    
    settings = Settings()
    redis_manager = RedisManager(settings=settings)
    
    # Mock Redis客户端抛出操作错误
    mock_client = AsyncMock()
    mock_client.ping = AsyncMock(return_value=True)
    mock_client.set = AsyncMock(side_effect=Exception("Operation failed"))
    mock_client.get = AsyncMock(side_effect=Exception("Operation failed"))
    mock_client.delete = AsyncMock(side_effect=Exception("Operation failed"))
    mock_client.exists = AsyncMock(side_effect=Exception("Operation failed"))
    
    with patch('core.cache.redis.redis.Redis', return_value=mock_client):
        await redis_manager.initialize()
        
        # 测试SET操作错误
        try:
            await redis_manager.set("test_key", "test_value")
            assert False, "应该抛出OperationError"
        except OperationError as e:
            assert "Redis SET操作失败" in str(e)
        
        # 测试GET操作错误
        try:
            await redis_manager.get("test_key")
            assert False, "应该抛出OperationError"
        except OperationError as e:
            assert "Redis GET操作失败" in str(e)
        
        # 测试DELETE操作错误
        try:
            await redis_manager.delete("test_key")
            assert False, "应该抛出OperationError"
        except OperationError as e:
            assert "Redis DELETE操作失败" in str(e)
        
        # 测试EXISTS操作错误
        try:
            await redis_manager.exists("test_key")
            assert False, "应该抛出OperationError"
        except OperationError as e:
            assert "Redis EXISTS操作失败" in str(e)
    
    print("✅ OperationError异常处理测试通过")


async def test_redis_connection_pool_management():
    """测试Redis连接管理"""
    print("=" * 60)
    print("测试11：Redis连接管理")
    print("=" * 60)
    
    settings = Settings()
    redis_manager = RedisManager(settings=settings)
    
    # Mock客户端
    mock_client = AsyncMock()
    mock_client.ping = AsyncMock(return_value=True)
    mock_client.close = AsyncMock()
    
    with patch('core.cache.redis.redis.Redis', return_value=mock_client):
        # 初始化连接
        await redis_manager.initialize()
        assert redis_manager._client is not None
        assert redis_manager._initialized is True
        
        # 测试关闭连接
        await redis_manager.close()
        mock_client.close.assert_called_once()
        assert redis_manager._client is None
        assert redis_manager._initialized is False
    
    print("✅ Redis连接管理测试通过")


async def test_redis_singleton_pattern():
    """测试Redis管理器单例模式"""
    print("=" * 60)
    print("测试12：Redis管理器单例模式")
    print("=" * 60)
    
    # 清除全局实例（用于测试）
    import core.cache.redis as redis_module
    redis_module._redis_manager = None
    
    manager1 = get_redis_manager()
    manager2 = get_redis_manager()
    
    assert manager1 is manager2
    print("✅ Redis管理器单例模式测试通过")


async def test_redis_integration_with_real_redis():
    """测试Redis集成（需要真实Redis服务）"""
    print("=" * 60)
    print("测试13：Redis集成测试（需要真实Redis服务）")
    print("=" * 60)
    
    # 检查是否启用集成测试
    enable_integration_test = os.getenv("ENABLE_REDIS_INTEGRATION_TEST", "false").lower() == "true"
    
    if not enable_integration_test:
        print("⏭️  跳过集成测试（设置环境变量 ENABLE_REDIS_INTEGRATION_TEST=true 启用）")
        return
    
    settings = Settings()
    redis_manager = RedisManager(settings=settings)
    
    try:
        # 初始化连接
        await redis_manager.initialize()
        
        # 测试基本操作
        test_key = "test_integration_key"
        test_value = "test_integration_value"
        
        # SET操作
        result = await redis_manager.set(test_key, test_value)
        assert result is True
        
        # GET操作
        value = await redis_manager.get(test_key)
        assert value == test_value
        
        # EXISTS操作
        exists = await redis_manager.exists(test_key)
        assert exists is True
        
        # DELETE操作
        deleted = await redis_manager.delete(test_key)
        assert deleted == 1
        
        # 验证已删除
        exists_after_delete = await redis_manager.exists(test_key)
        assert exists_after_delete is False
        
        # 关闭连接
        await redis_manager.close()
        
        print("✅ Redis集成测试通过")
    except ConnectionError as e:
        print(f"⚠️  Redis集成测试跳过：无法连接到Redis服务 ({str(e)})")
    except Exception as e:
        print(f"❌ Redis集成测试失败: {str(e)}")
        raise


async def main():
    """主测试函数"""
    print("=" * 60)
    print("开始测试Redis缓存管理模块...")
    print("=" * 60)
    print()
    
    # 运行所有测试
    await test_redis_initialization()
    print()
    
    await test_redis_initialization_with_mock()
    print()
    
    await test_redis_get_client()
    print()
    
    await test_redis_set_operation()
    print()
    
    await test_redis_get_operation()
    print()
    
    await test_redis_delete_operation()
    print()
    
    await test_redis_exists_operation()
    print()
    
    await test_redis_ping_operation()
    print()
    
    await test_redis_connection_error()
    print()
    
    await test_redis_operation_error()
    print()
    
    await test_redis_connection_pool_management()
    print()
    
    await test_redis_singleton_pattern()
    print()
    
    await test_redis_integration_with_real_redis()
    print()
    
    print("=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

