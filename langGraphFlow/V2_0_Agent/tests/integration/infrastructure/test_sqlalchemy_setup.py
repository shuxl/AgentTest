"""
SQLAlchemy 环境准备和依赖安装测试

本测试脚本用于验证：
1. SQLAlchemy 2.0+ 异步版本是否正确安装
2. SQLAlchemy 与 psycopg 驱动的兼容性
3. SQLAlchemy 与 LangGraph 的连接池兼容性（基础测试）
4. 基本功能测试

运行方式：
    conda run -n py_311_rag python tests/integration/infrastructure/test_sqlalchemy_setup.py
"""
import sys
import os
import asyncio
import logging

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

from core.config import get_settings
from core.database import get_db_pool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.postgres import AsyncPostgresStore

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_sqlalchemy_installation():
    """测试1：验证 SQLAlchemy 是否正确安装"""
    logger.info("=" * 60)
    logger.info("测试1：验证 SQLAlchemy 安装")
    logger.info("=" * 60)
    
    try:
        import sqlalchemy
        logger.info(f"✅ SQLAlchemy 版本: {sqlalchemy.__version__}")
        
        # 检查版本是否 >= 2.0.0
        version_parts = sqlalchemy.__version__.split('.')
        major_version = int(version_parts[0])
        if major_version < 2:
            logger.error(f"❌ SQLAlchemy 版本过低: {sqlalchemy.__version__}，需要 >= 2.0.0")
            return False
        
        # 检查 greenlet 依赖（SQLAlchemy 异步功能必需）
        try:
            import greenlet
            logger.info(f"✅ greenlet 版本: {greenlet.__version__}")
        except ImportError:
            logger.error("❌ greenlet 未安装，SQLAlchemy 异步功能需要 greenlet")
            logger.error("请运行: pip install greenlet>=3.0.0")
            return False
        
        # 检查异步支持
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        logger.info("✅ SQLAlchemy 异步模块导入成功")
        
        return True
    except ImportError as e:
        logger.error(f"❌ SQLAlchemy 导入失败: {str(e)}")
        logger.error("请运行: pip install sqlalchemy>=2.0.0 greenlet>=3.0.0")
        return False
    except Exception as e:
        logger.error(f"❌ SQLAlchemy 测试失败: {str(e)}")
        return False


async def test_sqlalchemy_psycopg_compatibility():
    """测试2：验证 SQLAlchemy 与 psycopg 驱动的兼容性"""
    logger.info("=" * 60)
    logger.info("测试2：验证 SQLAlchemy 与 psycopg 驱动兼容性")
    logger.info("=" * 60)
    
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        
        # 使用 psycopg 驱动创建引擎
        # 注意：SQLAlchemy 使用 postgresql+psycopg:// 作为连接字符串
        settings = get_settings()
        db_uri = settings.db_uri
        # 将 postgresql:// 转换为 postgresql+psycopg://
        if db_uri.startswith("postgresql://"):
            sqlalchemy_uri = db_uri.replace("postgresql://", "postgresql+psycopg://", 1)
        elif db_uri.startswith("postgresql+psycopg://"):
            sqlalchemy_uri = db_uri
        else:
            logger.error(f"❌ 不支持的数据库URI格式: {db_uri}")
            return False
        
        logger.info(f"SQLAlchemy URI: {sqlalchemy_uri}")
        
        # 创建异步引擎
        engine = create_async_engine(
            sqlalchemy_uri,
            echo=False,  # 设置为 True 可以看到 SQL 日志
            pool_pre_ping=True,  # 连接前ping，确保连接有效
            pool_size=5,
            max_overflow=10
        )
        
        # 测试连接
        from sqlalchemy import text
        async with engine.connect() as conn:
            result = await conn.execute(
                text("SELECT version()")
            )
            version = result.scalar()
            logger.info(f"✅ 数据库连接成功")
            logger.info(f"PostgreSQL 版本: {version[:50]}...")
        
        await engine.dispose()
        logger.info("✅ SQLAlchemy 引擎关闭成功")
        
        return True
    except Exception as e:
        logger.error(f"❌ SQLAlchemy 与 psycopg 兼容性测试失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_sqlalchemy_langgraph_pool_compatibility():
    """测试3：验证 SQLAlchemy 与 LangGraph 的连接池兼容性（基础测试）"""
    logger.info("=" * 60)
    logger.info("测试3：验证 SQLAlchemy 与 LangGraph 连接池兼容性")
    logger.info("=" * 60)
    
    try:
        # 1. 创建 psycopg 连接池（LangGraph 使用）
        settings = get_settings()
        db_pool = get_db_pool(settings)
        await db_pool.initialize()
        psycopg_pool = await db_pool.create_pool()
        logger.info("✅ psycopg 连接池创建成功")
        
        # 2. 创建 LangGraph 的 checkpointer 和 store
        checkpointer = AsyncPostgresSaver(psycopg_pool)
        await checkpointer.setup()
        logger.info("✅ LangGraph checkpointer 初始化成功")
        
        store = AsyncPostgresStore(psycopg_pool)
        await store.setup()
        logger.info("✅ LangGraph store 初始化成功")
        
        # 3. 创建 SQLAlchemy 引擎（使用相同的连接字符串）
        from sqlalchemy.ext.asyncio import create_async_engine
        
        db_uri = settings.db_uri
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
        logger.info("✅ SQLAlchemy 引擎创建成功")
        
        # 4. 测试 SQLAlchemy 连接
        from sqlalchemy import text
        async with sqlalchemy_engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            value = result.scalar()
            logger.info(f"✅ SQLAlchemy 查询成功: {value}")
        
        # 5. 测试 LangGraph 连接（使用同一个连接池）
        # 注意：这里我们使用不同的连接池，但连接到同一个数据库
        # 真正的共享连接池测试需要在后续阶段进行
        async with psycopg_pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1")
                result = await cur.fetchone()
                logger.info(f"✅ LangGraph 连接池查询成功: {result}")
        
        # 清理资源
        await sqlalchemy_engine.dispose()
        await db_pool.close()
        
        logger.info("✅ SQLAlchemy 与 LangGraph 基础兼容性测试通过")
        logger.info("⚠️  注意：真正的连接池共享测试需要在后续阶段进行")
        
        return True
    except Exception as e:
        logger.error(f"❌ SQLAlchemy 与 LangGraph 兼容性测试失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_sqlalchemy_basic_operations():
    """测试4：验证 SQLAlchemy 基本操作功能"""
    logger.info("=" * 60)
    logger.info("测试4：验证 SQLAlchemy 基本操作功能")
    logger.info("=" * 60)
    
    try:
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy import text
        
        settings = get_settings()
        db_uri = settings.db_uri
        if db_uri.startswith("postgresql://"):
            sqlalchemy_uri = db_uri.replace("postgresql://", "postgresql+psycopg://", 1)
        else:
            sqlalchemy_uri = db_uri
        
        engine = create_async_engine(
            sqlalchemy_uri,
            echo=False,
            pool_pre_ping=True
        )
        
        # 测试基本查询
        async with engine.connect() as conn:
            # 测试 SELECT
            result = await conn.execute(text("SELECT CURRENT_TIMESTAMP"))
            timestamp = result.scalar()
            logger.info(f"✅ SELECT 查询成功: {timestamp}")
            
            # 测试时区设置
            settings = get_settings()
            await conn.execute(text(f"SET timezone = '{settings.db_timezone}'"))
            result = await conn.execute(text("SHOW timezone"))
            timezone = result.scalar()
            logger.info(f"✅ 时区设置成功: {timezone}")
        
        # 测试事务
        async with engine.begin() as conn:
            # 创建一个测试表（如果不存在）
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS test_sqlalchemy_setup (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            logger.info("✅ 创建测试表成功")
            
            # 插入测试数据
            await conn.execute(text("""
                INSERT INTO test_sqlalchemy_setup (name) 
                VALUES ('test_record')
            """))
            logger.info("✅ 插入测试数据成功")
            
            # 查询测试数据
            result = await conn.execute(text("""
                SELECT id, name FROM test_sqlalchemy_setup 
                WHERE name = 'test_record'
            """))
            row = result.fetchone()
            if row:
                logger.info(f"✅ 查询测试数据成功: id={row[0]}, name={row[1]}")
            
            # 清理测试数据
            await conn.execute(text("DELETE FROM test_sqlalchemy_setup WHERE name = 'test_record'"))
            logger.info("✅ 清理测试数据成功")
        
        await engine.dispose()
        logger.info("✅ SQLAlchemy 基本操作测试通过")
        
        return True
    except Exception as e:
        logger.error(f"❌ SQLAlchemy 基本操作测试失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def main():
    """主测试函数"""
    logger.info("=" * 60)
    logger.info("SQLAlchemy 环境准备和依赖安装测试")
    logger.info("=" * 60)
    logger.info("")
    
    results = []
    
    # 测试1：验证 SQLAlchemy 安装
    result1 = await test_sqlalchemy_installation()
    results.append(("SQLAlchemy 安装验证", result1))
    logger.info("")
    
    if not result1:
        logger.error("❌ SQLAlchemy 安装失败，请先安装 SQLAlchemy 2.0+ 和 greenlet")
        logger.error("安装命令: pip install sqlalchemy>=2.0.0 greenlet>=3.0.0")
        return
    
    # 测试2：验证 SQLAlchemy 与 psycopg 兼容性
    result2 = await test_sqlalchemy_psycopg_compatibility()
    results.append(("SQLAlchemy 与 psycopg 兼容性", result2))
    logger.info("")
    
    # 测试3：验证 SQLAlchemy 与 LangGraph 兼容性
    result3 = await test_sqlalchemy_langgraph_pool_compatibility()
    results.append(("SQLAlchemy 与 LangGraph 兼容性", result3))
    logger.info("")
    
    # 测试4：验证 SQLAlchemy 基本操作
    result4 = await test_sqlalchemy_basic_operations()
    results.append(("SQLAlchemy 基本操作", result4))
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
        logger.info("🎉 所有测试通过！SQLAlchemy 环境准备完成。")
        logger.info("")
        logger.info("下一步：")
        logger.info("1. 进行连接池共享测试（任务2）")
        logger.info("2. 进行事务隔离测试（任务3）")
        logger.info("3. 进行性能对比测试（任务4）")
    else:
        logger.error("❌ 部分测试失败，请检查错误信息并修复问题。")
    
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

