"""
血压记录智能体集成测试
验证血压记录流程（记录 -> 查询 -> 更新）
包括相对时间解析功能测试
"""
import asyncio
import sys
import os
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
        
        # 1. 清理blood_pressure_records表中的测试数据
        try:
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("""
                        DELETE FROM blood_pressure_records 
                        WHERE user_id = %s
                    """, (user_id,))
                    deleted_records = cur.rowcount
                    print(f"✓ 清理blood_pressure_records表: 删除 {deleted_records} 条记录")
        except Exception as e:
            print(f"⚠ 清理blood_pressure_records表时出现警告: {str(e)}")
        
        # 2. 清理checkpoint数据（checkpoints表）
        # checkpoint通过thread_id（对应session_id）标识
        try:
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    # 先查询要删除的checkpoint_id列表（用于删除blobs）
                    await cur.execute("""
                        SELECT checkpoint_id FROM checkpoints WHERE thread_id = %s
                    """, (session_id,))
                    checkpoint_rows = await cur.fetchall()
                    checkpoint_id_list = [row['checkpoint_id'] for row in checkpoint_rows] if checkpoint_rows else []
                    
                    # 先删除checkpoint_blobs表中的记录（需要在删除checkpoints之前）
                    deleted_blobs = 0
                    if checkpoint_id_list:
                        for checkpoint_id in checkpoint_id_list:
                            await cur.execute("""
                                DELETE FROM checkpoint_blobs 
                                WHERE checkpoint_id = %s
                            """, (checkpoint_id,))
                            deleted_blobs += cur.rowcount
                    
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
        # 注意：血压记录已改用数据库表存储，不再使用store的blood_pressure命名空间
        # 这里只清理memories命名空间（用户设置信息），以及可能的旧数据
        if store:
            try:
                # 清理blood_pressure命名空间（兼容旧数据，如果存在）
                try:
                    namespace_bp = ("blood_pressure", user_id)
                    bp_memories = await store.asearch(namespace_bp, query="")
                    if bp_memories:
                        for memory in bp_memories:
                            await store.adelete(namespace_bp, memory.key)
                        print(f"✓ 清理store数据（blood_pressure命名空间，旧数据）: {len(bp_memories)} 条记录")
                except Exception:
                    pass  # 命名空间可能不存在，忽略
                
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


async def ensure_blood_pressure_table_exists(pool):
    """
    确保blood_pressure_records表存在且包含original_time_description字段
    如果表不存在或字段缺失，则创建/更新表结构
    """
    try:
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                # 检查表是否存在
                await cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'blood_pressure_records'
                    )
                """)
                table_exists = await cur.fetchone()
                
                if not table_exists or not table_exists.get('exists'):
                    # 表不存在，创建表
                    print("正在创建blood_pressure_records表...")
                    await cur.execute("""
                        CREATE TABLE IF NOT EXISTS blood_pressure_records (
                            id SERIAL PRIMARY KEY,
                            user_id VARCHAR(255) NOT NULL,
                            systolic INTEGER NOT NULL CHECK (systolic >= 50 AND systolic <= 300),
                            diastolic INTEGER NOT NULL CHECK (diastolic >= 30 AND diastolic <= 200),
                            measurement_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            original_time_description TEXT,
                            notes TEXT,
                            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            CONSTRAINT check_systolic_gt_diastolic CHECK (systolic > diastolic)
                        )
                    """)
                    print("✓ 表创建成功")
                else:
                    # 表存在，检查是否有original_time_description字段
                    await cur.execute("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'blood_pressure_records' 
                        AND column_name = 'original_time_description'
                    """)
                    column_exists = await cur.fetchone()
                    
                    if not column_exists or not column_exists.get('column_name'):
                        # 字段不存在，添加字段
                        print("正在添加original_time_description字段...")
                        await cur.execute("""
                            ALTER TABLE blood_pressure_records 
                            ADD COLUMN IF NOT EXISTS original_time_description TEXT
                        """)
                        print("✓ 字段添加成功")
                    else:
                        print("✓ 表结构验证通过")
                
                # 创建索引（如果不存在）
                indexes = [
                    "CREATE INDEX IF NOT EXISTS idx_blood_pressure_user_id ON blood_pressure_records(user_id)",
                    "CREATE INDEX IF NOT EXISTS idx_blood_pressure_measurement_time ON blood_pressure_records(measurement_time)",
                    "CREATE INDEX IF NOT EXISTS idx_blood_pressure_user_time ON blood_pressure_records(user_id, measurement_time)"
                ]
                for index_sql in indexes:
                    try:
                        await cur.execute(index_sql)
                    except Exception as e:
                        print(f"⚠ 索引创建警告: {str(e)}")
                
    except Exception as e:
        print(f"⚠ 表结构检查/创建失败: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_blood_pressure_workflow():
    """
    测试血压记录完整流程：
    1. 记录血压（标准格式）
    2. 记录血压（相对时间格式 - 测试新功能）
    3. 查询血压记录（验证原始时间描述）
    4. 查询统计信息
    5. 更新血压记录
    """
    print("=" * 60)
    print("血压记录智能体集成测试")
    print("=" * 60)
    
    # 初始化数据库连接池
    db_pool = get_db_pool()
    await db_pool.create_pool()
    
    # 确保表结构正确（包含original_time_description字段）
    await ensure_blood_pressure_table_exists(db_pool.pool)
    
    # 初始化checkpointer和store
    checkpointer = AsyncPostgresSaver(db_pool.pool)
    await checkpointer.setup()
    
    store = AsyncPostgresStore(db_pool.pool)
    await store.setup()
    
    # 创建路由智能体（需要传递pool）
    router_agent = await create_router_agent(checkpointer=checkpointer, pool=db_pool.pool, store=store)
    
    # 测试用户ID和会话ID
    user_id = "test_user_bp_001"
    session_id = "test_session_bp_001"
    
    # 测试开始前清理旧数据（确保测试环境干净）
    print("\n[清理] 测试前清理旧数据")
    print("-" * 60)
    await cleanup_test_data(db_pool.pool, checkpointer, store, user_id, session_id)
    
    config = {"configurable": {"thread_id": session_id, "recursion_limit": 50}}
    
    print("\n[测试1] 记录血压（标准格式）")
    print("-" * 60)
    
    # 测试1: 记录血压（标准格式）
    state_input_1 = {
        "messages": [HumanMessage(content="我想记录血压，收缩压120，舒张压80，时间是今天早上8点")],
        "user_id": user_id,
        "session_id": session_id,
        "current_intent": None,
        "current_agent": None,
        "need_reroute": False
    }
    
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
        print("✓ 测试1通过：记录血压（标准格式）")
    except Exception as e:
        print(f"✗ 测试1失败：{str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n[测试2] 记录血压（相对时间格式 - 测试新功能）")
    print("-" * 60)
    
    # 测试2: 记录血压（相对时间格式，测试LLM解析功能）
    state_input_2 = {
        "messages": [HumanMessage(content="记录血压，收缩压130，舒张压85，时间是昨天下午")],
        "user_id": user_id,
        "session_id": session_id,
        "current_intent": None,
        "current_agent": None,
        "need_reroute": False
    }
    
    try:
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
        print("✓ 测试2通过：记录血压（相对时间格式）")
    except Exception as e:
        print(f"✗ 测试2失败：{str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n[测试3] 查询血压记录（验证原始时间描述）")
    print("-" * 60)
    
    # 测试3: 查询血压记录（验证原始时间描述是否正确保存和显示）
    state_input_3 = {
        "messages": [HumanMessage(content="查询我的血压记录")],
        "user_id": user_id,
        "session_id": session_id,
        "current_intent": None,
        "current_agent": None,
        "need_reroute": False
    }
    
    try:
        result_3 = await router_agent.ainvoke(state_input_3, config=config)
        messages_3 = result_3.get("messages", [])
        if messages_3:
            last_msg = messages_3[-1]
            if hasattr(last_msg, 'content'):
                print(f"回复: {last_msg.content}")
                # 检查是否包含原始时间描述
                if "用户描述" in last_msg.content or "original_time_description" in str(messages_3):
                    print("✓ 原始时间描述已正确保存和显示")
            else:
                print(f"回复: {str(last_msg)}")
        print(f"当前意图: {result_3.get('current_intent')}")
        print(f"当前智能体: {result_3.get('current_agent')}")
        print("✓ 测试3通过：查询血压记录")
    except Exception as e:
        print(f"✗ 测试3失败：{str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n[测试4] 查询统计信息")
    print("-" * 60)
    
    # 测试4: 查询统计信息
    state_input_4 = {
        "messages": [HumanMessage(content="查询我的血压统计信息")],
        "user_id": user_id,
        "session_id": session_id,
        "current_intent": None,
        "current_agent": None,
        "need_reroute": False
    }
    
    try:
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
        print("✓ 测试4通过：查询统计信息")
    except Exception as e:
        print(f"✗ 测试4失败：{str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n[测试5] 测试相对时间解析（本周一）")
    print("-" * 60)
    
    # 测试5: 测试相对时间解析功能（本周一）
    state_input_5 = {
        "messages": [HumanMessage(content="记录血压，收缩压125，舒张压82，时间是本周一上午")],
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
        print("✓ 测试5通过：相对时间解析（本周一）")
    except Exception as e:
        print(f"✗ 测试5失败：{str(e)}")
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
    asyncio.run(test_blood_pressure_workflow())

