# 核心模块测试

本目录包含核心模块（core）的单元测试。

## 测试文件

- `test_config.py` - 配置管理模块单元测试

## 测试范围

### 配置管理模块测试 (`test_config.py`)

- `test_default_settings()` - 默认配置测试
- `test_backward_compatibility()` - 向后兼容属性测试
- `test_get_settings_singleton()` - 单例模式测试
- `test_port_validation()` - 端口验证测试
- `test_validate_db_uri_valid()` - 数据库URI验证（有效）测试
- `test_validate_db_uri_invalid()` - 数据库URI验证（无效）测试
- `test_validate_redis_config_valid()` - Redis配置验证（有效）测试
- `test_validate_redis_config_invalid()` - Redis配置验证（无效）测试

## 运行方式

```bash
cd langGraphFlow/V2_0_Agent

# 配置管理模块单元测试
conda run -n py_311_rag python tests/unit/core/test_config.py
```

## 测试特点

- **test_config.py**: 单元测试，不依赖数据库，测试配置管理核心功能
- 验证配置加载机制（环境变量、配置文件、默认值）
- 验证配置类型检查和验证规则
- 验证向后兼容属性
- 验证单例模式

## 前置条件

- 无特殊前置条件（纯单元测试，不依赖外部服务）

## 相关文档

- `core/config/` - 配置管理模块实现
- `V2.0-04-项目结构调整开发计划.md` - 配置管理模块重构计划

