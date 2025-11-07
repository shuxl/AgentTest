"""
测试 HNSW 索引性能
包括索引创建时间、索引大小、查询性能等指标
"""

import sys
import argparse
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DB_CONFIG, TEST_TABLE_NAME
from db_utils import PgVectorClient
import numpy as np


def drop_index_if_exists(client: PgVectorClient, index_name: str):
    """删除索引（如果存在）"""
    drop_query = f"DROP INDEX IF EXISTS {index_name} CASCADE;"
    client.execute_update(drop_query)


def create_hnsw_index(client: PgVectorClient, table_name: str, index_name: str,
                      dimension: int, distance_op: str = 'vector_cosine_ops',
                      m: int = 16, ef_construction: int = 64):
    """
    创建 HNSW 索引
    
    Args:
        client: 数据库客户端
        table_name: 表名
        index_name: 索引名
        dimension: 向量维度（用于验证）
        distance_op: 距离操作符（vector_cosine_ops, vector_l2_ops, vector_ip_ops）
        m: HNSW 参数 m（每个节点连接的最大邻居数）
        ef_construction: HNSW 参数 ef_construction（构建时搜索的候选数）
    
    Returns:
        dict: 包含创建时间和索引大小的信息
    """
    # 删除已存在的索引
    drop_index_if_exists(client, index_name)
    
    print(f"\n创建 HNSW 索引: {index_name}")
    print(f"  参数: m={m}, ef_construction={ef_construction}")
    print(f"  距离操作符: {distance_op}")
    
    # 记录开始时间
    start_time = time.time()
    
    # 创建索引
    create_index_query = f"""
    CREATE INDEX {index_name}
    ON {table_name}
    USING hnsw (embedding {distance_op})
    WITH (m = {m}, ef_construction = {ef_construction});
    """
    
    try:
        client.execute_update(create_index_query)
        build_time = time.time() - start_time
        
        # 获取索引大小
        size_query = f"""
        SELECT pg_size_pretty(pg_relation_size('{index_name}')) as size,
               pg_relation_size('{index_name}') as size_bytes
        """
        size_result = client.execute_query(size_query)
        index_size = size_result[0]['size'] if size_result else 'N/A'
        index_size_bytes = size_result[0]['size_bytes'] if size_result else 0
        
        print(f"✅ 索引创建成功")
        print(f"  构建时间: {build_time:.2f} 秒")
        print(f"  索引大小: {index_size}")
        
        return {
            'build_time': build_time,
            'index_size': index_size,
            'index_size_bytes': index_size_bytes,
            'm': m,
            'ef_construction': ef_construction,
            'distance_op': distance_op
        }
    except Exception as e:
        print(f"❌ 索引创建失败: {str(e)}")
        return None


def test_query_performance(client: PgVectorClient, table_name: str, 
                          dimension: int, ef_search: int = 40,
                          num_queries: int = 10, k: int = 10):
    """
    测试查询性能
    
    Args:
        client: 数据库客户端
        table_name: 表名
        dimension: 向量维度
        ef_search: HNSW 查询参数 ef_search
        num_queries: 测试查询数量
        k: 返回 Top-K 结果
    
    Returns:
        dict: 查询性能统计信息
    """
    print(f"\n测试查询性能 (ef_search={ef_search}, k={k})")
    
    # 设置查询参数
    client.execute_update(f"SET hnsw.ef_search = {ef_search};")
    
    # 生成随机查询向量
    query_vectors = np.random.randn(num_queries, dimension)
    norms = np.linalg.norm(query_vectors, axis=1, keepdims=True)
    query_vectors = query_vectors / (norms + 1e-8)
    
    # 执行查询并记录时间
    query_times = []
    
    for i, query_vec in enumerate(query_vectors):
        vector_str = '[' + ','.join(map(str, query_vec)) + ']'
        
        query = f"""
        SELECT id, name, embedding <=> %s::vector as distance
        FROM {table_name}
        ORDER BY embedding <=> %s::vector
        LIMIT {k};
        """
        
        start_time = time.time()
        client.execute_query(query, (vector_str, vector_str))
        query_time = (time.time() - start_time) * 1000  # 转换为毫秒
        query_times.append(query_time)
    
    # 计算统计信息
    query_times = np.array(query_times)
    stats = {
        'num_queries': num_queries,
        'ef_search': ef_search,
        'k': k,
        'avg_time_ms': float(np.mean(query_times)),
        'p50_time_ms': float(np.percentile(query_times, 50)),
        'p95_time_ms': float(np.percentile(query_times, 95)),
        'p99_time_ms': float(np.percentile(query_times, 99)),
        'min_time_ms': float(np.min(query_times)),
        'max_time_ms': float(np.max(query_times)),
    }
    
    print(f"✅ 查询性能测试完成")
    print(f"  平均查询时间: {stats['avg_time_ms']:.2f} ms")
    print(f"  P50: {stats['p50_time_ms']:.2f} ms")
    print(f"  P95: {stats['p95_time_ms']:.2f} ms")
    print(f"  P99: {stats['p99_time_ms']:.2f} ms")
    
    return stats


def get_table_stats(client: PgVectorClient, table_name: str):
    """获取表的基本统计信息"""
    count_query = f"SELECT COUNT(*) as count FROM {table_name};"
    count_result = client.execute_query(count_query)
    count = count_result[0]['count'] if count_result else 0
    
    # 方法1：从实际数据中解析向量维度（最可靠）
    # 因为表定义可能没有指定维度，所以直接从数据中获取最准确
    dimension = 0
    try:
        sample_query = f"""
        SELECT 
            array_length(
                string_to_array(
                    trim(both '[]' from embedding::text),
                    ','
                ),
                1
            ) as dim
        FROM {table_name}
        WHERE embedding IS NOT NULL
        LIMIT 1;
        """
        sample_result = client.execute_query(sample_query)
        if sample_result and sample_result[0]['dim']:
            dimension = int(sample_result[0]['dim'])
    except Exception:
        pass
    
    # 方法2：如果方法1失败，从系统表查询列的类型定义（后备方案）
    if dimension == 0:
        try:
            # pgvector 的 vector 类型：对于 vector(n)，atttypmod = n * 8 + 4
            # 对于 vector（无维度限制），atttypmod = -1
            dim_query = f"""
            SELECT 
                CASE 
                    WHEN atttypmod = -1 THEN NULL  -- 可变维度
                    WHEN atttypmod > 0 THEN (atttypmod - 4) / 8  -- 固定维度：atttypmod = 维度 * 8 + 4
                    ELSE NULL
                END as dim
            FROM pg_attribute 
            WHERE attrelid = '{table_name}'::regclass 
              AND attname = 'embedding'
              AND NOT attisdropped;
            """
            dim_result = client.execute_query(dim_query)
            if dim_result and len(dim_result) > 0 and dim_result[0]['dim'] is not None:
                dimension = int(dim_result[0]['dim'])
        except Exception:
            dimension = 0
    
    size_query = f"""
    SELECT pg_size_pretty(pg_total_relation_size('{table_name}')) as size,
           pg_total_relation_size('{table_name}') as size_bytes
    """
    size_result = client.execute_query(size_query)
    table_size = size_result[0]['size'] if size_result else 'N/A'
    table_size_bytes = size_result[0]['size_bytes'] if size_result else 0
    
    return {
        'count': count,
        'dimension': dimension,
        'table_size': table_size,
        'table_size_bytes': table_size_bytes
    }


def main():
    parser = argparse.ArgumentParser(description='测试 HNSW 索引性能')
    parser.add_argument('--table-name', type=str, default=TEST_TABLE_NAME,
                       help=f'表名（默认：{TEST_TABLE_NAME}）')
    parser.add_argument('--index-name', type=str, default='idx_items_embedding_hnsw',
                       help='索引名（默认：idx_items_embedding_hnsw）')
    parser.add_argument('--m', type=int, default=16,
                       help='HNSW 参数 m（默认：16）')
    parser.add_argument('--ef-construction', type=int, default=64,
                       help='HNSW 参数 ef_construction（默认：64）')
    parser.add_argument('--ef-search', type=int, default=40,
                       help='HNSW 查询参数 ef_search（默认：40）')
    parser.add_argument('--distance-op', type=str, default='vector_cosine_ops',
                       choices=['vector_cosine_ops', 'vector_l2_ops', 'vector_ip_ops'],
                       help='距离操作符（默认：vector_cosine_ops）')
    parser.add_argument('--num-queries', type=int, default=10,
                       help='测试查询数量（默认：10）')
    parser.add_argument('--k', type=int, default=10,
                       help='Top-K 结果数（默认：10）')
    parser.add_argument('--skip-create', action='store_true',
                       help='跳过索引创建（测试已有索引）')
    parser.add_argument('--skip-query', action='store_true',
                       help='跳过查询性能测试')
    
    args = parser.parse_args()
    
    print("="*60)
    print("HNSW 索引性能测试")
    print("="*60)
    
    # 创建数据库客户端
    client = PgVectorClient(**DB_CONFIG)
    
    # 测试连接
    if not client.test_connection():
        print("❌ 数据库连接失败！")
        return
    
    # 获取表统计信息
    print("\n获取表统计信息...")
    table_stats = get_table_stats(client, args.table_name)
    print(f"  记录数: {table_stats['count']:,}")
    print(f"  向量维度: {table_stats['dimension']}")
    print(f"  表大小: {table_stats['table_size']}")
    
    dimension = table_stats['dimension']
    if dimension == 0:
        print("❌ 无法确定向量维度，请检查表数据")
        return
    
    # 创建索引
    index_info = None
    if not args.skip_create:
        index_info = create_hnsw_index(
            client, args.table_name, args.index_name,
            dimension, args.distance_op,
            args.m, args.ef_construction
        )
    
    # 测试查询性能
    query_stats = None
    if not args.skip_query:
        query_stats = test_query_performance(
            client, args.table_name, dimension,
            args.ef_search, args.num_queries, args.k
        )
    
    # 汇总结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    if index_info:
        print(f"索引构建时间: {index_info['build_time']:.2f} 秒")
        print(f"索引大小: {index_info['index_size']}")
    if query_stats:
        print(f"平均查询时间: {query_stats['avg_time_ms']:.2f} ms")
        print(f"P95 查询时间: {query_stats['p95_time_ms']:.2f} ms")
    print("="*60)


if __name__ == "__main__":
    main()

