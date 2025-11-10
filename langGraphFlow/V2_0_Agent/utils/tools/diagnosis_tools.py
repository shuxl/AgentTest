"""
诊断工具实现
包含RAG检索工具 retrieve_diagnosis_knowledge
"""
import logging
from typing import Optional, Dict, Any
from langchain_core.tools import tool

from ..rag.knowledge_base_manager import KnowledgeBaseManager

logger = logging.getLogger(__name__)


@tool("retrieve_diagnosis_knowledge", description="检索诊断相关知识库，获取相关医学知识、病例和指南")
def retrieve_diagnosis_knowledge(
    query: str,
    department: str,
    top_k: int = 5,
    filter_metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    检索诊断相关知识
    
    Args:
        query: 检索查询（患者症状、检查结果等）
        department: 科室类型（internal_medicine/surgery/pediatrics等）
        top_k: 返回Top-K相关文档（默认5）
        filter_metadata: 元数据过滤条件（如知识来源、更新时间等）
    
    Returns:
        str: 格式化的相关知识文档
    """
    try:
        # 获取知识库管理器
        kb_manager = KnowledgeBaseManager(department=department)
        
        # 合并过滤条件
        search_filter = filter_metadata.copy() if filter_metadata else {}
        search_filter['department'] = department
        
        # 执行检索
        results = kb_manager.retrieve_knowledge(
            query=query,
            top_k=top_k,
            threshold=None,  # 不设置阈值，返回top_k结果
            filter_metadata=search_filter
        )
        
        if not results:
            return "未找到相关知识，将基于通用医学知识提供诊断建议。"
        
        # 格式化返回结果
        formatted_result = "检索到的相关知识：\n\n"
        for i, doc_info in enumerate(results, 1):
            formatted_result += f"[{i}] {doc_info['content']}\n"
            formatted_result += f"来源：{doc_info.get('source', '未知')}\n"
            formatted_result += f"相关性得分：{doc_info.get('similarity', 0):.3f}\n\n"
        
        return formatted_result
        
    except Exception as e:
        logger.error(f"RAG检索失败: {e}", exc_info=True)
        return "知识库检索暂时不可用，将基于通用医学知识提供诊断建议。"


def get_diagnosis_tools(department: str) -> list:
    """
    获取诊断智能体的工具列表
    
    Args:
        department: 科室类型
    
    Returns:
        list: 工具列表
    """
    return [retrieve_diagnosis_knowledge]

