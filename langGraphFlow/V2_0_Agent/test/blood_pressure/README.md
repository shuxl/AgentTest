# 血压记录智能体测试

本目录包含血压记录智能体的集成测试。

## 测试文件

- `test_blood_pressure_integration.py` - 血压记录集成测试

## 测试范围

- 完整业务流程测试（记录 -> 查询 -> 更新）
- 标准时间格式记录测试
- 相对时间格式解析测试（如"昨天下午"、"本周一"）
- 原始时间描述保存和显示验证
- 统计信息查询测试
- 数据库表结构验证

## 测试用例

1. **测试1**: 记录血压（标准格式 - "今天早上8点"）
2. **测试2**: 记录血压（相对时间格式 - "昨天下午"）
3. **测试3**: 查询血压记录（验证原始时间描述）
4. **测试4**: 查询统计信息
5. **测试5**: 相对时间解析测试（"本周一上午"）

## 运行方式

```bash
cd langGraphFlow/V2_0_Agent
conda run -n py_311_rag python test/blood_pressure/test_blood_pressure_integration.py
```

## 测试特点

- 集成测试，需要数据库连接
- 需要初始化checkpointer和store
- 自动创建和验证数据库表结构
- 包含测试数据清理功能
- 测试完整的智能体交互流程

## 前置条件

- 数据库连接配置正确（Config.DB_URI）
- LLM API配置正确（DEEPSEEK_API_KEY）
- 已创建blood_pressure_records表（或测试会自动创建）

## 测试数据

- 测试用户ID：`test_user_bp_001`
- 测试会话ID：`test_session_bp_001`

## 相关文档

- `V2.0-12-血压记录智能体详细设计.md` - 血压记录智能体详细设计
- `utils/agents/blood_pressure_agent.py` - 血压记录智能体实现
- `utils/tools/blood_pressure_tools.py` - 血压记录工具实现

