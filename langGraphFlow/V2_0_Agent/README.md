# V2.0 多智能体路由系统 - 里程碑1、2和3交付物

## 项目结构

```
V2_0_Agent/
├── app/                       # 应用入口模块
│   ├── __init__.py
│   ├── main.py                # 后端服务入口
│   ├── client.py              # 前端客户端入口
│   └── api/                   # API模块
│       ├── __init__.py
│       ├── routes.py          # API路由定义
│       └── models.py          # API数据模型
├── core/                      # 核心基础代码模块
│   ├── __init__.py
│   └── config/                # 配置管理模块
│       ├── __init__.py
│       ├── base.py            # 配置基类
│       ├── settings.py        # 项目配置
│       └── validators.py      # 配置验证器
├── domain/                    # 业务代码模块
│   ├── __init__.py
│   ├── router/                # 路由业务模块
│   │   ├── __init__.py
│   │   ├── state.py           # 路由状态定义
│   │   ├── node.py            # 路由节点实现
│   │   ├── graph.py           # 路由图创建
│   │   └── tools/             # 路由工具
│   ├── agents/                # 智能体业务模块
│   │   ├── __init__.py
│   │   ├── blood_pressure/    # 血压记录智能体
│   │   ├── appointment/       # 复诊管理智能体
│   │   └── diagnosis/         # 诊断智能体
│   ├── models/                # 数据模型模块
│   │   ├── __init__.py
│   │   ├── base.py            # 基础模型
│   │   ├── crud.py            # CRUD操作
│   │   └── schemas/           # 数据模式
│   └── rag/                   # RAG模块
│       ├── __init__.py
│       ├── knowledge_base_manager.py
│       └── ...
├── infrastructure/            # 基础设施模块
│   ├── __init__.py
│   ├── database/              # 数据库基础设施
│   │   ├── __init__.py
│   │   └── migrations/        # 数据库迁移
│   └── storage/               # 存储基础设施
│       └── __init__.py
├── tests/                     # 测试目录
│   ├── __init__.py
│   ├── conftest.py            # pytest配置和fixtures
│   ├── unit/                  # 单元测试
│   ├── integration/           # 集成测试
│   └── e2e/                   # 端到端测试
├── utils/                     # 工具模块（向后兼容层）
│   ├── __init__.py
│   ├── config.py              # 配置模块（向后兼容）
│   ├── database.py            # 数据库管理（待迁移）
│   ├── redis_manager.py       # Redis管理（待迁移）
│   └── ...
├── scripts/                   # 数据库脚本目录
│   ├── create_blood_pressure_table.py
│   └── create_appointment_table.py
├── logfile/                   # 日志文件目录（.gitignore）
├── generate_lock.py           # 依赖锁定文件生成脚本
├── requirements.txt           # 依赖包列表
└── requirements.lock          # 依赖锁定文件
```

## 环境配置

### 1. 安装依赖

```bash
# 激活conda环境
conda activate py_311_rag

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件或设置以下环境变量：

```bash
# 数据库配置
export DB_URI="postgresql://postgres:password@localhost:5432/dbname?sslmode=disable"

# Redis配置
export REDIS_HOST="localhost"
export REDIS_PORT="6379"
export REDIS_DB="0"

# LLM配置
export DEEPSEEK_API_KEY="your-api-key-here"
export LLM_TYPE="deepseek-chat"
export LLM_TEMPERATURE="0"
```

## 启动服务

### 启动后端服务

```bash
# 激活conda环境
conda activate py_311_rag

# 启动后端服务
conda run -n py_311_rag python app/main.py
```

### 启动前端客户端

```bash
# 激活conda环境
conda activate py_311_rag

# 启动前端客户端（需要先启动后端服务）
conda run -n py_311_rag python app/client.py
```

## 测试

测试文件已整理到 `tests/` 目录下，详细说明请参考 [tests/test_readme.md](tests/test_readme.md)。

### 运行测试

```bash
# 激活conda环境
conda activate py_311_rag

# 路由功能单元测试（不需要数据库）
conda run -n py_311_rag python tests/unit/router/test_router.py

# 血压记录集成测试（需要数据库和LLM API）
conda run -n py_311_rag python tests/integration/blood_pressure/test_blood_pressure_integration.py

# 复诊管理集成测试（需要数据库和LLM API）
conda run -n py_311_rag python tests/integration/appointment/test_appointment_integration.py
```

### 数据库表初始化

```bash
# 创建血压记录表
conda run -n py_311_rag python scripts/create_blood_pressure_table.py

# 创建复诊预约表
conda run -n py_311_rag python scripts/create_appointment_table.py
```

### 测试说明

- **路由功能测试**: 单元测试，测试路由核心逻辑，不依赖数据库
- **集成测试**: 需要数据库连接和LLM API配置，测试完整的智能体交互流程
- 详细测试文档请参考 [tests/test_readme.md](tests/test_readme.md)

## 模块说明

### config.py
统一配置管理模块，集中管理所有配置常量，支持环境变量覆盖。

### database.py
PostgreSQL数据库连接池管理模块，使用 `psycopg_pool` 的 `AsyncConnectionPool`，与LangGraph兼容。

### redis_manager.py
Redis连接管理模块，提供基本的Redis操作接口。

### llms.py
LLM初始化模块，支持根据配置自动选择合适的LLM模型。

### router_state.py
路由状态数据结构定义，包含RouterState和IntentResult。

### router.py
路由节点实现，包含router_node、clarify_intent_node和route_decision函数。

### router_tools.py
路由工具实现，包含identify_intent和clarify_intent工具。

### router_graph.py
路由图创建模块，使用LangGraph StateGraph构建完整的路由图结构，集成所有智能体。

### blood_pressure_tools.py
血压记录工具实现，包含record_blood_pressure、query_blood_pressure、update_blood_pressure、info工具。

### appointment_tools.py
复诊管理工具实现，包含create_appointment、query_appointments、update_appointment、cancel_appointment等工具。

### blood_pressure_agent.py
血压记录智能体实现，包含创建血压记录智能体和血压记录智能体节点。

### appointment_agent.py
复诊管理智能体实现，包含创建复诊管理智能体和复诊管理智能体节点。

## 里程碑1完成情况

- ✅ 项目结构完整，符合设计文档要求
- ✅ 配置文件（config.py）已实现
- ✅ 数据库连接池管理模块已实现
- ✅ Redis连接管理模块已实现
- ✅ LLM初始化模块已实现
- ✅ 日志配置模块已实现

## 里程碑2完成情况

- ✅ RouterState数据结构正确定义
- ✅ IntentResult模型正确定义
- ✅ identify_intent工具能够识别4种意图类型（blood_pressure、appointment、doctor_assistant、unclear）
- ✅ clarify_intent工具能够生成澄清问题
- ✅ router_node能够正确识别意图并更新状态
- ✅ route_decision能够根据意图正确路由
- ✅ StateGraph路由图结构已创建（包含所有智能体节点）
- ✅ 路由功能单元测试已创建并整理到test/router/

## 里程碑3完成情况

- ✅ 血压记录数据库表结构已创建（create_blood_pressure_table.py）
- ✅ 复诊预约数据库表结构已创建（create_appointment_table.py）
- ✅ 血压记录工具完整实现（record、query、update、info）
- ✅ 复诊管理工具完整实现（create、query、update、cancel）
- ✅ blood_pressure_agent_node函数已实现
- ✅ appointment_agent_node函数已实现
- ✅ 血压记录智能体（LangGraph）已创建并集成到路由图
- ✅ 复诊管理智能体（LangGraph）已创建并集成到路由图
- ✅ 集成测试已创建并整理到test/目录

## 项目状态

- ✅ 路由系统：已完成，支持4种意图类型识别和路由
- ✅ 血压记录智能体：已完成，支持完整CRUD操作和相对时间解析
- ✅ 复诊管理智能体：已完成，支持完整CRUD操作和相对时间解析
- ⏳ 医生助手智能体：待实现
- ✅ 测试体系：已整理，包含单元测试和集成测试

