"""
生成测试向量数据
支持生成随机向量和文本向量，用于索引性能测试
"""

import sys
import argparse
from pathlib import Path
import numpy as np
from tqdm import tqdm

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DB_CONFIG, MODEL_DIMENSION, TEST_TABLE_NAME
from db_utils import PgVectorClient


def generate_random_vectors(count: int, dimension: int) -> np.ndarray:
    """
    生成随机向量数据
    
    Args:
        count: 向量数量
        dimension: 向量维度
    
    Returns:
        numpy.ndarray: 形状为 (count, dimension) 的向量数组
    """
    # 生成随机向量（标准化，使向量在单位球面上）
    vectors = np.random.randn(count, dimension)
    # L2 归一化（用于余弦相似度）
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    vectors = vectors / (norms + 1e-8)
    return vectors


def create_test_table(client: PgVectorClient, table_name: str, dimension: int, drop_existing: bool = False):
    """
    创建测试表
    
    Args:
        client: 数据库客户端
        table_name: 表名
        dimension: 向量维度
        drop_existing: 是否删除已存在的表
    """
    if drop_existing:
        drop_query = f"DROP TABLE IF EXISTS {table_name} CASCADE;"
        client.execute_update(drop_query)
        print(f"✅ 已删除表 {table_name}")
    
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        embedding vector({dimension}),
        metadata JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    client.execute_update(create_table_query)
    print(f"✅ 表 {table_name} 已创建或已存在")


def insert_vectors_batch(client: PgVectorClient, table_name: str, vectors: np.ndarray, 
                         batch_size: int = 1000, verbose: bool = True):
    """
    批量插入向量数据
    
    Args:
        client: 数据库客户端
        table_name: 表名
        vectors: 向量数组
        batch_size: 批处理大小
        verbose: 是否显示进度
    """
    count = len(vectors)
    dimension = vectors.shape[1]
    
    # 准备插入 SQL
    insert_query = f"""
    INSERT INTO {table_name} (name, description, embedding)
    VALUES (%s, %s, %s::vector)
    """
    
    # 批量插入
    total_batches = (count + batch_size - 1) // batch_size
    inserted = 0
    
    if verbose:
        pbar = tqdm(total=count, desc="插入向量数据")
    
    for i in range(0, count, batch_size):
        batch = vectors[i:i+batch_size]
        batch_data = []
        
        for j, vector in enumerate(batch):
            # 将向量转换为字符串格式
            vector_str = '[' + ','.join(map(str, vector)) + ']'
            name = f"item_{i+j+1}"
            description = f"随机生成的测试向量 {i+j+1}"
            batch_data.append((name, description, vector_str))
        
        # 执行批量插入
        with client.get_connection() as conn:
            cur = conn.cursor()
            cur.executemany(insert_query, batch_data)
            conn.commit()
        
        inserted += len(batch_data)
        if verbose:
            pbar.update(len(batch_data))
    
    if verbose:
        pbar.close()
    
    print(f"✅ 成功插入 {inserted} 条向量数据")


def verify_data(client: PgVectorClient, table_name: str):
    """
    验证插入的数据
    
    Args:
        client: 数据库客户端
        table_name: 表名
    """
    # 统计总记录数
    count_query = f"SELECT COUNT(*) as count FROM {table_name};"
    result = client.execute_query(count_query)
    total_count = result[0]['count'] if result else 0
    
    # 获取向量维度 - 从系统表查询列的类型定义
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
    
    try:
        dim_result = client.execute_query(dim_query)
        if dim_result and len(dim_result) > 0 and dim_result[0]['dim'] is not None:
            dimension = dim_result[0]['dim']
        else:
            dimension = None
    except Exception:
        dimension = None
    
    # 如果从系统表获取失败，尝试从实际数据中解析（后备方案）
    if dimension is None or dimension == 0:
        try:
            # 方法2：通过实际查询向量并解析字符串（作为后备方案）
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
                dimension = sample_result[0]['dim']
        except Exception as e:
            # 如果还是失败，设为0（未知维度）
            dimension = 0
    
    # 获取表大小
    size_query = f"""
    SELECT pg_size_pretty(pg_total_relation_size('{table_name}')) as size;
    """
    size_result = client.execute_query(size_query)
    table_size = size_result[0]['size'] if size_result else 'N/A'
    
    print("\n" + "="*60)
    print("数据验证结果")
    print("="*60)
    print(f"表名: {table_name}")
    print(f"总记录数: {total_count:,}")
    print(f"向量维度: {dimension}")
    print(f"表大小: {table_size}")
    print("="*60)


def main():
    parser = argparse.ArgumentParser(description='生成测试向量数据')
    parser.add_argument('--count', type=int, default=1000, help='生成向量数量（默认：1000）')
    parser.add_argument('--dimension', type=int, default=MODEL_DIMENSION, 
                       help=f'向量维度（默认：{MODEL_DIMENSION}）')
    parser.add_argument('--table-name', type=str, default=TEST_TABLE_NAME,
                       help=f'表名（默认：{TEST_TABLE_NAME}）')
    parser.add_argument('--batch-size', type=int, default=1000,
                       help='批处理大小（默认：1000）')
    parser.add_argument('--type', type=str, default='random', choices=['random', 'text'],
                       help='数据类型：random（随机向量）或 text（文本向量，暂未实现）')
    parser.add_argument('--drop-existing', action='store_true',
                       help='删除已存在的表')
    parser.add_argument('--no-verify', action='store_true',
                       help='不验证插入的数据')
    
    args = parser.parse_args()
    
    print("="*60)
    print("生成测试向量数据")
    print("="*60)
    print(f"向量数量: {args.count:,}")
    print(f"向量维度: {args.dimension}")
    print(f"表名: {args.table_name}")
    print(f"数据类型: {args.type}")
    print("="*60)
    
    # 创建数据库客户端
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
    
    # 创建表
    print("\n创建测试表...")
    create_test_table(client, args.table_name, args.dimension, args.drop_existing)
    
    # 生成向量数据
    print(f"\n生成 {args.type} 向量数据...")
    if args.type == 'random':
        vectors = generate_random_vectors(args.count, args.dimension)
    else:
        print("❌ 文本向量生成暂未实现，请使用 generate_text_vectors.py")
        return
    
    # 插入数据
    print("\n插入向量数据到数据库...")
    insert_vectors_batch(client, args.table_name, vectors, args.batch_size)
    
    # 验证数据
    if not args.no_verify:
        verify_data(client, args.table_name)
    
    print("\n✅ 数据生成完成！")


if __name__ == "__main__":
    main()

