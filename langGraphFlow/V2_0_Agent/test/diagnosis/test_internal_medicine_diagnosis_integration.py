"""
内科诊断智能体集成测试
测试从路由到内科诊断智能体的完整流程
"""
import sys
import asyncio
from pathlib import Path
from langchain_core.messages import HumanMessage

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent  # test/diagnosis/ -> test/ -> V2_0_Agent/
sys.path.insert(0, str(project_root))

from utils.database import get_db_pool
from utils.router_graph import create_router_agent
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.postgres import AsyncPostgresStore
from utils.config import Config


async def test_internal_medicine_diagnosis_agent():
    """测试内科诊断智能体"""
    print("=" * 80)
    print("内科诊断智能体集成测试")
    print("=" * 80)
    
    # 1. 初始化数据库连接池和checkpointer
    print("\n1. 初始化数据库连接...")
    db_pool = get_db_pool()
    await db_pool.create_pool()
    
    checkpointer = AsyncPostgresSaver(db_pool.pool)
    store = AsyncPostgresStore(db_pool.pool)
    
    print("✅ 数据库连接成功")
    
    # 2. 创建路由智能体
    print("\n2. 创建路由智能体...")
    agent = await create_router_agent(checkpointer, db_pool.pool, store)
    print("✅ 路由智能体创建成功")
    
    # 3. 测试诊断意图识别和路由
    print("\n3. 测试诊断意图识别和路由...")
    test_queries = [
        "患者有高血压症状，帮我诊断一下",
        "这个患者有胸痛、心悸，可能是冠心病吗？",
        "患者有咳嗽、发热，怀疑是肺炎，请分析一下"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n测试 {i}: {query}")
        print("-" * 80)
        
        session_id = f"test_diagnosis_{i}"
        user_id = "test_user"
        
        config = {
            "configurable": {
                "thread_id": session_id
            }
        }
        
        try:
            # 调用路由智能体
            result = await agent.ainvoke(
                {
                    "messages": [HumanMessage(content=query)],
                    "user_id": user_id,
                    "session_id": session_id,
                    "current_intent": None,
                    "current_agent": None,
                    "need_reroute": False
                },
                config=config
            )
            
            # 显示结果
            print(f"当前意图: {result.get('current_intent')}")
            print(f"子意图: {result.get('sub_intent')}")
            print(f"当前智能体: {result.get('current_agent')}")
            
            # 显示最后一条AI消息
            messages = result.get("messages", [])
            if messages:
                last_message = messages[-1]
                if hasattr(last_message, 'content'):
                    print(f"\nAI回复（前200字符）:")
                    print(last_message.content[:200] + "...")
            
            print("✅ 测试通过")
            
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # 4. 清理
    print("\n4. 清理资源...")
    await db_pool.close()
    print("✅ 资源清理完成")
    
    print("\n" + "=" * 80)
    print("✅ 集成测试完成！")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_internal_medicine_diagnosis_agent())

