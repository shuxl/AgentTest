"""
模型配置文件
定义使用的 embedding 模型相关配置
"""

# 使用的模型名称（Hugging Face 模型ID）
MODEL_NAME = "moka-ai/m3e-base"

# 模型维度（用于创建数据库表结构）
MODEL_DIMENSION = 768

# Hugging Face 镜像地址（国内加速）
HF_ENDPOINT = "https://hf-mirror.com"

# 模型缓存目录（可选，使用默认路径时注释掉）
# MODEL_CACHE_DIR = None  # None 表示使用默认路径 ~/.cache/huggingface/hub

