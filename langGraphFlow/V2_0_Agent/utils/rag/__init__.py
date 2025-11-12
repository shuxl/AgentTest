"""
RAG工具模块（向后兼容层）
此模块已迁移到 domain.rag，保留此文件以保持向后兼容
建议新代码使用：from domain.rag import ...
"""
import warnings
from domain.rag import (
    DocumentLoader,
    TextSplitter,
    EmbeddingService,
    get_embedding_service,
    VectorStore,
    RAGRetriever,
    KnowledgeBaseManager,
    get_knowledge_base_manager
)

# 发出警告，提示使用新模块
warnings.warn(
    "utils.rag 已迁移到 domain.rag，"
    "建议使用：from domain.rag import ...",
    DeprecationWarning,
    stacklevel=2
)

__all__ = [
    'DocumentLoader',
    'TextSplitter',
    'EmbeddingService',
    'get_embedding_service',
    'VectorStore',
    'RAGRetriever',
    'KnowledgeBaseManager',
    'get_knowledge_base_manager'
]

