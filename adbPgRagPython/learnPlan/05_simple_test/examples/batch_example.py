"""
示例：批量插入向量数据
演示如何批量向量化和批量插入数据
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
    print("示例：批量插入向量数据")
    print("="*60)
    
    # 1. 创建数据库客户端
    print("\n1. 创建数据库客户端...")
    client = PgVectorClient(**DB_CONFIG)
    
    if not client.test_connection():
        print("❌ 数据库连接失败！")
        return
    
    print("✅ 数据库连接成功")
    
    # 2. 创建表
    print("\n2. 创建测试表...")
    create_table_query = """
    CREATE TABLE IF NOT EXISTS articles (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        category TEXT,
        embedding vector(768),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    client.execute_update(create_table_query)
    print("✅ 表 articles 已创建或已存在")
    
    # 3. 初始化文本向量化工具
    print("\n3. 初始化文本向量化工具...")
    embedder = TextEmbedder()
    embedder.load()
    print(f"✅ 模型加载成功")
    
    # 4. 创建向量操作对象
    print("\n4. 创建向量操作对象...")
    vector_ops = VectorOperations(client)
    
    # 5. 准备批量数据
    print("\n5. 准备批量数据...")
    articles = [
        {
            'title': 'Python 基础教程',
            'content': 'Python 是一种易于学习的编程语言，具有简洁的语法和强大的功能。它广泛应用于Web开发、数据分析、人工智能等领域。',
            'category': '编程'
        },
        {
            'title': 'PostgreSQL 使用指南',
            'content': 'PostgreSQL 是一个功能强大的开源数据库系统，支持复杂查询、事务处理和多种数据类型。它非常适合企业级应用。',
            'category': '数据库'
        },
        {
            'title': '向量数据库原理',
            'content': '向量数据库使用高维向量来存储和检索数据。通过相似度计算，可以快速找到与查询向量最相似的数据。',
            'category': '数据库'
        },
        {
            'title': '机器学习入门',
            'content': '机器学习是人工智能的核心技术之一，通过算法让计算机从数据中学习规律，从而做出预测和决策。',
            'category': 'AI'
        },
        {
            'title': '深度学习实践',
            'content': '深度学习使用多层神经网络来学习数据的复杂模式。在图像识别、自然语言处理等领域取得了突破性进展。',
            'category': 'AI'
        },
        {
            'title': '数据科学工具',
            'content': '数据科学需要掌握多种工具和技术，包括数据清洗、统计分析、可视化等。Python 和 R 是常用的数据科学语言。',
            'category': '数据科学'
        },
        {
            'title': 'SQL 查询优化',
            'content': 'SQL 查询优化是数据库性能调优的重要方面。通过合理使用索引、优化查询语句可以提高数据库的查询速度。',
            'category': '数据库'
        },
        {
            'title': '神经网络基础',
            'content': '神经网络是深度学习的基础，模拟人脑神经元的结构和功能。通过训练可以学习复杂的非线性关系。',
            'category': 'AI'
        }
    ]
    
    print(f"准备插入 {len(articles)} 篇文章")
    
    # 6. 批量向量化
    print("\n6. 批量向量化内容...")
    contents = [article['content'] for article in articles]
    vectors = embedder.encode_batch(contents)
    print(f"✅ 已向量化 {len(vectors)} 篇文章，向量维度: {vectors.shape}")
    
    # 7. 准备批量插入数据
    print("\n7. 准备批量插入数据...")
    data_list = []
    for article in articles:
        data_list.append({
            'title': article['title'],
            'content': article['content'],
            'category': article['category']
        })
    
    # 8. 批量插入
    print("\n8. 批量插入数据库...")
    rows_affected = vector_ops.batch_insert('articles', data_list, vectors)
    print(f"✅ 成功插入 {rows_affected} 条记录")
    
    # 9. 验证数据
    print("\n9. 验证插入的数据...")
    query = "SELECT id, title, category FROM articles ORDER BY id"
    results = client.execute_query(query)
    print(f"数据库中共有 {len(results)} 篇文章:")
    for result in results:
        print(f"  ID {result['id']}: {result['title']} [{result['category']}]")
    
    # 10. 测试批量搜索
    print("\n10. 测试批量搜索...")
    search_query = "人工智能和机器学习"
    print(f"搜索: {search_query}")
    
    query_vector = embedder.encode(search_query)
    search_results = vector_ops.cosine_search('articles', query_vector, limit=5)
    
    print(f"\n找到 {len(search_results)} 篇相关文章:")
    for i, result in enumerate(search_results, 1):
        print(f"\n{i}. {result['title']} [{result['category']}]")
        print(f"   相似度: {result['similarity']:.4f}")
        print(f"   内容: {result['content'][:80]}...")
    
    print("\n" + "="*60)
    print("✅ 示例完成！")
    print("="*60)


if __name__ == "__main__":
    main()

