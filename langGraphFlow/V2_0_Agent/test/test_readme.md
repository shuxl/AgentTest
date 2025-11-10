# 测试文档

本目录包含V2.0多智能体路由系统的所有测试用例。

## 📋 文档结构规范

**重要**：为了保持文档的可维护性和可读性，本目录采用分层文档结构：

1. **`test_readme.md`（本文件）**：测试目录的汇总介绍文档
   - 包含目录结构概览
   - 包含各测试模块的简要说明和链接
   - 包含测试环境要求、运行方式汇总等通用信息
   - **不包含**各测试模块的详细说明（详细说明在各子目录的README.md中）

2. **各子目录的 `README.md`**：每个测试子目录都有自己的README.md文件
   - 包含该目录下所有测试文件的详细说明
   - 包含测试范围、测试用例、运行方式、前置条件等详细信息
   - 例如：`router/README.md`、`blood_pressure/README.md` 等

**文档维护规则**：
- ✅ 新增测试模块时，在对应子目录创建或更新 `README.md`
- ✅ 在 `test_readme.md` 中添加简要说明和链接
- ❌ 不要在 `test_readme.md` 中写入详细的测试说明（应放在子目录的README.md中）
- ✅ 保持 `test_readme.md` 简洁，作为导航和汇总文档

---

## 目录结构

```
V2_0_Agent/
├── test/                         # 单元测试和集成测试
│   ├── router/                  # 路由功能测试
│   │   ├── README.md            # 路由测试详细说明
│   │   └── test_router.py      # 路由单元测试
│   ├── blood_pressure/          # 血压记录智能体测试
│   │   ├── README.md            # 血压记录测试详细说明
│   │   └── test_blood_pressure_integration.py
│   ├── appointment/             # 复诊管理智能体测试
│   │   ├── README.md            # 复诊管理测试详细说明
│   │   └── test_appointment_integration.py
│   ├── infrastructure/          # 基础设施测试
│   │   ├── README.md            # 基础设施测试详细说明
│   │   ├── test_sqlalchemy_setup.py
│   │   ├── test_pool_compatibility.py
│   │   ├── test_transaction_isolation.py
│   │   ├── test_performance_comparison.py
│   │   └── test_unified_pool_management.py
│   ├── db_models/               # 数据模型测试
│   │   ├── README.md            # 数据模型测试详细说明
│   │   └── test_db_models.py
│   ├── crud/                    # CRUD 操作测试
│   │   ├── README.md            # CRUD测试详细说明
│   │   └── test_crud_operations.py
│   ├── tools/                   # 工具单元测试
│   │   ├── README.md            # 工具测试详细说明
│   │   ├── test_blood_pressure_tools.py
│   │   └── test_appointment_tools.py
│   └── integration/             # 集成测试
│       ├── README.md            # 集成测试详细说明
│       ├── test_crud_integration.py
│       └── test_e2e_functionality.py
│   └── rag/                     # RAG模块测试
│       ├── README.md            # RAG模块测试详细说明
│       └── test_rag_modules.py
│   └── diagnosis/              # 诊断智能体测试
│       ├── README.md            # 诊断智能体测试详细说明
│       └── test_internal_medicine_diagnosis_integration.py
│   └── rag_env_check/          # RAG环境检查测试
│       ├── README.md            # RAG环境检查测试详细说明
│       ├── test_rag_infrastructure.py
│       ├── init_pgvector.sql   # pgvector扩展初始化SQL脚本
│       └── test_data/
│           ├── test_medical.md
│           └── test_surgery.txt
```

## 测试模块概览

### 1. 路由功能测试 (`router/`)

路由智能体的单元测试，测试意图识别和路由决策功能。

**详细说明**：参见 [`router/README.md`](router/README.md)

**运行方式**：
```bash
# 路由功能单元测试
conda run -n py_311_rag python test/router/test_router.py

# 路由图创建测试
conda run -n py_311_rag python test/router/test_router_graph.py

# 意图澄清功能测试
conda run -n py_311_rag python test/router/test_clarify_intent.py
```

---

### 2. 血压记录智能体测试 (`blood_pressure/`)

血压记录智能体的集成测试，测试完整的业务流程。

**详细说明**：参见 [`blood_pressure/README.md`](blood_pressure/README.md)

**运行方式**：
```bash
conda run -n py_311_rag python test/blood_pressure/test_blood_pressure_integration.py
```

---

### 3. 复诊管理智能体测试 (`appointment/`)

复诊管理智能体的集成测试，测试完整的业务流程。

**详细说明**：参见 [`appointment/README.md`](appointment/README.md)

**运行方式**：
```bash
conda run -n py_311_rag python test/appointment/test_appointment_integration.py
```

---

### 4. 基础设施测试 (`infrastructure/`)

数据库连接、SQLAlchemy兼容性等基础设施测试。

**详细说明**：参见 [`infrastructure/README.md`](infrastructure/README.md)

**测试文件**：
- `test_sqlalchemy_setup.py` - SQLAlchemy 环境准备测试
- `test_pool_compatibility.py` - 连接池兼容性测试
- `test_transaction_isolation.py` - 事务隔离测试
- `test_performance_comparison.py` - 性能对比测试
- `test_unified_pool_management.py` - 统一连接池管理测试

**运行方式**：
```bash
conda run -n py_311_rag python test/infrastructure/test_*.py
```

---

### 5. 数据模型测试 (`db_models/`)

SQLAlchemy数据模型和Alembic配置的验证测试。

**详细说明**：参见 [`db_models/README.md`](db_models/README.md)

**运行方式**：
```bash
conda run -n py_311_rag python test/db_models/test_db_models.py
```

---

### 6. CRUD 操作测试 (`crud/`)

CRUD基类的单元测试。

**详细说明**：参见 [`crud/README.md`](crud/README.md)

**运行方式**：
```bash
conda run -n py_311_rag python test/crud/test_crud_operations.py
```

---

### 7. 工具单元测试 (`tools/`)

各个工具模块的单元测试。

**详细说明**：参见 [`tools/README.md`](tools/README.md)

**测试文件**：
- `test_blood_pressure_tools.py` - 血压记录工具测试
- `test_appointment_tools.py` - 复诊管理工具测试

**运行方式**：
```bash
conda run -n py_311_rag python test/tools/test_*.py
```

---

### 8. 集成测试 (`integration/`)

CRUD重构后的集成测试和端到端功能测试。

**详细说明**：参见 [`integration/README.md`](integration/README.md)

**测试文件**：
- `test_crud_integration.py` - CRUD重构后集成测试
- `test_e2e_functionality.py` - 端到端功能测试

**运行方式**：
```bash
conda run -n py_311_rag python test/integration/test_*.py
```

---

### 9. RAG模块测试 (`rag/`)

RAG基础设施模块的单元测试，测试文档读取、分块、embedding、向量数据库操作和RAG检索流程。

**详细说明**：参见 [`rag/README.md`](rag/README.md)

**运行方式**：
```bash
conda run -n py_311_rag python test/rag/test_rag_modules.py
```

---

### 10. RAG环境检查测试 (`rag_env_check/`)

RAG基础设施的环境验证测试，用于验证本地环境是否支持诊断智能体所需的RAG功能。

**详细说明**：参见 [`rag_env_check/README.md`](rag_env_check/README.md)

**运行方式**：
```bash
conda run -n py_311_rag python test/rag_env_check/test_rag_infrastructure.py
```

---

### 11. 诊断智能体测试 (`diagnosis/`)

诊断智能体的集成测试，测试从路由到诊断智能体的完整流程。

**详细说明**：参见 [`diagnosis/README.md`](diagnosis/README.md)

**运行方式**：
```bash
conda run -n py_311_rag python test/diagnosis/test_internal_medicine_diagnosis_integration.py
```

---

## 快速运行所有测试

```bash
cd langGraphFlow/V2_0_Agent

# 路由功能测试
conda run -n py_311_rag python test/router/test_router.py
conda run -n py_311_rag python test/router/test_router_graph.py
conda run -n py_311_rag python test/router/test_clarify_intent.py

# 血压记录集成测试
conda run -n py_311_rag python test/blood_pressure/test_blood_pressure_integration.py

# 复诊管理集成测试
conda run -n py_311_rag python test/appointment/test_appointment_integration.py

# 基础设施测试
conda run -n py_311_rag python test/infrastructure/test_sqlalchemy_setup.py
conda run -n py_311_rag python test/infrastructure/test_pool_compatibility.py
conda run -n py_311_rag python test/infrastructure/test_transaction_isolation.py
conda run -n py_311_rag python test/infrastructure/test_performance_comparison.py
conda run -n py_311_rag python test/infrastructure/test_unified_pool_management.py

# 数据模型测试
conda run -n py_311_rag python test/db_models/test_db_models.py

# CRUD 操作测试
conda run -n py_311_rag python test/crud/test_crud_operations.py

# 工具单元测试
conda run -n py_311_rag python test/tools/test_blood_pressure_tools.py
conda run -n py_311_rag python test/tools/test_appointment_tools.py

# 集成测试
conda run -n py_311_rag python test/integration/test_crud_integration.py
conda run -n py_311_rag python test/integration/test_e2e_functionality.py

# RAG模块测试
conda run -n py_311_rag python test/rag/test_rag_modules.py

# 诊断智能体集成测试
conda run -n py_311_rag python test/diagnosis/test_internal_medicine_diagnosis_integration.py

# RAG环境检查测试
conda run -n py_311_rag python test/rag_env_check/test_rag_infrastructure.py
```

## 测试环境要求

1. **Python环境**: 使用conda环境 `py_311_rag` (Python 3.11)
2. **数据库**: PostgreSQL数据库，配置在环境变量 `DB_URI` 中
3. **LLM API**: DeepSeek API Key，配置在环境变量 `DEEPSEEK_API_KEY` 中
4. **依赖包**: 安装 `requirements.txt` 中的所有依赖

## 环境变量配置

确保以下环境变量已正确设置：

```bash
# 数据库配置
export DB_URI="postgresql://postgres:password@localhost:5432/dbname?sslmode=disable"

# Redis配置（如果需要）
export REDIS_HOST="localhost"
export REDIS_PORT="6379"
export REDIS_DB="0"

# LLM配置
export DEEPSEEK_API_KEY="your-api-key-here"
export LLM_TYPE="deepseek-chat"
export LLM_TEMPERATURE="0"
```

## 测试数据管理

### 自动清理

- 集成测试会在测试开始前清理旧的测试数据
- 测试结束后可选择保留或清理测试数据（默认保留，便于查看）

### 测试用户ID和会话ID

- 血压记录测试：`user_id="test_user_bp_001"`, `session_id="test_session_bp_001"`
- 复诊管理测试：`user_id="test_user_appt_001"`, `session_id="test_session_appt_001"`

### 数据库表

集成测试会自动创建所需的数据库表：
- `blood_pressure_records` - 血压记录表
- `appointments` - 预约记录表
- `checkpoints` - LangGraph checkpoint表
- `checkpoint_writes` - checkpoint写入记录表
- `checkpoint_blobs` - checkpoint数据blob表

## 测试覆盖率

### 当前覆盖范围

- ✅ 路由核心功能（意图识别、路由决策）
- ✅ 血压记录完整流程（CRUD操作）
- ✅ 复诊管理完整流程（CRUD操作）
- ✅ 相对时间解析功能
- ✅ 数据库表结构验证
- ✅ SQLAlchemy 数据模型定义验证
- ✅ Alembic 迁移配置验证
- ✅ CRUD 基类功能测试
- ✅ 重构后工具单元测试
- ✅ 重构后工具与 LangGraph 集成测试
- ✅ 统一连接池管理测试
- ✅ RAG环境检查测试（文档读取功能）
- ✅ RAG模块测试（文档读取、分块、Embedding、向量数据库、RAG检索流程）

### 待补充测试

- ⏳ RAG环境检查测试（文档分块、Embedding、向量数据库、RAG检索流程）
- ⏳ 诊断智能体测试
- ⏳ Redis连接测试
- ⏳ 工具函数单元测试
- ⏳ 异常情况和错误处理测试
- ⏳ 性能压力测试

## 注意事项

1. **测试顺序**: 路由功能测试可以独立运行，集成测试需要数据库和LLM API
2. **测试隔离**: 每个集成测试使用独立的user_id和session_id，避免冲突
3. **数据清理**: 集成测试会清理checkpoint和store数据，但默认保留数据库记录供查看
4. **路径处理**: 所有测试文件都已配置正确的路径处理，可以从项目根目录直接运行

## 故障排查

### 常见问题

1. **ImportError**: 确保从项目根目录运行测试，路径处理会正确设置
2. **数据库连接失败**: 检查 `DB_URI` 环境变量是否正确
3. **LLM API调用失败**: 检查 `DEEPSEEK_API_KEY` 是否正确设置
4. **表不存在错误**: 集成测试会自动创建表，如果失败请检查数据库权限

### 调试建议

- 查看测试输出中的详细日志信息
- 检查数据库中的测试数据是否正确创建
- 使用测试脚本验证数据库连接和配置
