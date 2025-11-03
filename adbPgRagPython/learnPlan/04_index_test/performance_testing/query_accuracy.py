"""
查询精度评估工具
用于评估索引查询的召回率（Recall@K）和准确率
需要真实数据才能进行有意义的精度评估
"""

import sys
import argparse
import time
import importlib.util
from pathlib import Path
from typing import List, Set, Dict, Tuple
import numpy as np
from tqdm import tqdm

# 明确导入 04_index_test 的 config（避免与 05_simple_test 的 config 冲突）
_04_index_test_path = Path(__file__).parent.parent
_config_path = _04_index_test_path / 'config.py'
spec = importlib.util.spec_from_file_location("_config_04", _config_path)
_config_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_config_module)
DB_CONFIG = _config_module.DB_CONFIG
TEST_TABLE_NAME = _config_module.TEST_TABLE_NAME

# 添加 05_simple_test 路径（用于导入 embedding_utils 和 db_utils）
_05_simple_test_path = Path(__file__).parent.parent.parent / '05_simple_test'
sys.path.insert(0, str(_05_simple_test_path))

from db_utils import PgVectorClient
from embedding_utils import TextEmbedder


def get_true_nearest_neighbors(
    client: PgVectorClient,
    table_name: str,
    query_vector: np.ndarray,
    k: int,
    distance_op: str = '<=>'
) -> List[int]:
    """
    使用暴力搜索获取真实最近邻（作为基准）
    
    Args:
        client: 数据库客户端
        table_name: 表名
        query_vector: 查询向量
        k: 返回 Top-K 结果
        distance_op: 距离操作符（<=> 余弦距离，<-> 欧氏距离）
    
    Returns:
        List[int]: 真实最近邻的 id 列表（按距离升序）
    """
    vector_str = '[' + ','.join(map(str, query_vector)) + ']'
    
    # 使用暴力搜索（不使用索引）
    query = f"""
    SELECT id, embedding {distance_op} %s::vector as distance
    FROM {table_name}
    ORDER BY embedding {distance_op} %s::vector
    LIMIT {k};
    """
    
    # 强制不使用索引
    client.execute_update("SET enable_seqscan = on;")
    client.execute_update("SET enable_indexscan = off;")
    
    result = client.execute_query(query, (vector_str, vector_str))
    
    # 恢复索引设置
    client.execute_update("SET enable_seqscan = on;")
    client.execute_update("SET enable_indexscan = on;")
    
    if result:
        return [row['id'] for row in result]
    return []


def get_index_query_results(
    client: PgVectorClient,
    table_name: str,
    query_vector: np.ndarray,
    k: int,
    ef_search: int = None,
    distance_op: str = '<=>'
) -> List[int]:
    """
    使用索引查询获取结果
    
    Args:
        client: 数据库客户端
        table_name: 表名
        query_vector: 查询向量
        k: 返回 Top-K 结果
        ef_search: HNSW ef_search 参数（仅对 HNSW 索引有效）
        distance_op: 距离操作符
    
    Returns:
        List[int]: 查询结果的 id 列表（按距离升序）
    """
    vector_str = '[' + ','.join(map(str, query_vector)) + ']'
    
    # 设置查询参数
    if ef_search:
        client.execute_update(f"SET hnsw.ef_search = {ef_search};")
    
    query = f"""
    SELECT id, embedding {distance_op} %s::vector as distance
    FROM {table_name}
    ORDER BY embedding {distance_op} %s::vector
    LIMIT {k};
    """
    
    result = client.execute_query(query, (vector_str, vector_str))
    
    if result:
        return [row['id'] for row in result]
    return []


def calculate_recall_at_k(
    true_neighbors: List[int],
    query_results: List[int],
    k: int
) -> float:
    """
    计算召回率@K（Recall@K）
    
    Recall@K = |查询结果 ∩ 真实最近邻| / min(K, |真实最近邻|)
    
    Args:
        true_neighbors: 真实最近邻 id 列表
        query_results: 查询结果 id 列表
        k: K 值
    
    Returns:
        float: 召回率（0.0 - 1.0）
    """
    if not true_neighbors:
        return 0.0
    
    # 取前 k 个真实最近邻
    true_set = set(true_neighbors[:k])
    
    # 取前 k 个查询结果
    result_set = set(query_results[:k])
    
    # 计算交集
    intersection = true_set & result_set
    
    # 召回率 = 交集大小 / min(k, 真实最近邻数量)
    denominator = min(k, len(true_neighbors))
    
    if denominator == 0:
        return 0.0
    
    recall = len(intersection) / denominator
    return recall


def calculate_precision_at_k(
    true_neighbors: List[int],
    query_results: List[int],
    k: int
) -> float:
    """
    计算精确率@K（Precision@K）
    
    Precision@K = |查询结果 ∩ 真实最近邻| / min(K, |查询结果|)
    
    Args:
        true_neighbors: 真实最近邻 id 列表
        query_results: 查询结果 id 列表
        k: K 值
    
    Returns:
        float: 精确率（0.0 - 1.0）
    """
    if not query_results:
        return 0.0
    
    true_set = set(true_neighbors)
    result_set = set(query_results[:k])
    
    intersection = result_set & true_set
    
    denominator = min(k, len(query_results))
    
    if denominator == 0:
        return 0.0
    
    precision = len(intersection) / denominator
    return precision


def evaluate_query_accuracy(
    client: PgVectorClient,
    embedder: TextEmbedder,
    table_name: str,
    query_texts: List[str],
    k: int = 10,
    ef_search: int = 40,
    distance_op: str = '<=>',
    num_queries: int = None,
    verbose: bool = True
) -> Dict:
    """
    评估查询精度
    
    Args:
        client: 数据库客户端
        embedder: 文本向量化工具
        table_name: 表名
        query_texts: 查询文本列表
        k: Top-K 结果数
        ef_search: HNSW ef_search 参数
        distance_op: 距离操作符
        num_queries: 评估的查询数量（None 表示使用所有查询文本）
        verbose: 是否显示详细进度
    
    Returns:
        Dict: 评估结果统计
    """
    if num_queries:
        query_texts = query_texts[:num_queries]
    
    print(f"\n评估查询精度")
    print(f"  查询数量: {len(query_texts)}")
    print(f"  K: {k}")
    print(f"  ef_search: {ef_search}")
    print(f"  距离操作符: {distance_op}")
    
    # 生成查询向量
    if verbose:
        print("\n生成查询向量...")
    query_vectors = embedder.encode(query_texts, show_progress_bar=verbose)
    
    # 评估每个查询
    recalls = []
    precisions = []
    query_times = []
    
    if verbose:
        pbar = tqdm(total=len(query_texts), desc="评估查询精度")
    
    for i, (query_text, query_vector) in enumerate(zip(query_texts, query_vectors)):
        # 获取真实最近邻（暴力搜索）
        start_time = time.time()
        true_neighbors = get_true_nearest_neighbors(
            client, table_name, query_vector, k, distance_op
        )
        true_search_time = time.time() - start_time
        
        # 使用索引查询
        start_time = time.time()
        query_results = get_index_query_results(
            client, table_name, query_vector, k, ef_search, distance_op
        )
        index_query_time = time.time() - start_time
        query_times.append(index_query_time * 1000)  # 转换为毫秒
        
        # 计算召回率和精确率
        recall = calculate_recall_at_k(true_neighbors, query_results, k)
        precision = calculate_precision_at_k(true_neighbors, query_results, k)
        
        recalls.append(recall)
        precisions.append(precision)
        
        if verbose:
            pbar.update(1)
    
    if verbose:
        pbar.close()
    
    # 计算统计信息
    recalls = np.array(recalls)
    precisions = np.array(precisions)
    query_times = np.array(query_times)
    
    stats = {
        'num_queries': len(query_texts),
        'k': k,
        'ef_search': ef_search,
        'avg_recall': float(np.mean(recalls)),
        'median_recall': float(np.median(recalls)),
        'min_recall': float(np.min(recalls)),
        'max_recall': float(np.max(recalls)),
        'avg_precision': float(np.mean(precisions)),
        'median_precision': float(np.median(precisions)),
        'avg_query_time_ms': float(np.mean(query_times)),
        'median_query_time_ms': float(np.median(query_times)),
        'p95_query_time_ms': float(np.percentile(query_times, 95)),
    }
    
    return stats


def main():
    parser = argparse.ArgumentParser(description='评估查询精度（召回率）')
    parser.add_argument('--table-name', type=str, default=TEST_TABLE_NAME,
                       help=f'表名（默认：{TEST_TABLE_NAME}）')
    parser.add_argument('--k', type=int, default=10,
                       help='Top-K 结果数（默认：10）')
    parser.add_argument('--ef-search', type=int, default=40,
                       help='HNSW ef_search 参数（默认：40）')
    parser.add_argument('--num-queries', type=int, default=50,
                       help='评估查询数量（默认：50）')
    parser.add_argument('--distance-op', type=str, default='<=>',
                       choices=['<=>', '<->', '<#>'],
                       help='距离操作符（默认：<=> 余弦距离）')
    parser.add_argument('--query-file', type=str,
                       help='查询文本文件（每行一个查询，如果不指定则从表中随机选择）')
    parser.add_argument('--sample-queries', action='store_true',
                       help='从表中随机采样查询（不使用文件）')
    
    args = parser.parse_args()
    
    print("="*60)
    print("查询精度评估")
    print("="*60)
    print(f"表名: {args.table_name}")
    print(f"K: {args.k}")
    print(f"ef_search: {args.ef_search}")
    print(f"查询数量: {args.num_queries}")
    print("="*60)
    
    # 创建数据库客户端
    client = PgVectorClient(**DB_CONFIG)
    
    # 测试连接
    if not client.test_connection():
        print("❌ 数据库连接失败！")
        return
    
    # 初始化文本向量化工具
    print("\n初始化文本向量化工具...")
    embedder = TextEmbedder(use_local_only=True)
    embedder.load()
    
    # 准备查询文本
    query_texts = []
    
    if args.query_file:
        # 从文件读取查询
        with open(args.query_file, 'r', encoding='utf-8') as f:
            query_texts = [line.strip() for line in f if line.strip()]
        print(f"✅ 从文件读取了 {len(query_texts)} 个查询")
    elif args.sample_queries:
        # 从表中随机采样
        query = f"""
        SELECT description FROM {args.table_name}
        ORDER BY RANDOM()
        LIMIT {args.num_queries};
        """
        results = client.execute_query(query)
        query_texts = [row['description'] for row in results if row['description']]
        print(f"✅ 从表中随机采样了 {len(query_texts)} 个查询")
    else:
        # 使用预设示例查询
        sample_queries = [
            "什么是人工智能？",
            "机器学习的基本原理是什么？",
            "如何优化数据库查询性能？",
            "向量数据库的应用场景有哪些？",
            "HNSW 算法的优势是什么？",
        ]
        query_texts = sample_queries * (args.num_queries // len(sample_queries) + 1)
        query_texts = query_texts[:args.num_queries]
        print(f"✅ 使用预设示例查询 {len(query_texts)} 个")
    
    if not query_texts:
        print("❌ 未准备到任何查询文本！")
        return
    
    # 评估精度
    stats = evaluate_query_accuracy(
        client, embedder, args.table_name,
        query_texts, args.k, args.ef_search,
        args.distance_op, args.num_queries,
        verbose=True
    )
    
    # 输出结果
    print("\n" + "="*60)
    print("评估结果")
    print("="*60)
    print(f"查询数量: {stats['num_queries']}")
    print(f"\n召回率@K (Recall@{stats['k']}):")
    print(f"  平均: {stats['avg_recall']:.4f} ({stats['avg_recall']*100:.2f}%)")
    print(f"  中位数: {stats['median_recall']:.4f} ({stats['median_recall']*100:.2f}%)")
    print(f"  最小值: {stats['min_recall']:.4f}")
    print(f"  最大值: {stats['max_recall']:.4f}")
    
    print(f"\n精确率@K (Precision@{stats['k']}):")
    print(f"  平均: {stats['avg_precision']:.4f} ({stats['avg_precision']*100:.2f}%)")
    print(f"  中位数: {stats['median_precision']:.4f} ({stats['median_precision']*100:.2f}%)")
    
    print(f"\n查询性能:")
    print(f"  平均查询时间: {stats['avg_query_time_ms']:.2f} ms")
    print(f"  中位数查询时间: {stats['median_query_time_ms']:.2f} ms")
    print(f"  P95 查询时间: {stats['p95_query_time_ms']:.2f} ms")
    print("="*60)
    
    print("\n💡 提示:")
    print("  - 召回率越高，说明索引找到的真实最近邻越多")
    print("  - 如果召回率较低，可以尝试增大 ef_search 参数")
    print("  - 召回率和查询速度需要平衡：ef_search 越大，召回率越高但查询越慢")


if __name__ == "__main__":
    main()

