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
├── tests/                        # 测试目录
│   ├── unit/                    # 单元测试
│   │   ├── core/                # 核心模块测试
│   │   │   ├── README.md        # 核心模块测试详细说明
│   │   │   └── test_config.py  # 配置管理模块测试
│   │   ├── router/              # 路由功能测试
│   │   │   ├── README.md        # 路由测试详细说明
│   │   │   ├── test_router.py   # 路由单元测试
│   │   │   ├── test_router_graph.py
│   │   │   └── test_clarify_intent.py
│   │   ├── crud/                # CRUD 操作测试
│   │   │   ├── README.md        # CRUD测试详细说明
│   │   │   └── test_crud_operations.py
│   │   ├── db_models/           # 数据模型测试
│   │   │   ├── README.md        # 数据模型测试详细说明
│   │   │   └── test_db_models.py
│   │   ├── cache/               # 缓存模块测试
│   │   │   ├── README.md        # 缓存模块测试详细说明
│   │   │   └── test_redis.py    # Redis缓存管理模块测试
│   │   ├── logging/             # 日志模块测试
│   │   │   ├── README.md        # 日志模块测试详细说明
│   │   │   └── test_config.py  # 日志管理模块测试
│   │   ├── llm/                 # LLM模块测试
│   │   │   ├── README.md        # LLM模块测试详细说明
│   │   │   ├── test_factory.py  # LLM工厂模块测试
│   │   │   └── test_callbacks.py # LLM回调模块测试
│   │   └── tools/               # 工具单元测试
│   │       ├── README.md        # 工具测试详细说明
│   │       ├── test_blood_pressure_tools.py
│   │       └── test_appointment_tools.py
│   ├── integration/             # 集成测试
│   │   ├── blood_pressure/      # 血压记录智能体测试
│   │   │   ├── README.md        # 血压记录测试详细说明
│   │   │   └── test_blood_pressure_integration.py
│   │   ├── appointment/         # 复诊管理智能体测试
│   │   │   ├── README.md        # 复诊管理测试详细说明
│   │   │   └── test_appointment_integration.py
│   │   ├── diagnosis/           # 诊断智能体测试
│   │   │   ├── README.md        # 诊断智能体测试详细说明
│   │   │   ├── test_internal_medicine_diagnosis_integration.py
│   │   │   └── test_multi_department_diagnosis.py
│   │   ├── infrastructure/      # 基础设施测试
│   │   │   ├── README.md        # 基础设施测试详细说明
│   │   │   ├── test_sqlalchemy_setup.py
│   │   │   ├── test_pool_compatibility.py
│   │   │   ├── test_transaction_isolation.py
│   │   │   ├── test_performance_comparison.py
│   │   │   └── test_unified_pool_management.py
│   │   ├── rag/                 # RAG模块测试
│   │   │   ├── README.md        # RAG模块测试详细说明
│   │   │   └── test_rag_modules.py
│   │   ├── rag_env_check/       # RAG环境检查测试
│   │   │   ├── README.md        # RAG环境检查测试详细说明
│   │   │   ├── test_rag_infrastructure.py
│   │   │   ├── init_pgvector.sql # pgvector扩展初始化SQL脚本
│   │   │   └── test_data/
│   │   │       ├── test_medical.md
│   │   │       └── test_surgery.txt
│   │   ├── README.md            # 集成测试详细说明
│   │   └── test_crud_integration.py
│   └── e2e/                     # 端到端测试
│       └── test_e2e_functionality.py
```

## pytest 执行方式

pytest 是项目的主要测试框架。**所有 pytest 命令必须在项目根目录（`V2_0_Agent/`）下执行**。

### 快速开始

```bash
# 运行所有测试
conda run -n py_311_rag python -m pytest

# 运行 core 目录下的所有测试文件（示例）
conda run -n py_311_rag python -m pytest tests/unit/core/ -sv

# 运行特定测试文件
conda run -n py_311_rag python -m pytest tests/unit/core/test_config.py -sv
conda run -n py_311_rag python -u -m pytest tests/unit/router/test_router.py -sv
```

**详细使用说明**：请参见 [pytest 使用指南](pytest_usage.md)

---

## 测试模块概览

### 1. 核心模块测试 (`unit/core/`)

核心模块（core）的单元测试，测试配置管理等功能。

**详细说明**：参见 [`unit/core/README.md`](unit/core/README.md)

**运行方式**：
```bash
# 配置管理模块单元测试
conda run -n py_311_rag python tests/unit/core/test_config.py
```

---

### 2. 路由功能测试 (`unit/router/`)

路由智能体的单元测试，测试意图识别和路由决策功能。

**详细说明**：参见 [`unit/router/README.md`](unit/router/README.md)

**运行方式**：
```bash
# 路由功能单元测试
conda run -n py_311_rag python tests/unit/router/test_router.py

# 路由图创建测试
conda run -n py_311_rag python tests/unit/router/test_router_graph.py

# 意图澄清功能测试
conda run -n py_311_rag python tests/unit/router/test_clarify_intent.py
```

---

### 3. 血压记录智能体测试 (`integration/blood_pressure/`)

血压记录智能体的集成测试，测试完整的业务流程。

**详细说明**：参见 [`integration/blood_pressure/README.md`](integration/blood_pressure/README.md)

**运行方式**：
```bash
conda run -n py_311_rag python tests/integration/blood_pressure/test_blood_pressure_integration.py
```

---

### 4. 复诊管理智能体测试 (`integration/appointment/`)

复诊管理智能体的集成测试，测试完整的业务流程。

**详细说明**：参见 [`integration/appointment/README.md`](integration/appointment/README.md)

**运行方式**：
```bash
conda run -n py_311_rag python tests/integration/appointment/test_appointment_integration.py
```

---

### 5. 基础设施测试 (`integration/infrastructure/`)

数据库连接、SQLAlchemy兼容性等基础设施测试。

**详细说明**：参见 [`integration/infrastructure/README.md`](integration/infrastructure/README.md)

**测试文件**：
- `test_sqlalchemy_setup.py` - SQLAlchemy 环境准备测试
- `test_pool_compatibility.py` - 连接池兼容性测试
- `test_transaction_isolation.py` - 事务隔离测试
- `test_performance_comparison.py` - 性能对比测试
- `test_unified_pool_management.py` - 统一连接池管理测试

**运行方式**：
```bash
conda run -n py_311_rag python tests/integration/infrastructure/test_*.py
```

---

### 6. 数据模型测试 (`unit/db_models/`)

SQLAlchemy数据模型和Alembic配置的验证测试。

**详细说明**：参见 [`unit/db_models/README.md`](unit/db_models/README.md)

**运行方式**：
```bash
conda run -n py_311_rag python tests/unit/db_models/test_db_models.py
```

---

### 7. 缓存模块测试 (`unit/cache/`)

Redis缓存管理模块的单元测试，测试Redis连接、基本操作和异常处理。

**详细说明**：参见 [`unit/cache/README.md`](unit/cache/README.md)

**运行方式**：
```bash
# Redis缓存管理模块单元测试（Mock测试，不需要真实Redis服务）
conda run -n py_311_rag python tests/unit/cache/test_redis.py

# 启用集成测试（需要真实Redis服务）
ENABLE_REDIS_INTEGRATION_TEST=true conda run -n py_311_rag python tests/unit/cache/test_redis.py
```

---

### 8. 日志模块测试 (`unit/logging/`)

日志管理模块的单元测试，测试日志配置、格式化器、处理器和日志输出。

**详细说明**：参见 [`unit/logging/README.md`](unit/logging/README.md)

**运行方式**：
```bash
# 日志管理模块单元测试
conda run -n py_311_rag python tests/unit/logging/test_config.py
```

---

### 9. LLM模块测试 (`unit/llm/`)

LLM管理模块的单元测试，测试LLM工厂和回调功能。

**详细说明**：参见 [`unit/llm/README.md`](unit/llm/README.md)

**运行方式**：
```bash
# LLM工厂模块单元测试
conda run -n py_311_rag python tests/unit/llm/test_factory.py

# LLM回调模块单元测试
conda run -n py_311_rag python tests/unit/llm/test_callbacks.py
```

---

### 10. CRUD 操作测试 (`unit/crud/`)

CRUD基类的单元测试。

**详细说明**：参见 [`unit/crud/README.md`](unit/crud/README.md)

**运行方式**：
```bash
conda run -n py_311_rag python tests/unit/crud/test_crud_operations.py
```

---

### 11. 工具单元测试 (`unit/tools/`)

各个工具模块的单元测试。

**详细说明**：参见 [`unit/tools/README.md`](unit/tools/README.md)

**测试文件**：
- `test_blood_pressure_tools.py` - 血压记录工具测试
- `test_appointment_tools.py` - 复诊管理工具测试

**运行方式**：
```bash
conda run -n py_311_rag python tests/unit/tools/test_*.py
```

---

### 12. 集成测试 (`integration/`)

CRUD重构后的集成测试和端到端功能测试。

**详细说明**：参见 [`integration/README.md`](integration/README.md)

**测试文件**：
- `test_crud_integration.py` - CRUD重构后集成测试

**运行方式**：
```bash
conda run -n py_311_rag python tests/integration/test_crud_integration.py
```

---

### 13. RAG模块测试 (`integration/rag/`)

RAG基础设施模块的单元测试，测试文档读取、分块、embedding、向量数据库操作和RAG检索流程。

**详细说明**：参见 [`integration/rag/README.md`](integration/rag/README.md)

**运行方式**：
```bash
conda run -n py_311_rag python tests/integration/rag/test_rag_modules.py
```

---

### 14. RAG环境检查测试 (`integration/rag_env_check/`)

RAG基础设施的环境验证测试，用于验证本地环境是否支持诊断智能体所需的RAG功能。

**详细说明**：参见 [`integration/rag_env_check/README.md`](integration/rag_env_check/README.md)

**运行方式**：
```bash
conda run -n py_311_rag python tests/integration/rag_env_check/test_rag_infrastructure.py
```

---

### 15. 诊断智能体测试 (`integration/diagnosis/`)

诊断智能体的集成测试，测试从路由到诊断智能体的完整流程。

**详细说明**：参见 [`integration/diagnosis/README.md`](integration/diagnosis/README.md)

**测试文件**：
- `test_internal_medicine_diagnosis_integration.py` - 内科诊断智能体集成测试
- `test_multi_department_diagnosis.py` - 多科室诊断智能体集成测试

**运行方式**：
```bash
# 内科诊断智能体集成测试
conda run -n py_311_rag python tests/integration/diagnosis/test_internal_medicine_diagnosis_integration.py

# 多科室诊断智能体集成测试
conda run -n py_311_rag python tests/integration/diagnosis/test_multi_department_diagnosis.py
```

---

### 16. 端到端测试 (`e2e/`)

端到端功能测试。

**运行方式**：
```bash
conda run -n py_311_rag python tests/e2e/test_e2e_functionality.py
```

---

## 快速运行所有测试

```bash
cd langGraphFlow/V2_0_Agent

# 核心模块测试
conda run -n py_311_rag python tests/unit/core/test_config.py

# 路由功能测试
conda run -n py_311_rag python tests/unit/router/test_router.py
conda run -n py_311_rag python tests/unit/router/test_router_graph.py
conda run -n py_311_rag python tests/unit/router/test_clarify_intent.py

# 血压记录集成测试
conda run -n py_311_rag python tests/integration/blood_pressure/test_blood_pressure_integration.py

# 复诊管理集成测试
conda run -n py_311_rag python tests/integration/appointment/test_appointment_integration.py

# 基础设施测试
conda run -n py_311_rag python tests/integration/infrastructure/test_sqlalchemy_setup.py
conda run -n py_311_rag python tests/integration/infrastructure/test_pool_compatibility.py
conda run -n py_311_rag python tests/integration/infrastructure/test_transaction_isolation.py
conda run -n py_311_rag python tests/integration/infrastructure/test_performance_comparison.py
conda run -n py_311_rag python tests/integration/infrastructure/test_unified_pool_management.py

# 数据模型测试
conda run -n py_311_rag python tests/unit/db_models/test_db_models.py

# 缓存模块测试
conda run -n py_311_rag python tests/unit/cache/test_redis.py

# 日志模块测试
conda run -n py_311_rag python tests/unit/logging/test_config.py

# LLM模块测试
conda run -n py_311_rag python tests/unit/llm/test_factory.py
conda run -n py_311_rag python tests/unit/llm/test_callbacks.py

# CRUD 操作测试
conda run -n py_311_rag python tests/unit/crud/test_crud_operations.py

# 工具单元测试
conda run -n py_311_rag python tests/unit/tools/test_blood_pressure_tools.py
conda run -n py_311_rag python tests/unit/tools/test_appointment_tools.py

# 集成测试
conda run -n py_311_rag python tests/integration/test_crud_integration.py

# RAG模块测试
conda run -n py_311_rag python tests/integration/rag/test_rag_modules.py

# 诊断智能体集成测试
conda run -n py_311_rag python tests/integration/diagnosis/test_internal_medicine_diagnosis_integration.py
conda run -n py_311_rag python tests/integration/diagnosis/test_multi_department_diagnosis.py

# RAG环境检查测试
conda run -n py_311_rag python tests/integration/rag_env_check/test_rag_infrastructure.py

# 端到端测试
conda run -n py_311_rag python tests/e2e/test_e2e_functionality.py
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

- ✅ 配置管理模块（配置加载、验证、类型检查）
- ✅ Redis缓存管理模块（连接初始化、基本操作、异常处理、连接池管理）
- ✅ 日志管理模块（日志配置初始化、格式化器创建、处理器创建、日志输出、日志格式）
- ✅ LLM管理模块（LLM工厂初始化、LLM创建、API Key管理、回调处理、异常处理）
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

---

## 相关文档

- **[pytest 使用指南](pytest_usage.md)** - pytest 详细使用说明，包括执行命令、输出选项、测试标记等
