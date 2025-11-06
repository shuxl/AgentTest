"""
端到端功能测试
测试完整的业务流程，验证 SQLAlchemy ORM 重构后的系统功能完整性
"""
import asyncio
import sys
import os
import logging
from datetime import datetime, timedelta

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from utils.config import Config
from utils.database import get_db_pool
from utils.db import get_async_session, BloodPressureRecord, Appointment, CRUDBase
from utils.logging_config import setup_logging
from sqlalchemy import select, delete

# 设置统一的日志配置
setup_logging()

logger = logging.getLogger(__name__)

# 测试用户ID
TEST_USER_ID = "test_user_e2e_001"


async def cleanup_test_data():
    """清理测试数据"""
    try:
        async_session_maker = get_async_session()
        async with async_session_maker() as session:
            # 清理血压记录
            await session.execute(
                delete(BloodPressureRecord).where(
                    BloodPressureRecord.user_id == TEST_USER_ID
                )
            )
            # 清理预约记录
            await session.execute(
                delete(Appointment).where(
                    Appointment.user_id == TEST_USER_ID
                )
            )
            await session.commit()
        logger.info("✓ 测试数据清理完成")
    except Exception as e:
        logger.warning(f"清理测试数据时出现警告: {str(e)}")


async def test_blood_pressure_e2e():
    """测试血压记录端到端流程"""
    logger.info("=" * 60)
    logger.info("测试1：血压记录端到端流程")
    logger.info("=" * 60)
    
    try:
        from utils.tools.blood_pressure_tools import create_blood_pressure_tools
        
        db_pool = get_db_pool()
        await db_pool.create_pool()
        
        # 创建工具
        tools = create_blood_pressure_tools(db_pool.pool, TEST_USER_ID)
        record_tool = tools[0]
        query_tool = tools[1]
        update_tool = tools[2]
        
        # 1. 记录血压
        result1 = await record_tool.ainvoke({
            "systolic": 120,
            "diastolic": 80,
            "date_time": None
        })
        assert "成功" in result1
        logger.info(f"✅ 记录血压成功: {result1[:50]}...")
        
        # 2. 查询血压记录
        result2 = await query_tool.ainvoke({
            "start_date": None,
            "end_date": None,
            "limit": 10
        })
        assert "记录" in result2 or len(result2) > 0
        logger.info(f"✅ 查询血压记录成功: {result2[:50]}...")
        
        # 3. 验证数据库中的数据
        async_session_maker = get_async_session()
        async with async_session_maker() as session:
            query = select(BloodPressureRecord).where(
                BloodPressureRecord.user_id == TEST_USER_ID
            )
            result = await session.execute(query)
            records = result.scalars().all()
            assert len(records) > 0
            logger.info(f"✅ 数据库验证成功: {len(records)} 条记录")
        
        await db_pool.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ 血压记录端到端测试失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_appointment_e2e():
    """测试复诊管理端到端流程"""
    logger.info("\n" + "=" * 60)
    logger.info("测试2：复诊管理端到端流程")
    logger.info("=" * 60)
    
    try:
        from utils.tools.appointment_tools import create_appointment_tools
        
        db_pool = get_db_pool()
        await db_pool.create_pool()
        
        # 创建工具
        tools = create_appointment_tools(db_pool.pool, TEST_USER_ID)
        booking_tool = tools[0]
        query_tool = tools[1]
        update_tool = tools[2]
        
        # 1. 创建预约
        future_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        result1 = await booking_tool.ainvoke({
            "department": "心内科",
            "appointment_date": future_date,
            "doctor_id": None,
            "doctor_name": None,
            "notes": None
        })
        assert "成功" in result1
        logger.info(f"✅ 创建预约成功: {result1[:50]}...")
        
        # 2. 查询预约
        result2 = await query_tool.ainvoke({
            "status": None,
            "start_date": None,
            "end_date": None,
            "limit": 10
        })
        assert "预约" in result2 or len(result2) > 0
        logger.info(f"✅ 查询预约成功: {result2[:50]}...")
        
        # 3. 验证数据库中的数据
        async_session_maker = get_async_session()
        async with async_session_maker() as session:
            query = select(Appointment).where(
                Appointment.user_id == TEST_USER_ID
            )
            result = await session.execute(query)
            appointments = result.scalars().all()
            assert len(appointments) > 0
            logger.info(f"✅ 数据库验证成功: {len(appointments)} 条记录")
        
        await db_pool.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ 复诊管理端到端测试失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_concurrent_operations():
    """测试并发操作"""
    logger.info("\n" + "=" * 60)
    logger.info("测试3：并发操作测试")
    logger.info("=" * 60)
    
    try:
        from utils.tools.blood_pressure_tools import create_blood_pressure_tools
        
        db_pool = get_db_pool()
        await db_pool.create_pool()
        
        tools = create_blood_pressure_tools(db_pool.pool, TEST_USER_ID)
        record_tool = tools[0]
        
        # 并发创建多条记录
        tasks = []
        for i in range(10):
            task = record_tool.ainvoke({
                "systolic": 120 + i,
                "diastolic": 80 + i,
                "date_time": None
            })
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = sum(1 for r in results if isinstance(r, str) and "成功" in r)
        assert success_count == 10
        logger.info(f"✅ 并发操作测试成功: {success_count}/10 条记录创建成功")
        
        await db_pool.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ 并发操作测试失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def main():
    """主测试函数"""
    logger.info("\n" + "=" * 60)
    logger.info("端到端功能测试")
    logger.info("=" * 60 + "\n")
    
    # 清理测试数据
    await cleanup_test_data()
    
    results = []
    
    # 运行测试
    results.append(await test_blood_pressure_e2e())
    results.append(await test_appointment_e2e())
    results.append(await test_concurrent_operations())
    
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

