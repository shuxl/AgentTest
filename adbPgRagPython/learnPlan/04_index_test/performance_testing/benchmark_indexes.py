"""
索引性能对比测试
对比无索引、HNSW 索引、IVFFlat 索引的性能差异
"""

import sys
import argparse
import json
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DB_CONFIG, TEST_TABLE_NAME
from db_utils import PgVectorClient
import numpy as np

# 导入索引测试函数（同目录下的模块）
# 添加当前目录到路径以便导入同目录模块
sys.path.insert(0, str(Path(__file__).parent))
from test_hnsw_index import create_hnsw_index, test_query_performance as test_hnsw_query, get_table_stats, drop_index_if_exists
from test_ivfflat_index import create_ivfflat_index, test_query_performance as test_ivfflat_query


def test_no_index_query(client: PgVectorClient, table_name: str, 
                       dimension: int, num_queries: int = 10, k: int = 10):
    """
    测试无索引时的查询性能（全表扫描）
    
    Args:
        client: 数据库客户端
        table_name: 表名
        dimension: 向量维度
        num_queries: 测试查询数量
        k: 返回 Top-K 结果
    
    Returns:
        dict: 查询性能统计信息
    """
    print(f"\n测试无索引查询性能 (全表扫描, k={k})")
    
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
        'index_type': 'no_index',
        'num_queries': num_queries,
        'k': k,
        'avg_time_ms': float(np.mean(query_times)),
        'p50_time_ms': float(np.percentile(query_times, 50)),
        'p95_time_ms': float(np.percentile(query_times, 95)),
        'p99_time_ms': float(np.percentile(query_times, 99)),
        'min_time_ms': float(np.min(query_times)),
        'max_time_ms': float(np.max(query_times)),
    }
    
    print(f"✅ 无索引查询测试完成")
    print(f"  平均查询时间: {stats['avg_time_ms']:.2f} ms")
    print(f"  P95: {stats['p95_time_ms']:.2f} ms")
    
    return stats


def compare_indexes(client: PgVectorClient, table_name: str, dimension: int,
                   hnsw_params: dict = None, ivfflat_params: dict = None,
                   query_params: dict = None):
    """
    对比不同索引的性能
    
    Args:
        client: 数据库客户端
        table_name: 表名
        dimension: 向量维度
        hnsw_params: HNSW 索引参数
        ivfflat_params: IVFFlat 索引参数
        query_params: 查询测试参数
    
    Returns:
        dict: 包含所有测试结果
    """
    results = {
        'table_name': table_name,
        'dimension': dimension,
        'timestamp': datetime.now().isoformat(),
        'results': {}
    }
    
    # 默认参数
    if hnsw_params is None:
        hnsw_params = {'m': 16, 'ef_construction': 64, 'ef_search': 40}
    if ivfflat_params is None:
        table_stats = get_table_stats(client, table_name)
        lists = max(10, table_stats['count'] // 1000)
        ivfflat_params = {'lists': lists, 'probes': 10}
    if query_params is None:
        query_params = {'num_queries': 10, 'k': 10}
    
    # 1. 测试无索引
    print("\n" + "="*60)
    print("1. 测试无索引查询性能")
    print("="*60)
    no_index_stats = test_no_index_query(
        client, table_name, dimension,
        query_params['num_queries'], query_params['k']
    )
    results['results']['no_index'] = no_index_stats
    
    # 2. 测试 HNSW 索引
    print("\n" + "="*60)
    print("2. 测试 HNSW 索引性能")
    print("="*60)
    
    hnsw_index_name = f"{table_name}_hnsw_idx"
    drop_index_if_exists(client, hnsw_index_name)
    
    hnsw_index_info = create_hnsw_index(
        client, table_name, hnsw_index_name, dimension,
        'vector_cosine_ops', hnsw_params['m'], hnsw_params['ef_construction']
    )
    
    if hnsw_index_info:
        hnsw_query_stats = test_hnsw_query(
            client, table_name, dimension,
            hnsw_params['ef_search'], query_params['num_queries'], query_params['k']
        )
        results['results']['hnsw'] = {
            'index_info': hnsw_index_info,
            'query_stats': hnsw_query_stats
        }
    
    # 3. 测试 IVFFlat 索引
    print("\n" + "="*60)
    print("3. 测试 IVFFlat 索引性能")
    print("="*60)
    
    # 删除 HNSW 索引（同一列不能同时有多个索引）
    drop_index_if_exists(client, hnsw_index_name)
    
    ivfflat_index_name = f"{table_name}_ivfflat_idx"
    drop_index_if_exists(client, ivfflat_index_name)
    
    ivfflat_index_info = create_ivfflat_index(
        client, table_name, ivfflat_index_name, dimension,
        'vector_cosine_ops', ivfflat_params['lists']
    )
    
    if ivfflat_index_info:
        ivfflat_query_stats = test_ivfflat_query(
            client, table_name, dimension,
            ivfflat_params['probes'], query_params['num_queries'], query_params['k']
        )
        results['results']['ivfflat'] = {
            'index_info': ivfflat_index_info,
            'query_stats': ivfflat_query_stats
        }
    
    return results


def print_comparison_summary(results: dict):
    """打印对比结果摘要"""
    print("\n" + "="*60)
    print("性能对比摘要")
    print("="*60)
    
    if 'no_index' in results['results']:
        no_index = results['results']['no_index']
        print(f"\n无索引:")
        print(f"  平均查询时间: {no_index['avg_time_ms']:.2f} ms")
        print(f"  P95 查询时间: {no_index['p95_time_ms']:.2f} ms")
    
    if 'hnsw' in results['results']:
        hnsw = results['results']['hnsw']
        index_info = hnsw['index_info']
        query_stats = hnsw['query_stats']
        print(f"\nHNSW 索引:")
        print(f"  索引构建时间: {index_info['build_time']:.2f} 秒")
        print(f"  索引大小: {index_info['index_size']}")
        print(f"  平均查询时间: {query_stats['avg_time_ms']:.2f} ms")
        print(f"  P95 查询时间: {query_stats['p95_time_ms']:.2f} ms")
        if 'no_index' in results['results']:
            speedup = no_index['avg_time_ms'] / query_stats['avg_time_ms']
            print(f"  相对无索引加速: {speedup:.2f}x")
    
    if 'ivfflat' in results['results']:
        ivfflat = results['results']['ivfflat']
        index_info = ivfflat['index_info']
        query_stats = ivfflat['query_stats']
        print(f"\nIVFFlat 索引:")
        print(f"  索引构建时间: {index_info['build_time']:.2f} 秒")
        print(f"  索引大小: {index_info['index_size']}")
        print(f"  平均查询时间: {query_stats['avg_time_ms']:.2f} ms")
        print(f"  P95 查询时间: {query_stats['p95_time_ms']:.2f} ms")
        if 'no_index' in results['results']:
            speedup = no_index['avg_time_ms'] / query_stats['avg_time_ms']
            print(f"  相对无索引加速: {speedup:.2f}x")
    
    print("="*60)


def main():
    parser = argparse.ArgumentParser(description='对比不同索引的性能')
    parser.add_argument('--table-name', type=str, default=TEST_TABLE_NAME,
                       help=f'表名（默认：{TEST_TABLE_NAME}）')
    parser.add_argument('--output', type=str, default=None,
                       help='输出结果 JSON 文件路径（可选）')
    parser.add_argument('--hnsw-m', type=int, default=16,
                       help='HNSW 参数 m（默认：16）')
    parser.add_argument('--hnsw-ef-construction', type=int, default=64,
                       help='HNSW 参数 ef_construction（默认：64）')
    parser.add_argument('--hnsw-ef-search', type=int, default=40,
                       help='HNSW 查询参数 ef_search（默认：40）')
    parser.add_argument('--ivfflat-lists', type=int, default=None,
                       help='IVFFlat 参数 lists（默认：自动计算）')
    parser.add_argument('--ivfflat-probes', type=int, default=10,
                       help='IVFFlat 查询参数 probes（默认：10）')
    parser.add_argument('--num-queries', type=int, default=10,
                       help='测试查询数量（默认：10）')
    parser.add_argument('--k', type=int, default=10,
                       help='Top-K 结果数（默认：10）')
    
    args = parser.parse_args()
    
    print("="*60)
    print("索引性能对比测试")
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
    
    # 准备参数
    hnsw_params = {
        'm': args.hnsw_m,
        'ef_construction': args.hnsw_ef_construction,
        'ef_search': args.hnsw_ef_search
    }
    
    ivfflat_params = {
        'lists': args.ivfflat_lists or max(10, table_stats['count'] // 1000),
        'probes': args.ivfflat_probes
    }
    
    query_params = {
        'num_queries': args.num_queries,
        'k': args.k
    }
    
    # 运行对比测试
    results = compare_indexes(
        client, args.table_name, dimension,
        hnsw_params, ivfflat_params, query_params
    )
    
    # 打印摘要
    print_comparison_summary(results)
    
    # 保存结果
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n✅ 结果已保存到: {args.output}")


if __name__ == "__main__":
    main()

