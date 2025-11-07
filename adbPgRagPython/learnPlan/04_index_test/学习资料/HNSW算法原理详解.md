# HNSW 算法原理详解

## 📖 目录

1. [算法概述](#算法概述)
2. [核心思想](#核心思想)
3. [算法原理](#算法原理)
4. [关键参数](#关键参数)
5. [性能特点](#性能特点)
6. [应用场景](#应用场景)
7. [在 pgvector 中的使用](#在-pgvector-中的使用)

---

## 算法概述

**HNSW**（Hierarchical Navigable Small World，分层导航小世界图）是一种基于图结构的近似最近邻搜索算法，由 Yury Malkov 等人在 2016 年提出。

### 算法特点

- **高效性**：查询时间复杂度 O(log n)，远优于线性搜索的 O(n)
- **准确性**：通过多层图结构，能够提供较高的搜索精度
- **可扩展性**：适用于大规模高维向量数据
- **参数可调**：通过调整参数可以平衡速度和精度

---

## 核心思想

### 1. 小世界网络理论

HNSW 算法的核心思想来源于**小世界网络理论**：

- **小世界特性**：任意两个节点之间的平均最短路径很短
- **高聚类性**：相邻节点之间联系紧密
- **稀疏连接**：每个节点只连接少量邻居，保持网络稀疏

### 2. 分层结构设计

HNSW 构建了**多层次的分层图结构**：

```
Layer 2: ○─────○─────○  (稀疏，少量节点)
         │     │     │
Layer 1: ○─○─○─○─○─○  (中等密度)
         │││││││││││
Layer 0: ○○○○○○○○○○○  (最底层，所有节点)
```

- **底层（Layer 0）**：包含所有数据点，连接最密集
- **上层**：节点越来越少，连接越来越稀疏
- **搜索路径**：从顶层开始，逐层向下搜索到最底层

---

## 算法原理

### 1. 图构建过程（插入新节点）

当需要插入一个新节点时，HNSW 按以下步骤进行：

#### 步骤 1：确定插入层数
```python
# 伪代码
level = random_level()  # 随机生成层数，遵循指数衰减分布
# 层数越高，概率越小（例如：第 1 层 50%，第 2 层 25%，第 3 层 12.5%...）
```

**为什么要随机分层？**
- 保证上层节点稀疏，加快搜索速度
- 保持图的平衡性

#### 步骤 2：顶层搜索入口
```python
# 从顶层开始，找到最接近插入点的节点作为入口
entry_point = search_in_layer(query, top_layer)
```

#### 步骤 3：逐层向下搜索并插入
```python
# 从顶层向下，在每一层找到最接近的节点
for layer in range(top_layer, -1, -1):
    # 在当前层搜索最近的节点
    candidates = search_layer(query, entry_point, ef_construction, layer)
    
    # 选择 M 个邻居连接
    neighbors = select_neighbors(candidates, m)
    
    # 建立连接
    connect(node, neighbors)
    
    # 更新入口点，为下一层做准备
    entry_point = candidates[0]
```

### 2. 搜索过程（查找最近邻）

#### 步骤 1：顶层入口搜索
```python
# 从顶层开始，找到初始入口点
current = search_in_layer(query, top_layer)
```

#### 步骤 2：逐层向下遍历
```python
# 从顶层到第 1 层，快速接近目标
for layer in range(top_layer, 1, -1):
    current = search_layer(query, current, ef_search=1, layer)
    # ef_search=1 表示每层只搜索一个最佳路径
```

#### 步骤 3：底层精确搜索
```python
# 在第 0 层进行精确搜索
candidates = search_layer(query, current, ef_search, layer=0)
# ef_search 控制搜索广度，值越大精度越高但速度越慢

# 返回 Top-K 结果
return select_top_k(candidates, k)
```

### 3. 搜索算法细节（search_layer）

```python
def search_layer(query, entry_point, ef, layer):
    """
    在指定层中搜索最近的节点
    
    参数:
        query: 查询向量
        entry_point: 起始节点
        ef: 候选集大小（ef_construction 或 ef_search）
        layer: 当前层
    """
    # 初始化候选集和已访问集合
    candidates = [entry_point]  # 候选节点集合（优先队列）
    visited = {entry_point}     # 已访问节点
    
    # 动态候选集，存储最接近的 ef 个节点
    dynamic_candidates = [entry_point]
    
    while len(candidates) > 0:
        # 取出最近的候选节点
        current = candidates.pop()
        furthest = dynamic_candidates[-1]
        
        # 如果当前节点比动态候选集中最远的节点还远，停止搜索
        if distance(query, current) > distance(query, furthest):
            break
        
        # 遍历当前节点的所有邻居
        for neighbor in current.neighbors[layer]:
            if neighbor not in visited:
                visited.add(neighbor)
                
                # 如果邻居比动态候选集中最远的节点更近
                if distance(query, neighbor) < distance(query, furthest):
                    candidates.add(neighbor)  # 加入候选集
                    
                    # 更新动态候选集（保持 ef 个最近节点）
                    dynamic_candidates.add(neighbor)
                    if len(dynamic_candidates) > ef:
                        dynamic_candidates.remove(furthest)
    
    return dynamic_candidates
```

---

## 关键参数

### 1. `m` - 每个节点的最大连接数

**含义**：每个节点在每层最多连接的邻居数量

**影响**：
- **m 越大**：
  - ✅ 搜索路径更多，精度更高
  - ❌ 索引构建时间更长，索引占用空间更大
  - ❌ 查询时需要遍历更多邻居，可能更慢
- **m 越小**：
  - ✅ 索引构建快，占用空间小
  - ❌ 搜索路径少，可能影响精度

**推荐值**：
- 小数据集（<10万）：`m = 8-16`
- 中等数据集（10-100万）：`m = 16-32`
- 大数据集（>100万）：`m = 32-64`

**物理意义**：
- 控制图的连接密度
- 影响图的"小世界"特性
- 决定搜索时的路径选择空间

### 2. `ef_construction` - 构建时的候选集大小

**含义**：构建索引时，每层搜索的候选节点数量

**影响**：
- **ef_construction 越大**：
  - ✅ 构建时选择更好的邻居，索引质量更高，查询精度更高
  - ❌ 构建时间显著增加
- **ef_construction 越小**：
  - ✅ 构建时间短
  - ❌ 可能选择次优邻居，影响查询精度

**推荐值**：
- 精度要求高：`ef_construction = 128-200`
- 平衡速度和精度：`ef_construction = 64-128`
- 追求构建速度：`ef_construction = 32-64`

**物理意义**：
- 影响构建时的"贪婪"程度
- 决定每个节点连接邻居的质量

### 3. `ef_search` - 查询时的候选集大小

**含义**：查询时在底层搜索的候选节点数量（仅在查询时设置，不是索引参数）

**影响**：
- **ef_search 越大**：
  - ✅ 搜索范围更广，召回率更高，精度更高
  - ❌ 查询时间增加
- **ef_search 越小**：
  - ✅ 查询速度快
  - ❌ 可能漏掉真正的最邻近点，精度下降

**推荐值**：
- 精度要求高：`ef_search = 100-200`
- 平衡速度和精度：`ef_search = 40-100`
- 追求查询速度：`ef_search = 20-40`

**注意**：
- `ef_search` 应该 **≥ k**（返回的结果数量）
- 通常设置为 `k` 的 2-10 倍

**物理意义**：
- 控制查询时的搜索广度
- 直接影响查询精度和速度的权衡

---

## 性能特点

### 优势

1. **查询速度快**
   - 时间复杂度：O(log n)
   - 通过多层图结构，快速定位目标区域

2. **查询精度高**
   - 通过 ef_search 参数可以灵活调整精度
   - 召回率通常可达 90% 以上

3. **适用场景广**
   - 支持高维向量（数百到数千维）
   - 适合各种距离度量（欧氏、余弦、内积）

### 劣势

1. **索引构建慢**
   - 构建时间比 IVFFlat 长
   - 需要更多计算资源

2. **索引占用空间大**
   - 需要存储图的连接关系
   - 通常比 IVFFlat 索引大 2-5 倍

3. **更新成本高**
   - 插入新向量需要更新图结构
   - 不适合频繁更新的场景

---

## 应用场景

### 适合使用 HNSW 的场景

✅ **读多写少**
- 数据相对稳定，查询频繁
- 例如：文档检索系统、推荐系统

✅ **查询精度要求高**
- 需要高召回率
- 例如：相似图片搜索、语义搜索

✅ **查询延迟要求低**
- 需要毫秒级响应
- 例如：实时推荐、在线搜索

✅ **数据量中等到大**
- 百万级到千万级数据
- 例如：电商平台商品搜索

### 不适合使用 HNSW 的场景

❌ **频繁更新数据**
- 插入、删除、更新操作频繁
- 每次更新可能触发索引重建

❌ **索引构建时间敏感**
- 需要快速完成索引构建
- 选择 IVFFlat 更合适

❌ **存储空间受限**
- 索引占用空间有限制
- IVFFlat 占用空间更小

---

## 在 pgvector 中的使用

### 创建 HNSW 索引

```sql
-- 创建 HNSW 索引（余弦距离）
CREATE INDEX ON items 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 创建 HNSW 索引（欧氏距离）
CREATE INDEX ON items 
USING hnsw (embedding vector_l2_ops)
WITH (m = 16, ef_construction = 64);

-- 创建 HNSW 索引（内积）
CREATE INDEX ON items 
USING hnsw (embedding vector_ip_ops)
WITH (m = 16, ef_construction = 64);
```

### 参数选择建议

**场景 1：小数据集（< 1万条）**
```sql
CREATE INDEX ON items 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 8, ef_construction = 32);
```

**场景 2：中等数据集（1万 - 10万条）**
```sql
CREATE INDEX ON items 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

**场景 3：大数据集（10万 - 100万条）**
```sql
CREATE INDEX ON items 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 32, ef_construction = 128);
```

**场景 4：超大数据集（> 100万条）**
```sql
CREATE INDEX ON items 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 64, ef_construction = 200);
```

### 查询时调整 ef_search

```sql
-- 设置查询参数（仅在当前会话有效）
SET hnsw.ef_search = 100;

-- 执行查询
SELECT id, name, embedding <=> query_vector AS distance
FROM items
ORDER BY embedding <=> query_vector
LIMIT 10;

-- 或者在查询中使用（pgvector 0.5.0+）
SELECT id, name, embedding <=> query_vector AS distance
FROM items
ORDER BY embedding <=> query_vector
LIMIT 10
SET hnsw.ef_search = 100;
```

### 性能对比测试

```sql
-- 测试不同 ef_search 值的影响
SET hnsw.ef_search = 20;
EXPLAIN ANALYZE SELECT ...;  -- 记录时间

SET hnsw.ef_search = 40;
EXPLAIN ANALYZE SELECT ...;  -- 记录时间

SET hnsw.ef_search = 100;
EXPLAIN ANALYZE SELECT ...;  -- 记录时间
```

---

## 总结

### 核心要点

1. **HNSW 通过多层图结构实现高效搜索**
   - 顶层稀疏连接，快速定位
   - 底层密集连接，精确搜索

2. **关键参数的作用**
   - `m`：控制连接密度，影响精度和速度
   - `ef_construction`：影响索引构建质量和时间
   - `ef_search`：控制查询精度和速度的平衡

3. **适用场景**
   - 读多写少、精度要求高、查询延迟要求低

4. **性能特点**
   - 查询快、精度高、但构建慢、占用空间大

### 学习建议

1. **理论理解**：先理解小世界网络理论和分层结构
2. **参数实验**：通过不同参数组合测试，观察性能变化
3. **对比学习**：与 IVFFlat 对比，理解各自的优劣
4. **实战应用**：在真实项目中应用，积累经验

---

## 参考资源

- **原始论文**：[Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs](https://arxiv.org/abs/1603.09320)
- **pgvector 官方文档**：https://github.com/pgvector/pgvector#hnsw
- **中文技术文章**：
  - 《高维向量检索的设计与实践（二）》
  - 《如何平衡向量检索速度和精度？深度解读HNSW算法》

---

**最后更新**：2025年1月

