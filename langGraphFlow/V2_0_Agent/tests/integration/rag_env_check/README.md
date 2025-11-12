# RAG环境检查测试

本目录包含RAG（检索增强生成）基础设施的环境验证测试，用于验证本地环境是否支持诊断智能体所需的RAG功能。

## 目录说明

```
rag_env_check/
├── test_rag_infrastructure.py  # RAG基础设施测试脚本
├── init_pgvector.sql            # pgvector扩展初始化SQL脚本
├── test_data/                    # 测试数据目录
│   ├── test_medical.md          # 内科测试文档（Markdown格式）
│   └── test_surgery.txt         # 外科测试文档（文本格式）
└── README.md                     # 本文件
```

## 测试目的

本测试脚本用于验证M5里程碑（诊断智能体基础环境搭建）所需的基础设施是否就绪：

1. **文档读取功能**：验证能否读取不同格式的文档（TXT、MD、PDF）
2. **文档分块功能**：验证文档分块（chunking）功能是否正常
3. **Embedding功能**：验证本地embedding模型是否能正常加载和使用
4. **向量数据库**：验证PostgreSQL + pgvector是否能正常连接和操作
5. **RAG检索流程**：验证完整的RAG检索流程是否能走通

## 运行方式

```bash
cd langGraphFlow/V2_0_Agent
conda run -n py_311_rag python test/rag_env_check/test_rag_infrastructure.py
```

## 测试结果说明

测试脚本会输出详细的测试结果，包括：
- 每个测试项的通过/失败状态
- 测试耗时
- 测试结果汇总（总测试数、通过数、失败数、通过率）

## 前置条件

1. **Python环境**：conda环境 `py_311_rag` (Python 3.11)
2. **数据库**：PostgreSQL数据库（doctor_agent_db），已安装pgvector扩展
3. **Embedding模型**：本地已下载m3e-base模型（或配置允许联网下载）
4. **依赖包**：sentence-transformers等必要包已安装

### pgvector扩展初始化

**重要**：在运行测试前，需要确保 `doctor_agent_db` 数据库已安装并启用pgvector扩展。

**快速初始化步骤**：

```bash
# 方法1：使用psql命令行
psql -h localhost -p 5433 -U postgres -d doctor_agent_db -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 方法2：使用SQL脚本
psql -h localhost -p 5433 -U postgres -d doctor_agent_db -f test/rag_env_check/init_pgvector.sql

# 方法3：使用docker exec
docker exec -it <postgres_container_name> psql -U postgres -d doctor_agent_db -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

**验证pgvector是否已启用**：

```sql
-- 连接到数据库
psql -h localhost -p 5433 -U postgres -d doctor_agent_db

-- 检查扩展
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';
```

如果看到结果，说明pgvector已启用。如果未启用，请参考 `V2.0-14-诊断智能体架构设计.md` 中的 3.10 章节进行安装和初始化。

**详细安装步骤**：请参考 `V2.0-14-诊断智能体架构设计.md` - 3.10 pgvector扩展安装和初始化

## 相关文档

- `V2.0-14-诊断智能体架构设计.md` - 诊断智能体架构设计文档
- `计划/项目开发计划.md` - M5里程碑详细说明
- `adbPgRagPython/learnPlan/05_simple_test/` - RAG简单功能实现参考

## 注意事项

- 本测试脚本是独立的环境验证工具，不依赖其他测试
- 测试数据位于 `test_data/` 目录中
- 测试脚本会自动检测环境并报告结果
- 部分测试功能（如PDF读取）为可选功能，不影响整体测试通过

