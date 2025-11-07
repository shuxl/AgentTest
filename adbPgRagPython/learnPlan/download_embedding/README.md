# PgVector 学习项目 - 开发环境准备

本项目是 PgVector 学习计划的代码实践部分，专注于 embedding 模型的使用。

## 📋 项目结构

```
learnCoding/
├── requirements.txt           # Python 依赖包
├── config/
│   └── model_config.py       # 模型配置文件
├── models/
│   ├── download_models.py    # 模型下载工具
│   └── model_manager.py      # 模型管理器
└── README.md                  # 本文件
```

## 🚀 快速开始

### 1. 安装依赖

确保已激活 conda 环境 `py_311_rag`：

```bash
conda activate py_311_rag
```

安装依赖包：

```bash
cd learnCoding
pip install -r requirements.txt
```

### 2. 下载模型

首次使用需要下载模型。本项目使用 **m3e-base** 模型，配置了国内镜像加速下载。

**重要：需要在 `learnCoding` 目录下运行脚本！**

```bash
# 确保在 learnCoding 目录下
cd /Users/m684620/work/github/agent_2025_02/adbPgRagPython/learnPlan/learnCoding
```

**方式1：使用下载脚本（推荐）**

```bash
python models/download_models.py
```

**方式2：直接运行模型管理器（会自动下载）**

```bash
python models/model_manager.py
```

模型下载后会自动缓存到本地，下次使用时无需重新下载。

### 3. 检查模型状态

```bash
# 确保在 learnCoding 目录下
python models/download_models.py --check-only
```

### 4. 在代码中使用

如果要在其他目录或脚本中使用模型，有两种方式：

**方式1：在 learnCoding 目录下运行**

```bash
cd learnCoding
python your_script.py
```

**方式2：在脚本中添加路径**

```python
import sys
from pathlib import Path

# 添加 learnCoding 目录到路径
learn_coding_path = Path(__file__).parent / "learnPlan" / "learnCoding"
sys.path.insert(0, str(learn_coding_path))

from models.model_manager import EmbeddingModel
```

## 📦 使用的模型

- **模型名称**: `moka-ai/m3e-base`
- **模型维度**: 768
- **特点**: 
  - 针对中文优化
  - 体积适中（约 400MB）
  - 性能优秀

## 💻 代码使用示例

### 基础使用

```python
from models.model_manager import EmbeddingModel

# 创建模型实例
embedder = EmbeddingModel()

# 加载模型（首次使用会自动下载）
embedder.load()

# 编码单个文本
text = "这是一个测试文本"
vector = embedder.encode(text)
print(f"向量维度: {vector.shape}")  # (768,)

# 批量编码多个文本
texts = ["文本1", "文本2", "文本3"]
vectors = embedder.encode(texts)
print(f"向量形状: {vectors.shape}")  # (3, 768)
```

### 使用全局单例

```python
from models.model_manager import get_embedding_model

# 获取全局模型实例
embedder = get_embedding_model()

# 使用方式相同
vector = embedder.encode("测试文本")
```

## ⚙️ 配置说明

### 修改模型配置

编辑 `config/model_config.py`：

```python
# 修改模型名称（如果需要）
MODEL_NAME = "moka-ai/m3e-base"

# 修改模型维度（通常不需要手动修改）
MODEL_DIMENSION = 768

# 修改镜像地址（如果需要）
HF_ENDPOINT = "https://hf-mirror.com"
```

### 支持的镜像地址

- `https://hf-mirror.com` （默认，hf-mirror 镜像）
- `https://huggingface.co` （官方地址，需要科学上网）

## 🔍 模型信息

### m3e-base 模型特性

- **开发公司**: 北京希瑞亚斯科技（Moka AI）
- **模型类型**: 中文文本嵌入模型
- **训练数据**: 大量中文语料
- **适用场景**: 
  - 文本相似度计算
  - 语义搜索
  - 文本聚类
  - 文档检索

### 模型性能

- 在中文文本检索任务上表现优异
- 超越了 OpenAI 的 text-embedding-ada-002 在中文任务上的表现
- 支持中英文混合文本

## 📝 注意事项

1. **首次下载**: 模型首次下载可能需要几分钟，请耐心等待
2. **网络要求**: 需要能够访问 Hugging Face 镜像（已配置国内镜像）
3. **存储空间**: 模型下载后约占用 400MB 磁盘空间
4. **内存要求**: 模型加载到内存约需要 1-2GB

## 🐛 常见问题

### Q: 下载模型很慢怎么办？

A: 已经配置了国内镜像 `https://hf-mirror.com`，如果还是很慢：
1. 检查网络连接
2. 尝试更换其他镜像地址
3. 使用代理工具

### Q: 模型下载失败怎么办？

A: 
1. 检查网络连接
2. 确认镜像地址可访问
3. 查看错误信息，可能需要手动设置代理

### Q: 如何更换模型？

A: 修改 `config/model_config.py` 中的 `MODEL_NAME` 即可，但需要确保 `MODEL_DIMENSION` 与模型实际维度匹配。

## 📚 下一步

完成模型环境准备后，可以继续：
1. 学习数据库连接和配置
2. 学习向量存储和检索
3. 构建完整的文档检索系统

---

**祝你学习顺利！** 🚀

