"""
示例：插入向量数据
演示如何将文本向量化并插入到 PgVector 数据库
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import DB_CONFIG
from db_utils import PgVectorClient
from vector_ops import VectorOperations
from embedding_utils import TextEmbedder


def main():
    print("="*60)
    print("示例：插入向量数据")
    print("="*60)
    
    # 1. 创建数据库客户端
    print("\n1. 创建数据库客户端...")
    client = PgVectorClient(**DB_CONFIG)
    
    # 测试连接
    if not client.test_connection():
        print("❌ 数据库连接失败！")
        return
    
    # 检查扩展
    if not client.check_extension('vector'):
        print("❌ pgvector 扩展未安装！")
        print("请在数据库中执行: CREATE EXTENSION IF NOT EXISTS vector;")
        return
    
    print("✅ 数据库连接成功")
    
    # 2. 创建表（如果不存在）
    print("\n2. 创建测试表...")
    create_table_query = """
    CREATE TABLE IF NOT EXISTS items (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        embedding vector(768),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    client.execute_update(create_table_query)
    print("✅ 表 items 已创建或已存在")
    
    # 3. 初始化文本向量化工具
    print("\n3. 初始化文本向量化工具...")
    embedder = TextEmbedder()
    embedder.load()
    print(f"✅ 模型加载成功，维度: {embedder.get_dimension()}")
    
    # 4. 创建向量操作对象
    print("\n4. 创建向量操作对象...")
    vector_ops = VectorOperations(client)
    
    # 5. 准备测试数据
    print("\n5. 准备测试数据...")
    test_items = [
        {
            'name': 'Python 编程',
            'description': 'Python 是一种高级编程语言，广泛用于数据科学和人工智能领域。'
        },
        {
            'name': 'PostgreSQL 数据库',
            'description': 'PostgreSQL 是一个功能强大的开源关系型数据库管理系统。'
        },
        {
            'name': '向量数据库',
            'description': '向量数据库专门用于存储和检索高维向量数据，适合相似度搜索。'
        },
        {
            'name': '机器学习',
            'description': '机器学习是人工智能的一个分支，通过算法让计算机从数据中学习。'
        },
        {
            'name': '深度学习',
            'description': '深度学习使用神经网络来模拟人脑的学习过程，在图像识别等领域表现优异。'
        }
    ]
    
    # 6. 向量化并插入数据
    print("\n6. 向量化并插入数据...")
    for item in test_items:
        # 向量化描述文本
        vector = embedder.encode(item['description'])
        
        # 插入数据
        data = {
            'name': item['name'],
            'description': item['description']
        }
        vector_ops.insert_vector('items', data, vector)
        print(f"  ✅ 已插入: {item['name']}")
    
    # 7. 验证插入的数据
    print("\n7. 验证插入的数据...")
    query = "SELECT id, name, description FROM items ORDER BY id"
    results = client.execute_query(query)
    print(f"✅ 共插入 {len(results)} 条记录")
    for result in results:
        print(f"  ID {result['id']}: {result['name']}")
    
    print("\n" + "="*60)
    print("✅ 示例完成！")
    print("="*60)


if __name__ == "__main__":
    main()

