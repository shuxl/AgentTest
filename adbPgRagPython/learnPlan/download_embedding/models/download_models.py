"""
模型下载工具
支持使用国内镜像下载模型
"""

import os
import sys
from pathlib import Path

# 添加 learnCoding 目录到路径（包含 config 目录的父目录）
learn_coding_root = Path(__file__).parent.parent
sys.path.insert(0, str(learn_coding_root))

from config.model_config import MODEL_NAME, HF_ENDPOINT
from sentence_transformers import SentenceTransformer


def set_hf_mirror():
    """
    设置 Hugging Face 镜像环境变量
    使用国内镜像加速下载
    """
    os.environ['HF_ENDPOINT'] = HF_ENDPOINT
    print(f"✅ 已设置 Hugging Face 镜像: {HF_ENDPOINT}")


def download_model(model_name: str = None):
    """
    下载 embedding 模型
    
    Args:
        model_name: 模型名称，默认使用配置文件中的模型
    
    Returns:
        SentenceTransformer: 加载后的模型对象
    """
    if model_name is None:
        model_name = MODEL_NAME
    
    print(f"\n{'='*60}")
    print(f"开始下载模型: {model_name}")
    print(f"使用镜像: {HF_ENDPOINT}")
    print(f"{'='*60}\n")
    
    try:
        # 设置镜像
        set_hf_mirror()
        
        # 下载并加载模型
        # 首次使用时会自动下载，之后会从缓存加载
        # 下载进度由 transformers 库自动显示
        print(f"正在下载模型...（首次下载可能需要几分钟）\n")
        model = SentenceTransformer(model_name)
        
        print(f"\n{'='*60}")
        print(f"✅ 模型下载/加载成功！")
        print(f"模型名称: {model_name}")
        print(f"模型维度: {model.get_sentence_embedding_dimension()}")
        print(f"{'='*60}\n")
        
        return model
        
    except Exception as e:
        print(f"\n❌ 模型下载失败: {str(e)}")
        print("\n提示:")
        print("1. 检查网络连接")
        print("2. 确认模型名称是否正确")
        print("3. 检查镜像地址是否可访问")
        raise


def check_model_cache(model_name: str = None):
    """
    检查模型是否已缓存
    
    Args:
        model_name: 模型名称，默认使用配置文件中的模型
    
    Returns:
        bool: 模型是否已缓存
        str: 缓存路径
    """
    if model_name is None:
        model_name = MODEL_NAME
    
    # sentence-transformers 的缓存路径
    from sentence_transformers import util
    cache_folder = util.get_cache_folder()
    
    # 模型在缓存中的路径（简化检查）
    # 实际路径可能更复杂，这里只是简单检查
    model_path = Path(cache_folder) / "models--" + model_name.replace("/", "--")
    
    exists = model_path.exists()
    return exists, str(cache_folder) if exists else None


if __name__ == "__main__":
    """
    直接运行此脚本可以下载模型
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="下载 embedding 模型")
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help=f"模型名称（默认: {MODEL_NAME}）"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="仅检查模型是否已缓存，不下载"
    )
    
    args = parser.parse_args()
    
    if args.check_only:
        print("\n检查模型缓存状态...\n")
        exists, cache_path = check_model_cache(args.model)
        if exists:
            print(f"✅ 模型已缓存")
            print(f"缓存路径: {cache_path}")
        else:
            print(f"❌ 模型未缓存")
            print(f"运行此脚本（不带 --check-only）可以下载模型")
    else:
        # 下载模型
        model = download_model(args.model)
        
        # 简单测试
        print("进行简单测试...")
        test_text = "这是一个测试文本"
        embedding = model.encode(test_text)
        print(f"测试文本: {test_text}")
        print(f"向量维度: {len(embedding)}")
        print(f"向量前5个值: {embedding[:5]}")
        print("\n✅ 模型测试成功！\n")

