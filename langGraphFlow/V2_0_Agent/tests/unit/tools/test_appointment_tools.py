"""
复诊管理工具单元测试（使用 SQLAlchemy ORM）
测试重构后的 appointment_tools 功能
"""
import asyncio
import sys
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

from core.database import get_db_pool
from domain.agents.appointment.tools import create_appointment_tools
from domain.models import get_async_session, Appointment
from langgraph.store.postgres import AsyncPostgresStore

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 测试用户ID
TEST_USER_ID = "test_user_appt_tools_001"


async def cleanup_test_data():
    """清理测试数据"""
    try:
        async_session_maker = get_async_session()
        async with async_session_maker() as session:
            from sqlalchemy import delete
            
            await session.execute(
                delete(Appointment).where(Appointment.user_id == TEST_USER_ID)
            )
            await session.commit()
            logger.info("✓ 测试数据清理完成")
    except Exception as e:
        logger.warning(f"清理测试数据时出现警告: {str(e)}")


async def test_appointment_booking():
    """测试 appointment_booking 工具"""
    logger.info("=" * 60)
    logger.info("测试1：appointment_booking 工具")
    logger.info("=" * 60)
    
    try:
        await cleanup_test_data()
        
        pool = get_db_pool()
        await pool.create_pool()
        
        # 创建工具
        tools = create_appointment_tools(pool.pool, TEST_USER_ID)
        booking_tool = tools[0]  # appointment_booking
        
        # 测试创建预约（使用未来时间）
        future_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        
        result = await booking_tool.ainvoke({
            "department": "心内科",
            "appointment_date": future_date,
            "doctor_name": "张医生",
            "notes": "测试预约"
        })
        
        assert "预约成功" in result or "预约编号" in result
        logger.info(f"✅ appointment_booking 测试成功")
        logger.info(f"   结果: {result[:100]}...")
        
        await pool.close()
        return True
    except Exception as e:
        logger.error(f"❌ appointment_booking 测试失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_query_appointment():
    """测试 query_appointment 工具"""
    logger.info("\n" + "=" * 60)
    logger.info("测试2：query_appointment 工具")
    logger.info("=" * 60)
    
    try:
        pool = get_db_pool()
        await pool.create_pool()
        
        # 先创建一些测试数据
        tools = create_appointment_tools(pool.pool, TEST_USER_ID)
        booking_tool = tools[0]
        
        future_date1 = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        future_date2 = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
        
        await booking_tool.ainvoke({
            "department": "心内科",
            "appointment_date": future_date1,
            "doctor_name": "张医生"
        })
        
        await booking_tool.ainvoke({
            "department": "神经科",
            "appointment_date": future_date2,
            "doctor_name": "李医生"
        })
        
        # 查询记录
        query_tool = tools[1]  # query_appointment
        result = await query_tool.ainvoke({
            "status": None,
            "start_date": None,
            "end_date": None,
            "limit": 10
        })
        
        assert "找到" in result or "条预约记录" in result
        logger.info(f"✅ query_appointment 测试成功")
        logger.info(f"   结果: {result[:200]}...")
        
        await pool.close()
        return True
    except Exception as e:
        logger.error(f"❌ query_appointment 测试失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_update_appointment():
    """测试 update_appointment 工具"""
    logger.info("\n" + "=" * 60)
    logger.info("测试3：update_appointment 工具")
    logger.info("=" * 60)
    
    try:
        pool = get_db_pool()
        await pool.create_pool()
        
        # 先创建一条记录
        tools = create_appointment_tools(pool.pool, TEST_USER_ID)
        booking_tool = tools[0]
        
        future_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        await booking_tool.ainvoke({
            "department": "心内科",
            "appointment_date": future_date,
            "doctor_name": "张医生",
            "status": "pending"
        })
        
        # 获取记录ID
        async_session_maker = get_async_session()
        async with async_session_maker() as session:
            from sqlalchemy import select
            query = select(Appointment).where(
                Appointment.user_id == TEST_USER_ID
            ).order_by(Appointment.id.desc()).limit(1)
            result_query = await session.execute(query)
            appointment = result_query.scalar_one_or_none()
            
            if appointment:
                appointment_id = str(appointment.id)
                
                # 更新记录
                update_tool = tools[2]  # update_appointment
                update_result = await update_tool.ainvoke({
                    "appointment_id": appointment_id,
                    "status": "completed",
                    "notes": "已完成"
                })
                
                assert "成功更新预约记录" in update_result
                logger.info(f"✅ update_appointment 测试成功")
                logger.info(f"   结果: {update_result[:100]}...")
            else:
                logger.warning("⚠️ 未找到测试记录，跳过更新测试")
        
        await pool.close()
        return True
    except Exception as e:
        logger.error(f"❌ update_appointment 测试失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def main():
    """主测试函数"""
    logger.info("\n" + "=" * 60)
    logger.info("复诊管理工具单元测试（SQLAlchemy ORM）")
    logger.info("=" * 60 + "\n")
    
    results = []
    
    # 运行测试
    results.append(await test_appointment_booking())
    results.append(await test_query_appointment())
    results.append(await test_update_appointment())
    
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

