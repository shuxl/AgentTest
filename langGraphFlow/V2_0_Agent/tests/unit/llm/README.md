# LLM模块测试

本目录包含LLM管理模块（core.llm）的单元测试。

## 测试文件

- `test_factory.py` - LLM工厂模块单元测试
- `test_callbacks.py` - LLM回调模块单元测试

## 测试范围

### LLM工厂模块测试 (`test_factory.py`)

- `test_llm_factory_initialization()` - LLMFactory初始化测试
- `test_get_api_key_success()` - _get_api_key方法（成功）测试
- `test_get_api_key_from_settings()` - _get_api_key方法（从配置获取环境变量名）测试
- `test_get_api_key_missing()` - _get_api_key方法（API Key缺失）测试
- `test_get_api_key_empty()` - _get_api_key方法（API Key为空）测试
- `test_create_with_defaults()` - create方法（使用默认配置）测试
- `test_create_with_custom_params()` - create方法（使用自定义参数）测试
- `test_create_with_callbacks()` - create方法（使用自定义回调）测试
- `test_create_initialization_error()` - create方法（初始化错误）测试
- `test_create_api_key_error()` - create方法（API Key错误）测试
- `test_create_by_config_deepseek()` - create_by_config方法（deepseek-chat）测试
- `test_create_by_config_invalid_type()` - create_by_config方法（无效的LLM类型）测试
- `test_create_by_config_empty_type()` - create_by_config方法（空的LLM类型）测试
- `test_create_by_config_invalid_temperature()` - create_by_config方法（无效的温度参数）测试
- `test_get_llm_factory_singleton()` - get_llm_factory单例模式测试
- `test_get_llm_by_config()` - get_llm_by_config函数测试

### LLM回调模块测试 (`test_callbacks.py`)

- `test_model_interaction_logger_initialization()` - ModelInteractionLogger初始化测试
- `test_on_llm_start()` - on_llm_start回调测试
- `test_on_llm_end()` - on_llm_end回调测试
- `test_on_llm_error()` - on_llm_error回调测试
- `test_on_chat_model_start()` - on_chat_model_start回调测试
- `test_on_chat_model_end()` - on_chat_model_end回调测试
- `test_on_chat_model_error()` - on_chat_model_error回调测试
- `test_on_llm_start_with_long_prompt()` - on_llm_start回调（长提示词截断）测试
- `test_on_llm_end_with_tool_calls()` - on_llm_end回调（包含工具调用）测试
- `test_get_model_interaction_logger()` - get_model_interaction_logger函数测试
- `test_multiple_run_ids()` - 多个run_id的管理测试

## 运行方式

```bash
cd langGraphFlow/V2_0_Agent

# LLM工厂模块单元测试
conda run -n py_311_rag python tests/unit/llm/test_factory.py

# LLM回调模块单元测试
conda run -n py_311_rag python tests/unit/llm/test_callbacks.py
```

## 测试特点

### LLM工厂模块测试
- **Mock测试**：使用Mock模拟LLM初始化，不需要真实API调用
- **异常处理测试**：测试InitializationError和APIError异常处理
- **配置验证测试**：测试LLM类型、温度参数等配置验证
- **单例模式测试**：验证get_llm_factory的单例行为

### LLM回调模块测试
- **回调功能测试**：测试所有LLM和ChatModel回调方法
- **日志输出测试**：验证回调能正确记录日志
- **错误处理测试**：测试错误回调的处理
- **边界情况测试**：测试长提示词截断、工具调用等特殊情况

## 前置条件

- 无特殊前置条件（使用Mock，不依赖外部服务或API）

## 相关文档

- `core/llm/` - LLM管理模块实现
- `V2.0-04-项目结构调整开发计划.md` - LLM管理模块重构计划

## 测试说明

### Mock测试

所有测试都使用Mock来模拟LLM初始化和API调用，不需要真实的API Key或网络连接，适合CI/CD环境。

### 异常处理测试

测试覆盖了以下异常场景：
- API Key缺失或为空（InitializationError）
- LLM初始化失败（InitializationError）
- 无效的LLM类型（InitializationError）
- 无效的温度参数（InitializationError）

### 回调测试

测试验证了所有回调方法：
- LLM回调：on_llm_start, on_llm_end, on_llm_error
- ChatModel回调：on_chat_model_start, on_chat_model_end, on_chat_model_error

### 日志记录

回调测试会验证日志记录功能，包括：
- 请求和响应信息的记录
- 错误信息的记录
- 工具调用的记录
- 长内容的截断处理

