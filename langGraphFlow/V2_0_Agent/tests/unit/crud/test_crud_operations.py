"""
CRUD 操作单元测试
测试 CRUDBase 和 QueryBuilder 的功能
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

from domain.models import get_async_session, BloodPressureRecord, Appointment, CRUDBase, QueryBuilder

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 测试用户ID
TEST_USER_ID = "test_user_crud_001"


async def cleanup_test_data():
    """清理测试数据"""
    try:
        async_session_maker = get_async_session()
        async with async_session_maker() as session:
            from sqlalchemy import delete
            
            # 清理血压记录
            await session.execute(
                delete(BloodPressureRecord).where(BloodPressureRecord.user_id == TEST_USER_ID)
            )
            
            # 清理预约记录
            await session.execute(
                delete(Appointment).where(Appointment.user_id == TEST_USER_ID)
            )
            
            await session.commit()
            logger.info("✓ 测试数据清理完成")
    except Exception as e:
        logger.warning(f"清理测试数据时出现警告: {str(e)}")


async def test_crud_create():
    """测试 CRUD create 操作"""
    logger.info("=" * 60)
    logger.info("测试1：CRUD create 操作")
    logger.info("=" * 60)
    
    try:
        await cleanup_test_data()
        
        crud = CRUDBase(BloodPressureRecord)
        async_session_maker = get_async_session()
        
        async with async_session_maker() as session:
            # 创建记录
            db_obj = await crud.create(
                session,
                {
                    "user_id": TEST_USER_ID,
                    "systolic": 120,
                    "diastolic": 80,
                    "measurement_time": datetime.now(),
                    "notes": "测试记录"
                }
            )
            await session.commit()
            
            assert db_obj.id is not None
            assert db_obj.user_id == TEST_USER_ID
            assert db_obj.systolic == 120
            assert db_obj.diastolic == 80
            logger.info(f"✅ create 操作成功: ID={db_obj.id}")
            
            return True
    except Exception as e:
        logger.error(f"❌ create 操作测试失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_crud_get():
    """测试 CRUD get 操作"""
    logger.info("\n" + "=" * 60)
    logger.info("测试2：CRUD get 操作")
    logger.info("=" * 60)
    
    try:
        crud = CRUDBase(BloodPressureRecord)
        async_session_maker = get_async_session()
        
        async with async_session_maker() as session:
            # 先创建一个记录
            db_obj = await crud.create(
                session,
                {
                    "user_id": TEST_USER_ID,
                    "systolic": 130,
                    "diastolic": 85,
                    "measurement_time": datetime.now()
                }
            )
            await session.commit()
            record_id = db_obj.id
            
            # 根据 ID 查询
            found_obj = await crud.get(session, id=record_id)
            assert found_obj is not None
            assert found_obj.id == record_id
            assert found_obj.systolic == 130
            logger.info(f"✅ get 操作成功（按ID）: ID={found_obj.id}")
            
            # 根据过滤条件查询
            found_obj2 = await crud.get(session, user_id=TEST_USER_ID, systolic=130)
            assert found_obj2 is not None
            assert found_obj2.systolic == 130
            logger.info(f"✅ get 操作成功（按过滤条件）: ID={found_obj2.id}")
            
            return True
    except Exception as e:
        logger.error(f"❌ get 操作测试失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_crud_get_multi():
    """测试 CRUD get_multi 操作"""
    logger.info("\n" + "=" * 60)
    logger.info("测试3：CRUD get_multi 操作")
    logger.info("=" * 60)
    
    try:
        crud = CRUDBase(BloodPressureRecord)
        async_session_maker = get_async_session()
        
        async with async_session_maker() as session:
            # 创建多条记录
            for i in range(5):
                await crud.create(
                    session,
                    {
                        "user_id": TEST_USER_ID,
                        "systolic": 120 + i,
                        "diastolic": 80 + i,
                        "measurement_time": datetime.now()
                    }
                )
            await session.commit()
            
            # 查询多条记录
            records = await crud.get_multi(
                session,
                user_id=TEST_USER_ID,
                limit=10,
                order_by="measurement_time",
                order_desc=True
            )
            
            assert len(records) >= 5
            logger.info(f"✅ get_multi 操作成功: 找到 {len(records)} 条记录")
            
            # 测试分页
            records_page1 = await crud.get_multi(
                session,
                user_id=TEST_USER_ID,
                skip=0,
                limit=2
            )
            assert len(records_page1) <= 2
            logger.info(f"✅ 分页功能正常: 第1页 {len(records_page1)} 条记录")
            
            return True
    except Exception as e:
        logger.error(f"❌ get_multi 操作测试失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_crud_update():
    """测试 CRUD update 操作"""
    logger.info("\n" + "=" * 60)
    logger.info("测试4：CRUD update 操作")
    logger.info("=" * 60)
    
    try:
        crud = CRUDBase(BloodPressureRecord)
        async_session_maker = get_async_session()
        
        async with async_session_maker() as session:
            # 创建记录
            db_obj = await crud.create(
                session,
                {
                    "user_id": TEST_USER_ID,
                    "systolic": 120,
                    "diastolic": 80,
                    "measurement_time": datetime.now(),
                    "notes": "原始备注"
                }
            )
            await session.commit()
            record_id = db_obj.id
            
            # 更新记录
            updated_obj = await crud.update(
                session,
                db_obj,
                {
                    "systolic": 125,
                    "notes": "更新后的备注"
                }
            )
            await session.commit()
            
            assert updated_obj.systolic == 125
            assert updated_obj.notes == "更新后的备注"
            assert updated_obj.diastolic == 80  # 未更新的字段保持不变
            logger.info(f"✅ update 操作成功: ID={updated_obj.id}, systolic={updated_obj.systolic}")
            
            return True
    except Exception as e:
        logger.error(f"❌ update 操作测试失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_crud_delete():
    """测试 CRUD delete 操作"""
    logger.info("\n" + "=" * 60)
    logger.info("测试5：CRUD delete 操作")
    logger.info("=" * 60)
    
    try:
        crud = CRUDBase(BloodPressureRecord)
        async_session_maker = get_async_session()
        
        async with async_session_maker() as session:
            # 创建记录
            db_obj = await crud.create(
                session,
                {
                    "user_id": TEST_USER_ID,
                    "systolic": 120,
                    "diastolic": 80,
                    "measurement_time": datetime.now()
                }
            )
            await session.commit()
            record_id = db_obj.id
            
            # 删除记录
            deleted = await crud.delete(session, id=record_id)
            await session.commit()
            
            assert deleted is True
            
            # 验证记录已删除
            found_obj = await crud.get(session, id=record_id)
            assert found_obj is None
            logger.info(f"✅ delete 操作成功: ID={record_id} 已删除")
            
            return True
    except Exception as e:
        logger.error(f"❌ delete 操作测试失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_crud_count():
    """测试 CRUD count 操作"""
    logger.info("\n" + "=" * 60)
    logger.info("测试6：CRUD count 操作")
    logger.info("=" * 60)
    
    try:
        crud = CRUDBase(BloodPressureRecord)
        async_session_maker = get_async_session()
        
        async with async_session_maker() as session:
            # 创建多条记录
            for i in range(3):
                await crud.create(
                    session,
                    {
                        "user_id": TEST_USER_ID,
                        "systolic": 120 + i,
                        "diastolic": 80 + i,
                        "measurement_time": datetime.now()
                    }
                )
            await session.commit()
            
            # 统计记录数
            count = await crud.count(session, user_id=TEST_USER_ID)
            assert count >= 3
            logger.info(f"✅ count 操作成功: 找到 {count} 条记录")
            
            return True
    except Exception as e:
        logger.error(f"❌ count 操作测试失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_query_builder():
    """测试 QueryBuilder"""
    logger.info("\n" + "=" * 60)
    logger.info("测试7：QueryBuilder 查询构建器")
    logger.info("=" * 60)
    
    try:
        async_session_maker = get_async_session()
        
        async with async_session_maker() as session:
            # 创建测试数据
            crud = CRUDBase(BloodPressureRecord)
            for i in range(5):
                await crud.create(
                    session,
                    {
                        "user_id": TEST_USER_ID,
                        "systolic": 120 + i * 5,
                        "diastolic": 80 + i * 2,
                        "measurement_time": datetime.now()
                    }
                )
            await session.commit()
            
            # 使用 QueryBuilder 构建查询
            builder = QueryBuilder(BloodPressureRecord)
            query = (
                builder
                .filter(user_id=TEST_USER_ID)
                .filter(systolic__gte=125)
                .order_by("measurement_time", desc=True)
                .limit(3)
                .build()
            )
            
            result = await session.execute(query)
            rows = result.scalars().all()
            
            assert len(rows) <= 3
            assert all(row.systolic >= 125 for row in rows)
            logger.info(f"✅ QueryBuilder 测试成功: 找到 {len(rows)} 条记录")
            
            return True
    except Exception as e:
        logger.error(f"❌ QueryBuilder 测试失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def main():
    """主测试函数"""
    logger.info("\n" + "=" * 60)
    logger.info("CRUD 操作单元测试")
    logger.info("=" * 60 + "\n")
    
    results = []
    
    # 运行测试
    results.append(await test_crud_create())
    results.append(await test_crud_get())
    results.append(await test_crud_get_multi())
    results.append(await test_crud_update())
    results.append(await test_crud_delete())
    results.append(await test_crud_count())
    results.append(await test_query_builder())
    
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

