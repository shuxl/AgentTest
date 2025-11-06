# 测试文档

本目录包含V2.0多智能体路由系统的所有测试用例。

## 目录结构

```
test/
├── router/                    # 路由功能测试
│   └── test_router.py        # 路由单元测试
├── blood_pressure/           # 血压记录智能体测试
│   └── test_blood_pressure_integration.py  # 血压记录集成测试
├── appointment/              # 复诊管理智能体测试
│   └── test_appointment_integration.py     # 复诊管理集成测试
└── infrastructure/           # 基础设施测试（预留）
```

## 测试分类说明

### 1. 路由功能测试 (`router/`)

**test_router.py** - 路由功能单元测试

#### 测试范围：
- RouterState数据结构测试
- IntentResult数据结构测试
- identify_intent工具测试（意图识别）
- clarify_intent工具测试（意图澄清）
- route_decision函数测试（路由决策）

#### 运行方式：
```bash
cd langGraphFlow/V2_0_Agent
conda run -n py_311_rag python test/router/test_router.py
```

#### 测试特点：
- 单元测试，不依赖数据库
- 测试路由核心逻辑
- 验证意图识别准确性
- 验证路由决策正确性

---

### 2. 血压记录智能体测试 (`blood_pressure/`)

**test_blood_pressure_integration.py** - 血压记录集成测试

#### 测试范围：
- 完整业务流程测试（记录 -> 查询 -> 更新）
- 标准时间格式记录测试
- 相对时间格式解析测试（如"昨天下午"、"本周一"）
- 原始时间描述保存和显示验证
- 统计信息查询测试
- 数据库表结构验证

#### 测试用例：
1. **测试1**: 记录血压（标准格式 - "今天早上8点"）
2. **测试2**: 记录血压（相对时间格式 - "昨天下午"）
3. **测试3**: 查询血压记录（验证原始时间描述）
4. **测试4**: 查询统计信息
5. **测试5**: 相对时间解析测试（"本周一上午"）

#### 运行方式：
```bash
cd langGraphFlow/V2_0_Agent
conda run -n py_311_rag python test/blood_pressure/test_blood_pressure_integration.py
```

#### 测试特点：
- 集成测试，需要数据库连接
- 需要初始化checkpointer和store
- 自动创建和验证数据库表结构
- 包含测试数据清理功能
- 测试完整的智能体交互流程

#### 前置条件：
- 数据库连接配置正确
- LLM API配置正确
- 已创建blood_pressure_records表（或测试会自动创建）

---

### 3. 复诊管理智能体测试 (`appointment/`)

**test_appointment_integration.py** - 复诊管理集成测试

#### 测试范围：
- 完整业务流程测试（预约 -> 查询 -> 更新）
- 标准时间格式预约测试
- 相对时间格式解析测试（如"本周一上午10点"）
- 预约状态更新测试
- 数据库记录验证

#### 测试用例：
1. **测试1**: 创建预约（标准格式 - "明天下午2点"）
2. **测试2**: 查询预约记录
3. **测试3**: 创建预约（相对时间格式 - "本周一上午10点"）
4. **测试4**: 查询所有预约记录
5. **测试5**: 更新预约状态
6. **测试6**: 验证数据库中的记录

#### 运行方式：
```bash
cd langGraphFlow/V2_0_Agent
conda run -n py_311_rag python test/appointment/test_appointment_integration.py
```

#### 测试特点：
- 集成测试，需要数据库连接
- 需要初始化checkpointer和store
- 自动创建和验证数据库表结构
- 包含测试数据清理功能
- 测试完整的智能体交互流程

#### 前置条件：
- 数据库连接配置正确
- LLM API配置正确
- 已创建appointments表（或测试会自动创建）

---

### 4. 基础设施测试 (`infrastructure/`)

**test_sqlalchemy_setup.py** - SQLAlchemy 环境准备和依赖安装测试

#### 测试范围：
- SQLAlchemy 2.0+ 安装验证
- SQLAlchemy 与 psycopg 驱动兼容性测试
- SQLAlchemy 与 LangGraph 连接池兼容性测试（基础）
- SQLAlchemy 基本操作功能测试

#### 测试用例：
1. **测试1**: SQLAlchemy 安装验证
   - 检查版本是否 >= 2.0.0
   - 验证异步模块是否可用

2. **测试2**: SQLAlchemy 与 psycopg 兼容性
   - 使用 psycopg 驱动创建引擎
   - 测试数据库连接

3. **测试3**: SQLAlchemy 与 LangGraph 兼容性（基础）
   - 验证两个框架能否同时连接数据库
   - 测试基本功能是否正常

4. **测试4**: SQLAlchemy 基本操作
   - 测试 SELECT、INSERT、UPDATE、DELETE
   - 测试事务功能
   - 测试时区设置

#### 运行方式：
```bash
cd langGraphFlow/V2_0_Agent
conda run -n py_311_rag python test/infrastructure/test_sqlalchemy_setup.py
```

#### 测试特点：
- 环境准备测试，验证 SQLAlchemy 是否正确安装和配置
- 需要数据库连接
- 为后续的兼容性测试做准备

#### 前置条件：
- 已安装 SQLAlchemy 2.0+：`pip install sqlalchemy>=2.0.0`
- 数据库连接配置正确
- 数据库服务正在运行

#### 相关文档：
- `test/infrastructure/README.md` - 基础设施测试详细说明
- `test/infrastructure/test_pool_compatibility.py` - 连接池兼容性测试
- `902-python数据库包管理方案思考.md` - 数据库包管理方案文档

---

### 5. 连接池兼容性测试 (`infrastructure/`)

**test_pool_compatibility.py** - SQLAlchemy 与 LangGraph 连接池兼容性测试

#### 测试范围：
- SQLAlchemy 使用 psycopg 驱动测试
- SQLAlchemy 和 LangGraph 独立连接池兼容性测试
- 连接池配置验证
- 并发稳定性测试
- 连接复用测试

#### 运行方式：
```bash
cd langGraphFlow/V2_0_Agent
conda run -n py_311_rag python test/infrastructure/test_pool_compatibility.py
```

#### 测试特点：
- 验证 SQLAlchemy 和 LangGraph 的连接池兼容性
- 测试并发场景下的稳定性
- 验证连接池配置和性能

#### 前置条件：
- 已安装 SQLAlchemy 2.0+ 和 greenlet
- 数据库连接配置正确
- 数据库服务正在运行

---

### 6. 事务隔离测试 (`infrastructure/`)

**test_transaction_isolation.py** - SQLAlchemy 与 LangGraph 事务隔离测试

#### 测试范围：
- SQLAlchemy 事务隔离测试
- LangGraph autocommit 行为测试
- 跨框架事务隔离测试
- 并发事务稳定性测试
- 事务回滚隔离测试

#### 运行方式：
```bash
cd langGraphFlow/V2_0_Agent
conda run -n py_311_rag python test/infrastructure/test_transaction_isolation.py
```

#### 测试特点：
- 验证 SQLAlchemy 和 LangGraph 的事务隔离
- 测试并发场景下的稳定性
- 验证事务回滚隔离

#### 前置条件：
- 已安装 SQLAlchemy 2.0+ 和 greenlet
- 数据库连接配置正确
- 数据库服务正在运行

---

### 7. 性能对比测试 (`infrastructure/`)

**test_performance_comparison.py** - SQLAlchemy 与原生 psycopg 性能对比测试

#### 测试范围：
- 简单 SELECT 查询性能对比
- INSERT 操作性能对比
- UPDATE 操作性能对比
- 批量 INSERT 性能对比
- 并发操作性能对比
- 复杂查询性能对比

#### 运行方式：
```bash
cd langGraphFlow/V2_0_Agent
conda run -n py_311_rag python test/infrastructure/test_performance_comparison.py
```

#### 测试特点：
- 对比 SQLAlchemy 和原生 psycopg 的性能差异
- 评估性能开销是否可接受（<20%）
- 生成详细的性能测试报告

#### 前置条件：
- 已安装 SQLAlchemy 2.0+ 和 greenlet
- 数据库连接配置正确
- 数据库服务正在运行

---

### 运行所有测试

分别运行各个测试文件：

```bash
# 路由功能测试
conda run -n py_311_rag python test/router/test_router.py

# 血压记录集成测试
conda run -n py_311_rag python test/blood_pressure/test_blood_pressure_integration.py

# 复诊管理集成测试
conda run -n py_311_rag python test/appointment/test_appointment_integration.py

# SQLAlchemy 环境准备测试
conda run -n py_311_rag python test/infrastructure/test_sqlalchemy_setup.py

# SQLAlchemy 连接池兼容性测试
conda run -n py_311_rag python test/infrastructure/test_pool_compatibility.py

# SQLAlchemy 事务隔离测试
conda run -n py_311_rag python test/infrastructure/test_transaction_isolation.py

# SQLAlchemy 性能对比测试
conda run -n py_311_rag python test/infrastructure/test_performance_comparison.py
```

### 测试环境要求

1. **Python环境**: 使用conda环境 `py_311_rag` (Python 3.11)
2. **数据库**: PostgreSQL数据库，配置在环境变量 `DB_URI` 中
3. **LLM API**: DeepSeek API Key，配置在环境变量 `DEEPSEEK_API_KEY` 中
4. **依赖包**: 安装 `requirements.txt` 中的所有依赖

### 环境变量配置

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

### 待补充测试

- ⏳ 医生助手智能体测试
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

