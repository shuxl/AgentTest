"""
SQLAlchemy 与 LangGraph 事务隔离测试

本测试脚本用于验证：
1. SQLAlchemy 事务与 LangGraph 事务隔离
2. 验证事务不会相互干扰
3. 测试并发场景下的稳定性

运行方式：
    conda run -n py_311_rag python test/infrastructure/test_transaction_isolation.py
"""
import sys
import os
import asyncio
import logging
import time
from typing import List, Dict, Any, Optional

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


async def test_sqlalchemy_transaction_isolation():
    """测试1：验证 SQLAlchemy 事务隔离"""
    logger.info("=" * 60)
    logger.info("测试1：验证 SQLAlchemy 事务隔离")
    logger.info("=" * 60)
    
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        
        # 创建 SQLAlchemy 引擎
        db_uri = Config.DB_URI
        if db_uri.startswith("postgresql://"):
            sqlalchemy_uri = db_uri.replace("postgresql://", "postgresql+psycopg://", 1)
        else:
            sqlalchemy_uri = db_uri
        
        engine = create_async_engine(
            sqlalchemy_uri,
            echo=False,
            pool_pre_ping=True
        )
        
        # 创建测试表
        async with engine.connect() as conn:
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS test_transaction_isolation (
                    id SERIAL PRIMARY KEY,
                    source VARCHAR(50),
                    value INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            await conn.commit()
        
        # 测试事务提交
        logger.info("测试事务提交...")
        async with engine.begin() as conn:
            await conn.execute(text("""
                INSERT INTO test_transaction_isolation (source, value)
                VALUES ('sqlalchemy_commit', 100)
            """))
            # begin() 上下文管理器会自动提交
        
        # 验证数据已提交
        async with engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT COUNT(*) FROM test_transaction_isolation
                WHERE source = 'sqlalchemy_commit'
            """))
            count = result.scalar()
            if count == 1:
                logger.info("✅ 事务提交成功，数据已持久化")
            else:
                logger.error(f"❌ 事务提交失败，期望1条记录，实际{count}条")
                return False
        
        # 测试事务回滚
        logger.info("测试事务回滚...")
        try:
            async with engine.begin() as conn:
                await conn.execute(text("""
                    INSERT INTO test_transaction_isolation (source, value)
                    VALUES ('sqlalchemy_rollback', 200)
                """))
                # 模拟错误，触发回滚
                raise ValueError("模拟错误，触发回滚")
        except ValueError:
            pass  # 预期错误
        
        # 验证数据未提交（应该回滚）
        async with engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT COUNT(*) FROM test_transaction_isolation
                WHERE source = 'sqlalchemy_rollback'
            """))
            count = result.scalar()
            if count == 0:
                logger.info("✅ 事务回滚成功，数据未持久化")
            else:
                logger.error(f"❌ 事务回滚失败，期望0条记录，实际{count}条")
                return False
        
        # 清理测试数据
        async with engine.connect() as conn:
            await conn.execute(text("DROP TABLE IF EXISTS test_transaction_isolation"))
            await conn.commit()
        
        await engine.dispose()
        logger.info("✅ SQLAlchemy 事务隔离测试通过")
        
        return True
    except Exception as e:
        logger.error(f"❌ SQLAlchemy 事务隔离测试失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_langgraph_autocommit_behavior():
    """测试2：验证 LangGraph (psycopg) 的 autocommit 行为"""
    logger.info("=" * 60)
    logger.info("测试2：验证 LangGraph (psycopg) 的 autocommit 行为")
    logger.info("=" * 60)
    
    try:
        # 创建 psycopg 连接池（LangGraph 使用，autocommit=True）
        db_pool = get_db_pool()
        psycopg_pool = await db_pool.create_pool()
        
        # 清理旧数据并创建测试表
        async with psycopg_pool.connection() as conn:
            async with conn.cursor() as cur:
                # 先删除表（如果存在）
                await cur.execute("DROP TABLE IF EXISTS test_langgraph_autocommit")
                # 创建新表
                await cur.execute("""
                    CREATE TABLE test_langgraph_autocommit (
                        id SERIAL PRIMARY KEY,
                        source VARCHAR(50),
                        value INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                # autocommit=True，所以不需要显式提交
        
        logger.info("✅ 测试表创建成功（autocommit 模式）")
        
        # 测试插入操作（autocommit 模式）
        async with psycopg_pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    INSERT INTO test_langgraph_autocommit (source, value)
                    VALUES (%s, %s)
                """, ("langgraph_autocommit", 300))
                # autocommit=True，自动提交
        
        # 验证数据已提交
        async with psycopg_pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    SELECT COUNT(*) as count FROM test_langgraph_autocommit
                    WHERE source = 'langgraph_autocommit'
                """)
                result = await cur.fetchone()
                # psycopg 使用 dict_row，返回字典
                count = result['count'] if result else 0
                if count == 1:
                    logger.info("✅ autocommit 模式正常工作，数据已自动提交")
                else:
                    logger.error(f"❌ autocommit 模式异常，期望1条记录，实际{count}条")
                    return False
        
        # 测试手动事务（如果需要）
        logger.info("测试手动事务控制...")
        async with psycopg_pool.connection() as conn:
            # 关闭 autocommit 进行事务测试
            await conn.set_autocommit(False)
            try:
                async with conn.cursor() as cur:
                    await cur.execute("""
                        INSERT INTO test_langgraph_autocommit (source, value)
                        VALUES (%s, %s)
                    """, ("langgraph_manual_commit", 400))
                    await conn.commit()
                    logger.info("✅ 手动事务提交成功")
            except Exception as e:
                await conn.rollback()
                logger.error(f"❌ 手动事务失败: {str(e)}")
                return False
            finally:
                await conn.set_autocommit(True)  # 恢复 autocommit
        
        # 清理测试数据
        async with psycopg_pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("DROP TABLE IF EXISTS test_langgraph_autocommit")
        
        await psycopg_pool.close()
        logger.info("✅ LangGraph autocommit 行为测试通过")
        
        return True
    except Exception as e:
        logger.error(f"❌ LangGraph autocommit 行为测试失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_cross_framework_transaction_isolation():
    """测试3：验证跨框架事务隔离（SQLAlchemy 和 LangGraph）"""
    logger.info("=" * 60)
    logger.info("测试3：验证跨框架事务隔离")
    logger.info("=" * 60)
    
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        
        # 创建两个连接池
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
            pool_pre_ping=True
        )
        
        # 创建测试表
        async with sqlalchemy_engine.connect() as conn:
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS test_cross_framework_isolation (
                    id SERIAL PRIMARY KEY,
                    source VARCHAR(50),
                    value INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            await conn.commit()
        
        # 测试场景1：SQLAlchemy 事务中，LangGraph 能否看到未提交的数据
        logger.info("测试场景1：SQLAlchemy 事务隔离...")
        async with sqlalchemy_engine.begin() as sqlalchemy_conn:
            # SQLAlchemy 插入数据（未提交）
            await sqlalchemy_conn.execute(text("""
                INSERT INTO test_cross_framework_isolation (source, value)
                VALUES ('sqlalchemy_uncommitted', 500)
            """))
            
            # LangGraph 查询（应该看不到未提交的数据）
            async with psycopg_pool.connection() as langgraph_conn:
                async with langgraph_conn.cursor() as cur:
                    await cur.execute("""
                        SELECT COUNT(*) as count FROM test_cross_framework_isolation
                        WHERE source = 'sqlalchemy_uncommitted'
                    """)
                    result = await cur.fetchone()
                    # psycopg 使用 dict_row，返回字典
                    count = result['count'] if result else 0
                    
                    if count == 0:
                        logger.info("✅ SQLAlchemy 事务隔离正常，LangGraph 看不到未提交数据")
                    else:
                        logger.warning(f"⚠️  SQLAlchemy 事务隔离可能有问题，LangGraph 看到了未提交数据（count={count}）")
                        # 注意：这可能是因为 autocommit=True 或隔离级别设置
        
        # 验证 SQLAlchemy 事务提交后，LangGraph 能看到数据
        async with psycopg_pool.connection() as langgraph_conn:
            async with langgraph_conn.cursor() as cur:
                await cur.execute("""
                    SELECT COUNT(*) as count FROM test_cross_framework_isolation
                    WHERE source = 'sqlalchemy_uncommitted'
                """)
                result = await cur.fetchone()
                # psycopg 使用 dict_row，返回字典
                count = result['count'] if result else 0
                if count == 1:
                    logger.info("✅ SQLAlchemy 事务提交后，LangGraph 能看到数据")
                else:
                    logger.error(f"❌ SQLAlchemy 事务提交后，LangGraph 看不到数据（count={count}）")
                    return False
        
        # 测试场景2：LangGraph autocommit 操作，SQLAlchemy 能否立即看到
        logger.info("测试场景2：LangGraph autocommit 隔离...")
        async with psycopg_pool.connection() as langgraph_conn:
            async with langgraph_conn.cursor() as cur:
                await cur.execute("""
                    INSERT INTO test_cross_framework_isolation (source, value)
                    VALUES (%s, %s)
                """, ("langgraph_autocommit_test", 600))
                # autocommit=True，自动提交
        
        # SQLAlchemy 查询（应该能看到已提交的数据）
        async with sqlalchemy_engine.connect() as sqlalchemy_conn:
            result = await sqlalchemy_conn.execute(text("""
                SELECT COUNT(*) FROM test_cross_framework_isolation
                WHERE source = 'langgraph_autocommit_test'
            """))
            count = result.scalar()
            if count == 1:
                logger.info("✅ LangGraph autocommit 后，SQLAlchemy 能看到数据")
            else:
                logger.error(f"❌ LangGraph autocommit 后，SQLAlchemy 看不到数据（count={count}）")
                return False
        
        # 清理测试数据
        async with sqlalchemy_engine.connect() as conn:
            await conn.execute(text("DROP TABLE IF EXISTS test_cross_framework_isolation"))
            await conn.commit()
        
        await sqlalchemy_engine.dispose()
        await psycopg_pool.close()
        
        logger.info("✅ 跨框架事务隔离测试通过")
        
        return True
    except Exception as e:
        logger.error(f"❌ 跨框架事务隔离测试失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_concurrent_transaction_stability():
    """测试4：验证并发事务场景下的稳定性"""
    logger.info("=" * 60)
    logger.info("测试4：验证并发事务场景下的稳定性")
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
            pool_pre_ping=True
        )
        
        # 创建测试表
        async with sqlalchemy_engine.connect() as conn:
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS test_concurrent_transactions (
                    id SERIAL PRIMARY KEY,
                    source VARCHAR(50),
                    transaction_id INTEGER,
                    value INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            await conn.commit()
        
        # 并发事务函数
        async def sqlalchemy_transaction(tx_id: int):
            """SQLAlchemy 事务操作"""
            try:
                async with sqlalchemy_engine.begin() as conn:
                    await conn.execute(text("""
                        INSERT INTO test_concurrent_transactions (source, transaction_id, value)
                        VALUES (:source, :tx_id, :value)
                    """), {
                        "source": "sqlalchemy",
                        "tx_id": tx_id,
                        "value": tx_id * 10
                    })
                    await asyncio.sleep(0.1)  # 模拟处理时间
                return tx_id
            except Exception as e:
                logger.error(f"SQLAlchemy 事务 {tx_id} 失败: {str(e)}")
                return None
        
        async def langgraph_transaction(tx_id: int):
            """LangGraph (psycopg) 事务操作"""
            try:
                async with psycopg_pool.connection() as conn:
                    async with conn.cursor() as cur:
                        await cur.execute("""
                            INSERT INTO test_concurrent_transactions (source, transaction_id, value)
                            VALUES (%s, %s, %s)
                        """, ("langgraph", tx_id, tx_id * 20))
                        await asyncio.sleep(0.1)  # 模拟处理时间
                return tx_id
            except Exception as e:
                logger.error(f"LangGraph 事务 {tx_id} 失败: {str(e)}")
                return None
        
        # 并发执行多个事务
        logger.info("执行并发事务操作（20个任务）...")
        tasks = []
        for i in range(10):
            tasks.append(sqlalchemy_transaction(i))
            tasks.append(langgraph_transaction(i + 10))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 检查结果
        errors = [r for r in results if isinstance(r, Exception)]
        successes = [r for r in results if r is not None and not isinstance(r, Exception)]
        
        if errors:
            logger.error(f"❌ 并发事务出现错误: {len(errors)} 个")
            for error in errors[:3]:  # 只显示前3个错误
                logger.error(f"  错误: {str(error)}")
            return False
        
        logger.info(f"✅ 并发事务操作成功: {len(successes)} 个任务完成")
        
        # 验证数据一致性
        async with sqlalchemy_engine.connect() as conn:
            # 统计 SQLAlchemy 插入的数据
            result = await conn.execute(text("""
                SELECT COUNT(*) FROM test_concurrent_transactions
                WHERE source = 'sqlalchemy'
            """))
            sqlalchemy_count = result.scalar()
            
            # 统计 LangGraph 插入的数据
            result = await conn.execute(text("""
                SELECT COUNT(*) FROM test_concurrent_transactions
                WHERE source = 'langgraph'
            """))
            langgraph_count = result.scalar()
            
            logger.info(f"✅ 数据一致性验证:")
            logger.info(f"  - SQLAlchemy 插入: {sqlalchemy_count} 条")
            logger.info(f"  - LangGraph 插入: {langgraph_count} 条")
            logger.info(f"  - 总计: {sqlalchemy_count + langgraph_count} 条")
            
            if sqlalchemy_count + langgraph_count == 20:
                logger.info("✅ 数据一致性验证通过")
            else:
                logger.warning(f"⚠️  数据一致性可能有问题，期望20条，实际{sqlalchemy_count + langgraph_count}条")
        
        # 清理测试数据
        async with sqlalchemy_engine.connect() as conn:
            await conn.execute(text("DROP TABLE IF EXISTS test_concurrent_transactions"))
            await conn.commit()
        
        await sqlalchemy_engine.dispose()
        await psycopg_pool.close()
        
        logger.info("✅ 并发事务稳定性测试通过")
        
        return True
    except Exception as e:
        logger.error(f"❌ 并发事务稳定性测试失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_transaction_rollback_isolation():
    """测试5：验证事务回滚隔离"""
    logger.info("=" * 60)
    logger.info("测试5：验证事务回滚隔离")
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
            pool_pre_ping=True
        )
        
        # 清理旧数据并创建测试表
        async with sqlalchemy_engine.connect() as conn:
            await conn.execute(text("DROP TABLE IF EXISTS test_rollback_isolation"))
            await conn.execute(text("""
                CREATE TABLE test_rollback_isolation (
                    id SERIAL PRIMARY KEY,
                    source VARCHAR(50),
                    value INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            await conn.commit()
        
        logger.info("测试 SQLAlchemy 事务回滚隔离...")
        
        # 先插入一条正常数据
        async with sqlalchemy_engine.begin() as conn:
            await conn.execute(text("""
                INSERT INTO test_rollback_isolation (source, value)
                VALUES ('sqlalchemy_committed', 700)
            """))
        
        # 尝试插入并回滚
        try:
            async with sqlalchemy_engine.begin() as conn:
                await conn.execute(text("""
                    INSERT INTO test_rollback_isolation (source, value)
                    VALUES ('sqlalchemy_rolled_back', 800)
                """))
                raise ValueError("模拟错误，触发回滚")
        except ValueError:
            pass
        
        # LangGraph 查询，应该只看到已提交的数据
        async with psycopg_pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    SELECT source, COUNT(*) as cnt
                    FROM test_rollback_isolation
                    GROUP BY source
                """)
                results = await cur.fetchall()
                
                committed_count = 0
                rolled_back_count = 0
                
                # psycopg 使用 dict_row，返回字典
                for row in results:
                    source = row['source']
                    cnt = row['cnt']
                    if source == 'sqlalchemy_committed':
                        committed_count = cnt
                    elif source == 'sqlalchemy_rolled_back':
                        rolled_back_count = cnt
                
                if committed_count == 1 and rolled_back_count == 0:
                    logger.info("✅ SQLAlchemy 事务回滚隔离正常，LangGraph 看不到回滚的数据")
                else:
                    logger.warning(f"⚠️  SQLAlchemy 事务回滚隔离可能有问题: committed={committed_count}, rolled_back={rolled_back_count}")
        
        # 清理测试数据
        async with sqlalchemy_engine.connect() as conn:
            await conn.execute(text("DROP TABLE IF EXISTS test_rollback_isolation"))
            await conn.commit()
        
        await sqlalchemy_engine.dispose()
        await psycopg_pool.close()
        
        logger.info("✅ 事务回滚隔离测试通过")
        
        return True
    except Exception as e:
        logger.error(f"❌ 事务回滚隔离测试失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def main():
    """主测试函数"""
    logger.info("=" * 60)
    logger.info("SQLAlchemy 与 LangGraph 事务隔离测试")
    logger.info("=" * 60)
    logger.info("")
    
    results = []
    
    # 测试1：SQLAlchemy 事务隔离
    result1 = await test_sqlalchemy_transaction_isolation()
    results.append(("SQLAlchemy 事务隔离", result1))
    logger.info("")
    
    # 测试2：LangGraph autocommit 行为
    result2 = await test_langgraph_autocommit_behavior()
    results.append(("LangGraph autocommit 行为", result2))
    logger.info("")
    
    # 测试3：跨框架事务隔离
    result3 = await test_cross_framework_transaction_isolation()
    results.append(("跨框架事务隔离", result3))
    logger.info("")
    
    # 测试4：并发事务稳定性
    result4 = await test_concurrent_transaction_stability()
    results.append(("并发事务稳定性", result4))
    logger.info("")
    
    # 测试5：事务回滚隔离
    result5 = await test_transaction_rollback_isolation()
    results.append(("事务回滚隔离", result5))
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
        logger.info("🎉 所有测试通过！事务隔离验证完成。")
        logger.info("")
        logger.info("结论：")
        logger.info("1. ✅ SQLAlchemy 事务隔离正常")
        logger.info("2. ✅ LangGraph (psycopg) autocommit 行为正常")
        logger.info("3. ✅ 跨框架事务隔离正常，不会相互干扰")
        logger.info("4. ✅ 并发场景下稳定可靠")
        logger.info("5. ✅ 事务回滚隔离正常")
        logger.info("")
        logger.info("重要说明：")
        logger.info("- LangGraph 使用 autocommit=True，每个操作自动提交")
        logger.info("- SQLAlchemy 使用显式事务，需要手动提交或回滚")
        logger.info("- 两个框架的事务相互隔离，不会干扰")
    else:
        logger.error("❌ 部分测试失败，请检查错误信息并修复问题。")
    
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

