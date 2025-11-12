# 基础设施测试

本目录包含基础设施相关的测试，包括数据库连接、SQLAlchemy 兼容性等测试。

## 测试文件说明

### test_sqlalchemy_setup.py

SQLAlchemy 环境准备和依赖安装测试脚本。

#### 测试内容

1. **SQLAlchemy 安装验证**
   - 检查 SQLAlchemy 版本（需要 >= 2.0.0）
   - 验证异步模块是否可用

2. **SQLAlchemy 与 psycopg 兼容性测试**
   - 验证 SQLAlchemy 能否使用 psycopg 驱动
   - 测试数据库连接功能

3. **SQLAlchemy 与 LangGraph 兼容性测试（基础）**
   - 验证 SQLAlchemy 和 LangGraph 能否同时连接到数据库
   - 测试基本功能是否正常

4. **SQLAlchemy 基本操作测试**
   - 测试 SELECT、INSERT、UPDATE、DELETE 操作
   - 测试事务功能
   - 测试时区设置

#### 运行方式

```bash
cd langGraphFlow/V2_0_Agent
conda run -n py_311_rag python tests/integration/infrastructure/test_sqlalchemy_setup.py
```

#### 前置条件

1. 已安装 SQLAlchemy 2.0+：
   ```bash
   pip install sqlalchemy>=2.0.0
   ```

2. 数据库连接配置正确（环境变量 `DB_URI`）

3. 数据库服务正在运行

#### 预期结果

所有测试应该通过，输出类似：

```
✅ SQLAlchemy 版本: 2.0.x
✅ SQLAlchemy 异步模块导入成功
✅ 数据库连接成功
✅ SQLAlchemy 与 LangGraph 基础兼容性测试通过
✅ SQLAlchemy 基本操作测试通过
🎉 所有测试通过！SQLAlchemy 环境准备完成。
```

## 测试文件说明

### test_pool_compatibility.py

SQLAlchemy 与 LangGraph 连接池兼容性测试脚本。

#### 测试内容

1. **SQLAlchemy 使用 psycopg 驱动测试**
   - 验证 SQLAlchemy 能否使用 psycopg 驱动
   - 测试基本连接和查询功能
   - 验证时区设置

2. **独立连接池兼容性测试**
   - 验证 SQLAlchemy 和 LangGraph 使用独立连接池时的兼容性
   - 测试两个连接池能否同时正常工作
   - 测试并发场景下的稳定性

3. **连接池配置验证**
   - 验证连接池配置参数
   - 测试连接池性能
   - 验证连接池状态

4. **并发稳定性测试**
   - 测试高并发场景下的稳定性
   - 验证两个连接池同时操作数据库时的正确性
   - 测试数据一致性

5. **连接复用测试**
   - 验证连接池是否正确复用连接
   - 测试连接池效率

#### 运行方式

```bash
cd langGraphFlow/V2_0_Agent
conda run -n py_311_rag python tests/integration/infrastructure/test_pool_compatibility.py
```

#### 前置条件

1. 已安装 SQLAlchemy 2.0+ 和 greenlet：
   ```bash
   pip install sqlalchemy>=2.0.0 greenlet>=3.0.0
   ```

2. 数据库连接配置正确（环境变量 `DB_URI`）

3. 数据库服务正在运行

#### 预期结果

所有测试应该通过，输出类似：

```
✅ SQLAlchemy 使用 psycopg 驱动: ✅ 通过
✅ 独立连接池兼容性: ✅ 通过
✅ 连接池配置验证: ✅ 通过
✅ 并发稳定性: ✅ 通过
✅ 连接复用: ✅ 通过
🎉 所有测试通过！连接池兼容性验证完成。
```

#### 重要说明

- **当前实现使用独立连接池**：SQLAlchemy 和 LangGraph 各自使用独立的连接池
- **不是真正的共享连接池**：要实现真正的共享连接池需要额外的适配器实现
- **独立连接池方案已足够**：测试证明独立连接池方案稳定可靠，性能影响可接受

### test_transaction_isolation.py

SQLAlchemy 与 LangGraph 事务隔离测试脚本。

#### 测试内容

1. **SQLAlchemy 事务隔离测试**
   - 验证 SQLAlchemy 事务提交和回滚功能
   - 测试事务隔离级别

2. **LangGraph autocommit 行为测试**
   - 验证 LangGraph (psycopg) 的 autocommit 模式
   - 测试手动事务控制

3. **跨框架事务隔离测试**
   - 验证 SQLAlchemy 和 LangGraph 事务相互隔离
   - 测试一个框架的事务不会影响另一个框架

4. **并发事务稳定性测试**
   - 测试高并发场景下的事务稳定性
   - 验证数据一致性

5. **事务回滚隔离测试**
   - 验证事务回滚后，另一个框架看不到回滚的数据

#### 运行方式

```bash
cd langGraphFlow/V2_0_Agent
conda run -n py_311_rag python tests/integration/infrastructure/test_transaction_isolation.py
```

#### 前置条件

1. 已安装 SQLAlchemy 2.0+ 和 greenlet：
   ```bash
   pip install sqlalchemy>=2.0.0 greenlet>=3.0.0
   ```

2. 数据库连接配置正确（环境变量 `DB_URI`）

3. 数据库服务正在运行

#### 预期结果

所有测试应该通过，输出类似：

```
✅ SQLAlchemy 事务隔离: ✅ 通过
✅ LangGraph autocommit 行为: ✅ 通过
✅ 跨框架事务隔离: ✅ 通过
✅ 并发事务稳定性: ✅ 通过
✅ 事务回滚隔离: ✅ 通过
🎉 所有测试通过！事务隔离验证完成。
```

#### 重要说明

- **LangGraph 使用 autocommit=True**：每个操作自动提交，不需要显式事务
- **SQLAlchemy 使用显式事务**：需要手动提交或回滚
- **事务相互隔离**：两个框架的事务不会相互干扰

### test_performance_comparison.py

SQLAlchemy 与原生 psycopg 性能对比测试脚本。

#### 测试内容

1. **简单 SELECT 查询性能对比**
   - 测试基本查询操作的性能差异

2. **INSERT 操作性能对比**
   - 测试单条插入操作的性能差异

3. **UPDATE 操作性能对比**
   - 测试更新操作的性能差异

4. **批量 INSERT 性能对比**
   - 测试批量插入操作的性能差异

5. **并发操作性能对比**
   - 测试高并发场景下的性能差异

6. **复杂查询性能对比**
   - 测试 JOIN 和聚合查询的性能差异

#### 运行方式

```bash
cd langGraphFlow/V2_0_Agent
conda run -n py_311_rag python tests/integration/infrastructure/test_performance_comparison.py
```

#### 前置条件

1. 已安装 SQLAlchemy 2.0+ 和 greenlet：
   ```bash
   pip install sqlalchemy>=2.0.0 greenlet>=3.0.0
   ```

2. 数据库连接配置正确（环境变量 `DB_URI`）

3. 数据库服务正在运行

#### 预期结果

测试会输出详细的性能对比报告，包括：
- 每个操作的 psycopg 和 SQLAlchemy 耗时
- 性能开销百分比
- 是否在可接受范围内（<20%）

#### 性能评估标准

- **< 20%**：性能开销可接受，可以用于生产环境
- **>= 20%**：性能开销较高，建议在高性能场景下使用原生 psycopg

#### 重要说明

- 性能测试结果会因硬件、数据库配置、网络延迟等因素而有所不同
- 建议在目标生产环境或类似环境中运行测试
- 性能开销 < 20% 通常被认为是可接受的

#### 性能测试结果

**测试环境**：
- Python 3.11
- SQLAlchemy 2.0.43
- PostgreSQL (本地数据库)
- 测试时间：2025-11-06

**测试结果汇总**：

| 操作 | psycopg (s) | SQLAlchemy (s) | 开销 (%) | 状态 |
|------|-------------|----------------|----------|------|
| 简单 SELECT 查询 | 0.1391 | 0.1274 | -8.41 | ✅ 可接受 |
| INSERT 操作 | 0.0354 | 0.1213 | 242.85 | ⚠️ 较高 |
| UPDATE 操作 | 0.0384 | 0.1139 | 196.62 | ⚠️ 较高 |
| 批量 INSERT (100条/批) | 0.0742 | 0.0816 | 10.07 | ✅ 可接受 |
| 并发操作 (20任务×10操作) | 0.0664 | 0.2253 | 239.42 | ⚠️ 较高 |
| 复杂查询 (JOIN+聚合) | 0.0203 | 0.0620 | 205.75 | ⚠️ 较高 |

**性能分析**：
- **平均性能开销**：147.72%
- **可接受的测试项**：2/6 (33%)
- **性能开销较高的测试项**：4/6 (67%)

**结论**：
1. ✅ **简单查询和批量操作**：SQLAlchemy 性能开销可接受（<20%）
2. ⚠️ **单条 INSERT/UPDATE 操作**：SQLAlchemy 性能开销较高（>200%）
3. ⚠️ **并发操作和复杂查询**：SQLAlchemy 性能开销较高（>200%）

**建议**：
- 对于**简单查询和批量操作**，SQLAlchemy 的性能开销可接受，可以使用
- 对于**高性能场景**（单条 INSERT/UPDATE、高并发），建议继续使用原生 psycopg
- SQLAlchemy 提供了更好的代码可维护性和类型安全，但需要权衡性能开销
- 可以考虑**混合方案**：简单查询使用 SQLAlchemy，高性能操作使用原生 psycopg

**注意**：
- 测试结果会因硬件、数据库配置、网络延迟等因素而有所不同
- 建议在目标生产环境或类似环境中运行测试以获取准确的性能数据
- 性能开销 < 20% 通常被认为是可接受的

### test_unified_pool_management.py

数据库连接池统一管理测试脚本。

#### 测试内容

1. **连接池统一初始化测试**
   - 验证 `DatabasePool.create_pool()` 同时初始化 LangGraph 和 SQLAlchemy 连接池
   - 检查两个连接池是否都已正确创建

2. **连接池状态验证**
   - 验证 `db_pool.pool` (LangGraph) 和 `db_pool.sqlalchemy_engine` 都不为 None
   - 确保两个连接池都已正确初始化

3. **连接池统计信息测试**
   - 测试 `get_pool_stats()` 方法
   - 验证统计信息包含 LangGraph 和 SQLAlchemy 连接池的详细信息

4. **SQLAlchemy 连接测试**
   - 使用统一管理的引擎执行查询
   - 验证 SQLAlchemy 连接正常工作

5. **LangGraph 连接池测试**
   - 使用 LangGraph 连接池执行查询
   - 验证 LangGraph 连接池正常工作

6. **连接池关闭测试**
   - 测试统一关闭所有连接池
   - 验证资源正确释放

#### 运行方式

```bash
cd langGraphFlow/V2_0_Agent
conda run -n py_311_rag python tests/integration/infrastructure/test_unified_pool_management.py
```

#### 前置条件

1. 已安装 SQLAlchemy 2.0+ 和 greenlet：
   ```bash
   pip install sqlalchemy>=2.0.0 greenlet>=3.0.0
   ```

2. 数据库连接配置正确（环境变量 `DB_URI`）

3. 数据库服务正在运行

#### 预期结果

所有测试应该通过，输出类似：

```
✅ 连接池初始化成功
✅ LangGraph 和 SQLAlchemy 连接池都已初始化
✅ 连接池统计信息: {...}
✅ SQLAlchemy 查询成功，返回 X 条记录
✅ LangGraph 连接池查询成功
✅ 连接池关闭成功
✅ 所有测试通过
```

#### 重要说明

- **统一管理**：`DatabasePool` 统一管理 LangGraph 和 SQLAlchemy 连接池
- **配置一致**：两个连接池使用相同的配置参数（`MIN_SIZE`、`MAX_SIZE`、`DB_TIMEZONE`）
- **资源优化**：避免重复创建连接池，统一关闭资源
- **监控能力**：提供连接池统计信息和健康检查接口

#### 相关文档

- `core/database/pool.py` - 统一连接池管理实现
- `domain/models/base.py` - SQLAlchemy 引擎管理
- `docs/数据库使用指南.md` - 数据库使用文档
- `01_backendServer.py` - 应用初始化示例

## 后续测试计划

根据项目整理计划，后续将添加：

1. **连接池共享实现**（可选）- 如果确实需要共享连接池，实现适配器

