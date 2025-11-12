# 集成测试

本目录包含CRUD重构后的集成测试和端到端功能测试。

## 测试文件

- `test_crud_integration.py` - CRUD 重构后集成测试
- `test_e2e_functionality.py` - 端到端功能测试

## 测试范围

### CRUD 重构后集成测试

- 工具接口兼容性测试
- 血压记录智能体集成测试
- 复诊管理智能体集成测试
- 并发操作测试

### 端到端功能测试

- 完整业务流程测试（血压记录、复诊管理）
- 多用户并发场景测试
- 数据一致性验证

## 运行方式

```bash
cd langGraphFlow/V2_0_Agent

# CRUD 重构后集成测试
conda run -n py_311_rag python tests/integration/test_crud_integration.py

# 端到端功能测试
conda run -n py_311_rag python tests/e2e/test_e2e_functionality.py
```

## 测试特点

- 验证重构后的工具与 LangGraph 集成正常
- 测试工具接口向后兼容性
- 验证并发操作稳定性
- 验证数据正确保存到数据库
- 需要数据库连接和LLM API

## 前置条件

- 已安装 SQLAlchemy 2.0+ 和 greenlet
- 数据库连接配置正确（Config.DB_URI）
- LLM API 配置正确（DEEPSEEK_API_KEY）
- 数据库服务正在运行

## 相关文档

- `domain/agents/` - 智能体实现
- `domain/agents/*/tools.py` - 工具实现
- `domain/models/crud.py` - CRUD 基类实现

