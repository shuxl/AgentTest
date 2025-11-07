"""
示例：向量相似度搜索
演示如何使用余弦相似度和欧氏距离进行向量搜索
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
    print("示例：向量相似度搜索")
    print("="*60)
    
    # 1. 创建数据库客户端
    print("\n1. 创建数据库客户端...")
    client = PgVectorClient(**DB_CONFIG)
    
    if not client.test_connection():
        print("❌ 数据库连接失败！")
        return
    
    print("✅ 数据库连接成功")
    
    # 2. 初始化文本向量化工具
    print("\n2. 初始化文本向量化工具...")
    embedder = TextEmbedder()
    embedder.load()
    print(f"✅ 模型加载成功")
    
    # 3. 创建向量操作对象
    print("\n3. 创建向量操作对象...")
    vector_ops = VectorOperations(client)
    
    # 4. 执行余弦相似度搜索
    print("\n4. 执行余弦相似度搜索...")
    query_text = "数据库管理系统"
    print(f"查询文本: {query_text}")
    
    # 向量化查询文本
    query_vector = embedder.encode(query_text)
    
    # 执行搜索
    results = vector_ops.cosine_search('items', query_vector, limit=5)
    
    print(f"\n找到 {len(results)} 条相关记录:")
    print("-" * 60)
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['name']}")
        print(f"   相似度: {result['similarity']:.4f}")
        print(f"   描述: {result['description']}")
    
    # 5. 执行带阈值的搜索
    print("\n\n5. 执行带相似度阈值的搜索（阈值 > 0.3）...")
    results_threshold = vector_ops.cosine_search(
        'items', 
        query_vector, 
        limit=10,
        threshold=0.3
    )
    print(f"找到 {len(results_threshold)} 条相似度 > 0.3 的记录")
    for i, result in enumerate(results_threshold, 1):
        print(f"  {i}. {result['name']} (相似度: {result['similarity']:.4f})")
    
    # 6. 执行欧氏距离搜索
    print("\n\n6. 执行欧氏距离搜索...")
    query_text2 = "人工智能"
    print(f"查询文本: {query_text2}")
    
    query_vector2 = embedder.encode(query_text2)
    results_euclidean = vector_ops.euclidean_search('items', query_vector2, limit=5)
    
    print(f"\n找到 {len(results_euclidean)} 条相关记录:")
    print("-" * 60)
    for i, result in enumerate(results_euclidean, 1):
        print(f"\n{i}. {result['name']}")
        print(f"   距离: {result['distance']:.4f}")
        print(f"   描述: {result['description']}")
    
    print("\n" + "="*60)
    print("✅ 示例完成！")
    print("="*60)


if __name__ == "__main__":
    main()

