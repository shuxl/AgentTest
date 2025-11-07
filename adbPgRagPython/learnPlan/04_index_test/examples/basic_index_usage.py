"""
基础索引使用示例
演示如何创建和使用 HNSW 和 IVFFlat 索引
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DB_CONFIG, TEST_TABLE_NAME
from db_utils import PgVectorClient

# 添加 performance_testing 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'performance_testing'))
from test_hnsw_index import create_hnsw_index, test_query_performance, get_table_stats
from test_ivfflat_index import create_ivfflat_index as create_ivfflat, test_query_performance as test_ivfflat_query


def main():
    print("="*60)
    print("基础索引使用示例")
    print("="*60)
    
    # 创建数据库客户端
    client = PgVectorClient(**DB_CONFIG)
    
    # 测试连接
    if not client.test_connection():
        print("❌ 数据库连接失败！")
        return
    
    # 获取表统计信息
    print("\n1. 获取表统计信息...")
    table_stats = get_table_stats(client, TEST_TABLE_NAME)
    print(f"   记录数: {table_stats['count']:,}")
    print(f"   向量维度: {table_stats['dimension']}")
    print(f"   表大小: {table_stats['table_size']}")
    
    dimension = table_stats['dimension']
    count = table_stats['count']
    
    if dimension == 0 or count == 0:
        print("❌ 表为空或无法确定向量维度，请先生成测试数据")
        print("   运行: python data_generation/generate_test_data.py --count 5000")
        return
    
    # 示例1：创建 HNSW 索引
    print("\n" + "="*60)
    print("2. 创建 HNSW 索引示例")
    print("="*60)
    
    hnsw_index_name = f"{TEST_TABLE_NAME}_hnsw_example"
    hnsw_info = create_hnsw_index(
        client, TEST_TABLE_NAME, hnsw_index_name,
        dimension, 'vector_cosine_ops',
        m=16, ef_construction=64
    )
    
    if hnsw_info:
        print("\n   测试 HNSW 查询性能...")
        hnsw_query_stats = test_query_performance(
            client, TEST_TABLE_NAME, dimension,
            ef_search=40, num_queries=5, k=10
        )
    
    # 示例2：创建 IVFFlat 索引
    print("\n" + "="*60)
    print("3. 创建 IVFFlat 索引示例")
    print("="*60)
    
    # 注意：需要先删除 HNSW 索引（同一列不能有多个索引）
    drop_query = f"DROP INDEX IF EXISTS {hnsw_index_name} CASCADE;"
    client.execute_update(drop_query)
    print("   已删除 HNSW 索引（为创建 IVFFlat 索引腾出空间）")
    
    ivfflat_index_name = f"{TEST_TABLE_NAME}_ivfflat_example"
    lists = max(10, count // 1000)
    ivfflat_info = create_ivfflat(
        client, TEST_TABLE_NAME, ivfflat_index_name,
        dimension, 'vector_cosine_ops', lists=lists
    )
    
    if ivfflat_info:
        print("\n   测试 IVFFlat 查询性能...")
        ivfflat_query_stats = test_ivfflat_query(
            client, TEST_TABLE_NAME, dimension,
            probes=10, num_queries=5, k=10
        )
    
    print("\n" + "="*60)
    print("示例完成！")
    print("="*60)
    print("\n💡 提示：")
    print("   - 运行 python performance_testing/benchmark_indexes.py 进行完整性能对比")
    print("   - 查看 README.md 了解更多索引优化技巧")


if __name__ == "__main__":
    main()

