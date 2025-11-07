"""
文档检索系统
完整的文档向量化、存储和检索功能
"""

from typing import Optional, List, Dict, Any
from db_utils import PgVectorClient
from vector_ops import VectorOperations
from embedding_utils import TextEmbedder
from config import MODEL_DIMENSION


class DocumentSearch:
    """
    文档检索系统
    支持文档的向量化、存储和相似度搜索
    """
    
    def __init__(self, db_client: PgVectorClient, embedder: TextEmbedder):
        """
        初始化文档检索系统
        
        Args:
            db_client: 数据库客户端
            embedder: 文本向量化工具
        """
        self.vector_ops = VectorOperations(db_client)
        self.embedder = embedder
        self.table_name = "documents"
    
    def create_table_if_not_exists(self, drop_if_exists: bool = False):
        """
        创建文档表（如果不存在）
        
        Args:
            drop_if_exists: 如果表已存在但维度不匹配，是否删除重建
        """
        # 检查表是否已存在
        check_query = """
        SELECT EXISTS(
            SELECT 1 FROM information_schema.tables 
            WHERE table_name = %s
        ) as exists;
        """
        result = self.vector_ops.client.execute_query(check_query, (self.table_name,))
        table_exists = result[0]['exists'] if result else False
        
        if table_exists:
            # 检查现有表的维度
            try:
                # 尝试从表定义中获取维度信息
                type_query = f"""
                SELECT 
                    CASE 
                        WHEN atttypmod != -1 THEN atttypmod - 4
                        ELSE NULL
                    END as dimension
                FROM pg_attribute 
                WHERE attrelid = '{self.table_name}'::regclass 
                AND attname = 'embedding';
                """
                dim_result = self.vector_ops.client.execute_query(type_query)
                if dim_result and dim_result[0].get('dimension'):
                    existing_dim = dim_result[0]['dimension']
                    if existing_dim != MODEL_DIMENSION:
                        if drop_if_exists:
                            print(f"⚠️  表 {self.table_name} 已存在但维度不匹配（现有: {existing_dim}, 需要: {MODEL_DIMENSION}）")
                            print(f"正在删除旧表并重建...")
                            drop_query = f"DROP TABLE IF EXISTS {self.table_name} CASCADE;"
                            self.vector_ops.client.execute_update(drop_query)
                            print(f"✅ 旧表已删除")
                        else:
                            raise ValueError(
                                f"表 {self.table_name} 已存在但维度不匹配！\n"
                                f"现有维度: {existing_dim}, 需要维度: {MODEL_DIMENSION}\n"
                                f"请删除表或使用 drop_if_exists=True 参数自动重建"
                            )
                    else:
                        print(f"✅ 表 {self.table_name} 已存在且维度匹配")
                        return
            except Exception as e:
                # 如果查询失败，尝试创建表（可能表结构不完整）
                print(f"⚠️  无法检查表维度: {str(e)}")
                if drop_if_exists:
                    print(f"正在删除旧表并重建...")
                    drop_query = f"DROP TABLE IF EXISTS {self.table_name} CASCADE;"
                    self.vector_ops.client.execute_update(drop_query)
        
        # 创建表
        query = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            id SERIAL PRIMARY KEY,
            title TEXT,
            content TEXT NOT NULL,
            embedding vector({MODEL_DIMENSION}),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        self.vector_ops.client.execute_update(query)
        print(f"✅ 表 {self.table_name} 已创建")
    
    def create_index_if_not_exists(self, index_type: str = "hnsw"):
        """
        创建向量索引（如果不存在）
        
        Args:
            index_type: 索引类型，'hnsw' 或 'ivfflat'
        """
        index_name = f"{self.table_name}_embedding_{index_type}_idx"
        
        # 检查索引是否已存在
        check_query = """
        SELECT EXISTS(
            SELECT 1 FROM pg_indexes 
            WHERE indexname = %s
        ) as exists;
        """
        result = self.vector_ops.client.execute_query(check_query, (index_name,))
        if result and result[0]['exists']:
            print(f"✅ 索引 {index_name} 已存在")
            return
        
        if index_type.lower() == "hnsw":
            query = f"""
            CREATE INDEX {index_name} ON {self.table_name} 
            USING hnsw (embedding vector_cosine_ops)
            WITH (m = 16, ef_construction = 64);
            """
        elif index_type.lower() == "ivfflat":
            query = f"""
            CREATE INDEX {index_name} ON {self.table_name} 
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100);
            """
        else:
            raise ValueError(f"不支持的索引类型: {index_type}")
        
        print(f"正在创建 {index_type.upper()} 索引...")
        self.vector_ops.client.execute_update(query)
        print(f"✅ 索引 {index_name} 创建成功")
    
    def add_document(self, content: str, title: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        添加文档
        
        Args:
            content: 文档内容
            title: 文档标题（可选）
            metadata: 其他元数据（可选）
        
        Returns:
            int: 受影响的行数
        """
        # 向量化文档内容
        vector = self.embedder.encode(content)
        
        # 构建数据字典
        data = {'content': content}
        if title:
            data['title'] = title
        if metadata:
            data.update(metadata)
        
        # 插入数据库
        return self.vector_ops.insert_vector(self.table_name, data, vector)
    
    def add_documents_batch(self, documents: List[Dict[str, str]], 
                           titles: Optional[List[str]] = None) -> int:
        """
        批量添加文档
        
        Args:
            documents: 文档列表，每个文档是一个包含 'content' 的字典
            titles: 标题列表（可选，长度需与 documents 相同）
        
        Returns:
            int: 插入的总行数
        """
        if titles and len(titles) != len(documents):
            raise ValueError("标题数量必须与文档数量相同")
        
        # 提取所有文档内容
        contents = [doc['content'] for doc in documents]
        
        # 批量向量化
        vectors = self.embedder.encode_batch(contents)
        
        # 构建数据列表
        data_list = []
        for i, doc in enumerate(documents):
            data = {'content': doc['content']}
            if titles:
                data['title'] = titles[i]
            if 'title' in doc:
                data['title'] = doc['title']
            # 添加其他元数据
            for key, value in doc.items():
                if key != 'content':
                    data[key] = value
            data_list.append(data)
        
        # 批量插入
        return self.vector_ops.batch_insert(self.table_name, data_list, vectors)
    
    def search(self, query: str, limit: int = 5, threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        搜索相关文档
        
        Args:
            query: 查询文本
            limit: 返回结果数量上限
            threshold: 相似度阈值（0-1之间），只返回相似度大于阈值的记录
        
        Returns:
            List[Dict]: 搜索结果列表，包含 similarity 字段
        """
        # 向量化查询文本
        query_vector = self.embedder.encode(query)
        
        # 执行相似度搜索
        results = self.vector_ops.cosine_search(
            self.table_name, 
            query_vector, 
            limit=limit,
            threshold=threshold
        )
        
        return results
    
    def get_all_documents(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        获取所有文档
        
        Args:
            limit: 返回数量限制（可选）
        
        Returns:
            List[Dict]: 文档列表
        """
        query = f"SELECT * FROM {self.table_name} ORDER BY id"
        if limit:
            query += f" LIMIT {limit}"
        
        return self.vector_ops.client.execute_query(query)
    
    def delete_document(self, doc_id: int) -> int:
        """
        删除文档
        
        Args:
            doc_id: 文档ID
        
        Returns:
            int: 受影响的行数
        """
        return self.vector_ops.delete_vector(self.table_name, doc_id)


if __name__ == "__main__":
    """
    简单测试示例
    """
    from config import DB_CONFIG
    
    print("="*60)
    print("文档检索系统测试")
    print("="*60)
    
    # 创建组件
    client = PgVectorClient(**DB_CONFIG)
    embedder = TextEmbedder()
    doc_search = DocumentSearch(client, embedder)
    
    # 测试数据库连接
    print("\n测试数据库连接...")
    if not client.test_connection():
        print("❌ 数据库连接失败，请检查配置")
        exit(1)
    print("✅ 数据库连接成功")
    
    # 检查 pgvector 扩展
    print("\n检查 pgvector 扩展...")
    if not client.check_extension('vector'):
        print("❌ pgvector 扩展未安装")
        print("请在数据库中执行: CREATE EXTENSION IF NOT EXISTS vector;")
        exit(1)
    print("✅ pgvector 扩展已安装")
    
    # 创建表和索引
    print("\n初始化数据库表...")
    # 如果表已存在但维度不匹配，自动删除重建
    doc_search.create_table_if_not_exists(drop_if_exists=True)
    doc_search.create_index_if_not_exists("hnsw")
    
    # 添加测试文档
    print("\n添加测试文档...")
    test_docs = [
        {"content": "Python 是一种高级编程语言，广泛用于数据科学和人工智能领域。"},
        {"content": "PostgreSQL 是一个功能强大的开源关系型数据库管理系统。"},
        {"content": "向量数据库专门用于存储和检索高维向量数据，适合相似度搜索。"},
        {"content": "机器学习是人工智能的一个分支，通过算法让计算机从数据中学习。"},
        {"content": "深度学习使用神经网络来模拟人脑的学习过程，在图像识别等领域表现优异。"}
    ]
    
    for i, doc in enumerate(test_docs, 1):
        doc_search.add_document(doc['content'], title=f"文档{i}")
        print(f"  已添加: {doc['content'][:30]}...")
    
    # 执行搜索
    print("\n执行搜索测试...")
    queries = [
        "数据库管理系统",
        "人工智能和机器学习",
        "编程语言"
    ]
    
    for query in queries:
        print(f"\n查询: {query}")
        results = doc_search.search(query, limit=3)
        for i, result in enumerate(results, 1):
            print(f"  {i}. [相似度: {result['similarity']:.4f}] {result['title']}")
            print(f"     {result['content'][:50]}...")
    
    print("\n" + "="*60)
    print("✅ 测试完成！")
    print("="*60)

