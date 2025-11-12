"""
文档分块工具
使用LangChain的文本分割器进行文档分块
"""
from typing import List, Optional, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging

logger = logging.getLogger(__name__)


class TextSplitter:
    """
    文档分块工具类
    使用LangChain的RecursiveCharacterTextSplitter进行中文文档分块
    """
    
    def __init__(
        self,
        chunk_size: int = 200,
        chunk_overlap: int = 50,
        separators: Optional[List[str]] = None
    ):
        """
        初始化文档分块工具
        
        Args:
            chunk_size: 每个块的最大字符数
            chunk_overlap: 块之间的重叠字符数
            separators: 分隔符列表，按优先级排序
                        默认: ["\n\n", "\n", "。", "，", " ", ""]
        """
        if separators is None:
            # 中文文档的分隔符优先级
            separators = ["\n\n", "\n", "。", "，", " ", ""]
        
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators
        
        # 创建文本分割器
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=separators
        )
    
    def split_text(self, text: str) -> List[str]:
        """
        将文本分割成多个块
        
        Args:
            text: 要分割的文本
        
        Returns:
            List[str]: 文本块列表
        """
        if not text or len(text.strip()) == 0:
            logger.warning("输入文本为空")
            return []
        
        try:
            chunks = self.splitter.split_text(text)
            logger.debug(f"文本分割完成: 原始长度={len(text)}字符, 块数={len(chunks)}")
            return chunks
        except Exception as e:
            logger.error(f"文本分割失败: {str(e)}")
            raise
    
    def split_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量分割文档
        
        Args:
            documents: 文档列表，每个文档是一个包含'content'字段的字典
        
        Returns:
            List[Dict]: 分割后的文档块列表，每个块包含原始文档的元数据
        """
        all_chunks = []
        
        for doc in documents:
            content = doc.get('content', '')
            if not content:
                logger.warning(f"文档缺少content字段，跳过: {doc.get('file_name', 'unknown')}")
                continue
            
            # 分割文本
            chunks = self.split_text(content)
            
            # 为每个块创建文档对象，保留原始元数据
            for i, chunk in enumerate(chunks):
                chunk_doc = {
                    'content': chunk,
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    # 保留原始文档的元数据
                    'source_file': doc.get('file_path'),
                    'source_file_name': doc.get('file_name'),
                    'source_file_type': doc.get('file_type'),
                }
                all_chunks.append(chunk_doc)
        
        logger.info(f"批量文档分割完成: {len(documents)}个文档 -> {len(all_chunks)}个块")
        return all_chunks
    
    def get_chunk_info(self, chunks: List[str]) -> Dict[str, Any]:
        """
        获取分块统计信息
        
        Args:
            chunks: 文本块列表
        
        Returns:
            Dict: 统计信息
                - total_chunks: 总块数
                - total_chars: 总字符数
                - avg_chunk_size: 平均块大小
                - max_chunk_size: 最大块大小
                - min_chunk_size: 最小块大小
        """
        if not chunks:
            return {
                'total_chunks': 0,
                'total_chars': 0,
                'avg_chunk_size': 0,
                'max_chunk_size': 0,
                'min_chunk_size': 0
            }
        
        chunk_sizes = [len(chunk) for chunk in chunks]
        
        return {
            'total_chunks': len(chunks),
            'total_chars': sum(chunk_sizes),
            'avg_chunk_size': sum(chunk_sizes) / len(chunks),
            'max_chunk_size': max(chunk_sizes),
            'min_chunk_size': min(chunk_sizes)
        }


if __name__ == "__main__":
    """
    测试代码
    """
    import sys
    from pathlib import Path
    
    # 添加项目根目录到路径
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    from domain.rag.document_loader import DocumentLoader
    
    print("=" * 60)
    print("文档分块工具测试")
    print("=" * 60)
    
    # 创建分块器
    splitter = TextSplitter(chunk_size=200, chunk_overlap=50)
    print(f"\n分块器配置:")
    print(f"  chunk_size: {splitter.chunk_size}")
    print(f"  chunk_overlap: {splitter.chunk_overlap}")
    print(f"  separators: {splitter.separators}")
    
    # 读取测试文档
    loader = DocumentLoader()
    test_data_dir = Path(__file__).parent.parent.parent / "rag_env_check" / "test_data"
    md_file = test_data_dir / "test_medical.md"
    
    if md_file.exists():
        print(f"\n读取测试文档: {md_file}")
        doc = loader.load_document(str(md_file))
        print(f"原始文档大小: {doc['file_size']}字符")
        
        # 分割文档
        print("\n分割文档...")
        chunks = splitter.split_text(doc['content'])
        
        # 显示统计信息
        info = splitter.get_chunk_info(chunks)
        print(f"\n分块统计信息:")
        print(f"  总块数: {info['total_chunks']}")
        print(f"  总字符数: {info['total_chars']}")
        print(f"  平均块大小: {info['avg_chunk_size']:.1f}字符")
        print(f"  最大块大小: {info['max_chunk_size']}字符")
        print(f"  最小块大小: {info['min_chunk_size']}字符")
        
        # 显示前3个块
        print("\n前3个块预览:")
        for i, chunk in enumerate(chunks[:3], 1):
            print(f"\n块 {i} ({len(chunk)}字符):")
            print(f"  {chunk[:100]}...")
    
    print("\n" + "=" * 60)

