# 日志模块测试

本目录包含日志管理模块（core.logging）的单元测试。

## 测试文件

- `test_config.py` - 日志管理模块单元测试

## 测试范围

### 日志管理模块测试 (`test_config.py`)

- `test_create_formatter_default()` - 日志格式化器创建（默认格式）测试
- `test_create_formatter_custom()` - 日志格式化器创建（自定义格式）测试
- `test_create_console_handler_default()` - 控制台处理器创建（默认配置）测试
- `test_create_console_handler_custom()` - 控制台处理器创建（自定义配置）测试
- `test_create_file_handler_default()` - 文件处理器创建（默认配置）测试
- `test_create_file_handler_custom()` - 文件处理器创建（自定义配置）测试
- `test_console_handler_log_output()` - 控制台处理器日志输出测试
- `test_file_handler_log_output()` - 文件处理器日志输出测试
- `test_log_format()` - 日志格式测试
- `test_setup_logging_initialization()` - 日志配置初始化测试
- `test_setup_logging_with_default_settings()` - 日志配置初始化（使用默认配置）测试
- `test_log_level_filtering()` - 日志级别过滤测试
- `test_file_handler_directory_creation()` - 文件处理器自动创建目录测试

## 运行方式

```bash
cd langGraphFlow/V2_0_Agent

# 日志管理模块单元测试
conda run -n py_311_rag python tests/unit/logging/test_config.py
```

## 测试特点

- **格式化器测试**：测试默认和自定义日志格式
- **处理器测试**：测试控制台和文件处理器的创建和配置
- **日志输出测试**：验证日志能正确输出到控制台和文件
- **日志格式测试**：验证日志格式包含必要字段（时间戳、级别、消息等）
- **配置初始化测试**：测试日志系统的完整初始化流程
- **级别过滤测试**：验证日志级别过滤功能
- **目录创建测试**：验证文件处理器能自动创建不存在的目录

## 前置条件

- 无特殊前置条件（使用临时文件，不依赖外部服务）

## 相关文档

- `core/logging/` - 日志管理模块实现
- `V2.0-04-项目结构调整开发计划.md` - 日志管理模块重构计划

## 测试说明

### 临时文件管理

测试使用临时文件和目录，测试完成后会自动清理，不会在系统中留下测试文件。

### 日志格式验证

测试验证日志格式包含以下字段：
- 时间戳（asctime）
- 日志记录器名称（name）
- 日志级别（levelname）
- 日志消息（message）

### 处理器类型

测试覆盖了以下处理器类型：
- `logging.StreamHandler` - 控制台处理器
- `logging.handlers.RotatingFileHandler` / `ConcurrentRotatingFileHandler` - 文件处理器

