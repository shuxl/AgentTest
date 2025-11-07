"""
文本向量化工具
使用 sentence-transformers 进行文本嵌入
"""

import os
import sys
from pathlib import Path
from typing import Union, List
import numpy as np
from sentence_transformers import SentenceTransformer
from sentence_transformers import util
from config import MODEL_NAME, MODEL_DIMENSION

# Hugging Face 镜像地址（国内加速）
HF_ENDPOINT = "https://hf-mirror.com"


class TextEmbedder:
    """
    文本向量化工具类
    使用已下载的 m3e-base 模型进行文本嵌入
    优先使用本地缓存，避免每次访问网络
    """
    
    def __init__(self, model_name: str = None, use_local_only: bool = True):
        """
        初始化文本向量化工具
        
        Args:
            model_name: 模型名称，默认使用配置文件中的模型
            use_local_only: 是否只使用本地缓存（True：强制使用本地，False：允许联网检查更新）
        """
        if model_name is None:
            model_name = MODEL_NAME
        
        self.model_name = model_name
        self.dimension = MODEL_DIMENSION
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
            # 方法1：直接尝试加载，如果成功则说明已缓存
            # 这是最可靠的方法
            from sentence_transformers import SentenceTransformer
            try:
                # 尝试以本地模式加载，如果失败说明未缓存
                test_model = SentenceTransformer(self.model_name, local_files_only=True)
                # 加载成功，说明已缓存
                return True
            except (FileNotFoundError, OSError):
                # 加载失败，说明未缓存
                return False
            except Exception:
                # 其他错误，可能是部分文件存在但损坏
                return False
        except Exception:
            # 如果检查过程出错，返回 False
            return False
    
    def load(self):
        """
        加载模型
        优先使用本地缓存，避免网络访问
        """
        if self._model is None:
            print(f"正在加载模型: {self.model_name}")
            
            # 如果启用本地优先模式，先检查缓存
            if self.use_local_only:
                print("检查本地模型缓存...")
                cache_exists = self._check_model_cache()
                if not cache_exists:
                    print("⚠️  本地缓存未找到，尝试使用联网模式加载（使用镜像）...")
                    # 如果本地模式失败，自动切换到联网模式（使用镜像）
                    self.use_local_only = False
                else:
                    print("✅ 检测到本地模型缓存，使用本地模式加载（不访问网络）")
            
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
                    print(f"⚠️  警告: 配置的模型维度({self.dimension})与实际模型维度({actual_dim})不一致")
                    print(f"已自动更新为实际维度: {actual_dim}")
                    self.dimension = actual_dim
                
                print(f"✅ 模型加载成功，维度: {self.dimension}")
            except FileNotFoundError as e:
                print(f"❌ 模型加载失败: {str(e)}")
                if self.use_local_only:
                    print("\n提示:")
                    print("1. 模型未找到，请先下载模型")
                    print("2. 或者将 use_local_only=False 以允许联网下载")
                raise
            except Exception as e:
                print(f"❌ 模型加载失败: {str(e)}")
                raise
    
    @property
    def model(self) -> SentenceTransformer:
        """
        获取模型对象（懒加载）
        
        Returns:
            SentenceTransformer: 模型对象
        """
        if self._model is None:
            self.load()
        return self._model
    
    def encode(self, text: Union[str, List[str]], 
               batch_size: int = 32,
               show_progress_bar: bool = False) -> np.ndarray:
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
            self.load()
        return self.dimension
    
    def __repr__(self):
        return f"TextEmbedder(model='{self.model_name}', dimension={self.dimension})"


# 全局单例实例（可选）
_global_embedder = None

def get_embedder() -> TextEmbedder:
    """
    获取全局文本向量化工具实例（单例模式）
    
    Returns:
        TextEmbedder: 工具实例
    """
    global _global_embedder
    if _global_embedder is None:
        _global_embedder = TextEmbedder()
    return _global_embedder


if __name__ == "__main__":
    """
    测试代码
    """
    print("="*60)
    print("文本向量化测试")
    print("="*60)
    
    # 创建向量化工具实例
    embedder = TextEmbedder()
    print(f"\n模型信息: {embedder}")
    
    # 加载模型
    print("\n加载模型...")
    embedder.load()
    
    # 测试单个文本编码
    print("\n测试单个文本编码...")
    text1 = "这是一个测试文本"
    vector1 = embedder.encode(text1)
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
    vectors = embedder.encode(texts)
    print(f"文本数量: {len(texts)}")
    print(f"向量形状: {vectors.shape}")
    
    # 测试相似度
    print("\n测试相似度计算...")
    text2 = "这是另一个测试文本"
    vector2 = embedder.encode(text2)
    
    # 余弦相似度
    similarity = np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))
    print(f"文本1: {text1}")
    print(f"文本2: {text2}")
    print(f"余弦相似度: {similarity:.4f}")
    
    print("\n" + "="*60)
    print("✅ 测试完成！")
    print("="*60)

