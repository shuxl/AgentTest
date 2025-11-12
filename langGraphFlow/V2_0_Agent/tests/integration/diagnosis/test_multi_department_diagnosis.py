"""
多科室诊断智能体集成测试
测试各科室诊断智能体的基本功能
"""
import sys
import asyncio
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent  # tests/integration/diagnosis/ -> tests/integration/ -> tests/ -> V2_0_Agent/
sys.path.insert(0, str(project_root))

from domain.agents.diagnosis import (
    get_diagnosis_system_prompt,
    create_internal_medicine_diagnosis_agent_node,
    create_surgery_diagnosis_agent_node,
    create_pediatrics_diagnosis_agent_node,
    create_gynecology_diagnosis_agent_node,
    create_cardiology_diagnosis_agent_node,
    create_general_diagnosis_agent_node
)
from core.database import get_db_pool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.postgres import AsyncPostgresStore
from langchain_core.messages import HumanMessage
from domain.router import RouterState


async def test_diagnosis_system_prompts():
    """测试各科室系统提示词生成"""
    print("=" * 80)
    print("测试各科室系统提示词生成")
    print("=" * 80)
    
    departments = [
        "internal_medicine",
        "surgery",
        "pediatrics",
        "gynecology",
        "cardiology",
        "general"
    ]
    
    for dept in departments:
        prompt = get_diagnosis_system_prompt(dept)
        print(f"\n[{dept}] 系统提示词长度: {len(prompt)} 字符")
        print(f"前100字符: {prompt[:100]}...")
        assert len(prompt) > 0, f"{dept} 系统提示词为空"
        assert dept in prompt.lower() or "诊断" in prompt, f"{dept} 系统提示词不包含科室信息"
    
    print("\n✅ 所有科室系统提示词生成正常")


async def test_diagnosis_agent_nodes_creation():
    """测试各科室诊断智能体节点创建"""
    print("\n" + "=" * 80)
    print("测试各科室诊断智能体节点创建")
    print("=" * 80)
    
    # 初始化数据库连接池
    print("\n1. 初始化数据库连接...")
    db_pool = get_db_pool()
    await db_pool.create_pool()
    print("✅ 数据库连接成功")
    
    # 创建checkpointer和store
    print("\n2. 创建checkpointer和store...")
    checkpointer = AsyncPostgresSaver(db_pool.pool)
    await checkpointer.setup()
    store = AsyncPostgresStore(db_pool.pool)
    await store.setup()
    print("✅ checkpointer和store创建成功")
    
    # 测试各科室节点创建
    departments = [
        ("internal_medicine", create_internal_medicine_diagnosis_agent_node),
        ("surgery", create_surgery_diagnosis_agent_node),
        ("pediatrics", create_pediatrics_diagnosis_agent_node),
        ("gynecology", create_gynecology_diagnosis_agent_node),
        ("cardiology", create_cardiology_diagnosis_agent_node),
        ("general", create_general_diagnosis_agent_node),
    ]
    
    for dept_name, create_func in departments:
        print(f"\n3. 测试 {dept_name} 诊断智能体节点创建...")
        try:
            node = create_func(db_pool.pool, checkpointer, store)
            assert node is not None, f"{dept_name} 节点创建失败"
            print(f"✅ {dept_name} 诊断智能体节点创建成功")
        except Exception as e:
            print(f"❌ {dept_name} 诊断智能体节点创建失败: {e}")
            raise
    
    print("\n✅ 所有科室诊断智能体节点创建成功")
    
    # 清理
    await db_pool.close()


async def test_diagnosis_agent_basic_execution():
    """测试各科室诊断智能体基本执行（不调用LLM，仅测试节点创建）"""
    print("\n" + "=" * 80)
    print("测试各科室诊断智能体基本执行")
    print("=" * 80)
    
    # 初始化数据库连接池
    print("\n1. 初始化数据库连接...")
    db_pool = get_db_pool()
    await db_pool.create_pool()
    print("✅ 数据库连接成功")
    
    # 创建checkpointer和store
    print("\n2. 创建checkpointer和store...")
    checkpointer = AsyncPostgresSaver(db_pool.pool)
    await checkpointer.setup()
    store = AsyncPostgresStore(db_pool.pool)
    await store.setup()
    print("✅ checkpointer和store创建成功")
    
    # 测试节点函数签名
    departments = [
        ("internal_medicine", create_internal_medicine_diagnosis_agent_node),
        ("surgery", create_surgery_diagnosis_agent_node),
        ("pediatrics", create_pediatrics_diagnosis_agent_node),
        ("gynecology", create_gynecology_diagnosis_agent_node),
        ("cardiology", create_cardiology_diagnosis_agent_node),
        ("general", create_general_diagnosis_agent_node),
    ]
    
    for dept_name, create_func in departments:
        print(f"\n3. 测试 {dept_name} 诊断智能体节点函数...")
        try:
            node = create_func(db_pool.pool, checkpointer, store)
            
            # 创建测试状态
            test_state: RouterState = {
                "messages": [HumanMessage(content="测试消息")],
                "user_id": "test_user",
                "session_id": f"test_session_{dept_name}",
                "current_intent": f"{dept_name}_diagnosis",
                "current_agent": f"{dept_name}_diagnosis_agent",
                "need_reroute": False,
                "sub_intent": None
            }
            
            # 验证节点函数可调用（不实际执行，因为需要LLM）
            assert callable(node), f"{dept_name} 节点不是可调用函数"
            print(f"✅ {dept_name} 诊断智能体节点函数验证成功")
        except Exception as e:
            print(f"❌ {dept_name} 诊断智能体节点验证失败: {e}")
            raise
    
    print("\n✅ 所有科室诊断智能体节点基本验证成功")
    
    # 清理
    await db_pool.close()


async def main():
    """主测试函数"""
    try:
        await test_diagnosis_system_prompts()
        await test_diagnosis_agent_nodes_creation()
        await test_diagnosis_agent_basic_execution()
        
        print("\n" + "=" * 80)
        print("✅ 所有测试通过！")
        print("=" * 80)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(main())

