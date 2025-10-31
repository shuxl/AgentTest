# 项目结构说明

## 📁 目录结构

```
04_index_test/
├── README.md                          # 完整学习方案文档（核心文档）
├── QUICK_START.md                     # 快速开始指南
├── PROJECT_STRUCTURE.md               # 本文件：项目结构说明
├── requirements.txt                   # Python 依赖包
├── config.py                          # 数据库和测试配置
├── db_utils.py                        # 数据库工具类（复用05_simple_test）
├── test_imports.py                    # 模块导入测试脚本
├── setup.sh                           # 环境一键设置脚本
│
├── data_generation/                   # 数据生成工具
│   ├── __init__.py
│   └── generate_test_data.py         # 生成随机测试向量
│
├── performance_testing/               # 性能测试脚本
│   ├── __init__.py
│   ├── test_hnsw_index.py            # HNSW 索引测试
│   ├── test_ivfflat_index.py         # IVFFlat 索引测试
│   └── benchmark_indexes.py          # 索引性能对比
│
├── examples/                          # 示例代码
│   ├── __init__.py
│   └── basic_index_usage.py          # 基础索引使用示例
│
├── index_operations/                  # 索引操作工具（预留）
├── optimization/                      # 优化工具（预留）
└── results/                           # 测试结果目录
    ├── benchmarks/                    # 性能基准测试结果
    └── reports/                       # 分析报告
```

## 📄 核心文件说明

### 文档文件

| 文件 | 说明 | 用途 |
|------|------|------|
| `README.md` | 完整学习方案 | 详细的学习路径、数据需求、工具说明 |
| `QUICK_START.md` | 快速开始指南 | 5分钟快速上手 |
| `PROJECT_STRUCTURE.md` | 项目结构说明 | 本文件 |

### 配置和工具

| 文件 | 说明 | 用途 |
|------|------|------|
| `config.py` | 配置文件 | 数据库连接、模型配置、测试参数 |
| `db_utils.py` | 数据库工具 | 复用05_simple_test的数据库连接类 |
| `requirements.txt` | 依赖包列表 | Python依赖包清单 |
| `setup.sh` | 环境设置脚本 | 一键安装依赖和验证环境 |
| `test_imports.py` | 导入测试脚本 | 验证所有模块能否正常导入 |

### 数据生成

| 文件 | 说明 | 命令行示例 |
|------|------|-----------|
| `data_generation/generate_test_data.py` | 生成测试向量数据 | `python data_generation/generate_test_data.py --count 5000` |

### 性能测试

| 文件 | 说明 | 命令行示例 |
|------|------|-----------|
| `performance_testing/test_hnsw_index.py` | 测试HNSW索引性能 | `python performance_testing/test_hnsw_index.py --m 16` |
| `performance_testing/test_ivfflat_index.py` | 测试IVFFlat索引性能 | `python performance_testing/test_ivfflat_index.py --lists 100` |
| `performance_testing/benchmark_indexes.py` | 对比所有索引性能 | `python performance_testing/benchmark_indexes.py` |

### 示例代码

| 文件 | 说明 | 用途 |
|------|------|------|
| `examples/basic_index_usage.py` | 基础索引使用示例 | 演示如何创建和使用索引 |

## 🚀 使用流程

### 第一步：环境设置

```bash
# 方式1：使用自动脚本
./setup.sh

# 方式2：手动设置
conda activate py_311_rag
pip install -r requirements.txt
python test_imports.py  # 验证
```

### 第二步：生成测试数据

```bash
# 基础学习：1,000-5,000条
python data_generation/generate_test_data.py --count 5000 --dimension 768

# 深入学习：10,000-50,000条
python data_generation/generate_test_data.py --count 50000 --dimension 768
```

### 第三步：测试索引性能

```bash
# 测试HNSW索引
python performance_testing/test_hnsw_index.py

# 测试IVFFlat索引
python performance_testing/test_ivfflat_index.py

# 完整性能对比
python performance_testing/benchmark_indexes.py --num-queries 20
```

### 第四步：查看示例代码

```bash
# 运行基础示例
python examples/basic_index_usage.py
```

## 🔧 常见问题排查

### 问题1：导入错误

```bash
# 运行诊断脚本
python test_imports.py

# 检查依赖
pip list | grep -E "psycopg2|numpy|tqdm"
```

### 问题2：数据库连接失败

```bash
# 检查config.py中的数据库配置
cat config.py

# 测试数据库连接（需要在Python中运行）
python -c "from db_utils import PgVectorClient; from config import DB_CONFIG; client = PgVectorClient(**DB_CONFIG); print('✅' if client.test_connection() else '❌')"
```

### 问题3：循环导入错误

如果遇到循环导入，确保：
- `db_utils.py` 使用 `importlib.util` 加载模块
- 所有脚本都在正确的目录下运行
- Python路径设置正确

## 📊 文件依赖关系

```
config.py
  └─> 被所有脚本引用

db_utils.py
  └─> 动态加载 05_simple_test/db_utils.py
  └─> 被所有数据操作脚本引用

generate_test_data.py
  ├─> 依赖: config.py, db_utils.py
  └─> 功能: 生成测试数据

test_hnsw_index.py
  ├─> 依赖: config.py, db_utils.py
  └─> 功能: 测试HNSW索引

test_ivfflat_index.py
  ├─> 依赖: config.py, db_utils.py
  └─> 功能: 测试IVFFlat索引

benchmark_indexes.py
  ├─> 依赖: config.py, db_utils.py
  ├─> 导入: test_hnsw_index.py, test_ivfflat_index.py
  └─> 功能: 性能对比

basic_index_usage.py
  ├─> 依赖: config.py, db_utils.py
  ├─> 导入: test_hnsw_index.py, test_ivfflat_index.py
  └─> 功能: 示例代码
```

## 💡 开发建议

1. **修改配置**：编辑 `config.py` 调整数据库连接和测试参数
2. **添加功能**：在对应的目录下创建新文件
3. **调试工具**：使用 `test_imports.py` 验证导入
4. **查看日志**：测试结果会输出到终端，也可以保存到 `results/` 目录

## 📚 相关文档

- [README.md](README.md) - 完整学习方案
- [QUICK_START.md](QUICK_START.md) - 快速开始指南
- [../05_simple_test/README.md](../05_simple_test/README.md) - 基础操作参考

