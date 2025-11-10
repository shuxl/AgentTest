# 复诊管理智能体测试

本目录包含复诊管理智能体的集成测试。

## 测试文件

- `test_appointment_integration.py` - 复诊管理集成测试

## 测试范围

- 完整业务流程测试（预约 -> 查询 -> 更新）
- 标准时间格式预约测试
- 相对时间格式解析测试（如"本周一上午10点"）
- 预约状态更新测试
- 数据库记录验证

## 测试用例

1. **测试1**: 创建预约（标准格式 - "明天下午2点"）
2. **测试2**: 查询预约记录
3. **测试3**: 创建预约（相对时间格式 - "本周一上午10点"）
4. **测试4**: 查询所有预约记录
5. **测试5**: 更新预约状态
6. **测试6**: 验证数据库中的记录

## 运行方式

```bash
cd langGraphFlow/V2_0_Agent
conda run -n py_311_rag python test/appointment/test_appointment_integration.py
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
- 已创建appointments表（或测试会自动创建）

## 测试数据

- 测试用户ID：`test_user_appt_001`
- 测试会话ID：`test_session_appt_001`

## 相关文档

- `V2.0-13-复诊管理智能体详细设计.md` - 复诊管理智能体详细设计
- `utils/agents/appointment_agent.py` - 复诊管理智能体实现
- `utils/tools/appointment_tools.py` - 复诊管理工具实现

