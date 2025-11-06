# Python 数据库包管理方案思考

## 一、当前状况分析

### 1.1 数据库包使用情况

**LangGraph 使用的包**：
- `langgraph-checkpoint-postgres`：提供 `AsyncPostgresSaver`（checkpointer）和 `AsyncPostgresStore`（store）
- 内部依赖：`psycopg_pool` 的 `AsyncConnectionPool`
- 使用方式：共享同一个连接池实例

**业务代码使用的包**：
- ~~`psycopg[binary,pool]>=3.1.0`：直接使用 `AsyncConnectionPool` 进行 CRUD 操作~~（已废弃）
- ✅ **SQLAlchemy 2.0+ async**：使用 SQLAlchemy ORM 进行 CRUD 操作（已完成改造）
- 当前代码位置：`utils/tools/appointment_tools.py`、`utils/tools/blood_pressure_tools.py`（已重构为使用 SQLAlchemy）

### 1.2 当前 CRUD 代码存在的问题

#### 问题 1：代码重复度高
- `appointment_tools.py` 和 `blood_pressure_tools.py` 中有大量相似的数据库操作代码
- 每个工具函数都需要手动管理连接和游标
- SQL 语句分散在各个函数中，难以统一管理

#### 问题 2：缺少抽象层
- 直接使用 `pool.connection()` 和 `cur.execute()`
- 没有统一的查询构建器
- 没有统一的错误处理机制
- 缺少参数验证和类型安全

#### 问题 3：维护成本高
- SQL 语句硬编码在业务逻辑中
- 修改表结构需要修改多处代码
- 缺少统一的日志记录和性能监控

#### 问题 4：功能不完善
- 没有统一的 CRUD 操作封装
- 缺少批量操作支持
- 没有事务管理封装
- 缺少查询结果缓存机制

### 1.3 代码示例对比

**当前代码（appointment_tools.py）**：
```python
async with pool.connection() as conn:
    async with conn.cursor() as cur:
        await cur.execute("""
            INSERT INTO appointments 
            (user_id, department, doctor_id, doctor_name, appointment_date, status, notes)
            VALUES (%s, %s, %s, %s, %s, 'pending', %s)
            RETURNING id
        """, (user_id, department, doctor_id, doctor_name, appointment_datetime, notes or ""))
        result = await cur.fetchone()
        appointment_id = result['id'] if result else None
```

**问题**：
- SQL 语句冗长，可读性差
- 参数传递容易出错
- 缺少错误处理和日志记录
- 没有类型检查

---

## 二、解决方案设计

### 2.1 方案选择原则

1. **兼容性优先**：必须与 LangGraph 的 `AsyncPostgresSaver` 和 `AsyncPostgresStore` 兼容
2. **性能优先**：保持 `psycopg_pool` 的高性能特性
3. **渐进式改进**：可以逐步迁移，不破坏现有代码
4. **开发效率**：提高代码可维护性和开发效率

### 2.2 推荐方案：基于 psycopg_pool 封装数据库工具层 ⭐

#### 方案概述

基于现有的 `psycopg_pool`，封装一个轻量级的数据库管理工具层，提供：
- 统一的 CRUD 操作接口
- 查询构建器（Query Builder）
- 事务管理
- 错误处理和日志记录
- 类型安全（使用 Pydantic）

#### 优点

✅ **完全兼容 LangGraph**：继续使用 `psycopg_pool`，与 LangGraph 共享连接池  
✅ **性能优秀**：保持原生性能，无额外开销  
✅ **渐进式迁移**：可以逐步重构现有代码  
✅ **轻量级**：不引入重型依赖，保持项目简洁  
✅ **灵活性强**：支持复杂 SQL 查询，不限制功能  

#### 缺点

❌ **需要自行实现**：需要开发团队实现和维护  
❌ **功能有限**：相比成熟 ORM，功能相对简单  

---

### 2.3 备选方案：引入 SQLAlchemy async（长期方案）

#### 方案概述

引入 SQLAlchemy 2.0+ 的异步版本，使用 ORM 进行数据库操作。

#### 兼容性处理

**关键点**：SQLAlchemy 可以使用 `psycopg` 作为驱动，共享连接池。

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from psycopg_pool import AsyncConnectionPool

# 方式1：SQLAlchemy 使用 psycopg 驱动
engine = create_async_engine(
    'postgresql+psycopg://...',
    poolclass=...  # 可以配置连接池
)

# 方式2：共享连接池（需要适配）
# 注意：SQLAlchemy 和 LangGraph 需要共享同一个连接池实例
pool = AsyncConnectionPool(...)
# 将 pool 传递给 SQLAlchemy 和 LangGraph
```

#### 优点

✅ **功能强大**：完整的 ORM 功能，支持关系映射、迁移等  
✅ **类型安全**：SQLAlchemy 2.0+ 支持类型提示  
✅ **生态丰富**：有 Alembic 迁移工具、丰富的插件  
✅ **代码简洁**：ORM 操作更直观，减少 SQL 代码  

#### 缺点

❌ **兼容性风险**：需要验证与 LangGraph 的兼容性  
❌ **学习曲线**：团队需要学习 SQLAlchemy  
❌ **重构成本**：需要重构现有代码  
❌ **性能开销**：ORM 层会有一定性能开销（通常可接受）  

#### 兼容性验证建议

1. **测试共享连接池**：验证 SQLAlchemy 和 LangGraph 能否共享同一个连接池
2. **测试事务隔离**：确保两个框架的事务不会相互干扰
3. **性能测试**：对比性能差异，确保可接受

---

### 2.4 备选方案：混合方案（渐进式迁移）

#### 方案概述

- **LangGraph 相关**：继续使用 `psycopg_pool`（保持兼容）
- **业务数据模型**：使用 SQLAlchemy/SQLModel（ORM 优势）
- **高性能查询**：使用 `psycopg_pool`（性能优势）

#### 优点

✅ **兼顾兼容性和开发效率**  
✅ **可以逐步迁移**  
✅ **不同场景使用不同工具**  

#### 缺点

❌ **需要管理两套代码**  
❌ **学习成本较高**  

---

## 三、推荐方案详细设计

### 3.1 数据库工具层架构设计

```
utils/
├── database.py              # 连接池管理（现有）
├── db/
│   ├── __init__.py
│   ├── base.py             # 基础数据库操作类
│   ├── query_builder.py    # 查询构建器
│   ├── crud.py             # CRUD 操作封装
│   └── models.py            # 数据模型（Pydantic）
```

### 3.2 核心功能设计

#### 3.2.1 基础数据库操作类（base.py）

```python
"""
基础数据库操作类
提供统一的数据库操作接口，封装连接管理和错误处理
"""
from typing import Optional, List, Dict, Any
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """数据库管理器，封装基础数据库操作"""
    
    def __init__(self, pool: AsyncConnectionPool):
        self.pool = pool
    
    async def execute(
        self,
        query: str,
        params: Optional[tuple] = None,
        fetch: bool = False,
        fetch_one: bool = False
    ) -> Optional[Any]:
        """
        执行 SQL 查询
        
        Args:
            query: SQL 查询语句
            params: 查询参数
            fetch: 是否获取所有结果
            fetch_one: 是否只获取一条结果
        
        Returns:
            查询结果（根据 fetch 参数返回不同格式）
        """
        try:
            async with self.pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(query, params)
                    
                    if fetch_one:
                        return await cur.fetchone()
                    elif fetch:
                        return await cur.fetchall()
                    else:
                        return None
        except Exception as e:
            logger.error(f"数据库操作失败: {query[:100]}, 错误: {str(e)}")
            raise
    
    async def execute_many(
        self,
        query: str,
        params_list: List[tuple]
    ) -> None:
        """批量执行 SQL 查询"""
        try:
            async with self.pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.executemany(query, params_list)
        except Exception as e:
            logger.error(f"批量数据库操作失败: {query[:100]}, 错误: {str(e)}")
            raise
    
    async def execute_transaction(
        self,
        operations: List[tuple]  # [(query, params), ...]
    ) -> None:
        """执行事务操作"""
        async with self.pool.connection() as conn:
            # 注意：如果 autocommit=True，需要临时关闭
            async with conn.transaction():
                async with conn.cursor() as cur:
                    for query, params in operations:
                        await cur.execute(query, params)
```

#### 3.2.2 查询构建器（query_builder.py）

```python
"""
查询构建器
提供链式查询构建接口，简化 SQL 查询编写
"""
from typing import Optional, List, Dict, Any
from .base import DatabaseManager


class QueryBuilder:
    """查询构建器，支持链式调用"""
    
    def __init__(self, db_manager: DatabaseManager, table_name: str):
        self.db_manager = db_manager
        self.table_name = table_name
        self._select_fields: List[str] = ["*"]
        self._where_conditions: List[str] = []
        self._where_params: List[Any] = []
        self._order_by: Optional[str] = None
        self._limit: Optional[int] = None
        self._offset: Optional[int] = None
    
    def select(self, *fields: str) -> 'QueryBuilder':
        """设置查询字段"""
        self._select_fields = list(fields) if fields else ["*"]
        return self
    
    def where(self, condition: str, *params: Any) -> 'QueryBuilder':
        """添加 WHERE 条件"""
        self._where_conditions.append(condition)
        self._where_params.extend(params)
        return self
    
    def order_by(self, field: str, desc: bool = False) -> 'QueryBuilder':
        """设置排序"""
        direction = "DESC" if desc else "ASC"
        self._order_by = f"{field} {direction}"
        return self
    
    def limit(self, count: int) -> 'QueryBuilder':
        """设置限制数量"""
        self._limit = count
        return self
    
    def offset(self, count: int) -> 'QueryBuilder':
        """设置偏移量"""
        self._offset = count
        return self
    
    def build_query(self) -> tuple[str, tuple]:
        """构建 SQL 查询语句和参数"""
        query_parts = ["SELECT", ", ".join(self._select_fields), "FROM", self.table_name]
        params = []
        
        if self._where_conditions:
            query_parts.append("WHERE")
            query_parts.append(" AND ".join(self._where_conditions))
            params.extend(self._where_params)
        
        if self._order_by:
            query_parts.append("ORDER BY")
            query_parts.append(self._order_by)
        
        if self._limit:
            query_parts.append(f"LIMIT {self._limit}")
        
        if self._offset:
            query_parts.append(f"OFFSET {self._offset}")
        
        query = " ".join(query_parts)
        return query, tuple(params)
    
    async def fetch_all(self) -> List[Dict[str, Any]]:
        """执行查询并返回所有结果"""
        query, params = self.build_query()
        return await self.db_manager.execute(query, params, fetch=True)
    
    async def fetch_one(self) -> Optional[Dict[str, Any]]:
        """执行查询并返回一条结果"""
        query, params = self.build_query()
        return await self.db_manager.execute(query, params, fetch_one=True)
```

#### 3.2.3 CRUD 操作封装（crud.py）

```python
"""
CRUD 操作封装
提供通用的 CRUD 操作接口，支持 Pydantic 模型
"""
from typing import Optional, List, Dict, Any, TypeVar, Generic
from pydantic import BaseModel
from .base import DatabaseManager
from .query_builder import QueryBuilder

T = TypeVar('T', bound=BaseModel)


class CRUDManager(Generic[T]):
    """CRUD 管理器，提供通用的 CRUD 操作"""
    
    def __init__(self, db_manager: DatabaseManager, table_name: str, model_class: type[T]):
        self.db_manager = db_manager
        self.table_name = table_name
        self.model_class = model_class
    
    async def create(self, data: Dict[str, Any], returning: str = "id") -> Optional[Any]:
        """
        创建记录
        
        Args:
            data: 记录数据（字典格式）
            returning: 返回字段名
        
        Returns:
            返回字段的值
        """
        fields = list(data.keys())
        placeholders = ", ".join(["%s"] * len(fields))
        values = tuple(data.values())
        
        query = f"""
            INSERT INTO {self.table_name} ({", ".join(fields)})
            VALUES ({placeholders})
            RETURNING {returning}
        """
        
        result = await self.db_manager.execute(query, values, fetch_one=True)
        return result[returning] if result else None
    
    async def get_by_id(self, id_value: Any, id_field: str = "id") -> Optional[Dict[str, Any]]:
        """根据 ID 获取记录"""
        query = f"SELECT * FROM {self.table_name} WHERE {id_field} = %s"
        return await self.db_manager.execute(query, (id_value,), fetch_one=True)
    
    async def update(
        self,
        id_value: Any,
        data: Dict[str, Any],
        id_field: str = "id"
    ) -> bool:
        """更新记录"""
        fields = list(data.keys())
        set_clause = ", ".join([f"{field} = %s" for field in fields])
        values = tuple(data.values()) + (id_value,)
        
        query = f"""
            UPDATE {self.table_name}
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE {id_field} = %s
        """
        
        await self.db_manager.execute(query, values)
        return True
    
    async def delete(self, id_value: Any, id_field: str = "id") -> bool:
        """删除记录"""
        query = f"DELETE FROM {self.table_name} WHERE {id_field} = %s"
        await self.db_manager.execute(query, (id_value,))
        return True
    
    async def list(
        self,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """列表查询"""
        builder = QueryBuilder(self.db_manager, self.table_name)
        
        if filters:
            for field, value in filters.items():
                builder.where(f"{field} = %s", value)
        
        if order_by:
            builder.order_by(order_by, desc=True)
        
        if limit:
            builder.limit(limit)
        
        if offset:
            builder.offset(offset)
        
        return await builder.fetch_all()
```

#### 3.2.4 数据模型（models.py）

```python
"""
数据模型定义
使用 Pydantic 定义数据模型，提供类型安全和验证
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class AppointmentModel(BaseModel):
    """预约记录模型"""
    id: Optional[int] = None
    user_id: str
    department: str
    doctor_id: Optional[str] = None
    doctor_name: Optional[str] = None
    appointment_date: datetime
    status: str = "pending"
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class BloodPressureModel(BaseModel):
    """血压记录模型"""
    id: Optional[int] = None
    user_id: str
    systolic: int = Field(ge=50, le=300)
    diastolic: int = Field(ge=30, le=200)
    measurement_time: datetime
    original_time_description: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
```

### 3.3 使用示例

#### 3.3.1 重构后的 appointment_tools.py

```python
from ..db.base import DatabaseManager
from ..db.crud import CRUDManager
from ..db.models import AppointmentModel

# 初始化
db_manager = DatabaseManager(pool)
appointment_crud = CRUDManager(db_manager, "appointments", AppointmentModel)

@tool("appointment_booking")
async def appointment_booking(...) -> str:
    # 使用 CRUD 管理器
    appointment_data = {
        "user_id": user_id,
        "department": department,
        "doctor_id": doctor_id,
        "doctor_name": doctor_name,
        "appointment_date": appointment_datetime,
        "status": "pending",
        "notes": notes or ""
    }
    
    appointment_id = await appointment_crud.create(appointment_data)
    return f"预约成功！预约编号：{appointment_id}"
```

#### 3.3.2 使用查询构建器

```python
from ..db.query_builder import QueryBuilder

# 复杂查询示例
builder = QueryBuilder(db_manager, "appointments")
builder.select("id", "department", "appointment_date", "status")
builder.where("user_id = %s", user_id)
builder.where("status = %s", "pending")
builder.order_by("appointment_date", desc=True)
builder.limit(10)

results = await builder.fetch_all()
```

---

## 四、实施计划

### 4.1 阶段一：基础工具层开发（1-2周）

1. **创建数据库工具层目录结构**
   - 创建 `utils/db/` 目录
   - 实现 `base.py`（基础数据库操作类）
   - 实现 `query_builder.py`（查询构建器）

2. **编写单元测试**
   - 测试基础数据库操作
   - 测试查询构建器功能

### 4.2 阶段二：CRUD 封装开发（1周）

1. **实现 CRUD 管理器**
   - 实现 `crud.py`（CRUD 操作封装）
   - 实现 `models.py`（数据模型定义）

2. **编写单元测试**
   - 测试 CRUD 操作
   - 测试数据模型验证

### 4.3 阶段三：重构现有代码（2-3周）

1. **重构 appointment_tools.py**
   - 使用新的数据库工具层
   - 保持接口不变，只重构内部实现

2. **重构 blood_pressure_tools.py**
   - 使用新的数据库工具层
   - 保持接口不变，只重构内部实现

3. **编写集成测试**
   - 确保重构后功能正常
   - 性能对比测试

### 4.4 阶段四：优化和文档（1周）

1. **性能优化**
   - 查询优化
   - 连接池优化

2. **文档编写**
   - API 文档
   - 使用示例
   - 最佳实践

---

## 五、兼容性考虑

### 5.1 LangGraph 兼容性

**关键点**：继续使用 `psycopg_pool` 的 `AsyncConnectionPool`，确保与 LangGraph 完全兼容。

**验证方法**：
1. 确保 `AsyncPostgresSaver` 和 `AsyncPostgresStore` 使用同一个连接池实例
2. 测试连接池共享是否正常工作
3. 测试事务隔离是否正常

### 5.2 引入其他包的兼容性评估

#### 5.2.1 SQLAlchemy async

**兼容性**：⚠️ 需要验证

**验证步骤**：
1. 测试 SQLAlchemy 能否使用 `psycopg` 驱动
2. 测试能否共享连接池
3. 测试事务隔离

**推荐做法**：
- 如果引入 SQLAlchemy，建议先在小范围测试
- 确保 LangGraph 和 SQLAlchemy 使用同一个连接池实例
- 注意事务管理，避免冲突

#### 5.2.2 其他 ORM（Tortoise、SQLModel 等）

**兼容性**：⚠️ 需要验证

**建议**：
- 优先考虑 SQLAlchemy（生态最成熟）
- 如果选择其他 ORM，需要充分测试兼容性

---

## 六、推荐方案总结

### 6.1 短期方案（推荐）

**方案**：基于 `psycopg_pool` 封装数据库工具层

**理由**：
- ✅ 完全兼容 LangGraph，无兼容性风险
- ✅ 性能优秀，无额外开销
- ✅ 可以逐步迁移，不破坏现有代码
- ✅ 轻量级，不引入重型依赖

**实施时间**：4-6 周

### 6.2 长期方案（已完成 ✅）

**方案**：引入 SQLAlchemy async

**实施状态**：✅ **已完成**（2025-11-07）

**理由**：
- ✅ 功能强大，生态丰富
- ✅ 支持数据库迁移（已集成 Alembic）
- ✅ 代码更易维护（已重构完成）

**实施结果**：
- ✅ 已充分验证与 LangGraph 的兼容性
- ✅ 已完成所有业务代码重构
- ✅ 性能开销在可接受范围内
- ✅ 代码质量显著提升

**实施时间**：实际用时约 4-5 周（包括测试和优化）

---

## 七、建议（已实施完成 ✅）

### 7.1 实施结果

1. ✅ **已完成 SQLAlchemy async 改造**：所有业务代码已迁移到 SQLAlchemy ORM
2. ✅ **已完成重构**：`appointment_tools.py` 和 `blood_pressure_tools.py` 已重构完成
3. ✅ **已完成测试**：包括兼容性测试、性能测试、端到端测试等

### 7.2 后续维护

1. **性能监控**：继续监控 SQLAlchemy 的性能表现，必要时进行优化
2. **文档维护**：保持文档更新，确保新团队成员能够快速上手
3. **代码质量**：继续使用 SQLAlchemy ORM 的优势，保持代码的可维护性

### 7.3 经验总结

1. ✅ **兼容性验证很重要**：通过充分的兼容性测试确保了与 LangGraph 的完美兼容
2. ✅ **渐进式迁移有效**：分阶段实施降低了风险，确保了改造的顺利进行
3. ✅ **统一管理是关键**：通过 `DatabasePool` 统一管理连接池，确保了配置一致性

---

## 八、参考资料

1. [psycopg3 官方文档](https://www.psycopg.org/psycopg3/docs/)
2. [LangGraph PostgreSQL Store 文档](https://langchain-ai.github.io/langgraph/how-tos/persistence/postgres/)
3. [SQLAlchemy 2.0 异步文档](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
4. [项目内数据库管理库对比分析](./9001-数据库管理库对比分析.md)

---

---

## 九、实施状态更新（2025-11-07）

### 9.1 改造完成情况

✅ **已完成 SQLAlchemy async 改造**（2025-11-07）

**实施内容**：
1. ✅ 已完成兼容性验证（连接池兼容性、事务隔离、性能对比）
2. ✅ 已完成数据模型设计（BloodPressureRecord、Appointment）
3. ✅ 已完成 CRUD 操作重构（使用 SQLAlchemy ORM）
4. ✅ 已完成数据库连接管理优化（统一连接池管理）
5. ✅ 已完成测试和优化（端到端测试、并发测试、代码清理）

**当前状态**：
- ✅ 业务代码已全部迁移到 SQLAlchemy ORM
- ✅ 使用统一的 `DatabasePool` 管理连接池
- ✅ 所有工具函数已重构为使用 `CRUDBase`
- ✅ 保持了与 LangGraph 的完全兼容性

**技术架构**：
- LangGraph：继续使用 `psycopg_pool.AsyncConnectionPool`
- 业务代码：使用 SQLAlchemy async ORM（通过 `psycopg` 驱动）
- 连接池管理：统一由 `utils.database.DatabasePool` 管理
- 配置一致性：两个连接池使用相同的配置参数

**相关文档**：
- `docs/数据库使用指南.md` - 详细的使用文档
- `test/infrastructure/` - 兼容性和性能测试
- `utils/db/` - SQLAlchemy ORM 实现

---

**文档版本**：v2.0  
**创建日期**：2025-02-XX  
**最后更新**：2025-11-07（SQLAlchemy async 改造完成）

