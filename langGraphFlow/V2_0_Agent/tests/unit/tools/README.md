# 工具单元测试

本目录包含各个工具模块的单元测试。

## 测试文件

- `test_blood_pressure_tools.py` - 血压记录工具单元测试（SQLAlchemy ORM）
- `test_appointment_tools.py` - 复诊管理工具单元测试（SQLAlchemy ORM）

## 测试用例

### 血压记录工具测试 (`test_blood_pressure_tools.py`)

1. **test_record_blood_pressure**：测试 `record_blood_pressure` 工具
2. **test_query_blood_pressure**：测试 `query_blood_pressure` 工具
3. **test_update_blood_pressure**：测试 `update_blood_pressure` 工具
4. **test_info_tool**：测试 `info` 工具

### 复诊管理工具测试 (`test_appointment_tools.py`)

1. **test_appointment_booking**：测试 `appointment_booking` 工具
2. **test_query_appointment**：测试 `query_appointment` 工具
3. **test_update_appointment**：测试 `update_appointment` 工具

## 运行方式

```bash
# 血压记录工具测试
cd langGraphFlow/V2_0_Agent
conda run -n py_311_rag python tests/unit/tools/test_blood_pressure_tools.py

# 复诊管理工具测试
conda run -n py_311_rag python tests/unit/tools/test_appointment_tools.py
```

## 测试特点

- 验证重构后的工具功能正常
- 测试工具接口兼容性
- 验证 SQLAlchemy ORM 操作
- 单元测试，需要数据库连接

## 前置条件

- 已安装 SQLAlchemy 2.0+ 和 greenlet
- 数据库连接配置正确（Config.DB_URI）
- 数据库服务正在运行
- 已创建相应的数据库表（blood_pressure_records、appointments）

## 相关文档

- `domain/agents/blood_pressure/tools.py` - 血压记录工具实现
- `domain/agents/appointment/tools.py` - 复诊管理工具实现
- `domain/models/crud.py` - CRUD 基类实现

**注意**：工具模块已从 `utils/tools/` 迁移到 `domain/agents/*/tools.py`，测试文件仍使用向后兼容层 `utils.tools`，建议新代码使用 `domain.agents`。

