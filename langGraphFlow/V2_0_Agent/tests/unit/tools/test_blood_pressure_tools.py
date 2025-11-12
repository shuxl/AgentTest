"""
血压记录工具单元测试（使用 SQLAlchemy ORM）
测试重构后的 blood_pressure_tools 功能
"""
import asyncio
import sys
import os
import logging
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

from core.database import get_db_pool
from domain.agents.blood_pressure.tools import create_blood_pressure_tools
from domain.models import get_async_session, BloodPressureRecord
from langgraph.store.postgres import AsyncPostgresStore

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 测试用户ID
TEST_USER_ID = "test_user_bp_tools_001"


async def cleanup_test_data():
    """清理测试数据"""
    try:
        async_session_maker = get_async_session()
        async with async_session_maker() as session:
            from sqlalchemy import delete
            
            await session.execute(
                delete(BloodPressureRecord).where(BloodPressureRecord.user_id == TEST_USER_ID)
            )
            await session.commit()
            logger.info("✓ 测试数据清理完成")
    except Exception as e:
        logger.warning(f"清理测试数据时出现警告: {str(e)}")


async def test_record_blood_pressure():
    """测试 record_blood_pressure 工具"""
    logger.info("=" * 60)
    logger.info("测试1：record_blood_pressure 工具")
    logger.info("=" * 60)
    
    try:
        await cleanup_test_data()
        
        pool = get_db_pool()
        await pool.create_pool()
        
        # 创建工具
        tools = create_blood_pressure_tools(pool.pool, TEST_USER_ID)
        record_tool = tools[0]  # record_blood_pressure
        
        # 测试记录血压
        result = await record_tool.ainvoke({
            "systolic": 120,
            "diastolic": 80,
            "date_time": None,
            "original_time_description": None,
            "notes": "测试记录"
        })
        
        assert "成功保存血压记录" in result
        assert "120" in result
        assert "80" in result
        logger.info(f"✅ record_blood_pressure 测试成功")
        logger.info(f"   结果: {result[:100]}...")
        
        await pool.close()
        return True
    except Exception as e:
        logger.error(f"❌ record_blood_pressure 测试失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_query_blood_pressure():
    """测试 query_blood_pressure 工具"""
    logger.info("\n" + "=" * 60)
    logger.info("测试2：query_blood_pressure 工具")
    logger.info("=" * 60)
    
    try:
        pool = get_db_pool()
        await pool.create_pool()
        
        # 先创建一些测试数据
        tools = create_blood_pressure_tools(pool.pool, TEST_USER_ID)
        record_tool = tools[0]
        
        for i in range(3):
            await record_tool.ainvoke({
                "systolic": 120 + i,
                "diastolic": 80 + i,
                "date_time": None,
                "notes": f"测试记录{i+1}"
            })
        
        # 查询记录
        query_tool = tools[1]  # query_blood_pressure
        result = await query_tool.ainvoke({
            "start_date": None,
            "end_date": None,
            "limit": 10
        })
        
        assert "找到" in result or "条血压记录" in result
        logger.info(f"✅ query_blood_pressure 测试成功")
        logger.info(f"   结果: {result[:200]}...")
        
        await pool.close()
        return True
    except Exception as e:
        logger.error(f"❌ query_blood_pressure 测试失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_update_blood_pressure():
    """测试 update_blood_pressure 工具"""
    logger.info("\n" + "=" * 60)
    logger.info("测试3：update_blood_pressure 工具")
    logger.info("=" * 60)
    
    try:
        pool = get_db_pool()
        await pool.create_pool()
        
        # 先创建一条记录
        tools = create_blood_pressure_tools(pool.pool, TEST_USER_ID)
        record_tool = tools[0]
        
        result = await record_tool.ainvoke({
            "systolic": 120,
            "diastolic": 80,
            "date_time": None,
            "notes": "原始备注"
        })
        
        # 获取记录ID（从返回消息中提取，或从数据库查询）
        async_session_maker = get_async_session()
        async with async_session_maker() as session:
            from sqlalchemy import select
            query = select(BloodPressureRecord).where(
                BloodPressureRecord.user_id == TEST_USER_ID
            ).order_by(BloodPressureRecord.id.desc()).limit(1)
            result_query = await session.execute(query)
            record = result_query.scalar_one_or_none()
            
            if record:
                record_id = str(record.id)
                
                # 更新记录
                update_tool = tools[2]  # update_blood_pressure
                update_result = await update_tool.ainvoke({
                    "record_id": record_id,
                    "systolic": 125,
                    "diastolic": 85,
                    "notes": "更新后的备注"
                })
                
                assert "成功更新血压记录" in update_result
                assert "125" in update_result
                logger.info(f"✅ update_blood_pressure 测试成功")
                logger.info(f"   结果: {update_result[:100]}...")
            else:
                logger.warning("⚠️ 未找到测试记录，跳过更新测试")
        
        await pool.close()
        return True
    except Exception as e:
        logger.error(f"❌ update_blood_pressure 测试失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_info_tool():
    """测试 info 工具"""
    logger.info("\n" + "=" * 60)
    logger.info("测试4：info 工具")
    logger.info("=" * 60)
    
    try:
        pool = get_db_pool()
        await pool.create_pool()
        
        # 创建一些测试数据
        tools = create_blood_pressure_tools(pool.pool, TEST_USER_ID)
        record_tool = tools[0]
        
        for i in range(3):
            await record_tool.ainvoke({
                "systolic": 120 + i * 5,
                "diastolic": 80 + i * 2,
                "date_time": None
            })
        
        # 查询信息
        info_tool = tools[3]  # info
        result = await info_tool.ainvoke({})
        
        assert "血压信息统计" in result or "总记录数" in result
        logger.info(f"✅ info 工具测试成功")
        logger.info(f"   结果: {result[:300]}...")
        
        await pool.close()
        return True
    except Exception as e:
        logger.error(f"❌ info 工具测试失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def main():
    """主测试函数"""
    logger.info("\n" + "=" * 60)
    logger.info("血压记录工具单元测试（SQLAlchemy ORM）")
    logger.info("=" * 60 + "\n")
    
    results = []
    
    # 运行测试
    results.append(await test_record_blood_pressure())
    results.append(await test_query_blood_pressure())
    results.append(await test_update_blood_pressure())
    results.append(await test_info_tool())
    
    # 清理测试数据
    await cleanup_test_data()
    
    # 汇总结果
    logger.info("\n" + "=" * 60)
    logger.info("测试结果汇总")
    logger.info("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        logger.info(f"✅ 所有测试通过 ({passed}/{total})")
        return 0
    else:
        logger.error(f"❌ 部分测试失败 ({passed}/{total} 通过)")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

