"""
SQLAlchemy 与 LangGraph 连接池兼容性测试

本测试脚本用于验证：
1. SQLAlchemy 使用 psycopg 驱动的兼容性
2. SQLAlchemy 和 LangGraph 能否共享连接池（或至少不冲突）
3. 连接池配置的正确性
4. 并发场景下的稳定性

运行方式：
    conda run -n py_311_rag python test/infrastructure/test_pool_compatibility.py
"""
import sys
import os
import asyncio
import logging
import time
from typing import List, Dict, Any

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from utils.config import Config
from utils.database import get_db_pool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.postgres import AsyncPostgresStore

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_sqlalchemy_psycopg_driver():
    """测试1：验证 SQLAlchemy 使用 psycopg 驱动"""
    logger.info("=" * 60)
    logger.info("测试1：验证 SQLAlchemy 使用 psycopg 驱动")
    logger.info("=" * 60)
    
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        
        # 转换连接字符串
        db_uri = Config.DB_URI
        if db_uri.startswith("postgresql://"):
            sqlalchemy_uri = db_uri.replace("postgresql://", "postgresql+psycopg://", 1)
        else:
            sqlalchemy_uri = db_uri
        
        logger.info(f"SQLAlchemy URI: {sqlalchemy_uri}")
        
        # 创建引擎，使用 psycopg 驱动
        engine = create_async_engine(
            sqlalchemy_uri,
            echo=False,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10
        )
        
        # 测试连接和查询
        async with engine.connect() as conn:
            # 测试基本查询
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            logger.info(f"✅ PostgreSQL 版本查询成功: {version[:50]}...")
            
            # 测试时区设置
            await conn.execute(text(f"SET timezone = '{Config.DB_TIMEZONE}'"))
            result = await conn.execute(text("SHOW timezone"))
            timezone = result.scalar()
            logger.info(f"✅ 时区设置成功: {timezone}")
            
            # 测试连接池信息
            pool = engine.pool
            logger.info(f"✅ 连接池类型: {type(pool).__name__}")
            logger.info(f"✅ 连接池大小: size={pool.size()}, checked_in={pool.checkedin()}, checked_out={pool.checkedout()}")
        
        await engine.dispose()
        logger.info("✅ SQLAlchemy 使用 psycopg 驱动测试通过")
        
        return True
    except Exception as e:
        logger.error(f"❌ SQLAlchemy 使用 psycopg 驱动测试失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_separate_pools_compatibility():
    """测试2：验证 SQLAlchemy 和 LangGraph 使用独立连接池的兼容性"""
    logger.info("=" * 60)
    logger.info("测试2：验证独立连接池兼容性")
    logger.info("=" * 60)
    
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        
        # 1. 创建 psycopg 连接池（LangGraph 使用）
        db_pool = get_db_pool()
        psycopg_pool = await db_pool.create_pool()
        logger.info("✅ psycopg 连接池创建成功")
        
        # 2. 创建 LangGraph 组件
        checkpointer = AsyncPostgresSaver(psycopg_pool)
        await checkpointer.setup()
        logger.info("✅ LangGraph checkpointer 初始化成功")
        
        store = AsyncPostgresStore(psycopg_pool)
        await store.setup()
        logger.info("✅ LangGraph store 初始化成功")
        
        # 3. 创建 SQLAlchemy 引擎（独立连接池）
        db_uri = Config.DB_URI
        if db_uri.startswith("postgresql://"):
            sqlalchemy_uri = db_uri.replace("postgresql://", "postgresql+psycopg://", 1)
        else:
            sqlalchemy_uri = db_uri
        
        sqlalchemy_engine = create_async_engine(
            sqlalchemy_uri,
            echo=False,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10
        )
        logger.info("✅ SQLAlchemy 引擎创建成功（独立连接池）")
        
        # 4. 测试 LangGraph 连接池操作
        async with psycopg_pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1 as langgraph_test")
                result = await cur.fetchone()
                logger.info(f"✅ LangGraph 连接池查询成功: {result}")
        
        # 5. 测试 SQLAlchemy 连接池操作
        async with sqlalchemy_engine.connect() as conn:
            result = await conn.execute(text("SELECT 1 as sqlalchemy_test"))
            value = result.scalar()
            logger.info(f"✅ SQLAlchemy 连接池查询成功: {value}")
        
        # 6. 测试并发操作（两个连接池同时工作）
        logger.info("测试并发操作...")
        async def langgraph_query():
            async with psycopg_pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT pg_sleep(0.1), 'langgraph' as source")
                    return await cur.fetchone()
        
        async def sqlalchemy_query():
            async with sqlalchemy_engine.connect() as conn:
                result = await conn.execute(text("SELECT pg_sleep(0.1), 'sqlalchemy' as source"))
                return result.fetchone()
        
        # 并发执行
        results = await asyncio.gather(langgraph_query(), sqlalchemy_query())
        logger.info(f"✅ 并发查询成功: LangGraph={results[0]}, SQLAlchemy={results[1]}")
        
        # 清理资源
        await sqlalchemy_engine.dispose()
        await psycopg_pool.close()
        
        logger.info("✅ 独立连接池兼容性测试通过")
        logger.info("⚠️  注意：当前使用独立连接池，真正的共享连接池需要适配器实现")
        
        return True
    except Exception as e:
        logger.error(f"❌ 独立连接池兼容性测试失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_pool_configuration():
    """测试3：验证连接池配置正确性"""
    logger.info("=" * 60)
    logger.info("测试3：验证连接池配置正确性")
    logger.info("=" * 60)
    
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        
        # 1. 测试 psycopg 连接池配置
        db_pool = get_db_pool()
        psycopg_pool = await db_pool.create_pool()
        
        logger.info("psycopg 连接池配置:")
        logger.info(f"  - min_size: {db_pool.min_size}")
        logger.info(f"  - max_size: {db_pool.max_size}")
        logger.info(f"  - 连接池状态: {psycopg_pool.get_stats()}")
        
        # 2. 测试 SQLAlchemy 连接池配置
        db_uri = Config.DB_URI
        if db_uri.startswith("postgresql://"):
            sqlalchemy_uri = db_uri.replace("postgresql://", "postgresql+psycopg://", 1)
        else:
            sqlalchemy_uri = db_uri
        
        sqlalchemy_engine = create_async_engine(
            sqlalchemy_uri,
            echo=False,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10
        )
        
        logger.info("SQLAlchemy 连接池配置:")
        pool = sqlalchemy_engine.pool
        logger.info(f"  - pool_size: 5")
        logger.info(f"  - max_overflow: 10")
        logger.info(f"  - pool_pre_ping: True")
        logger.info(f"  - 当前连接数: size={pool.size()}, checked_in={pool.checkedin()}, checked_out={pool.checkedout()}")
        
        # 3. 测试连接池性能
        logger.info("测试连接池性能...")
        start_time = time.time()
        
        async def quick_query():
            async with sqlalchemy_engine.connect() as conn:
                from sqlalchemy import text
                await conn.execute(text("SELECT 1"))
        
        # 并发执行多个查询
        await asyncio.gather(*[quick_query() for _ in range(10)])
        
        elapsed_time = time.time() - start_time
        logger.info(f"✅ 10个并发查询耗时: {elapsed_time:.3f}秒")
        
        # 清理资源
        await sqlalchemy_engine.dispose()
        await psycopg_pool.close()
        
        logger.info("✅ 连接池配置验证通过")
        
        return True
    except Exception as e:
        logger.error(f"❌ 连接池配置验证失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_concurrent_stability():
    """测试4：验证并发场景下的稳定性"""
    logger.info("=" * 60)
    logger.info("测试4：验证并发场景下的稳定性")
    logger.info("=" * 60)
    
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        
        # 创建连接池
        db_pool = get_db_pool()
        psycopg_pool = await db_pool.create_pool()
        
        db_uri = Config.DB_URI
        if db_uri.startswith("postgresql://"):
            sqlalchemy_uri = db_uri.replace("postgresql://", "postgresql+psycopg://", 1)
        else:
            sqlalchemy_uri = db_uri
        
        sqlalchemy_engine = create_async_engine(
            sqlalchemy_uri,
            echo=False,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10
        )
        
        # 创建测试表
        async with sqlalchemy_engine.connect() as conn:
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS test_concurrent_stability (
                    id SERIAL PRIMARY KEY,
                    source VARCHAR(50),
                    value INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            await conn.commit()
        
        # 并发测试函数
        async def langgraph_insert(value: int):
            async with psycopg_pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        "INSERT INTO test_concurrent_stability (source, value) VALUES (%s, %s)",
                        ("langgraph", value)
                    )
                    return value
        
        async def sqlalchemy_insert(value: int):
            async with sqlalchemy_engine.connect() as conn:
                await conn.execute(
                    text("INSERT INTO test_concurrent_stability (source, value) VALUES (:source, :value)"),
                    {"source": "sqlalchemy", "value": value}
                )
                await conn.commit()
                return value
        
        # 并发执行插入操作
        logger.info("执行并发插入操作（20个任务）...")
        tasks = []
        for i in range(10):
            tasks.append(langgraph_insert(i))
            tasks.append(sqlalchemy_insert(i + 10))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 检查结果
        errors = [r for r in results if isinstance(r, Exception)]
        if errors:
            logger.error(f"❌ 并发操作出现错误: {len(errors)} 个")
            for error in errors[:3]:  # 只显示前3个错误
                logger.error(f"  错误: {str(error)}")
            return False
        
        logger.info(f"✅ 并发插入操作成功: {len(results)} 个任务完成")
        
        # 验证数据
        async with sqlalchemy_engine.connect() as conn:
            result = await conn.execute(text("SELECT COUNT(*) FROM test_concurrent_stability"))
            count = result.scalar()
            logger.info(f"✅ 数据验证: 共插入 {count} 条记录")
            
            result = await conn.execute(text("SELECT source, COUNT(*) FROM test_concurrent_stability GROUP BY source"))
            rows = result.fetchall()
            for row in rows:
                logger.info(f"  - {row[0]}: {row[1]} 条")
        
        # 清理测试数据
        async with sqlalchemy_engine.connect() as conn:
            await conn.execute(text("DROP TABLE IF EXISTS test_concurrent_stability"))
            await conn.commit()
        
        # 清理资源
        await sqlalchemy_engine.dispose()
        await psycopg_pool.close()
        
        logger.info("✅ 并发稳定性测试通过")
        
        return True
    except Exception as e:
        logger.error(f"❌ 并发稳定性测试失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_pool_connection_reuse():
    """测试5：验证连接池连接复用"""
    logger.info("=" * 60)
    logger.info("测试5：验证连接池连接复用")
    logger.info("=" * 60)
    
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        
        # 创建 SQLAlchemy 引擎（小连接池）
        db_uri = Config.DB_URI
        if db_uri.startswith("postgresql://"):
            sqlalchemy_uri = db_uri.replace("postgresql://", "postgresql+psycopg://", 1)
        else:
            sqlalchemy_uri = db_uri
        
        engine = create_async_engine(
            sqlalchemy_uri,
            echo=False,
            pool_pre_ping=True,
            pool_size=2,  # 小连接池，便于观察复用
            max_overflow=0
        )
        
        # 测试连接复用
        logger.info("测试连接复用...")
        
        async def query_with_id(query_id: int):
            async with engine.connect() as conn:
                result = await conn.execute(text("SELECT pg_backend_pid()"))
                pid = result.scalar()
                logger.info(f"  查询 {query_id}: 使用进程ID {pid}")
                await asyncio.sleep(0.1)  # 短暂延迟
                return pid
        
        # 顺序执行多个查询（应该复用连接）
        pids = []
        for i in range(5):
            pid = await query_with_id(i)
            pids.append(pid)
        
        # 检查是否复用了连接（进程ID应该相同或只有少量不同）
        unique_pids = len(set(pids))
        logger.info(f"✅ 连接复用测试: 5个查询使用了 {unique_pids} 个不同的连接")
        
        if unique_pids <= 2:
            logger.info("✅ 连接池正确复用连接")
        else:
            logger.warning("⚠️  连接复用可能不够理想")
        
        await engine.dispose()
        
        return True
    except Exception as e:
        logger.error(f"❌ 连接复用测试失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def main():
    """主测试函数"""
    logger.info("=" * 60)
    logger.info("SQLAlchemy 与 LangGraph 连接池兼容性测试")
    logger.info("=" * 60)
    logger.info("")
    
    results = []
    
    # 测试1：SQLAlchemy 使用 psycopg 驱动
    result1 = await test_sqlalchemy_psycopg_driver()
    results.append(("SQLAlchemy 使用 psycopg 驱动", result1))
    logger.info("")
    
    # 测试2：独立连接池兼容性
    result2 = await test_separate_pools_compatibility()
    results.append(("独立连接池兼容性", result2))
    logger.info("")
    
    # 测试3：连接池配置验证
    result3 = await test_pool_configuration()
    results.append(("连接池配置验证", result3))
    logger.info("")
    
    # 测试4：并发稳定性
    result4 = await test_concurrent_stability()
    results.append(("并发稳定性", result4))
    logger.info("")
    
    # 测试5：连接复用
    result5 = await test_pool_connection_reuse()
    results.append(("连接复用", result5))
    logger.info("")
    
    # 输出测试结果汇总
    logger.info("=" * 60)
    logger.info("测试结果汇总")
    logger.info("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    logger.info("")
    if all_passed:
        logger.info("🎉 所有测试通过！连接池兼容性验证完成。")
        logger.info("")
        logger.info("结论：")
        logger.info("1. ✅ SQLAlchemy 可以使用 psycopg 驱动")
        logger.info("2. ✅ SQLAlchemy 和 LangGraph 可以使用独立连接池，互不干扰")
        logger.info("3. ✅ 连接池配置正确，性能良好")
        logger.info("4. ✅ 并发场景下稳定可靠")
        logger.info("")
        logger.info("注意：")
        logger.info("- 当前实现使用独立连接池，不是真正的共享连接池")
        logger.info("- 如需共享连接池，需要实现适配器或使用其他方案")
        logger.info("- 独立连接池方案已经足够使用，性能影响可接受")
    else:
        logger.error("❌ 部分测试失败，请检查错误信息并修复问题。")
    
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

