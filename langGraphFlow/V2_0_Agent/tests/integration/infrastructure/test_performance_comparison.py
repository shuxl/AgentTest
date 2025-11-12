"""
SQLAlchemy 与原生 psycopg 性能对比测试

本测试脚本用于对比：
1. SQLAlchemy 和原生 psycopg 的性能差异
2. 评估性能开销是否可接受（<20%）
3. 生成性能测试报告

运行方式：
    conda run -n py_311_rag python tests/integration/infrastructure/test_performance_comparison.py
"""
import sys
import os
import asyncio
import logging
import time
import statistics
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

from core.config import get_settings
from core.database import get_db_pool

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceResult:
    """性能测试结果"""
    operation: str
    psycopg_time: float
    sqlalchemy_time: float
    overhead: float
    overhead_percent: float
    iterations: int


class PerformanceBenchmark:
    """性能基准测试类"""
    
    def __init__(self):
        self.results: List[PerformanceResult] = []
    
    def calculate_overhead(self, psycopg_time: float, sqlalchemy_time: float) -> Tuple[float, float]:
        """计算性能开销"""
        overhead = sqlalchemy_time - psycopg_time
        overhead_percent = (overhead / psycopg_time * 100) if psycopg_time > 0 else 0
        return overhead, overhead_percent
    
    def add_result(self, operation: str, psycopg_time: float, sqlalchemy_time: float, iterations: int):
        """添加测试结果"""
        overhead, overhead_percent = self.calculate_overhead(psycopg_time, sqlalchemy_time)
        result = PerformanceResult(
            operation=operation,
            psycopg_time=psycopg_time,
            sqlalchemy_time=sqlalchemy_time,
            overhead=overhead,
            overhead_percent=overhead_percent,
            iterations=iterations
        )
        self.results.append(result)
    
    def print_report(self):
        """打印性能测试报告"""
        logger.info("=" * 80)
        logger.info("性能测试报告")
        logger.info("=" * 80)
        logger.info("")
        
        logger.info(f"{'操作':<30} {'psycopg (s)':<15} {'SQLAlchemy (s)':<15} {'开销 (%)':<15} {'状态':<10}")
        logger.info("-" * 80)
        
        for result in self.results:
            status = "✅ 可接受" if result.overhead_percent < 20 else "⚠️  较高"
            logger.info(
                f"{result.operation:<30} "
                f"{result.psycopg_time:<15.4f} "
                f"{result.sqlalchemy_time:<15.4f} "
                f"{result.overhead_percent:<15.2f} "
                f"{status:<10}"
            )
        
        logger.info("")
        logger.info("性能开销评估标准：< 20% 为可接受")
        logger.info("=" * 80)


async def benchmark_simple_select(iterations: int = 100) -> Tuple[float, float]:
    """基准测试1：简单 SELECT 查询"""
    logger.info(f"基准测试1：简单 SELECT 查询（{iterations} 次迭代）")
    
    # 准备连接池
    settings = get_settings()
    db_pool = get_db_pool(settings)
    await db_pool.initialize()
    psycopg_pool = await db_pool.create_pool()
    
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text
    
    settings = get_settings()
    db_uri = settings.db_uri
    if db_uri.startswith("postgresql://"):
        sqlalchemy_uri = db_uri.replace("postgresql://", "postgresql+psycopg://", 1)
    else:
        sqlalchemy_uri = db_uri
    
    sqlalchemy_engine = create_async_engine(
        sqlalchemy_uri,
        echo=False,
        pool_pre_ping=True
    )
    
    # 测试 psycopg
    logger.info("测试 psycopg...")
    psycopg_times = []
    for _ in range(iterations):
        start = time.perf_counter()
        async with psycopg_pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1")
                await cur.fetchone()
        psycopg_times.append(time.perf_counter() - start)
    
    psycopg_avg = statistics.mean(psycopg_times)
    psycopg_total = sum(psycopg_times)
    logger.info(f"  psycopg 平均耗时: {psycopg_avg*1000:.2f}ms, 总耗时: {psycopg_total:.4f}s")
    
    # 测试 SQLAlchemy
    logger.info("测试 SQLAlchemy...")
    sqlalchemy_times = []
    for _ in range(iterations):
        start = time.perf_counter()
        async with sqlalchemy_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        sqlalchemy_times.append(time.perf_counter() - start)
    
    sqlalchemy_avg = statistics.mean(sqlalchemy_times)
    sqlalchemy_total = sum(sqlalchemy_times)
    logger.info(f"  SQLAlchemy 平均耗时: {sqlalchemy_avg*1000:.2f}ms, 总耗时: {sqlalchemy_total:.4f}s")
    
    await sqlalchemy_engine.dispose()
    await psycopg_pool.close()
    
    return psycopg_total, sqlalchemy_total


async def benchmark_insert_operation(iterations: int = 100) -> Tuple[float, float]:
    """基准测试2：INSERT 操作"""
    logger.info(f"基准测试2：INSERT 操作（{iterations} 次迭代）")
    
    # 准备连接池
    settings = get_settings()
    db_pool = get_db_pool(settings)
    await db_pool.initialize()
    psycopg_pool = await db_pool.create_pool()
    
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text
    
    settings = get_settings()
    db_uri = settings.db_uri
    if db_uri.startswith("postgresql://"):
        sqlalchemy_uri = db_uri.replace("postgresql://", "postgresql+psycopg://", 1)
    else:
        sqlalchemy_uri = db_uri
    
    sqlalchemy_engine = create_async_engine(
        sqlalchemy_uri,
        echo=False,
        pool_pre_ping=True
    )
    
    # 创建测试表
    async with sqlalchemy_engine.connect() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS test_perf_insert"))
        await conn.execute(text("""
            CREATE TABLE test_perf_insert (
                id SERIAL PRIMARY KEY,
                value INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        await conn.commit()
    
    # 测试 psycopg
    logger.info("测试 psycopg...")
    psycopg_times = []
    for i in range(iterations):
        start = time.perf_counter()
        async with psycopg_pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "INSERT INTO test_perf_insert (value) VALUES (%s)",
                    (i,)
                )
        psycopg_times.append(time.perf_counter() - start)
    
    psycopg_avg = statistics.mean(psycopg_times)
    psycopg_total = sum(psycopg_times)
    logger.info(f"  psycopg 平均耗时: {psycopg_avg*1000:.2f}ms, 总耗时: {psycopg_total:.4f}s")
    
    # 清理数据
    async with psycopg_pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("TRUNCATE TABLE test_perf_insert")
    
    # 测试 SQLAlchemy
    logger.info("测试 SQLAlchemy...")
    sqlalchemy_times = []
    for i in range(iterations):
        start = time.perf_counter()
        async with sqlalchemy_engine.begin() as conn:
            await conn.execute(
                text("INSERT INTO test_perf_insert (value) VALUES (:value)"),
                {"value": i}
            )
        sqlalchemy_times.append(time.perf_counter() - start)
    
    sqlalchemy_avg = statistics.mean(sqlalchemy_times)
    sqlalchemy_total = sum(sqlalchemy_times)
    logger.info(f"  SQLAlchemy 平均耗时: {sqlalchemy_avg*1000:.2f}ms, 总耗时: {sqlalchemy_total:.4f}s")
    
    # 清理
    async with sqlalchemy_engine.connect() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS test_perf_insert"))
        await conn.commit()
    
    await sqlalchemy_engine.dispose()
    await psycopg_pool.close()
    
    return psycopg_total, sqlalchemy_total


async def benchmark_update_operation(iterations: int = 100) -> Tuple[float, float]:
    """基准测试3：UPDATE 操作"""
    logger.info(f"基准测试3：UPDATE 操作（{iterations} 次迭代）")
    
    # 准备连接池
    settings = get_settings()
    db_pool = get_db_pool(settings)
    await db_pool.initialize()
    psycopg_pool = await db_pool.create_pool()
    
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text
    
    settings = get_settings()
    db_uri = settings.db_uri
    if db_uri.startswith("postgresql://"):
        sqlalchemy_uri = db_uri.replace("postgresql://", "postgresql+psycopg://", 1)
    else:
        sqlalchemy_uri = db_uri
    
    sqlalchemy_engine = create_async_engine(
        sqlalchemy_uri,
        echo=False,
        pool_pre_ping=True
    )
    
    # 创建测试表并插入初始数据
    async with sqlalchemy_engine.connect() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS test_perf_update"))
        await conn.execute(text("""
            CREATE TABLE test_perf_update (
                id SERIAL PRIMARY KEY,
                value INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        await conn.commit()
    
    # 插入初始数据
    async with psycopg_pool.connection() as conn:
        async with conn.cursor() as cur:
            for i in range(iterations):
                await cur.execute(
                    "INSERT INTO test_perf_update (value) VALUES (%s)",
                    (i,)
                )
    
    # 测试 psycopg
    logger.info("测试 psycopg...")
    psycopg_times = []
    for i in range(iterations):
        start = time.perf_counter()
        async with psycopg_pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "UPDATE test_perf_update SET value = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
                    (i + 1000, i + 1)
                )
        psycopg_times.append(time.perf_counter() - start)
    
    psycopg_avg = statistics.mean(psycopg_times)
    psycopg_total = sum(psycopg_times)
    logger.info(f"  psycopg 平均耗时: {psycopg_avg*1000:.2f}ms, 总耗时: {psycopg_total:.4f}s")
    
    # 重置数据
    async with psycopg_pool.connection() as conn:
        async with conn.cursor() as cur:
            for i in range(iterations):
                await cur.execute(
                    "UPDATE test_perf_update SET value = %s WHERE id = %s",
                    (i, i + 1)
                )
    
    # 测试 SQLAlchemy
    logger.info("测试 SQLAlchemy...")
    sqlalchemy_times = []
    for i in range(iterations):
        start = time.perf_counter()
        async with sqlalchemy_engine.begin() as conn:
            await conn.execute(
                text("UPDATE test_perf_update SET value = :value, updated_at = CURRENT_TIMESTAMP WHERE id = :id"),
                {"value": i + 1000, "id": i + 1}
            )
        sqlalchemy_times.append(time.perf_counter() - start)
    
    sqlalchemy_avg = statistics.mean(sqlalchemy_times)
    sqlalchemy_total = sum(sqlalchemy_times)
    logger.info(f"  SQLAlchemy 平均耗时: {sqlalchemy_avg*1000:.2f}ms, 总耗时: {sqlalchemy_total:.4f}s")
    
    # 清理
    async with sqlalchemy_engine.connect() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS test_perf_update"))
        await conn.commit()
    
    await sqlalchemy_engine.dispose()
    await psycopg_pool.close()
    
    return psycopg_total, sqlalchemy_total


async def benchmark_batch_insert(iterations: int = 10, batch_size: int = 100) -> Tuple[float, float]:
    """基准测试4：批量 INSERT 操作"""
    logger.info(f"基准测试4：批量 INSERT 操作（{iterations} 次迭代，每批 {batch_size} 条）")
    
    # 准备连接池
    settings = get_settings()
    db_pool = get_db_pool(settings)
    await db_pool.initialize()
    psycopg_pool = await db_pool.create_pool()
    
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text
    
    settings = get_settings()
    db_uri = settings.db_uri
    if db_uri.startswith("postgresql://"):
        sqlalchemy_uri = db_uri.replace("postgresql://", "postgresql+psycopg://", 1)
    else:
        sqlalchemy_uri = db_uri
    
    sqlalchemy_engine = create_async_engine(
        sqlalchemy_uri,
        echo=False,
        pool_pre_ping=True
    )
    
    # 创建测试表
    async with sqlalchemy_engine.connect() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS test_perf_batch"))
        await conn.execute(text("""
            CREATE TABLE test_perf_batch (
                id SERIAL PRIMARY KEY,
                value INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        await conn.commit()
    
    # 测试 psycopg
    logger.info("测试 psycopg...")
    psycopg_times = []
    for _ in range(iterations):
        start = time.perf_counter()
        async with psycopg_pool.connection() as conn:
            async with conn.cursor() as cur:
                # 批量插入
                values = [(i,) for i in range(batch_size)]
                await cur.executemany(
                    "INSERT INTO test_perf_batch (value) VALUES (%s)",
                    values
                )
        psycopg_times.append(time.perf_counter() - start)
        
        # 清理数据
        async with psycopg_pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("TRUNCATE TABLE test_perf_batch")
    
    psycopg_avg = statistics.mean(psycopg_times)
    psycopg_total = sum(psycopg_times)
    logger.info(f"  psycopg 平均耗时: {psycopg_avg*1000:.2f}ms, 总耗时: {psycopg_total:.4f}s")
    
    # 测试 SQLAlchemy
    logger.info("测试 SQLAlchemy...")
    sqlalchemy_times = []
    for _ in range(iterations):
        start = time.perf_counter()
        async with sqlalchemy_engine.begin() as conn:
            # SQLAlchemy 批量插入
            values = [{"value": i} for i in range(batch_size)]
            await conn.execute(
                text("INSERT INTO test_perf_batch (value) VALUES (:value)"),
                values
            )
        sqlalchemy_times.append(time.perf_counter() - start)
        
        # 清理数据
        async with sqlalchemy_engine.connect() as conn:
            await conn.execute(text("TRUNCATE TABLE test_perf_batch"))
            await conn.commit()
    
    sqlalchemy_avg = statistics.mean(sqlalchemy_times)
    sqlalchemy_total = sum(sqlalchemy_times)
    logger.info(f"  SQLAlchemy 平均耗时: {sqlalchemy_avg*1000:.2f}ms, 总耗时: {sqlalchemy_total:.4f}s")
    
    # 清理
    async with sqlalchemy_engine.connect() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS test_perf_batch"))
        await conn.commit()
    
    await sqlalchemy_engine.dispose()
    await psycopg_pool.close()
    
    return psycopg_total, sqlalchemy_total


async def benchmark_concurrent_operations(concurrent_tasks: int = 20, operations_per_task: int = 10) -> Tuple[float, float]:
    """基准测试5：并发操作"""
    logger.info(f"基准测试5：并发操作（{concurrent_tasks} 个并发任务，每个任务 {operations_per_task} 次操作）")
    
    # 准备连接池
    settings = get_settings()
    db_pool = get_db_pool(settings)
    await db_pool.initialize()
    psycopg_pool = await db_pool.create_pool()
    
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text
    
    settings = get_settings()
    db_uri = settings.db_uri
    if db_uri.startswith("postgresql://"):
        sqlalchemy_uri = db_uri.replace("postgresql://", "postgresql+psycopg://", 1)
    else:
        sqlalchemy_uri = db_uri
    
    sqlalchemy_engine = create_async_engine(
        sqlalchemy_uri,
        echo=False,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )
    
    # 创建测试表
    async with sqlalchemy_engine.connect() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS test_perf_concurrent"))
        await conn.execute(text("""
            CREATE TABLE test_perf_concurrent (
                id SERIAL PRIMARY KEY,
                task_id INTEGER,
                value INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        await conn.commit()
    
    # 测试 psycopg
    logger.info("测试 psycopg...")
    async def psycopg_task(task_id: int):
        for i in range(operations_per_task):
            async with psycopg_pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        "INSERT INTO test_perf_concurrent (task_id, value) VALUES (%s, %s)",
                        (task_id, i)
                    )
    
    start = time.perf_counter()
    await asyncio.gather(*[psycopg_task(i) for i in range(concurrent_tasks)])
    psycopg_time = time.perf_counter() - start
    
    logger.info(f"  psycopg 总耗时: {psycopg_time:.4f}s")
    
    # 清理数据
    async with psycopg_pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("TRUNCATE TABLE test_perf_concurrent")
    
    # 测试 SQLAlchemy
    logger.info("测试 SQLAlchemy...")
    async def sqlalchemy_task(task_id: int):
        for i in range(operations_per_task):
            async with sqlalchemy_engine.begin() as conn:
                await conn.execute(
                    text("INSERT INTO test_perf_concurrent (task_id, value) VALUES (:task_id, :value)"),
                    {"task_id": task_id, "value": i}
                )
    
    start = time.perf_counter()
    await asyncio.gather(*[sqlalchemy_task(i) for i in range(concurrent_tasks)])
    sqlalchemy_time = time.perf_counter() - start
    
    logger.info(f"  SQLAlchemy 总耗时: {sqlalchemy_time:.4f}s")
    
    # 清理
    async with sqlalchemy_engine.connect() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS test_perf_concurrent"))
        await conn.commit()
    
    await sqlalchemy_engine.dispose()
    await psycopg_pool.close()
    
    return psycopg_time, sqlalchemy_time


async def benchmark_complex_query(iterations: int = 50) -> Tuple[float, float]:
    """基准测试6：复杂查询（JOIN + 聚合）"""
    logger.info(f"基准测试6：复杂查询（{iterations} 次迭代）")
    
    # 准备连接池
    settings = get_settings()
    db_pool = get_db_pool(settings)
    await db_pool.initialize()
    psycopg_pool = await db_pool.create_pool()
    
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text
    
    settings = get_settings()
    db_uri = settings.db_uri
    if db_uri.startswith("postgresql://"):
        sqlalchemy_uri = db_uri.replace("postgresql://", "postgresql+psycopg://", 1)
    else:
        sqlalchemy_uri = db_uri
    
    sqlalchemy_engine = create_async_engine(
        sqlalchemy_uri,
        echo=False,
        pool_pre_ping=True
    )
    
    # 创建测试表并插入数据
    async with sqlalchemy_engine.connect() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS test_perf_complex_a"))
        await conn.execute(text("DROP TABLE IF EXISTS test_perf_complex_b"))
        await conn.execute(text("""
            CREATE TABLE test_perf_complex_a (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50),
                category_id INTEGER
            )
        """))
        await conn.execute(text("""
            CREATE TABLE test_perf_complex_b (
                id SERIAL PRIMARY KEY,
                category_name VARCHAR(50)
            )
        """))
        await conn.commit()
    
    # 插入测试数据
    async with psycopg_pool.connection() as conn:
        async with conn.cursor() as cur:
            # 插入分类数据
            for i in range(10):
                await cur.execute(
                    "INSERT INTO test_perf_complex_b (category_name) VALUES (%s)",
                    (f"category_{i}",)
                )
            # 插入主数据
            for i in range(100):
                await cur.execute(
                    "INSERT INTO test_perf_complex_a (name, category_id) VALUES (%s, %s)",
                    (f"item_{i}", i % 10 + 1)
                )
    
    # 测试 psycopg
    logger.info("测试 psycopg...")
    psycopg_times = []
    for _ in range(iterations):
        start = time.perf_counter()
        async with psycopg_pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    SELECT b.category_name, COUNT(a.id) as count, AVG(a.id) as avg_id
                    FROM test_perf_complex_a a
                    JOIN test_perf_complex_b b ON a.category_id = b.id
                    GROUP BY b.category_name
                    ORDER BY count DESC
                """)
                await cur.fetchall()
        psycopg_times.append(time.perf_counter() - start)
    
    psycopg_avg = statistics.mean(psycopg_times)
    psycopg_total = sum(psycopg_times)
    logger.info(f"  psycopg 平均耗时: {psycopg_avg*1000:.2f}ms, 总耗时: {psycopg_total:.4f}s")
    
    # 测试 SQLAlchemy
    logger.info("测试 SQLAlchemy...")
    sqlalchemy_times = []
    for _ in range(iterations):
        start = time.perf_counter()
        async with sqlalchemy_engine.connect() as conn:
            await conn.execute(text("""
                SELECT b.category_name, COUNT(a.id) as count, AVG(a.id) as avg_id
                FROM test_perf_complex_a a
                JOIN test_perf_complex_b b ON a.category_id = b.id
                GROUP BY b.category_name
                ORDER BY count DESC
            """))
        sqlalchemy_times.append(time.perf_counter() - start)
    
    sqlalchemy_avg = statistics.mean(sqlalchemy_times)
    sqlalchemy_total = sum(sqlalchemy_times)
    logger.info(f"  SQLAlchemy 平均耗时: {sqlalchemy_avg*1000:.2f}ms, 总耗时: {sqlalchemy_total:.4f}s")
    
    # 清理
    async with sqlalchemy_engine.connect() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS test_perf_complex_a"))
        await conn.execute(text("DROP TABLE IF EXISTS test_perf_complex_b"))
        await conn.commit()
    
    await sqlalchemy_engine.dispose()
    await psycopg_pool.close()
    
    return psycopg_total, sqlalchemy_total


async def main():
    """主测试函数"""
    logger.info("=" * 80)
    logger.info("SQLAlchemy 与原生 psycopg 性能对比测试")
    logger.info("=" * 80)
    logger.info("")
    
    benchmark = PerformanceBenchmark()
    
    # 测试1：简单 SELECT 查询
    logger.info("")
    psycopg_time, sqlalchemy_time = await benchmark_simple_select(iterations=100)
    benchmark.add_result("简单 SELECT 查询", psycopg_time, sqlalchemy_time, 100)
    
    # 测试2：INSERT 操作
    logger.info("")
    psycopg_time, sqlalchemy_time = await benchmark_insert_operation(iterations=100)
    benchmark.add_result("INSERT 操作", psycopg_time, sqlalchemy_time, 100)
    
    # 测试3：UPDATE 操作
    logger.info("")
    psycopg_time, sqlalchemy_time = await benchmark_update_operation(iterations=100)
    benchmark.add_result("UPDATE 操作", psycopg_time, sqlalchemy_time, 100)
    
    # 测试4：批量 INSERT
    logger.info("")
    psycopg_time, sqlalchemy_time = await benchmark_batch_insert(iterations=10, batch_size=100)
    benchmark.add_result("批量 INSERT (100条/批)", psycopg_time, sqlalchemy_time, 10)
    
    # 测试5：并发操作
    logger.info("")
    psycopg_time, sqlalchemy_time = await benchmark_concurrent_operations(concurrent_tasks=20, operations_per_task=10)
    benchmark.add_result("并发操作 (20任务×10操作)", psycopg_time, sqlalchemy_time, 200)
    
    # 测试6：复杂查询
    logger.info("")
    psycopg_time, sqlalchemy_time = await benchmark_complex_query(iterations=50)
    benchmark.add_result("复杂查询 (JOIN+聚合)", psycopg_time, sqlalchemy_time, 50)
    
    # 打印性能报告
    logger.info("")
    benchmark.print_report()
    
    # 总结
    logger.info("")
    logger.info("=" * 80)
    logger.info("性能测试总结")
    logger.info("=" * 80)
    
    acceptable_count = sum(1 for r in benchmark.results if r.overhead_percent < 20)
    total_count = len(benchmark.results)
    
    logger.info(f"可接受的测试项: {acceptable_count}/{total_count}")
    
    if acceptable_count == total_count:
        logger.info("✅ 所有测试项的性能开销都在可接受范围内（<20%）")
        logger.info("✅ SQLAlchemy 可以用于生产环境")
    else:
        logger.warning(f"⚠️  {total_count - acceptable_count} 个测试项的性能开销较高（>=20%）")
        logger.warning("⚠️  建议在高性能场景下继续使用原生 psycopg")
    
    # 计算平均开销
    avg_overhead = statistics.mean([r.overhead_percent for r in benchmark.results])
    logger.info(f"平均性能开销: {avg_overhead:.2f}%")
    
    logger.info("")
    logger.info("建议：")
    logger.info("1. 对于简单查询和CRUD操作，SQLAlchemy 的性能开销可接受")
    logger.info("2. 对于高性能场景，可以考虑继续使用原生 psycopg")
    logger.info("3. SQLAlchemy 提供了更好的代码可维护性和类型安全")
    logger.info("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

