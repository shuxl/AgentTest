"""
路由图创建测试
验证路由图是否正确创建，包含所有必要的节点
"""
import sys
import asyncio
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent  # test/router/ -> test/ -> V2_0_Agent/
sys.path.insert(0, str(project_root))

from utils.router_graph import create_router_graph
from utils.database import get_db_pool
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
    required_nodes = [
        'router',
        'clarify_intent',
        'blood_pressure_agent',
        'appointment_agent',
        'internal_medicine_diagnosis_agent',
        'doctor_assistant_agent'
    ]
    
    missing_nodes = []
    for node_name in required_nodes:
        if node_name in nodes:
            print(f"  ✅ {node_name}")
        else:
            print(f"  ❌ {node_name} (缺失)")
            missing_nodes.append(node_name)
    
    # 检查诊断智能体节点
    if 'internal_medicine_diagnosis_agent' in nodes:
        print("\n✅ 包含内科诊断智能体节点")
    else:
        print("\n❌ 未找到内科诊断智能体节点")
    
    # 总结
    print("\n" + "=" * 80)
    if missing_nodes:
        print(f"❌ 测试失败：缺失节点 {missing_nodes}")
        return False
    else:
        print("✅ 所有必需节点都存在，测试通过")
        return True
    
    # 清理
    await db_pool.close()
    print("\n✅ 资源清理完成")


if __name__ == "__main__":
    asyncio.run(test_router_graph_creation())

