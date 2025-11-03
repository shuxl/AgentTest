"""
生成真实文本向量数据
使用 embedding 模型将文本数据转换为向量并存储到数据库
用于索引性能测试和查询精度评估
"""

import sys
import argparse
import json
import importlib.util
import os
import urllib.request
import gzip
from pathlib import Path
from typing import List, Tuple, Iterator, Optional
import numpy as np
from tqdm import tqdm

# 明确导入 04_index_test 的 config（避免与 05_simple_test 的 config 冲突）
_04_index_test_path = Path(__file__).parent.parent
_config_path = _04_index_test_path / 'config.py'
spec = importlib.util.spec_from_file_location("_config_04", _config_path)
_config_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_config_module)
DB_CONFIG = _config_module.DB_CONFIG
MODEL_DIMENSION = _config_module.MODEL_DIMENSION
TEST_TABLE_NAME = _config_module.TEST_TABLE_NAME

# 添加 05_simple_test 路径（用于导入 embedding_utils 和 db_utils）
_05_simple_test_path = Path(__file__).parent.parent.parent / '05_simple_test'
sys.path.insert(0, str(_05_simple_test_path))

from db_utils import PgVectorClient
from embedding_utils import TextEmbedder


def read_text_file(file_path: str, encoding: str = 'utf-8') -> List[str]:
    """
    从文本文件读取内容
    
    Args:
        file_path: 文件路径
        encoding: 文件编码
    
    Returns:
        List[str]: 文本列表（按行分割，过滤空行）
    """
    texts = []
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            for line in f:
                line = line.strip()
                if line:  # 过滤空行
                    texts.append(line)
    except UnicodeDecodeError:
        # 如果 UTF-8 失败，尝试其他编码
        with open(file_path, 'r', encoding='gbk') as f:
            for line in f:
                line = line.strip()
                if line:
                    texts.append(line)
    return texts


def read_text_directory(dir_path: str, extensions: List[str] = None) -> Iterator[Tuple[str, str]]:
    """
    从目录读取所有文本文件
    
    Args:
        dir_path: 目录路径
        extensions: 文件扩展名列表（如 ['.txt', '.md']），None 表示所有文件
    
    Yields:
        Tuple[str, str]: (文件路径, 文件内容)
    """
    if extensions is None:
        extensions = ['.txt', '.md', '.py', '.java', '.json', '.csv']
    
    dir_path_obj = Path(dir_path)
    if not dir_path_obj.exists():
        raise ValueError(f"目录不存在: {dir_path}")
    
    for file_path in dir_path_obj.rglob('*'):
        if file_path.is_file() and file_path.suffix in extensions:
            try:
                content = file_path.read_text(encoding='utf-8')
                if content.strip():
                    yield (str(file_path), content)
            except Exception as e:
                print(f"⚠️  跳过文件 {file_path}: {str(e)}")
                continue


def download_wikipedia_sample(output_file: str, limit: int = 10000):
    """
    下载 Wikipedia 示例文本（简化版）
    注意：这是一个示例实现，实际使用时建议：
    1. 使用 wikimedia API 下载
    2. 或使用已处理好的 Wikipedia 文本数据集
    
    Args:
        output_file: 输出文件路径
        limit: 限制文本数量
    """
    print("⚠️  这是一个示例实现，实际使用时建议使用已处理好的 Wikipedia 数据集")
    print("📝 建议方法：")
    print("   1. 从 https://dumps.wikimedia.org/ 下载 Wikipedia 转储")
    print("   2. 使用工具（如 WikiExtractor）提取纯文本")
    print("   3. 将文本保存为文件，使用 --file 或 --dir 参数")
    print(f"\n💡 当前将创建一个示例文件：{output_file}")
    
    # 创建示例文本文件
    sample_texts = generate_sample_texts(min(limit, 100))
    with open(output_file, 'w', encoding='utf-8') as f:
        for text in sample_texts:
            f.write(text + '\n')
    
    print(f"✅ 已创建示例文件：{output_file}")
    return output_file


def load_precomputed_vectors(vector_file: str, limit: Optional[int] = None) -> Tuple[np.ndarray, List[str]]:
    """
    加载预计算的向量数据（如 SIFT1M、GIST1M、Ann-benchmarks 数据集）
    
    支持的格式：
    1. NumPy 格式 (.npy)：形状为 (n, dimension) 的数组
    2. 文本格式 (.txt)：每行一个向量，空格分隔
    
    Args:
        vector_file: 向量文件路径
        limit: 限制加载数量
    
    Returns:
        Tuple[np.ndarray, List[str]]: (向量数组, 元数据文本列表)
    """
    vector_file_path = Path(vector_file)
    
    if not vector_file_path.exists():
        raise FileNotFoundError(f"向量文件不存在: {vector_file}")
    
    print(f"正在加载预计算向量: {vector_file}")
    
    if vector_file_path.suffix == '.npy':
        # NumPy 格式
        vectors = np.load(vector_file)
        if limit:
            vectors = vectors[:limit]
        
        # 生成元数据文本（因为没有原始文本）
        texts = [f"vector_{i+1}" for i in range(len(vectors))]
        print(f"✅ 加载了 {len(vectors)} 个向量（维度: {vectors.shape[1]}）")
        return vectors, texts
    
    elif vector_file_path.suffix in ['.txt', '.dat']:
        # 文本格式（每行一个向量，空格或逗号分隔）
        vectors = []
        texts = []
        with open(vector_file_path, 'r') as f:
            for i, line in enumerate(f):
                if limit and i >= limit:
                    break
                
                parts = line.strip().split()
                if len(parts) > 1:
                    try:
                        vector = [float(x) for x in parts]
                        vectors.append(vector)
                        texts.append(f"vector_{i+1}")
                    except ValueError:
                        continue
        
        if not vectors:
            raise ValueError("未能从文件中解析出向量数据")
        
        vectors_array = np.array(vectors)
        print(f"✅ 加载了 {len(vectors_array)} 个向量（维度: {vectors_array.shape[1]}）")
        return vectors_array, texts
    
    else:
        raise ValueError(f"不支持的文件格式: {vector_file_path.suffix}")


def generate_sample_texts(count: int) -> List[str]:
    """
    生成示例测试文本（用于快速测试）
    
    Args:
        count: 生成文本数量
    
    Returns:
        List[str]: 文本列表
    """
    # 预设的测试文本模板
    templates = [
        "人工智能是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。",
        "机器学习是人工智能的一个子领域，使计算机能够从数据中学习而无需明确编程。",
        "深度学习是机器学习的一个分支，使用人工神经网络来模拟人脑的工作方式。",
        "自然语言处理是计算机科学和人工智能的一个领域，专注于计算机和人类语言之间的交互。",
        "计算机视觉是人工智能的一个分支，使计算机能够识别和理解图像和视频内容。",
        "数据挖掘是从大量数据中发现模式和知识的过程，结合了统计学、机器学习和数据库系统。",
        "大数据是指数据量太大、变化太快或结构太复杂而无法用传统数据处理工具有效处理的数据集。",
        "云计算是通过互联网提供计算资源、存储和应用程序的服务模式。",
        "区块链是一种分布式账本技术，以安全、透明和去中心化的方式记录交易。",
        "物联网是将日常物体连接到互联网，使它们能够收集和交换数据的技术网络。",
        "向量数据库是专门用于存储和查询高维向量数据的数据库系统，支持相似度搜索。",
        "语义搜索是通过理解查询意图和上下文来改进搜索结果的信息检索方法。",
        "检索增强生成(RAG)是一种结合信息检索和文本生成的技术，用于提高AI系统的准确性。",
        "索引优化是提高数据库查询性能的关键技术，包括选择合适的索引类型和参数。",
        "近似最近邻搜索(ANN)是快速查找相似向量的算法，在精度和速度之间取得平衡。",
        "HNSW是一种分层导航小世界图算法，用于高效的向量相似度搜索。",
        "PostgreSQL是一个强大的开源关系数据库管理系统，支持扩展功能如pgvector。",
        "向量嵌入是将离散对象（如单词、句子或图像）转换为连续向量空间的表示方法。",
        "相似度度量是衡量两个向量之间相似程度的数学方法，包括余弦相似度和欧氏距离。",
        "数据库索引是数据结构，用于快速定位和访问数据库中的特定数据。",
    ]
    
    texts = []
    for i in range(count):
        # 使用模板，添加变化
        template = templates[i % len(templates)]
        # 可以添加一些变化
        if i > 0:
            text = f"{template} 这是第 {i+1} 条测试数据。"
        else:
            text = template
        texts.append(text)
    
    return texts


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 0) -> List[str]:
    """
    将长文本分块
    
    Args:
        text: 原始文本
        chunk_size: 每块字符数
        overlap: 重叠字符数
    
    Returns:
        List[str]: 文本块列表
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)
        start = end - overlap
        if start >= len(text):
            break
    
    return chunks


def create_test_table(client: PgVectorClient, table_name: str, dimension: int, drop_existing: bool = False):
    """
    创建测试表（与 generate_test_data.py 一致的结构）
    
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


def insert_text_vectors_batch(client: PgVectorClient, table_name: str, 
                                texts: List[str], vectors: np.ndarray,
                                batch_size: int = 100, verbose: bool = True):
    """
    批量插入文本向量数据
    
    Args:
        client: 数据库客户端
        table_name: 表名
        texts: 文本列表
        vectors: 向量数组
        batch_size: 批处理大小
        verbose: 是否显示进度
    """
    count = len(vectors)
    dimension = vectors.shape[1]
    
    if len(texts) != count:
        raise ValueError(f"文本数量({len(texts)})与向量数量({count})不匹配")
    
    # 准备插入 SQL
    insert_query = f"""
    INSERT INTO {table_name} (name, description, embedding, metadata)
    VALUES (%s, %s, %s::vector, %s::jsonb)
    """
    
    # 批量插入
    total_batches = (count + batch_size - 1) // batch_size
    inserted = 0
    
    if verbose:
        pbar = tqdm(total=count, desc="插入向量数据")
    
    for i in range(0, count, batch_size):
        batch_texts = texts[i:i+batch_size]
        batch_vectors = vectors[i:i+batch_size]
        batch_data = []
        
        for j, (text, vector) in enumerate(zip(batch_texts, batch_vectors)):
            # 将向量转换为字符串格式
            vector_str = '[' + ','.join(map(str, vector)) + ']'
            name = f"text_item_{i+j+1}"
            description = text[:200] if len(text) > 200 else text  # 限制长度
            # 存储完整文本到 metadata（使用 JSON 安全转义）
            metadata_dict = {"full_text": text[:1000]}
            metadata_json = json.dumps(metadata_dict, ensure_ascii=False)
            batch_data.append((name, description, vector_str, metadata_json))
        
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
    
    print(f"✅ 成功插入 {inserted} 条文本向量数据")


def verify_data(client: PgVectorClient, table_name: str):
    """
    验证插入的数据（与 generate_test_data.py 一致）
    
    Args:
        client: 数据库客户端
        table_name: 表名
    """
    # 统计总记录数
    count_query = f"SELECT COUNT(*) as count FROM {table_name};"
    result = client.execute_query(count_query)
    total_count = result[0]['count'] if result else 0
    
    # 获取向量维度
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
    parser = argparse.ArgumentParser(description='生成真实文本向量数据')
    parser.add_argument('--count', type=int, default=None,
                       help='限制向量数量（可选，用于限制加载的数据量）')
    parser.add_argument('--table-name', type=str, default=TEST_TABLE_NAME,
                       help=f'表名（默认：{TEST_TABLE_NAME}）')
    parser.add_argument('--batch-size', type=int, default=100,
                       help='批处理大小（默认：100）')
    parser.add_argument('--embedding-batch-size', type=int, default=32,
                       help='Embedding 批处理大小（默认：32）')
    
    # 数据源选项
    data_source_group = parser.add_mutually_exclusive_group(required=True)
    data_source_group.add_argument('--sample', action='store_true',
                                   help='使用预设示例文本')
    data_source_group.add_argument('--file', type=str,
                                   help='从文本文件读取（每行一个文本）')
    data_source_group.add_argument('--dir', type=str,
                                   help='从目录读取所有文本文件')
    data_source_group.add_argument('--vectors', type=str,
                                   help='直接加载预计算向量文件（.npy 或 .txt 格式，如 SIFT1M、GIST1M 数据集）')
    data_source_group.add_argument('--wikipedia', type=str,
                                   help='下载 Wikipedia 文本（示例实现，实际建议使用已处理的文件）')
    
    parser.add_argument('--chunk-size', type=int, default=0,
                       help='文本分块大小（0 表示不分块，默认：0）')
    parser.add_argument('--chunk-overlap', type=int, default=0,
                       help='文本分块重叠大小（默认：0）')
    parser.add_argument('--drop-existing', action='store_true',
                       help='删除已存在的表')
    parser.add_argument('--no-verify', action='store_true',
                       help='不验证插入的数据')
    
    args = parser.parse_args()
    
    print("="*60)
    print("生成真实文本向量数据")
    print("="*60)
    
    # 确定数据源类型
    if args.sample:
        data_source_type = '示例文本'
        data_source_desc = f"数量: {args.count or '默认'}"
    elif args.file:
        data_source_type = '文本文件'
        data_source_desc = f"文件: {args.file}"
    elif args.dir:
        data_source_type = '目录'
        data_source_desc = f"目录: {args.dir}"
    elif args.vectors:
        data_source_type = '预计算向量'
        data_source_desc = f"文件: {args.vectors}"
    elif args.wikipedia:
        data_source_type = 'Wikipedia（示例）'
        data_source_desc = f"输出文件: {args.wikipedia}"
    
    print(f"数据源: {data_source_type}")
    print(f"  {data_source_desc}")
    print(f"表名: {args.table_name}")
    
    if args.vectors:
        print(f"⚠️  注意：预计算向量文件的维度必须与模型维度({MODEL_DIMENSION})匹配，否则需要调整")
    else:
        print(f"文本分块: {'是' if args.chunk_size > 0 else '否'}")
        if args.chunk_size > 0:
            print(f"  分块大小: {args.chunk_size}")
            print(f"  重叠大小: {args.chunk_overlap}")
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
    
    # 处理预计算向量数据（直接加载，不需要 embedding）
    if args.vectors:
        vectors, texts = load_precomputed_vectors(args.vectors, args.count)
        actual_dimension = vectors.shape[1]
        
        # 验证维度
        if actual_dimension != MODEL_DIMENSION:
            print(f"⚠️  警告：向量维度({actual_dimension})与配置的模型维度({MODEL_DIMENSION})不一致")
            response = input(f"是否继续使用维度 {actual_dimension}？(y/n): ")
            if response.lower() != 'y':
                print("❌ 已取消操作")
                return
            actual_dimension = vectors.shape[1]
        
        print(f"\n✅ 已加载预计算向量（跳过 embedding 步骤）")
        print(f"  向量数量: {len(vectors)}")
        print(f"  向量维度: {actual_dimension}")
    
    else:
        # 文本数据需要 embedding
        # 初始化文本向量化工具
        print("\n初始化文本向量化工具...")
        embedder = TextEmbedder(use_local_only=True)
        embedder.load()
        actual_dimension = embedder.get_dimension()
        
        # 读取文本数据
        print("\n读取文本数据...")
        texts = []
        
        if args.sample:
            count = args.count if args.count else 1000  # 默认 1000
            texts = generate_sample_texts(count)
            print(f"✅ 生成了 {len(texts)} 条示例文本")
        elif args.file:
            texts = read_text_file(args.file)
            print(f"✅ 从文件读取了 {len(texts)} 条文本")
        elif args.dir:
            all_texts = []
            for file_path, content in read_text_directory(args.dir):
                if args.chunk_size > 0:
                    chunks = chunk_text(content, args.chunk_size, args.chunk_overlap)
                    all_texts.extend(chunks)
                else:
                    all_texts.append(content)
            texts = all_texts
            print(f"✅ 从目录读取了 {len(texts)} 条文本（或文本块）")
        elif args.wikipedia:
            # Wikipedia 示例（实际使用建议下载后使用 --file 或 --dir）
            wikipedia_file = download_wikipedia_sample(args.wikipedia, args.count)
            texts = read_text_file(wikipedia_file)
            print(f"✅ 从 Wikipedia 示例文件读取了 {len(texts)} 条文本")
        
        if not texts:
            print("❌ 未读取到任何文本数据！")
            return
        
        # 限制数量（如果指定）
        if args.count and len(texts) > args.count:
            texts = texts[:args.count]
            print(f"📝 限制为 {len(texts)} 条文本")
        
        # 生成向量
        print(f"\n生成向量（使用模型: {embedder.model_name}）...")
        print(f"文本数量: {len(texts)}")
        print(f"向量维度: {actual_dimension}")
        
        vectors = embedder.encode(
            texts,
            batch_size=args.embedding_batch_size,
            show_progress_bar=True
        )
        
        print(f"✅ 生成了 {len(vectors)} 个向量")
    
    # 创建表
    print("\n创建测试表...")
    create_test_table(client, args.table_name, actual_dimension, args.drop_existing)
    
    # 插入数据
    print("\n插入向量数据到数据库...")
    insert_text_vectors_batch(
        client, args.table_name, texts, vectors,
        args.batch_size, verbose=True
    )
    
    # 验证数据
    if not args.no_verify:
        verify_data(client, args.table_name)
    
    print("\n✅ 数据生成完成！")
    print("\n💡 提示：")
    print("   - 现在可以使用真实数据测试索引性能")
    print("   - 使用 performance_testing/test_hnsw_index.py 测试索引")
    print("   - 使用 performance_testing/query_accuracy.py 评估查询精度")


if __name__ == "__main__":
    main()

