"""
Embedding服务
使用sentence-transformers进行文本向量化
"""
import os
from typing import Union, List
import numpy as np
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

# 默认模型配置
DEFAULT_MODEL_NAME = "moka-ai/m3e-base"
DEFAULT_MODEL_DIMENSION = 768
# Hugging Face 镜像地址（国内加速）
HF_ENDPOINT = "https://hf-mirror.com"


class EmbeddingService:
    """
    Embedding服务类
    使用sentence-transformers进行文本向量化
    """
    
    def __init__(
        self,
        model_name: str = DEFAULT_MODEL_NAME,
        use_local_only: bool = True
    ):
        """
        初始化Embedding服务
        
        Args:
            model_name: 模型名称，默认使用m3e-base
            use_local_only: 是否只使用本地缓存（True：强制使用本地，False：允许联网检查更新）
        """
        self.model_name = model_name
        self.dimension = DEFAULT_MODEL_DIMENSION
        self._model = None
        self.use_local_only = use_local_only
        
        # 设置 Hugging Face 镜像（用于可能的下载）
        os.environ['HF_ENDPOINT'] = HF_ENDPOINT
    
    def _check_model_cache(self) -> bool:
        """
        检查模型是否已缓存
        
        Returns:
            bool: 模型是否已缓存
        """
        try:
            from sentence_transformers import SentenceTransformer
            try:
                # 尝试以本地模式加载，如果失败说明未缓存
                test_model = SentenceTransformer(self.model_name, local_files_only=True)
                return True
            except (FileNotFoundError, OSError):
                return False
            except Exception:
                return False
        except Exception:
            return False
    
    def load_model(self):
        """
        加载模型
        优先使用本地缓存，避免网络访问
        """
        if self._model is None:
            logger.info(f"正在加载模型: {self.model_name}")
            
            # 如果启用本地优先模式，先检查缓存
            if self.use_local_only:
                logger.debug("检查本地模型缓存...")
                cache_exists = self._check_model_cache()
                if not cache_exists:
                    logger.warning("本地缓存未找到，尝试使用联网模式加载（使用镜像）...")
                    self.use_local_only = False
                else:
                    logger.debug("检测到本地模型缓存，使用本地模式加载（不访问网络）")
            
            try:
                # 如果启用本地模式，强制只使用本地文件
                if self.use_local_only:
                    self._model = SentenceTransformer(
                        self.model_name,
                        local_files_only=True
                    )
                else:
                    # 允许联网，但设置镜像
                    self._model = SentenceTransformer(self.model_name)
                
                # 验证模型维度
                actual_dim = self._model.get_sentence_embedding_dimension()
                if actual_dim != self.dimension:
                    logger.warning(
                        f"配置的模型维度({self.dimension})与实际模型维度({actual_dim})不一致，"
                        f"已自动更新为实际维度: {actual_dim}"
                    )
                    self.dimension = actual_dim
                
                logger.info(f"模型加载成功，维度: {self.dimension}")
            except FileNotFoundError as e:
                logger.error(f"模型加载失败: {str(e)}")
                if self.use_local_only:
                    logger.error(
                        "\n提示:\n"
                        "1. 模型未找到，请先下载模型\n"
                        "2. 或者将 use_local_only=False 以允许联网下载"
                    )
                raise
            except Exception as e:
                logger.error(f"模型加载失败: {str(e)}")
                raise
    
    @property
    def model(self) -> SentenceTransformer:
        """
        获取模型对象（懒加载）
        
        Returns:
            SentenceTransformer: 模型对象
        """
        if self._model is None:
            self.load_model()
        return self._model
    
    def encode(
        self,
        text: Union[str, List[str]],
        batch_size: int = 32,
        show_progress_bar: bool = False
    ) -> np.ndarray:
        """
        将文本编码为向量
        
        Args:
            text: 单个文本字符串或文本列表
            batch_size: 批量编码时的批次大小
            show_progress_bar: 是否显示进度条
        
        Returns:
            numpy.ndarray: 向量数组
                - 单个文本: shape (dimension,)
                - 多个文本: shape (n, dimension)
        """
        if isinstance(text, str):
            # 单个文本
            vector = self.model.encode(text, show_progress_bar=show_progress_bar)
            return vector
        else:
            # 多个文本，批量编码
            vectors = self.model.encode(
                text,
                batch_size=batch_size,
                show_progress_bar=show_progress_bar
            )
            return vectors
    
    def encode_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        批量编码文本
        
        Args:
            texts: 文本列表
            batch_size: 批次大小
        
        Returns:
            numpy.ndarray: 向量数组，shape (n, dimension)
        """
        return self.encode(texts, batch_size=batch_size)
    
    def get_dimension(self) -> int:
        """
        获取模型输出维度
        
        Returns:
            int: 向量维度
        """
        if self._model is None:
            self.load_model()
        return self.dimension
    
    def __repr__(self):
        return f"EmbeddingService(model='{self.model_name}', dimension={self.dimension})"


# 全局单例实例（可选）
_global_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    """
    获取全局Embedding服务实例（单例模式）
    
    Returns:
        EmbeddingService: 服务实例
    """
    global _global_embedding_service
    if _global_embedding_service is None:
        _global_embedding_service = EmbeddingService()
    return _global_embedding_service


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
    print("Embedding服务测试")
    print("=" * 60)
    
    # 创建服务实例
    service = EmbeddingService()
    print(f"\n服务信息: {service}")
    
    # 加载模型
    print("\n加载模型...")
    service.load_model()
    
    # 测试单个文本编码
    print("\n测试单个文本编码...")
    text1 = "这是一个测试文本"
    vector1 = service.encode(text1)
    print(f"文本: {text1}")
    print(f"向量维度: {vector1.shape}")
    print(f"向量前10个值: {vector1[:10]}")
    
    # 测试多个文本批量编码
    print("\n测试批量文本编码...")
    texts = [
        "这是第一个文本",
        "这是第二个文本",
        "这是第三个文本"
    ]
    vectors = service.encode(texts)
    print(f"文本数量: {len(texts)}")
    print(f"向量形状: {vectors.shape}")
    
    # 测试相似度
    print("\n测试相似度计算...")
    text2 = "这是另一个测试文本"
    vector2 = service.encode(text2)
    
    # 余弦相似度
    similarity = np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))
    print(f"文本1: {text1}")
    print(f"文本2: {text2}")
    print(f"余弦相似度: {similarity:.4f}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)

