"""
向量操作封装
提供向量的插入、查询、相似度搜索等功能
"""

import numpy as np
from typing import Union, List, Dict, Any, Optional
from db_utils import PgVectorClient


class VectorOperations:
    """
    向量操作类
    封装向量数据的增删改查操作
    """
    
    def __init__(self, client: PgVectorClient):
        """
        初始化向量操作类
        
        Args:
            client: PgVectorClient 数据库客户端实例
        """
        self.client = client
    
    def insert_vector(self, table_name: str, data_dict: Dict[str, Any], embedding: Union[np.ndarray, List[float]]) -> int:
        """
        插入向量数据
        
        Args:
            table_name: 表名
            data_dict: 其他字段的字典（不包含 embedding）
            embedding: 向量（numpy array 或 list）
        
        Returns:
            int: 受影响的行数
        """
        # 将向量转换为字符串格式
        if isinstance(embedding, np.ndarray):
            embedding = embedding.tolist()
        
        # 构建向量字符串
        vector_str = '[' + ','.join(map(str, embedding)) + ']'
        
        # 构建插入 SQL
        fields = list(data_dict.keys()) + ['embedding']
        placeholders = ', '.join(['%s'] * len(data_dict) + ['%s::vector'])
        fields_str = ', '.join(fields)
        
        values = list(data_dict.values()) + [vector_str]
        
        query = f"INSERT INTO {table_name} ({fields_str}) VALUES ({placeholders})"
        
        return self.client.execute_update(query, tuple(values))
    
    def batch_insert(self, table_name: str, data_list: List[Dict[str, Any]], embeddings: Union[np.ndarray, List[List[float]]]) -> int:
        """
        批量插入向量数据
        
        Args:
            table_name: 表名
            data_list: 数据字典列表（每个字典对应一行数据，不包含 embedding）
            embeddings: 向量数组（numpy array 或 list of lists）
        
        Returns:
            int: 受影响的总行数
        """
        if len(data_list) != len(embeddings):
            raise ValueError(f"数据数量({len(data_list)})与向量数量({len(embeddings)})不匹配")
        
        # 转换为列表格式
        if isinstance(embeddings, np.ndarray):
            embeddings = embeddings.tolist()
        
        # 构建向量字符串列表
        vector_strs = ['[' + ','.join(map(str, vec)) + ']' for vec in embeddings]
        
        # 获取所有字段名（假设所有数据字典的字段相同）
        if not data_list:
            raise ValueError("数据列表不能为空")
        
        fields = list(data_list[0].keys()) + ['embedding']
        placeholders = ', '.join(['%s'] * len(data_list[0]) + ['%s::vector'])
        fields_str = ', '.join(fields)
        
        query = f"INSERT INTO {table_name} ({fields_str}) VALUES ({placeholders})"
        
        # 构建参数列表
        params_list = []
        for data, vector_str in zip(data_list, vector_strs):
            values = list(data.values()) + [vector_str]
            params_list.append(tuple(values))
        
        return self.client.execute_many(query, params_list)
    
    def cosine_search(self, table_name: str, query_vector: Union[np.ndarray, List[float]], 
                     limit: int = 10, threshold: Optional[float] = None, 
                     where_clause: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        余弦相似度搜索
        
        Args:
            table_name: 表名
            query_vector: 查询向量
            limit: 返回结果数量上限
            threshold: 相似度阈值（余弦相似度，0-1之间），只返回相似度大于阈值的记录
            where_clause: 额外的 WHERE 条件（不含 WHERE 关键字）
        
        Returns:
            List[Dict]: 查询结果列表，包含 similarity 字段
        """
        # 将向量转换为字符串格式
        if isinstance(query_vector, np.ndarray):
            query_vector = query_vector.tolist()
        vector_str = '[' + ','.join(map(str, query_vector)) + ']'
        
        # 构建查询 SQL
        # 注意：<=> 运算符返回余弦距离（0表示完全相同，1表示完全不相似）
        # similarity = 1 - distance 得到余弦相似度（1表示完全相同，0表示完全不相似）
        query = f"""
            SELECT 
                *,
                1 - (embedding <=> %s::vector) AS similarity
            FROM {table_name}
        """
        
        params = [vector_str]
        
        # 添加 WHERE 条件
        where_conditions = []
        if threshold is not None:
            where_conditions.append("(1 - (embedding <=> %s::vector)) > %s")
            params.extend([vector_str, threshold])
        
        if where_clause:
            where_conditions.append(where_clause)
        
        if where_conditions:
            query += " WHERE " + " AND ".join(where_conditions)
        
        # 添加排序和限制
        query += """
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """
        params.extend([vector_str, limit])
        
        return self.client.execute_query(query, tuple(params))
    
    def euclidean_search(self, table_name: str, query_vector: Union[np.ndarray, List[float]], 
                        limit: int = 10, max_distance: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        欧氏距离搜索
        
        Args:
            table_name: 表名
            query_vector: 查询向量
            limit: 返回结果数量上限
            max_distance: 最大距离阈值，只返回距离小于阈值的记录
        
        Returns:
            List[Dict]: 查询结果列表，包含 distance 字段
        """
        # 将向量转换为字符串格式
        if isinstance(query_vector, np.ndarray):
            query_vector = query_vector.tolist()
        vector_str = '[' + ','.join(map(str, query_vector)) + ']'
        
        # 构建查询 SQL
        # <-> 运算符返回欧氏距离
        query = f"""
            SELECT 
                *,
                embedding <-> %s::vector AS distance
            FROM {table_name}
        """
        
        params = [vector_str]
        
        # 添加距离阈值条件
        if max_distance is not None:
            query += " WHERE embedding <-> %s::vector < %s"
            params.extend([vector_str, max_distance])
        
        # 添加排序和限制
        query += """
            ORDER BY embedding <-> %s::vector
            LIMIT %s
        """
        params.extend([vector_str, limit])
        
        return self.client.execute_query(query, tuple(params))
    
    def update_vector(self, table_name: str, record_id: int, 
                     data_dict: Optional[Dict[str, Any]] = None,
                     embedding: Optional[Union[np.ndarray, List[float]]] = None) -> int:
        """
        更新向量数据
        
        Args:
            table_name: 表名
            record_id: 记录ID
            data_dict: 要更新的其他字段字典
            embedding: 新的向量（可选）
        
        Returns:
            int: 受影响的行数
        """
        updates = []
        params = []
        
        if data_dict:
            for key, value in data_dict.items():
                updates.append(f"{key} = %s")
                params.append(value)
        
        if embedding is not None:
            if isinstance(embedding, np.ndarray):
                embedding = embedding.tolist()
            vector_str = '[' + ','.join(map(str, embedding)) + ']'
            updates.append("embedding = %s::vector")
            params.append(vector_str)
        
        if not updates:
            return 0
        
        query = f"UPDATE {table_name} SET {', '.join(updates)} WHERE id = %s"
        params.append(record_id)
        
        return self.client.execute_update(query, tuple(params))
    
    def delete_vector(self, table_name: str, record_id: int) -> int:
        """
        删除向量数据
        
        Args:
            table_name: 表名
            record_id: 记录ID
        
        Returns:
            int: 受影响的行数
        """
        query = f"DELETE FROM {table_name} WHERE id = %s"
        return self.client.execute_update(query, (record_id,))


if __name__ == "__main__":
    """
    简单测试
    """
    from config import DB_CONFIG
    
    print("="*60)
    print("向量操作测试")
    print("="*60)
    
    # 创建客户端和向量操作对象
    client = PgVectorClient(**DB_CONFIG)
    vector_ops = VectorOperations(client)
    
    print("\n✅ 向量操作对象创建成功！")
    print(f"可以使用的表: 需要先创建包含 vector 类型的表")

