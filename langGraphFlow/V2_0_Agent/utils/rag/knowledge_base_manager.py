"""
知识库管理工具
用于管理不同科室的知识库，包括文档入库、更新、查询等功能
"""
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from .rag_retriever import RAGRetriever

logger = logging.getLogger(__name__)


class KnowledgeBaseManager:
    """
    知识库管理工具类
    用于管理不同科室的知识库
    """
    
    # 科室与表名映射
    DEPARTMENT_TABLE_MAP = {
        'internal_medicine': 'internal_medicine_kb',
        'surgery': 'surgery_kb',
        'pediatrics': 'pediatrics_kb',
        'gynecology': 'gynecology_kb',
        'cardiology': 'cardiology_kb',
        'neurology': 'neurology_kb',
        'dermatology': 'dermatology_kb',
        'general': 'general_diagnosis_kb'
    }
    
    def __init__(self, department: str, chunk_size: int = 300, chunk_overlap: int = 50):
        """
        初始化知识库管理器
        
        Args:
            department: 科室类型（internal_medicine/surgery等）
            chunk_size: 文档分块大小
            chunk_overlap: 文档分块重叠大小
        """
        if department not in self.DEPARTMENT_TABLE_MAP:
            raise ValueError(
                f"不支持的科室类型: {department}\n"
                f"支持的科室: {', '.join(self.DEPARTMENT_TABLE_MAP.keys())}"
            )
        
        self.department = department
        self.table_name = self.DEPARTMENT_TABLE_MAP[department]
        
        # 创建RAG检索器
        self.retriever = RAGRetriever(
            table_name=self.table_name,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
    
    def initialize_knowledge_base(self, drop_if_exists: bool = False) -> bool:
        """
        初始化知识库（创建表和索引）
        
        Args:
            drop_if_exists: 如果表已存在，是否删除重建
        
        Returns:
            bool: 是否初始化成功
        """
        return self.retriever.initialize_table(drop_if_exists=drop_if_exists)
    
    def add_document(
        self,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        添加文档到知识库
        
        Args:
            file_path: 文档文件路径
            metadata: 文档元数据（可选）
        
        Returns:
            int: 插入的块数量
        """
        if metadata is None:
            metadata = {}
        
        # 添加科室信息
        metadata['department'] = self.department
        metadata.setdefault('source_type', 'medical_guideline')
        
        return self.retriever.add_document(file_path, metadata=metadata)
    
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
        if metadata_list is None:
            metadata_list = []
        
        # 为每个文档添加科室信息
        for metadata in metadata_list:
            metadata['department'] = self.department
            metadata.setdefault('source_type', 'medical_guideline')
        
        return self.retriever.add_documents_batch(file_paths, metadata_list=metadata_list)
    
    def retrieve_knowledge(
        self,
        query: str,
        top_k: int = 5,
        threshold: Optional[float] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        检索知识库
        
        Args:
            query: 查询文本
            top_k: 返回Top-K相关文档
            threshold: 相似度阈值
            filter_metadata: 元数据过滤条件
        
        Returns:
            List[Dict]: 检索结果列表
        """
        return self.retriever.retrieve(
            query=query,
            top_k=top_k,
            threshold=threshold,
            filter_metadata=filter_metadata
        )
    
    def get_document_count(self) -> int:
        """
        获取知识库中的文档块总数
        
        Returns:
            int: 文档块总数
        """
        return self.retriever.get_document_count()
    
    def build_knowledge_base_from_directory(
        self,
        directory_path: str,
        file_extensions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        从目录批量构建知识库
        
        Args:
            directory_path: 文档目录路径
            file_extensions: 文件扩展名列表（如['.md', '.txt', '.pdf']），None表示所有支持格式
        
        Returns:
            Dict: 构建结果统计
        """
        if file_extensions is None:
            file_extensions = ['.md', '.txt', '.pdf']
        
        doc_dir = Path(directory_path)
        if not doc_dir.exists():
            raise FileNotFoundError(f"目录不存在: {directory_path}")
        
        # 收集所有文件
        all_files = []
        for ext in file_extensions:
            all_files.extend(list(doc_dir.glob(f"**/*{ext}")))
        
        if not all_files:
            logger.warning(f"目录中未找到文件: {directory_path}")
            return {
                'total_files': 0,
                'success_files': 0,
                'failed_files': 0,
                'total_chunks': 0
            }
        
        # 批量添加文档
        file_paths = [str(f) for f in all_files]
        metadata_list = [
            {
                'department': self.department,
                'source_type': 'medical_guideline',
                'file_name': f.name,
                'file_path': str(f)
            }
            for f in all_files
        ]
        
        total_chunks = 0
        success_files = 0
        failed_files = 0
        
        for file_path, metadata in zip(file_paths, metadata_list):
            try:
                chunks = self.add_document(file_path, metadata=metadata)
                total_chunks += chunks
                success_files += 1
                logger.info(f"✅ {Path(file_path).name}: 插入 {chunks} 个块")
            except Exception as e:
                failed_files += 1
                logger.error(f"❌ {Path(file_path).name}: {str(e)}")
        
        return {
            'total_files': len(all_files),
            'success_files': success_files,
            'failed_files': failed_files,
            'total_chunks': total_chunks
        }


def get_knowledge_base_manager(department: str) -> KnowledgeBaseManager:
    """
    获取知识库管理器实例
    
    Args:
        department: 科室类型
    
    Returns:
        KnowledgeBaseManager: 知识库管理器实例
    """
    return KnowledgeBaseManager(department=department)

