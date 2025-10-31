# """
# 模型管理器
# 简单的单模型管理，负责加载和使用 embedding 模型
# """

# import os
# import sys
# from pathlib import Path
# from typing import Union, List
# import numpy as np

# # 添加 learnCoding 目录到路径（包含 config 目录的父目录）
# learn_coding_root = Path(__file__).parent.parent
# sys.path.insert(0, str(learn_coding_root))

# from config.model_config import MODEL_NAME, MODEL_DIMENSION, HF_ENDPOINT
# from sentence_transformers import SentenceTransformer


# class EmbeddingModel:
#     """
#     简单的 Embedding 模型封装类
#     固定使用配置文件中指定的模型
#     """
    
#     def __init__(self, model_name: str = None):
#         """
#         初始化模型
        
#         Args:
#             model_name: 模型名称，默认使用配置文件中的模型
#         """
#         if model_name is None:
#             model_name = MODEL_NAME
        
#         self.model_name = model_name
#         self.dimension = MODEL_DIMENSION
#         self._model = None
        
#         # 设置镜像环境变量
#         os.environ['HF_ENDPOINT'] = HF_ENDPOINT
        
#         # 延迟加载：不在初始化时加载模型
#         # 需要时调用 load() 方法加载
    
#     def load(self):
#         """
#         加载模型
#         如果模型未缓存，会自动下载
#         """
#         if self._model is None:
#             print(f"正在加载模型: {self.model_name}")
#             print(f"使用镜像: {HF_ENDPOINT}")
            
#             try:
#                 self._model = SentenceTransformer(self.model_name)
#                 # 验证模型维度
#                 actual_dim = self._model.get_sentence_embedding_dimension()
#                 if actual_dim != self.dimension:
#                     print(f"⚠️  警告: 配置的模型维度({self.dimension})与实际模型维度({actual_dim})不一致")
#                     print(f"已自动更新为实际维度: {actual_dim}")
#                     self.dimension = actual_dim
                
#                 print(f"✅ 模型加载成功，维度: {self.dimension}")
#             except Exception as e:
#                 print(f"❌ 模型加载失败: {str(e)}")
#                 raise
    
#     @property
#     def model(self) -> SentenceTransformer:
#         """
#         获取模型对象（懒加载）
        
#         Returns:
#             SentenceTransformer: 模型对象
#         """
#         if self._model is None:
#             self.load()
#         return self._model
    
#     def encode(self, text: Union[str, List[str]], 
#                batch_size: int = 32,
#                show_progress_bar: bool = False) -> np.ndarray:
#         """
#         将文本编码为向量
        
#         Args:
#             text: 单个文本字符串或文本列表
#             batch_size: 批量编码时的批次大小
#             show_progress_bar: 是否显示进度条
        
#         Returns:
#             numpy.ndarray: 向量数组
#             - 单个文本: shape (dimension,)
#             - 多个文本: shape (n, dimension)
#         """
#         if isinstance(text, str):
#             # 单个文本
#             vector = self.model.encode(text, show_progress_bar=show_progress_bar)
#             return vector
#         else:
#             # 多个文本，批量编码
#             vectors = self.model.encode(
#                 text, 
#                 batch_size=batch_size,
#                 show_progress_bar=show_progress_bar
#             )
#             return vectors
    
#     def get_dimension(self) -> int:
#         """
#         获取模型输出维度
        
#         Returns:
#             int: 向量维度
#         """
#         if self._model is None:
#             self.load()
#         return self.dimension
    
#     def __repr__(self):
#         return f"EmbeddingModel(model='{self.model_name}', dimension={self.dimension})"


# # 全局单例实例（可选）
# _global_model = None

# def get_embedding_model() -> EmbeddingModel:
#     """
#     获取全局 embedding 模型实例（单例模式）
    
#     Returns:
#         EmbeddingModel: 模型实例
#     """
#     global _global_model
#     if _global_model is None:
#         _global_model = EmbeddingModel()
#     return _global_model


# if __name__ == "__main__":
#     """
#     测试代码
#     """
#     print("="*60)
#     print("Embedding 模型测试")
#     print("="*60)
    
#     # 创建模型实例
#     embedder = EmbeddingModel()
#     print(f"\n模型信息: {embedder}")
    
#     # 加载模型（首次会下载）
#     print("\n加载模型...")
#     embedder.load()
    
#     # 测试单个文本编码
#     print("\n测试单个文本编码...")
#     text1 = "这是一个测试文本"
#     vector1 = embedder.encode(text1)
#     print(f"文本: {text1}")
#     print(f"向量维度: {vector1.shape}")
#     print(f"向量前10个值: {vector1[:10]}")
    
#     # 测试多个文本批量编码
#     print("\n测试批量文本编码...")
#     texts = [
#         "这是第一个文本",
#         "这是第二个文本",
#         "这是第三个文本"
#     ]
#     vectors = embedder.encode(texts)
#     print(f"文本数量: {len(texts)}")
#     print(f"向量形状: {vectors.shape}")
    
#     # 测试相似度
#     print("\n测试相似度计算...")
#     text2 = "这是另一个测试文本"
#     vector2 = embedder.encode(text2)
    
#     # 余弦相似度
#     similarity = np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))
#     print(f"文本1: {text1}")
#     print(f"文本2: {text2}")
#     print(f"余弦相似度: {similarity:.4f}")
    
#     print("\n" + "="*60)
#     print("✅ 测试完成！")
#     print("="*60)

