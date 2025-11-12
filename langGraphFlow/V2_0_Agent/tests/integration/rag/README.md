# RAG模块测试

本目录包含RAG基础设施模块的单元测试用例。

## 测试文件

- `test_rag_modules.py` - RAG模块综合测试，测试文档读取、分块、embedding、向量数据库操作和RAG检索流程

## 运行方式

```bash
cd langGraphFlow/V2_0_Agent
conda run -n py_311_rag python tests/integration/rag/test_rag_modules.py
```

## 测试用例

1. **test_document_loading**：文档读取功能测试
   - 测试TXT、MD文件读取
   - 检查PDF库支持
   
2. **test_text_chunking**：文档分块功能测试
   - 测试文档分块功能
   - 验证分块结果合理性
   
3. **test_embedding**：向量化功能测试
   - 测试模型加载
   - 测试单个/批量文本向量化
   - 测试相似度计算
   
4. **test_vector_database**：向量数据库操作测试
   - 测试数据库连接
   - 测试扩展检查
   - 测试表创建
   - 测试向量插入和检索
   
5. **test_rag_retrieval_flow**：RAG检索完整流程测试
   - 测试完整的RAG流程（文档入库 -> 向量化 -> 检索）

## 前置条件

1. **Python环境**：conda环境 `py_311_rag` (Python 3.11)
2. **数据库**：PostgreSQL数据库（doctor_agent_db），已安装pgvector扩展
3. **Embedding模型**：本地已下载m3e-base模型（或配置允许联网下载）
4. **依赖包**：sentence-transformers、langchain、psycopg2等必要包已安装

