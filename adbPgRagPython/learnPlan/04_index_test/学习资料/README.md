# 学习资料索引

本目录包含 PgVector 索引优化的系统化中文学习资料。

## 📚 文档列表

### 1. [HNSW算法原理详解](./HNSW算法原理详解.md)

**内容概览**：
- 算法概述和核心思想
- 分层图结构原理详解
- 图构建和搜索过程
- 关键参数（m, ef_construction, ef_search）详解
- 性能特点和适用场景
- 在 pgvector 中的使用方法

**适合人群**：需要深入理解 HNSW 算法原理的开发者

**阅读时间**：约 30-45 分钟

---

### 2. [IVFFlat算法原理详解](./IVFFlat算法原理详解.md)

**内容概览**：
- 算法概述和核心思想
- 聚类和倒排索引机制
- 索引构建和搜索过程
- 关键参数（lists, probes）详解
- 性能特点和适用场景
- 与 HNSW 的对比分析
- 在 pgvector 中的使用方法

**适合人群**：需要深入理解 IVFFlat 算法原理的开发者

**阅读时间**：约 30-45 分钟

---

### 3. [向量距离度量详解](./向量距离度量详解.md)

**内容概览**：
- 欧氏距离（L2 距离）详解
- 余弦相似度详解
- 内积（点积）详解
- 三种距离度量的对比分析
- 如何选择距离度量（决策指南）
- 在 pgvector 中的使用方法
- 距离度量对索引的影响

**适合人群**：需要理解向量相似度计算的开发者

**阅读时间**：约 25-35 分钟

---

## 🎯 学习路径建议

### 第一步：理解基础概念
1. 先阅读 [向量距离度量详解](./向量距离度量详解.md)
   - 理解向量相似度的计算方式
   - 为后续学习索引算法打下基础

### 第二步：学习索引算法
2. 阅读 [HNSW算法原理详解](./HNSW算法原理详解.md)
   - 理解基于图结构的索引方法
   - 掌握分层搜索的机制

3. 阅读 [IVFFlat算法原理详解](./IVFFlat算法原理详解.md)
   - 理解基于聚类的索引方法
   - 掌握倒排索引的机制

### 第三步：对比和实践
4. 对比两种算法的优缺点
5. 根据实际场景选择合适的索引类型
6. 参考文档中的 pgvector 使用示例进行实践

---

## 📖 快速查找

### 查找参数含义

- **HNSW 参数**：查看 [HNSW算法原理详解](./HNSW算法原理详解.md) 的"关键参数"章节
- **IVFFlat 参数**：查看 [IVFFlat算法原理详解](./IVFFlat算法原理详解.md) 的"关键参数"章节

### 查找使用示例

- **HNSW 使用**：查看 [HNSW算法原理详解](./HNSW算法原理详解.md) 的"在 pgvector 中的使用"章节
- **IVFFlat 使用**：查看 [IVFFlat算法原理详解](./IVFFlat算法原理详解.md) 的"在 pgvector 中的使用"章节
- **距离度量使用**：查看 [向量距离度量详解](./向量距离度量详解.md) 的"在 pgvector 中的使用"章节

### 查找场景选择

- **选择索引类型**：查看 [IVFFlat算法原理详解](./IVFFlat算法原理详解.md) 的"与 HNSW 的对比"章节
- **选择距离度量**：查看 [向量距离度量详解](./向量距离度量详解.md) 的"如何选择距离度量"章节

---

## 💡 学习建议

1. **循序渐进**：按照学习路径建议的顺序阅读
2. **动手实践**：每阅读一个算法，立即在 pgvector 中实践
3. **对比理解**：对比两种算法的异同，加深理解
4. **参数实验**：尝试不同的参数组合，观察性能变化
5. **做笔记**：记录自己的理解和实践经验

---

## 🔗 相关资源

### 原始论文

- **HNSW**：[Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs](https://arxiv.org/abs/1603.09320)
- **IVF**：[Product Quantization for Nearest Neighbor Search](https://ieeexplore.ieee.org/document/5432202)

### 官方文档

- **pgvector GitHub**：https://github.com/pgvector/pgvector
- **pgvector 文档**：https://github.com/pgvector/pgvector#readme

### 项目文档

- [../README.md](../README.md) - 完整学习方案
- [../QUICK_START.md](../QUICK_START.md) - 快速开始指南

---

**最后更新**：2025年1月

