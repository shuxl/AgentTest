"""
文档读取工具
支持多种格式的文档读取（TXT、MD、PDF等）
"""
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class DocumentLoader:
    """
    文档读取工具类
    支持多种格式的文档读取
    """
    
    def __init__(self):
        """初始化文档读取工具"""
        self.supported_formats = {'.txt', '.md', '.markdown', '.pdf'}
        self._pdf_support = None
    
    def _check_pdf_support(self) -> bool:
        """
        检查PDF库是否可用
        
        Returns:
            bool: PDF库是否可用
        """
        if self._pdf_support is None:
            try:
                import PyPDF2
                self._pdf_support = 'PyPDF2'
            except ImportError:
                try:
                    import pdfplumber
                    self._pdf_support = 'pdfplumber'
                except ImportError:
                    self._pdf_support = False
        return self._pdf_support is not False
    
    def load_text_file(self, file_path: str, encoding: str = 'utf-8') -> str:
        """
        读取文本文件（TXT、MD等）
        
        Args:
            file_path: 文件路径
            encoding: 文件编码，默认utf-8
        
        Returns:
            str: 文件内容
        
        Raises:
            FileNotFoundError: 文件不存在
            UnicodeDecodeError: 编码错误
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            logger.debug(f"成功读取文本文件: {file_path}, 大小: {len(content)}字符")
            return content
        except UnicodeDecodeError as e:
            logger.error(f"文件编码错误: {file_path}, {str(e)}")
            raise
    
    def load_pdf_file(self, file_path: str) -> str:
        """
        读取PDF文件
        
        Args:
            file_path: PDF文件路径
        
        Returns:
            str: PDF文件内容（提取的文本）
        
        Raises:
            FileNotFoundError: 文件不存在
            ImportError: PDF库未安装
        """
        if not self._check_pdf_support():
            raise ImportError(
                "PDF库未安装，请安装 PyPDF2 或 pdfplumber:\n"
                "pip install PyPDF2 或 pip install pdfplumber"
            )
        
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        try:
            if self._pdf_support == 'PyPDF2':
                import PyPDF2
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    text_parts = []
                    for page in pdf_reader.pages:
                        text_parts.append(page.extract_text())
                    content = '\n\n'.join(text_parts)
            
            elif self._pdf_support == 'pdfplumber':
                import pdfplumber
                with pdfplumber.open(file_path) as pdf:
                    text_parts = []
                    for page in pdf.pages:
                        text_parts.append(page.extract_text())
                    content = '\n\n'.join(text_parts)
            
            logger.debug(f"成功读取PDF文件: {file_path}, 大小: {len(content)}字符")
            return content
        except Exception as e:
            logger.error(f"PDF文件读取失败: {file_path}, {str(e)}")
            raise
    
    def load_document(self, file_path: str, encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        根据文件扩展名自动选择读取方法
        
        Args:
            file_path: 文件路径
            encoding: 文本文件编码，默认utf-8
        
        Returns:
            dict: 包含文件信息的字典
                - content: 文件内容
                - file_path: 文件路径
                - file_name: 文件名
                - file_type: 文件类型
                - file_size: 文件大小（字符数）
        
        Raises:
            ValueError: 不支持的文件格式
            FileNotFoundError: 文件不存在
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        file_ext = file_path.suffix.lower()
        file_name = file_path.name
        
        if file_ext not in self.supported_formats:
            raise ValueError(
                f"不支持的文件格式: {file_ext}\n"
                f"支持的格式: {', '.join(self.supported_formats)}"
            )
        
        # 根据文件类型选择读取方法
        if file_ext == '.pdf':
            content = self.load_pdf_file(str(file_path))
        else:
            content = self.load_text_file(str(file_path), encoding=encoding)
        
        return {
            'content': content,
            'file_path': str(file_path),
            'file_name': file_name,
            'file_type': file_ext,
            'file_size': len(content)
        }
    
    def load_documents_batch(self, file_paths: List[str], encoding: str = 'utf-8') -> List[Dict[str, Any]]:
        """
        批量读取文档
        
        Args:
            file_paths: 文件路径列表
            encoding: 文本文件编码，默认utf-8
        
        Returns:
            List[Dict]: 文档信息列表
        
        Raises:
            ValueError: 如果某个文件读取失败
        """
        results = []
        errors = []
        
        for file_path in file_paths:
            try:
                doc = self.load_document(file_path, encoding=encoding)
                results.append(doc)
            except Exception as e:
                error_msg = f"文件读取失败: {file_path}, 错误: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        if errors:
            raise ValueError(f"批量读取文档时发生错误:\n" + "\n".join(errors))
        
        return results
    
    def get_supported_formats(self) -> List[str]:
        """
        获取支持的文件格式列表
        
        Returns:
            List[str]: 支持的文件格式列表
        """
        formats = list(self.supported_formats)
        if not self._check_pdf_support():
            formats.remove('.pdf')
        return formats


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
    print("文档读取工具测试")
    print("=" * 60)
    
    loader = DocumentLoader()
    print(f"\n支持的文件格式: {', '.join(loader.get_supported_formats())}")
    
    # 测试读取MD文件
    test_data_dir = Path(__file__).parent.parent.parent / "rag_env_check" / "test_data"
    md_file = test_data_dir / "test_medical.md"
    
    if md_file.exists():
        print(f"\n测试读取MD文件: {md_file}")
        try:
            doc = loader.load_document(str(md_file))
            print(f"✅ 文件读取成功")
            print(f"  文件名: {doc['file_name']}")
            print(f"  文件类型: {doc['file_type']}")
            print(f"  文件大小: {doc['file_size']}字符")
            print(f"  内容预览: {doc['content'][:100]}...")
        except Exception as e:
            print(f"❌ 文件读取失败: {str(e)}")
    
    print("\n" + "=" * 60)

