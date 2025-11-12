"""
路由图创建测试
验证路由图是否正确创建，包含所有必要的节点
"""
import sys
import asyncio
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent  # tests/unit/router/ -> tests/unit/ -> tests/ -> V2_0_Agent/
sys.path.insert(0, str(project_root))

from domain.router import create_router_graph
from core.database import get_db_pool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.postgres import AsyncPostgresStore


async def test_router_graph_creation():
    """测试路由图创建"""
    print("=" * 80)
    print("路由图创建测试")
    print("=" * 80)
    
    # 初始化数据库连接池
    print("\n1. 初始化数据库连接...")
    db_pool = get_db_pool()
    await db_pool.create_pool()
    print("✅ 数据库连接成功")
    
    # 创建checkpointer和store
    print("\n2. 创建checkpointer和store...")
    checkpointer = AsyncPostgresSaver(db_pool.pool)
    store = AsyncPostgresStore(db_pool.pool)
    print("✅ checkpointer和store创建成功")
    
    # 创建路由图
    print("\n3. 创建路由图...")
    graph = create_router_graph(checkpointer, db_pool.pool, store)
    print("✅ 路由图创建成功")
    
    # 检查节点
    print("\n4. 检查路由图节点...")
    # 尝试获取节点列表
    nodes = []
    if hasattr(graph, 'nodes'):
        nodes = list(graph.nodes.keys())
    elif hasattr(graph, 'get_graph'):
        graph_def = graph.get_graph()
        if hasattr(graph_def, 'nodes'):
            nodes = list(graph_def.nodes.keys())
    
    print(f"节点列表: {nodes}")
    
    # 检查必需的节点
    # 核心节点
    core_nodes = [
        'router',
        'clarify_intent'
    ]
    
    # 业务智能体节点
    business_agent_nodes = [
        'blood_pressure_agent',
        'appointment_agent'
    ]
    
    # 诊断智能体节点（多个科室）
    diagnosis_agent_nodes = [
        'internal_medicine_diagnosis_agent',
        'surgery_diagnosis_agent',
        'pediatrics_diagnosis_agent',
        'gynecology_diagnosis_agent',
        'cardiology_diagnosis_agent',
        'general_diagnosis_agent'
    ]
    
    # 其他智能体节点
    other_agent_nodes = [
        'doctor_assistant_agent'
    ]
    
    # 所有必需节点
    required_nodes = core_nodes + business_agent_nodes + diagnosis_agent_nodes + other_agent_nodes
    
    missing_nodes = []
    
    # 检查核心节点
    print("\n核心节点:")
    for node_name in core_nodes:
        if node_name in nodes:
            print(f"  ✅ {node_name}")
        else:
            print(f"  ❌ {node_name} (缺失)")
            missing_nodes.append(node_name)
    
    # 检查业务智能体节点
    print("\n业务智能体节点:")
    for node_name in business_agent_nodes:
        if node_name in nodes:
            print(f"  ✅ {node_name}")
        else:
            print(f"  ❌ {node_name} (缺失)")
            missing_nodes.append(node_name)
    
    # 检查诊断智能体节点
    print("\n诊断智能体节点:")
    for node_name in diagnosis_agent_nodes:
        if node_name in nodes:
            print(f"  ✅ {node_name}")
        else:
            print(f"  ❌ {node_name} (缺失)")
            missing_nodes.append(node_name)
    
    # 检查其他智能体节点
    print("\n其他智能体节点:")
    for node_name in other_agent_nodes:
        if node_name in nodes:
            print(f"  ✅ {node_name}")
        else:
            print(f"  ❌ {node_name} (缺失)")
            missing_nodes.append(node_name)
    
    # 总结
    print("\n" + "=" * 80)
    if missing_nodes:
        print(f"❌ 测试失败：缺失节点 {missing_nodes}")
        print(f"   实际节点数: {len(nodes)}, 必需节点数: {len(required_nodes)}")
        await db_pool.close()
        return False
    else:
        print("✅ 所有必需节点都存在，测试通过")
        print(f"   总节点数: {len(nodes)} (包含 __start__ 等系统节点)")
        print(f"   必需节点数: {len(required_nodes)}")
        await db_pool.close()
        print("\n✅ 资源清理完成")
        return True


if __name__ == "__main__":
    asyncio.run(test_router_graph_creation())

