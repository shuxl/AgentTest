"""
RAG检索工具
完整的RAG检索流程：文档入库 -> 向量化 -> 检索
"""
from typing import List, Dict, Any, Optional
import logging

from .document_loader import DocumentLoader
from .text_splitter import TextSplitter
from .embedding_service import EmbeddingService
from .vector_store import VectorStore

logger = logging.getLogger(__name__)


class RAGRetriever:
    """
    RAG检索工具类
    提供完整的RAG检索流程
    """
    
    def __init__(
        self,
        table_name: str = "rag_documents",
        chunk_size: int = 200,
        chunk_overlap: int = 50,
        embedding_model_name: str = "moka-ai/m3e-base",
        db_uri: Optional[str] = None
    ):
        """
        初始化RAG检索工具
        
        Args:
            table_name: 向量数据库表名
            chunk_size: 文档分块大小
            chunk_overlap: 文档分块重叠大小
            embedding_model_name: Embedding模型名称
            db_uri: 数据库连接URI，默认使用Config.DB_URI
        """
        self.table_name = table_name
        self.document_loader = DocumentLoader()
        self.text_splitter = TextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        self.embedding_service = EmbeddingService(model_name=embedding_model_name)
        self.vector_store = VectorStore(db_uri=db_uri)
        
        # 确保模型已加载
        self.embedding_service.load_model()
        self.dimension = self.embedding_service.get_dimension()
    
    def initialize_table(self, drop_if_exists: bool = False) -> bool:
        """
        初始化向量数据库表
        
        Args:
            drop_if_exists: 如果表已存在，是否删除重建
        
        Returns:
            bool: 是否初始化成功
        """
        try:
            # 检查数据库连接
            if not self.vector_store.test_connection():
                logger.error("数据库连接失败")
                return False
            
            # 检查pgvector扩展
            if not self.vector_store.check_extension('vector'):
                logger.error("pgvector扩展未安装")
                return False
            
            # 创建表
            if not self.vector_store.create_table(
                self.table_name,
                dimension=self.dimension,
                drop_if_exists=drop_if_exists
            ):
                return False
            
            # 创建索引
            if not self.vector_store.create_index(self.table_name, index_type="hnsw"):
                logger.warning("索引创建失败，但表已创建")
            
            logger.info(f"向量数据库表 {self.table_name} 初始化成功")
            return True
        except Exception as e:
            logger.error(f"初始化表失败: {str(e)}")
            return False
    
    def add_document(
        self,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        添加单个文档到知识库
        
        Args:
            file_path: 文档文件路径
            metadata: 文档元数据（可选）
        
        Returns:
            int: 插入的块数量
        """
        try:
            # 1. 读取文档
            doc = self.document_loader.load_document(file_path)
            
            # 2. 分块
            chunks = self.text_splitter.split_text(doc['content'])
            
            if not chunks:
                logger.warning(f"文档分块后为空: {file_path}")
                return 0
            
            # 3. 向量化
            embeddings = self.embedding_service.encode_batch(chunks)
            
            # 4. 准备元数据
            if metadata is None:
                metadata = {}
            metadata.update({
                'source_file': doc['file_path'],
                'source_file_name': doc['file_name'],
                'source_file_type': doc['file_type']
            })
            
            # 5. 批量插入
            contents = chunks
            metadata_list = [
                {
                    **metadata,
                    'chunk_index': i,
                    'total_chunks': len(chunks)
                }
                for i in range(len(chunks))
            ]
            
            inserted_count = self.vector_store.batch_insert(
                self.table_name,
                contents,
                embeddings,
                metadata_list
            )
            
            logger.info(f"文档添加成功: {file_path}, 共插入 {inserted_count} 个块")
            return inserted_count
        except Exception as e:
            logger.error(f"添加文档失败: {str(e)}")
            raise
    
    def add_documents_batch(
        self,
        file_paths: List[str],
        metadata_list: Optional[List[Dict[str, Any]]] = None
    ) -> int:
        """
        批量添加文档到知识库
        
        Args:
            file_paths: 文档文件路径列表
            metadata_list: 文档元数据列表（可选）
        
        Returns:
            int: 插入的总块数量
        """
        total_inserted = 0
        
        for i, file_path in enumerate(file_paths):
            metadata = metadata_list[i] if metadata_list and i < len(metadata_list) else None
            try:
                inserted = self.add_document(file_path, metadata=metadata)
                total_inserted += inserted
            except Exception as e:
                logger.error(f"批量添加文档时失败: {file_path}, {str(e)}")
                # 继续处理下一个文档
                continue
        
        logger.info(f"批量添加文档完成，共插入 {total_inserted} 个块")
        return total_inserted
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        threshold: Optional[float] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        检索相关知识
        
        Args:
            query: 查询文本
            top_k: 返回Top-K相关文档
            threshold: 相似度阈值（0-1之间），只返回相似度大于阈值的记录
            filter_metadata: 元数据过滤条件（可选）
        
        Returns:
            List[Dict]: 检索结果列表，每个结果包含：
                - content: 文档内容
                - similarity: 相似度得分
                - metadata: 元数据
                - id: 记录ID
        """
        try:
            # 1. 查询向量化
            query_vector = self.embedding_service.encode(query)
            
            # 2. 构建WHERE条件
            where_clause = None
            if filter_metadata:
                conditions = []
                for key, value in filter_metadata.items():
                    conditions.append(f"metadata->>'{key}' = '{value}'")
                if conditions:
                    where_clause = " AND ".join(conditions)
            
            # 3. 执行相似度搜索
            results = self.vector_store.cosine_search(
                self.table_name,
                query_vector,
                limit=top_k,
                threshold=threshold,
                where_clause=where_clause
            )
            
            # 4. 格式化结果
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'id': result['id'],
                    'content': result['content'],
                    'similarity': float(result['similarity']),
                    'metadata': result.get('metadata', {}),
                    'source': result.get('metadata', {}).get('source_file_name', '未知')
                })
            
            logger.debug(f"检索完成: 查询='{query}', 返回 {len(formatted_results)} 条结果")
            return formatted_results
        except Exception as e:
            logger.error(f"检索失败: {str(e)}")
            raise
    
    def delete_document(self, record_id: int) -> bool:
        """
        删除文档块
        
        Args:
            record_id: 记录ID
        
        Returns:
            bool: 是否删除成功
        """
        return self.vector_store.delete_vector(self.table_name, record_id)
    
    def get_document_count(self) -> int:
        """
        获取知识库中的文档块总数
        
        Returns:
            int: 文档块总数
        """
        try:
            with self.vector_store.get_connection() as conn:
                cur = conn.cursor()
                cur.execute(f"SELECT COUNT(*) FROM {self.table_name}")
                count = cur.fetchone()[0]
                return count
        except Exception as e:
            logger.error(f"获取文档数量失败: {str(e)}")
            return 0


if __name__ == "__main__":
    """
    测试代码
    """
    import sys
    from pathlib import Path
    
    # 添加项目根目录到路径
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    print("=" * 60)
    print("RAG检索工具测试")
    print("=" * 60)
    
    # 创建RAG检索器
    retriever = RAGRetriever(table_name="test_rag_documents")
    
    # 初始化表
    print("\n初始化向量数据库表...")
    if retriever.initialize_table(drop_if_exists=True):
        print("✅ 表初始化成功")
    else:
        print("❌ 表初始化失败")
        exit(1)
    
    # 添加测试文档
    print("\n添加测试文档...")
    test_data_dir = Path(__file__).parent.parent.parent / "rag_env_check" / "test_data"
    md_file = test_data_dir / "test_medical.md"
    
    if md_file.exists():
        try:
            inserted = retriever.add_document(str(md_file))
            print(f"✅ 文档添加成功，共插入 {inserted} 个块")
        except Exception as e:
            print(f"❌ 文档添加失败: {str(e)}")
    
    # 执行检索
    print("\n执行检索测试...")
    queries = [
        "高血压的症状有哪些",
        "如何诊断疾病"
    ]
    
    for query in queries:
        print(f"\n查询: {query}")
        results = retriever.retrieve(query, top_k=3)
        for i, result in enumerate(results, 1):
            print(f"  {i}. [相似度: {result['similarity']:.4f}] {result['source']}")
            print(f"     {result['content'][:80]}...")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)

