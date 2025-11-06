"""
测试数据库连接池统一管理
验证 LangGraph 和 SQLAlchemy 连接池的统一管理是否正常工作
"""
import asyncio
import sys
import os
import logging

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from utils.config import Config
from utils.database import get_db_pool
from utils.db import get_async_session, BloodPressureRecord
from utils.logging_config import setup_logging
from sqlalchemy import select

# 设置统一的日志配置
setup_logging()

logger = logging.getLogger(__name__)


async def test_unified_pool_management():
    """测试统一连接池管理"""
    logger.info("=" * 60)
    logger.info("测试统一连接池管理")
    logger.info("=" * 60)
    
    try:
        # 1. 初始化连接池
        db_pool = get_db_pool()
        langgraph_pool = await db_pool.create_pool()
        
        logger.info("✅ 连接池初始化成功")
        
        # 2. 检查连接池状态
        langgraph_ok = db_pool.pool is not None
        sqlalchemy_ok = db_pool.sqlalchemy_engine is not None
        
        assert langgraph_ok, "LangGraph 连接池未初始化"
        assert sqlalchemy_ok, "SQLAlchemy 引擎未初始化"
        logger.info("✅ LangGraph 和 SQLAlchemy 连接池都已初始化")
        
        # 3. 获取连接池统计信息
        stats = db_pool.get_pool_stats()
        logger.info(f"✅ 连接池统计信息: {stats}")
        
        # 4. 测试 SQLAlchemy 连接
        async_session_maker = get_async_session()
        async with async_session_maker() as session:
            # 执行一个简单查询
            query = select(BloodPressureRecord).limit(1)
            result = await session.execute(query)
            records = result.scalars().all()
            logger.info(f"✅ SQLAlchemy 查询成功，返回 {len(records)} 条记录")
        
        # 5. 测试 LangGraph 连接（简单测试）
        async with langgraph_pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1 as test_value")
                result = await cur.fetchone()
                # psycopg 使用 dict_row，返回字典
                assert result['test_value'] == 1
                logger.info("✅ LangGraph 连接池查询成功")
        
        # 6. 关闭连接池
        await db_pool.close()
        logger.info("✅ 连接池关闭成功")
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ 所有测试通过")
        logger.info("=" * 60)
        return True
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def main():
    """主测试函数"""
    success = await test_unified_pool_management()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

