# PgVector 学习项目 - 第五阶段实践代码

这是 PgVector 学习计划第五阶段的完整实践代码，包含数据库连接、向量操作、文本向量化和文档检索系统。

## 📋 项目结构

```
05_simple_test/
├── config.py              # 数据库和模型配置
├── db_utils.py            # 数据库连接工具类
├── vector_ops.py          # 向量操作封装
├── embedding_utils.py     # 文本向量化工具
├── document_search.py     # 完整的文档检索系统
├── examples/              # 示例代码
│   ├── insert_example.py # 插入向量数据示例
│   ├── search_example.py # 向量搜索示例
│   └── batch_example.py  # 批量插入示例
├── requirements.txt       # Python 依赖包
└── README.md              # 本文件
```

## 🚀 快速开始

### 1. 环境准备

确保已激活 conda 环境 `py_311_rag`：

```bash
conda activate py_311_rag
```

### 2. 安装依赖

```bash
cd 05_simple_test
pip install -r requirements.txt
```

### 3. 配置数据库

确保你的 PostgreSQL 数据库已启动并且安装了 pgvector 扩展。

根据 `本地的数据库连接方式.txt`，数据库配置如下：
- 主机: localhost
- 端口: 5433
- 数据库: sxl_pg_db1
- 用户: postgres
- 密码: sxl_pwd_123

### 4. 安装 pgvector 扩展

连接到数据库并安装扩展：

```bash
docker exec -it postgres-pgvector-17 psql -U postgres -d sxl_pg_db1
```

在 psql 中执行：

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 5. 运行示例代码

#### 示例1：插入向量数据

```bash
python examples/insert_example.py
```

#### 示例2：向量搜索

```bash
python examples/search_example.py
```

#### 示例3：批量插入

```bash
python examples/batch_example.py
```

#### 完整文档检索系统

```bash
python document_search.py
```

## 📚 代码说明

### config.py
数据库和模型配置文件：
- 数据库连接参数
- Embedding 模型名称和维度

### db_utils.py
数据库连接工具类 `PgVectorClient`：
- 连接管理（上下文管理器）
- 查询和更新操作
- 扩展检查

### vector_ops.py
向量操作类 `VectorOperations`：
- `insert_vector()`: 插入单个向量
- `batch_insert()`: 批量插入向量
- `cosine_search()`: 余弦相似度搜索
- `euclidean_search()`: 欧氏距离搜索
- `update_vector()`: 更新向量
- `delete_vector()`: 删除向量

### embedding_utils.py
文本向量化工具 `TextEmbedder`：
- 使用已下载的 m3e-base 模型
- `encode()`: 单个或批量文本向量化
- 自动模型加载和维度验证

### document_search.py
完整的文档检索系统 `DocumentSearch`：
- 自动创建表和索引
- 文档添加和批量添加
- 相似度搜索
- 文档管理（查询、删除）

## 💻 使用示例

### 基础使用

```python
from config import DB_CONFIG
from db_utils import PgVectorClient
from vector_ops import VectorOperations
from embedding_utils import TextEmbedder

# 创建客户端
client = PgVectorClient(**DB_CONFIG)

# 创建向量化工具
embedder = TextEmbedder()
embedder.load()

# 创建向量操作对象
vector_ops = VectorOperations(client)

# 向量化文本
text = "这是一个测试文本"
vector = embedder.encode(text)

# 插入向量
data = {'name': '测试', 'description': text}
vector_ops.insert_vector('items', data, vector)

# 搜索相似向量
results = vector_ops.cosine_search('items', vector, limit=5)
```

### 使用文档检索系统

```python
from document_search import DocumentSearch
from db_utils import PgVectorClient
from embedding_utils import TextEmbedder
from config import DB_CONFIG

# 创建组件
client = PgVectorClient(**DB_CONFIG)
embedder = TextEmbedder()
doc_search = DocumentSearch(client, embedder)

# 初始化（创建表和索引）
doc_search.create_table_if_not_exists()
doc_search.create_index_if_not_exists("hnsw")

# 添加文档
doc_search.add_document("文档内容", title="文档标题")

# 搜索文档
results = doc_search.search("查询文本", limit=5)
```

## 🔍 模型信息

- **模型名称**: `moka-ai/m3e-base`
- **模型维度**: 768
- **特点**: 针对中文优化，性能优秀

**注意**: 模型已经下载完成，代码会自动从缓存加载。

## 📝 数据库表结构示例

### items 表（示例）
```sql
CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    embedding vector(768),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ON items USING hnsw (embedding vector_cosine_ops);
```

### documents 表（文档检索系统）
```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT NOT NULL,
    embedding vector(768),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops);
```

## 🎯 学习目标

通过本项目的代码，你将学会：

1. ✅ 使用 Python 连接 PgVector 数据库
2. ✅ 封装数据库操作（连接、查询、更新）
3. ✅ 使用 embedding 模型进行文本向量化
4. ✅ 实现向量的插入、更新、删除操作
5. ✅ 实现余弦相似度和欧氏距离搜索
6. ✅ 构建完整的文档检索系统
7. ✅ 批量操作和性能优化

## 🐛 常见问题

### Q: 数据库连接失败怎么办？

A: 检查以下几点：
1. 确保 Docker 容器正在运行：`docker ps | grep postgres-pgvector-17`
2. 检查端口是否正确（5433）
3. 检查用户名和密码是否正确
4. 尝试使用 psql 手动连接测试

### Q: pgvector 扩展未安装怎么办？

A: 连接到数据库并执行：
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### Q: 模型加载失败怎么办？

A: 模型应该已经下载完成。如果失败：
1. 检查模型名称是否正确
2. 确认模型缓存路径可访问
3. 可以尝试重新下载模型

## 📚 下一步

完成本阶段后，可以：
1. 尝试修改代码，测试不同的搜索参数
2. 添加更多功能（如文档更新、删除）
3. 性能测试和优化
4. 进入第六阶段：综合项目实践

---

**祝你学习顺利！** 🚀

