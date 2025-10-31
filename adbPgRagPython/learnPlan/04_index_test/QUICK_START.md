# 索引优化学习 - 快速开始指南

## 🚀 5 分钟快速开始

### 1. 环境准备

```bash
# 激活 conda 环境
conda activate py_311_rag

# 进入项目目录
cd adbPgRagPython/learnPlan/04_index_test

# 安装依赖
pip install -r requirements.txt
```

### 2. 生成测试数据

```bash
# 生成 5,000 条 768 维随机向量（适合快速测试）
python data_generation/generate_test_data.py --count 5000 --dimension 768

# 或者生成更大规模的数据（适合深入学习）
python data_generation/generate_test_data.py --count 50000 --dimension 768
```

### 3. 测试 HNSW 索引

```bash
# 创建并测试 HNSW 索引
python performance_testing/test_hnsw_index.py --table-name index_test_items --m 16 --ef-construction 64
```

### 4. 测试 IVFFlat 索引

```bash
# 创建并测试 IVFFlat 索引
python performance_testing/test_ivfflat_index.py --table-name index_test_items --lists 50
```

### 5. 性能对比

```bash
# 对比无索引、HNSW、IVFFlat 的性能
python performance_testing/benchmark_indexes.py --table-name index_test_items --num-queries 20
```

---

## 📊 推荐学习路径

### 第一天：基础了解
1. 阅读 `README.md` 中的数据需求分析部分
2. 生成 1,000 条测试数据
3. 运行基础示例：`python examples/basic_index_usage.py`

### 第二天：HNSW 索引
1. 生成 10,000 条测试数据
2. 测试不同 m 值：`--m 8`, `--m 16`, `--m 32`
3. 测试不同 ef_search 值的影响

### 第三天：IVFFlat 索引
1. 生成 50,000 条测试数据
2. 测试不同 lists 值：`--lists 50`, `--lists 100`, `--lists 200`
3. 测试不同 probes 值的影响

### 第四天：性能对比
1. 运行完整的性能对比测试
2. 分析不同场景下的最优索引选择
3. 记录测试结果和心得体会

### 第五天：实战应用
1. 使用真实文本数据（可选）
2. 模拟实际应用场景
3. 优化索引参数

---

## 💡 常用命令速查

### 数据生成
```bash
# 基础数据（1K）
python data_generation/generate_test_data.py --count 1000

# 中等规模（10K）
python data_generation/generate_test_data.py --count 10000

# 大规模（100K）
python data_generation/generate_test_data.py --count 100000

# 指定维度
python data_generation/generate_test_data.py --count 5000 --dimension 384

# 删除已有表重新生成
python data_generation/generate_test_data.py --count 5000 --drop-existing
```

### HNSW 索引测试
```bash
# 默认参数
python performance_testing/test_hnsw_index.py

# 自定义参数
python performance_testing/test_hnsw_index.py --m 32 --ef-construction 128 --ef-search 100

# 只测试查询（不创建索引）
python performance_testing/test_hnsw_index.py --skip-create
```

### IVFFlat 索引测试
```bash
# 默认参数（自动计算 lists）
python performance_testing/test_ivfflat_index.py

# 自定义 lists
python performance_testing/test_ivfflat_index.py --lists 100 --probes 20
```

### 性能对比
```bash
# 快速对比（10 次查询）
python performance_testing/benchmark_indexes.py --num-queries 10

# 详细对比（50 次查询，保存结果）
python performance_testing/benchmark_indexes.py --num-queries 50 --output results/benchmark_50000.json

# 自定义所有参数
python performance_testing/benchmark_indexes.py \
    --hnsw-m 32 \
    --hnsw-ef-construction 128 \
    --ivfflat-lists 100 \
    --num-queries 30
```

---

## ⚠️ 常见问题

### Q1: 数据量应该选多少？
- **基础学习**：1,000 - 5,000 条
- **深入学习**：10,000 - 50,000 条
- **生产模拟**：100,000+ 条

### Q2: 索引创建很慢怎么办？
- 小规模数据（<10K）：正常，通常 < 1 分钟
- 中等规模（10K-100K）：可能需要几分钟，正常
- 大规模（>100K）：可能需要 10 分钟以上，建议降低测试数据量

### Q3: 如何选择最优参数？
1. 先使用默认参数测试
2. 逐步调整参数观察性能变化
3. 使用 `benchmark_indexes.py` 对比不同参数组合

### Q4: 如何查看索引信息？
```sql
-- 连接数据库后执行
SELECT 
    indexname,
    pg_size_pretty(pg_relation_size(indexname::regclass)) as size
FROM pg_indexes
WHERE tablename = 'index_test_items';
```

---

## 📚 下一步

- 阅读完整的 `README.md` 了解详细的学习方案
- 查看 `examples/` 目录下的示例代码
- 记录你的测试结果和优化经验

祝你学习顺利！🎉

