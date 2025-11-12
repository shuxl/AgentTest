# 缓存模块测试

本目录包含缓存模块（core.cache）的单元测试。

## 测试文件

- `test_redis.py` - Redis缓存管理模块单元测试

## 测试范围

### Redis缓存管理模块测试 (`test_redis.py`)

- `test_redis_initialization()` - Redis连接初始化测试
- `test_redis_initialization_with_mock()` - Redis连接初始化（Mock测试）
- `test_redis_get_client()` - 获取Redis客户端测试
- `test_redis_set_operation()` - Redis SET操作测试
- `test_redis_get_operation()` - Redis GET操作测试
- `test_redis_delete_operation()` - Redis DELETE操作测试
- `test_redis_exists_operation()` - Redis EXISTS操作测试
- `test_redis_ping_operation()` - Redis PING操作测试
- `test_redis_connection_error()` - Redis连接错误异常处理测试
- `test_redis_operation_error()` - Redis操作错误异常处理测试
- `test_redis_connection_pool_management()` - Redis连接池管理测试
- `test_redis_singleton_pattern()` - Redis管理器单例模式测试
- `test_redis_integration_with_real_redis()` - Redis集成测试（需要真实Redis服务）

## 运行方式

```bash
cd langGraphFlow/V2_0_Agent

# Redis缓存管理模块单元测试（Mock测试，不需要真实Redis服务）
conda run -n py_311_rag python tests/unit/cache/test_redis.py

# 启用集成测试（需要真实Redis服务）
ENABLE_REDIS_INTEGRATION_TEST=true conda run -n py_311_rag python tests/unit/cache/test_redis.py
```

## 测试特点

- **Mock测试**：大部分测试使用Mock，不需要真实Redis服务
- **异常处理测试**：测试ConnectionError和OperationError异常处理
- **连接池管理测试**：测试连接池的创建、使用和关闭
- **单例模式测试**：验证get_redis_manager的单例行为
- **集成测试**：可选的真实Redis服务集成测试（需要设置环境变量）

## 前置条件

### Mock测试（默认）
- 无特殊前置条件（使用Mock，不依赖外部服务）

### 集成测试（可选）
- Redis服务正在运行
- 环境变量 `ENABLE_REDIS_INTEGRATION_TEST=true`
- Redis配置正确（通过Settings配置）

## 相关文档

- `core/cache/` - 缓存管理模块实现
- `V2.0-04-项目结构调整开发计划.md` - 缓存管理模块重构计划

## 测试说明

### Mock测试 vs 集成测试

- **Mock测试**：使用unittest.mock模拟Redis客户端，不需要真实Redis服务，适合CI/CD环境
- **集成测试**：需要真实Redis服务，测试实际连接和操作，适合本地开发环境验证

### 异常处理测试

测试覆盖了以下异常场景：
- 连接初始化失败（ConnectionError）
- 操作失败（OperationError）
- 各种Redis操作的异常情况

### 连接池管理

测试验证了：
- 连接池的创建和初始化
- 连接池的正确使用
- 连接池的关闭和清理

