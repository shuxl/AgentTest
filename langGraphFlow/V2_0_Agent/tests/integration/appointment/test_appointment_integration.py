"""
复诊管理智能体集成测试
验证复诊管理流程（预约 -> 查询 -> 更新）
包括相对时间解析功能测试
"""
import asyncio
import sys
import os
import logging
import time
from langchain_core.messages import HumanMessage

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

from core.database import get_db_pool
from domain.router import create_router_agent
from core.logging import setup_logging
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.postgres import AsyncPostgresStore

# 设置统一的日志配置
setup_logging()

logger = logging.getLogger(__name__)


async def cleanup_test_data(pool, checkpointer, store, user_id: str, session_id: str):
    """
    清理测试数据
    
    Args:
        pool: 数据库连接池
        checkpointer: AsyncPostgresSaver实例
        store: AsyncPostgresStore实例
        user_id: 测试用户ID
        session_id: 测试会话ID（对应checkpoint的thread_id）
    """
    try:
        print("正在清理测试数据...")
        
        # 1. 清理appointments表中的测试数据
        try:
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("""
                        DELETE FROM appointments 
                        WHERE user_id = %s
                    """, (user_id,))
                    deleted_records = cur.rowcount
                    print(f"✓ 清理appointments表: 删除 {deleted_records} 条记录")
        except Exception as e:
            print(f"⚠ 清理appointments表时出现警告: {str(e)}")
        
        # 2. 清理checkpoint数据（checkpoints表）
        # checkpoint通过thread_id（对应session_id）标识
        try:
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    # 先删除checkpoint_blobs表中的记录（使用thread_id和checkpoint_ns）
                    deleted_blobs = 0
                    try:
                        await cur.execute("""
                            DELETE FROM checkpoint_blobs 
                            WHERE thread_id = %s
                        """, (session_id,))
                        deleted_blobs = cur.rowcount
                    except Exception as e:
                        # checkpoint_blobs表结构可能不同，忽略错误
                        logger.debug(f"清理checkpoint_blobs时出现警告: {str(e)}")
                    
                    # 删除checkpoint_writes表中的记录
                    await cur.execute("""
                        DELETE FROM checkpoint_writes 
                        WHERE thread_id = %s
                    """, (session_id,))
                    deleted_writes = cur.rowcount
                    
                    # 最后删除checkpoints表中的记录
                    await cur.execute("""
                        DELETE FROM checkpoints 
                        WHERE thread_id = %s
                    """, (session_id,))
                    deleted_checkpoints = cur.rowcount
                    
                    print(f"✓ 清理checkpoint数据: checkpoints={deleted_checkpoints}, writes={deleted_writes}, blobs={deleted_blobs}")
        except Exception as e:
            # checkpoint表可能不存在（如果checkpointer未初始化），这是正常的
            print(f"⚠ 清理checkpoint数据时出现警告（可能表不存在）: {str(e)}")
        
        # 3. 清理store数据（长期记忆）
        if store:
            try:
                # 清理memories命名空间（用户设置信息）
                namespace_memories = ("memories", user_id)
                memories_data = await store.asearch(namespace_memories, query="")
                if memories_data:
                    for memory in memories_data:
                        await store.adelete(namespace_memories, memory.key)
                    print(f"✓ 清理store数据（memories命名空间）: {len(memories_data)} 条记录")
            except Exception as e:
                print(f"⚠ 清理store数据时出现警告: {str(e)}")
        
        print("✓ 测试数据清理完成")
        
    except Exception as e:
        print(f"⚠ 清理测试数据时出现错误: {str(e)}")
        import traceback
        traceback.print_exc()


async def ensure_appointment_table_exists(pool):
    """
    确保appointments表存在
    如果表不存在，则创建表结构
    """
    try:
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                # 检查表是否存在
                await cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'appointments'
                    )
                """)
                table_exists = await cur.fetchone()
                
                if not table_exists or not table_exists.get('exists'):
                    # 表不存在，创建表
                    print("正在创建appointments表...")
                    await cur.execute("""
                        CREATE TABLE IF NOT EXISTS appointments (
                            id SERIAL PRIMARY KEY,
                            user_id VARCHAR(255) NOT NULL,
                            department VARCHAR(255) NOT NULL,
                            doctor_id VARCHAR(255),
                            doctor_name VARCHAR(255),
                            appointment_date TIMESTAMP NOT NULL,
                            status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'cancelled')),
                            notes TEXT,
                            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    print("✓ 表创建成功")
                    
                    # 创建索引（如果不存在）
                    indexes = [
                        "CREATE INDEX IF NOT EXISTS idx_appointments_user_id ON appointments(user_id)",
                        "CREATE INDEX IF NOT EXISTS idx_appointments_appointment_date ON appointments(appointment_date)",
                        "CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status)",
                        "CREATE INDEX IF NOT EXISTS idx_appointments_user_status ON appointments(user_id, status)"
                    ]
                    for index_sql in indexes:
                        try:
                            await cur.execute(index_sql)
                        except Exception as e:
                            print(f"⚠ 索引创建警告: {str(e)}")
                else:
                    print("✓ 表结构验证通过")
                
    except Exception as e:
        print(f"⚠ 表结构检查/创建失败: {str(e)}")
        import traceback
        traceback.print_exc()


async def query_appointments_from_db(pool, user_id: str, status: str = None):
    """
    从数据库查询预约记录（用于测试验证）
    
    Args:
        pool: 数据库连接池
        user_id: 用户ID
        status: 预约状态（可选），用于过滤
    
    Returns:
        list: 预约记录列表，每个记录是字典格式
    """
    try:
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                if status:
                    await cur.execute("""
                        SELECT id, department, doctor_id, doctor_name, appointment_date, status, notes, created_at
                        FROM appointments
                        WHERE user_id = %s AND status = %s
                        ORDER BY created_at DESC
                    """, (user_id, status))
                else:
                    await cur.execute("""
                        SELECT id, department, doctor_id, doctor_name, appointment_date, status, notes, created_at
                        FROM appointments
                        WHERE user_id = %s
                        ORDER BY created_at DESC
                    """, (user_id,))
                rows = await cur.fetchall()
                return rows
    except Exception as e:
        logger.error(f"查询数据库预约记录失败: {str(e)}")
        return []


async def test_appointment_workflow():
    """
    测试复诊管理完整流程：
    1. 创建预约（标准格式）
    2. 创建预约（相对时间格式）
    3. 查询预约记录
    4. 更新预约记录
    5. 查询更新后的预约记录
    """
    print("=" * 60)
    print("复诊管理智能体集成测试")
    print("=" * 60)
    
    # 初始化数据库连接池
    db_pool = get_db_pool()
    await db_pool.create_pool()
    
    # 确保表结构正确
    await ensure_appointment_table_exists(db_pool.pool)
    
    # 初始化checkpointer和store
    checkpointer = AsyncPostgresSaver(db_pool.pool)
    await checkpointer.setup()
    
    store = AsyncPostgresStore(db_pool.pool)
    await store.setup()
    
    # 创建路由智能体（需要传递pool）
    router_agent = await create_router_agent(checkpointer=checkpointer, pool=db_pool.pool, store=store)
    
    # 测试用户ID和会话ID（添加时间戳后缀以保留测试数据）
    timestamp = int(time.time())
    user_id = f"test_user_appt_{timestamp}"
    session_id = f"test_session_appt_{timestamp}"
    print(f"测试用户ID: {user_id}")
    print(f"测试会话ID: {session_id}")
    
    # 测试开始前清理旧数据（确保测试环境干净）
    print("\n[清理] 测试前清理旧数据")
    print("-" * 60)
    await cleanup_test_data(db_pool.pool, checkpointer, store, user_id, session_id)
    
    config = {"configurable": {"thread_id": session_id, "recursion_limit": 50}}
    
    print("\n[测试1] 创建预约（标准格式）")
    print("-" * 60)
    
    # 记录测试前的预约数量
    appointments_before = await query_appointments_from_db(db_pool.pool, user_id)
    count_before = len(appointments_before)
    print(f"测试前预约记录数: {count_before}")
    
    # 测试1: 创建预约（标准格式）
    # 第一轮：发起预约请求
    state_input_1 = {
        "messages": [HumanMessage(content="我想预约复诊，科室是心内科，时间是明天下午2点，不需要指定医生")],
        "user_id": user_id,
        "session_id": session_id,
        "current_intent": None,
        "current_agent": None,
        "need_reroute": False
    }
    
    test1_passed = False
    try:
        result_1 = await router_agent.ainvoke(state_input_1, config=config)
        messages_1 = result_1.get("messages", [])
        if messages_1:
            last_msg = messages_1[-1]
            if hasattr(last_msg, 'content'):
                print(f"回复: {last_msg.content}")
            else:
                print(f"回复: {str(last_msg)}")
        print(f"当前意图: {result_1.get('current_intent')}")
        print(f"当前智能体: {result_1.get('current_agent')}")
        
        # 检查是否需要继续对话（如果模型询问医生信息）
        if messages_1:
            last_msg = messages_1[-1]
            if hasattr(last_msg, 'content'):
                content = last_msg.content
                # 如果模型询问医生信息，继续对话确认不需要指定医生
                if "医生" in content and ("指定" in content or "哪位" in content or "姓名" in content or "安排" in content):
                    print("\n[继续对话] 模型询问医生信息，回复不需要指定医生")
                    state_input_1_continue = {
                        "messages": result_1.get("messages", []) + [HumanMessage(content="不需要指定医生，直接创建预约即可")],
                        "user_id": user_id,
                        "session_id": session_id,
                        "current_intent": result_1.get("current_intent"),
                        "current_agent": result_1.get("current_agent"),
                        "need_reroute": False
                    }
                    result_1 = await router_agent.ainvoke(state_input_1_continue, config=config)
                    messages_1 = result_1.get("messages", [])
                    if messages_1:
                        last_msg = messages_1[-1]
                        if hasattr(last_msg, 'content'):
                            print(f"回复: {last_msg.content}")
        
        # 验证数据库中的记录
        appointments_after = await query_appointments_from_db(db_pool.pool, user_id)
        count_after = len(appointments_after)
        print(f"\n[数据库验证] 测试后预约记录数: {count_after}")
        
        if count_after > count_before:
            print(f"✓ 数据库验证通过：成功创建了 {count_after - count_before} 条预约记录")
            # 显示最新创建的记录
            latest = appointments_after[0]
            print(f"  最新记录: ID={latest['id']}, 科室={latest['department']}, "
                  f"时间={latest['appointment_date']}, 状态={latest['status']}")
            test1_passed = True
        else:
            print(f"✗ 数据库验证失败：预约记录数量未增加（测试前: {count_before}, 测试后: {count_after}）")
        
        if test1_passed:
            print("✓ 测试1通过：创建预约")
        else:
            print("✗ 测试1失败：数据库验证未通过")
    except Exception as e:
        print(f"✗ 测试1失败：{str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n[测试2] 查询预约记录")
    print("-" * 60)
    
    # 测试2: 查询预约记录
    state_input_2 = {
        "messages": [HumanMessage(content="查询我的预约记录")],
        "user_id": user_id,
        "session_id": session_id,
        "current_intent": None,
        "current_agent": None,
        "need_reroute": False
    }
    
    test2_passed = False
    try:
        # 先查询数据库中的实际记录
        db_appointments = await query_appointments_from_db(db_pool.pool, user_id)
        db_count = len(db_appointments)
        print(f"[数据库验证] 数据库中实际有 {db_count} 条预约记录")
        
        result_2 = await router_agent.ainvoke(state_input_2, config=config)
        messages_2 = result_2.get("messages", [])
        if messages_2:
            last_msg = messages_2[-1]
            if hasattr(last_msg, 'content'):
                print(f"回复: {last_msg.content}")
            else:
                print(f"回复: {str(last_msg)}")
        print(f"当前意图: {result_2.get('current_intent')}")
        print(f"当前智能体: {result_2.get('current_agent')}")
        
        # 验证数据库记录与模型返回的一致性
        if db_count > 0:
            # 检查模型回复中是否包含预约信息
            if messages_2:
                last_msg = messages_2[-1]
                if hasattr(last_msg, 'content'):
                    content = last_msg.content
                    # 检查是否提到了预约记录
                    if "预约" in content or "appointment" in content.lower() or str(db_appointments[0]['id']) in content:
                        print(f"✓ 模型返回包含预约信息")
                        test2_passed = True
                    else:
                        print(f"⚠ 模型返回可能未包含预约信息")
            
            # 显示数据库中的实际记录
            print(f"\n[数据库验证] 数据库中的预约记录：")
            for idx, apt in enumerate(db_appointments[:5], 1):  # 最多显示5条
                print(f"  {idx}. ID={apt['id']}, 科室={apt['department']}, "
                      f"时间={apt['appointment_date']}, 状态={apt['status']}")
            
            if test2_passed:
                print("✓ 测试2通过：查询预约记录")
            else:
                print("⚠ 测试2部分通过：数据库有记录，但模型返回可能不完整")
        else:
            print("✗ 测试2失败：数据库中无预约记录，无法进行查询测试")
            
    except Exception as e:
        print(f"✗ 测试2失败：{str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n[测试3] 创建预约（相对时间格式 - 下周一）")
    print("-" * 60)
    
    # 记录测试前的预约数量
    appointments_before_3 = await query_appointments_from_db(db_pool.pool, user_id)
    count_before_3 = len(appointments_before_3)
    print(f"测试前预约记录数: {count_before_3}")
    
    # 测试3: 创建预约（相对时间格式）- 使用"下周一"确保是未来时间
    # 第一轮：发起预约请求
    state_input_3 = {
        "messages": [HumanMessage(content="预约复诊，科室是骨科，时间是下周一上午10点，不需要指定医生")],
        "user_id": user_id,
        "session_id": session_id,
        "current_intent": None,
        "current_agent": None,
        "need_reroute": False
    }
    
    test3_passed = False
    try:
        result_3 = await router_agent.ainvoke(state_input_3, config=config)
        messages_3 = result_3.get("messages", [])
        if messages_3:
            last_msg = messages_3[-1]
            if hasattr(last_msg, 'content'):
                print(f"回复: {last_msg.content}")
            else:
                print(f"回复: {str(last_msg)}")
        print(f"当前意图: {result_3.get('current_intent')}")
        print(f"当前智能体: {result_3.get('current_agent')}")
        
        # 检查是否需要继续对话（如果模型询问医生信息）
        if messages_3:
            last_msg = messages_3[-1]
            if hasattr(last_msg, 'content'):
                content = last_msg.content
                # 如果模型询问医生信息，继续对话确认不需要指定医生
                if "医生" in content and ("指定" in content or "哪位" in content or "姓名" in content or "安排" in content):
                    print("\n[继续对话] 模型询问医生信息，回复不需要指定医生")
                    state_input_3_continue = {
                        "messages": result_3.get("messages", []) + [HumanMessage(content="不需要指定医生，直接创建预约即可")],
                        "user_id": user_id,
                        "session_id": session_id,
                        "current_intent": result_3.get("current_intent"),
                        "current_agent": result_3.get("current_agent"),
                        "need_reroute": False
                    }
                    result_3 = await router_agent.ainvoke(state_input_3_continue, config=config)
                    messages_3 = result_3.get("messages", [])
                    if messages_3:
                        last_msg = messages_3[-1]
                        if hasattr(last_msg, 'content'):
                            print(f"回复: {last_msg.content}")
        
        # 验证数据库中的记录
        appointments_after_3 = await query_appointments_from_db(db_pool.pool, user_id)
        count_after_3 = len(appointments_after_3)
        print(f"\n[数据库验证] 测试后预约记录数: {count_after_3}")
        
        if count_after_3 > count_before_3:
            print(f"✓ 数据库验证通过：成功创建了 {count_after_3 - count_before_3} 条预约记录")
            # 查找新创建的骨科预约
            new_appointments = appointments_after_3[:count_after_3 - count_before_3]
            for apt in new_appointments:
                if apt['department'] == '骨科':
                    print(f"  新记录: ID={apt['id']}, 科室={apt['department']}, "
                          f"时间={apt['appointment_date']}, 状态={apt['status']}")
                    test3_passed = True
                    break
            if not test3_passed:
                print(f"⚠ 创建了预约记录，但未找到骨科预约")
        else:
            print(f"✗ 数据库验证失败：预约记录数量未增加（测试前: {count_before_3}, 测试后: {count_after_3}）")
        
        if test3_passed:
            print("✓ 测试3通过：创建预约（相对时间格式）")
        else:
            print("✗ 测试3失败：数据库验证未通过")
    except Exception as e:
        print(f"✗ 测试3失败：{str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n[测试4] 查询所有预约记录")
    print("-" * 60)
    
    # 测试4: 查询所有预约记录
    state_input_4 = {
        "messages": [HumanMessage(content="查询我的所有预约")],
        "user_id": user_id,
        "session_id": session_id,
        "current_intent": None,
        "current_agent": None,
        "need_reroute": False
    }
    
    test4_passed = False
    try:
        # 先查询数据库中的实际记录
        db_appointments_4 = await query_appointments_from_db(db_pool.pool, user_id)
        db_count_4 = len(db_appointments_4)
        print(f"[数据库验证] 数据库中实际有 {db_count_4} 条预约记录")
        
        result_4 = await router_agent.ainvoke(state_input_4, config=config)
        messages_4 = result_4.get("messages", [])
        if messages_4:
            last_msg = messages_4[-1]
            if hasattr(last_msg, 'content'):
                print(f"回复: {last_msg.content}")
            else:
                print(f"回复: {str(last_msg)}")
        print(f"当前意图: {result_4.get('current_intent')}")
        print(f"当前智能体: {result_4.get('current_agent')}")
        
        # 验证数据库记录
        if db_count_4 > 0:
            # 检查模型回复中是否包含所有预约信息
            if messages_4:
                last_msg = messages_4[-1]
                if hasattr(last_msg, 'content'):
                    content = last_msg.content
                    # 检查是否提到了预约记录数量或具体预约信息
                    found_ids = []
                    for apt in db_appointments_4:
                        if str(apt['id']) in content:
                            found_ids.append(apt['id'])
                    
                    if len(found_ids) > 0 or "预约" in content or str(db_count_4) in content:
                        print(f"✓ 模型返回包含预约信息（找到 {len(found_ids)}/{db_count_4} 个预约ID）")
                        test4_passed = True
                    else:
                        print(f"⚠ 模型返回可能未包含预约信息")
            
            # 显示数据库中的实际记录
            print(f"\n[数据库验证] 数据库中的所有预约记录：")
            for idx, apt in enumerate(db_appointments_4, 1):
                print(f"  {idx}. ID={apt['id']}, 科室={apt['department']}, "
                      f"时间={apt['appointment_date']}, 状态={apt['status']}")
            
            if test4_passed:
                print("✓ 测试4通过：查询所有预约记录")
            else:
                print("⚠ 测试4部分通过：数据库有记录，但模型返回可能不完整")
        else:
            print("✗ 测试4失败：数据库中无预约记录，无法进行查询测试")
            
    except Exception as e:
        print(f"✗ 测试4失败：{str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n[测试5] 更新预约状态")
    print("-" * 60)
    
    # 先查询数据库，获取第一个待处理的预约ID
    db_appointments_before_update = await query_appointments_from_db(db_pool.pool, user_id, status='pending')
    test5_passed = False
    if not db_appointments_before_update:
        print("⚠ 警告：数据库中没有待处理的预约记录，跳过更新测试")
        print("✗ 测试5失败：没有可更新的预约记录")
    else:
        target_appointment = db_appointments_before_update[0]  # 取第一个待处理的预约
        target_id = target_appointment['id']
        target_status_before = target_appointment['status']
        print(f"[数据库验证] 准备更新预约 ID={target_id}，当前状态={target_status_before}")
        
        # 测试5: 更新预约状态
        state_input_5 = {
            "messages": [HumanMessage(content=f"将我的预约编号{target_id}的状态更新为已完成")],
            "user_id": user_id,
            "session_id": session_id,
            "current_intent": None,
            "current_agent": None,
            "need_reroute": False
        }
        
        try:
            result_5 = await router_agent.ainvoke(state_input_5, config=config)
            messages_5 = result_5.get("messages", [])
            if messages_5:
                last_msg = messages_5[-1]
                if hasattr(last_msg, 'content'):
                    print(f"回复: {last_msg.content}")
                else:
                    print(f"回复: {str(last_msg)}")
            print(f"当前意图: {result_5.get('current_intent')}")
            print(f"当前智能体: {result_5.get('current_agent')}")
            
            # 验证数据库中的状态是否已更新
            async with db_pool.pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("""
                        SELECT id, status FROM appointments 
                        WHERE id = %s AND user_id = %s
                    """, (target_id, user_id))
                    updated_row = await cur.fetchone()
                    
                    if updated_row:
                        new_status = updated_row['status']
                        print(f"\n[数据库验证] 更新后的状态: {new_status}")
                        
                        if new_status == 'completed' and new_status != target_status_before:
                            print(f"✓ 数据库验证通过：预约状态已从 '{target_status_before}' 更新为 '{new_status}'")
                            test5_passed = True
                        elif new_status == target_status_before:
                            print(f"⚠ 数据库验证：状态未改变（仍为 '{new_status}'）")
                        else:
                            print(f"⚠ 数据库验证：状态已更新，但不是预期的 'completed'（当前: '{new_status}'）")
                    else:
                        print(f"✗ 数据库验证失败：无法找到ID为 {target_id} 的预约记录")
            
            if test5_passed:
                print("✓ 测试5通过：更新预约状态")
            else:
                print("✗ 测试5失败：数据库验证未通过")
        except Exception as e:
            print(f"✗ 测试5失败：{str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n[测试6] 验证数据库中的记录")
    print("-" * 60)
    
    # 测试6: 直接查询数据库验证记录是否存在
    try:
        async with db_pool.pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    SELECT id, department, doctor_id, doctor_name, appointment_date, status, notes
                    FROM appointments
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                """, (user_id,))
                rows = await cur.fetchall()
                
                if rows:
                    print(f"✓ 数据库中找到 {len(rows)} 条预约记录：")
                    for idx, row in enumerate(rows, 1):
                        print(f"  {idx}. ID={row['id']}, 科室={row['department']}, "
                              f"时间={row['appointment_date']}, 状态={row['status']}")
                else:
                    print("✗ 数据库中未找到预约记录！")
        print("✓ 测试6通过：数据库验证")
    except Exception as e:
        print(f"✗ 测试6失败：{str(e)}")
        import traceback
        traceback.print_exc()
    
    # 测试结束后清理数据（保持测试环境干净）
    # 如果希望保留测试数据用于查看，可以注释掉下面的清理调用
    # print("\n[清理] 测试后清理数据")
    # print("-" * 60)
    # await cleanup_test_data(db_pool.pool, checkpointer, store, user_id, session_id)
    
    # 清理资源
    await db_pool.close()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_appointment_workflow())

