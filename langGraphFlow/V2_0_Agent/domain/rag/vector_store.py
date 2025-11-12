"""
向量数据库操作工具
封装PostgreSQL + pgvector的向量数据库操作
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Optional, List, Dict, Any, Union
from urllib.parse import urlparse
import numpy as np
import logging

from core.config import get_settings

logger = logging.getLogger(__name__)


class VectorStore:
    """
    向量数据库操作工具类
    封装PostgreSQL + pgvector的向量数据库操作
    """
    
    def __init__(self, db_uri: Optional[str] = None):
        """
        初始化向量数据库操作工具
        
        Args:
            db_uri: 数据库连接URI，默认使用Settings中的db_uri
        """
        settings = get_settings()
        self.db_uri = db_uri or settings.db_uri
        self._conn_params = self._parse_db_uri(self.db_uri)
    
    def _parse_db_uri(self, db_uri: str) -> Dict[str, Any]:
        """
        解析数据库URI
        
        Args:
            db_uri: 数据库连接URI
        
        Returns:
            dict: 数据库连接参数字典
        """
        parsed = urlparse(db_uri)
        return {
            'host': parsed.hostname or 'localhost',
            'port': parsed.port or 5432,
            'database': parsed.path.lstrip('/').split('?')[0] or 'doctor_agent_db',
            'user': parsed.username or 'postgres',
            'password': parsed.password or ''
        }
    
    @contextmanager
    def get_connection(self):
        """
        获取数据库连接的上下文管理器
        自动处理连接的打开和关闭
        
        Yields:
            psycopg2.connection: 数据库连接对象
        """
        conn = psycopg2.connect(**self._conn_params)
        try:
            yield conn
        finally:
            conn.close()
    
    def test_connection(self) -> bool:
        """
        测试数据库连接是否正常
        
        Returns:
            bool: 连接是否成功
        """
        try:
            with self.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"数据库连接失败: {str(e)}")
            return False
    
    def check_extension(self, extension_name: str = 'vector') -> bool:
        """
        检查pgvector扩展是否已安装
        
        Args:
            extension_name: 扩展名称，默认'vector'
        
        Returns:
            bool: 扩展是否已安装
        """
        try:
            query = """
                SELECT EXISTS(
                    SELECT 1 FROM pg_extension 
                    WHERE extname = %s
                ) as exists;
            """
            with self.get_connection() as conn:
                cur = conn.cursor()
                cur.execute(query, (extension_name,))
                result = cur.fetchone()
                return result[0] if result else False
        except Exception as e:
            logger.error(f"检查扩展失败: {str(e)}")
            return False
    
    def create_table(
        self,
        table_name: str,
        dimension: int = 768,
        drop_if_exists: bool = False
    ) -> bool:
        """
        创建包含向量字段的表
        
        Args:
            table_name: 表名
            dimension: 向量维度，默认768
            drop_if_exists: 如果表已存在，是否删除重建
        
        Returns:
            bool: 是否创建成功
        """
        try:
            with self.get_connection() as conn:
                cur = conn.cursor()
                
                # 如果drop_if_exists为True，先删除表
                if drop_if_exists:
                    cur.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
                    conn.commit()
                
                # 创建表
                create_table_sql = f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    embedding vector({dimension}),
                    metadata JSONB DEFAULT '{{}}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
                cur.execute(create_table_sql)
                conn.commit()
                logger.info(f"表 {table_name} 创建成功（维度: {dimension}）")
                return True
        except Exception as e:
            logger.error(f"创建表失败: {str(e)}")
            return False
    
    def create_index(
        self,
        table_name: str,
        index_type: str = "hnsw",
        m: int = 16,
        ef_construction: int = 64
    ) -> bool:
        """
        创建向量索引
        
        Args:
            table_name: 表名
            index_type: 索引类型，'hnsw' 或 'ivfflat'
            m: HNSW索引的m参数（仅用于hnsw）
            ef_construction: HNSW索引的ef_construction参数（仅用于hnsw）
        
        Returns:
            bool: 是否创建成功
        """
        try:
            index_name = f"{table_name}_embedding_{index_type}_idx"
            
            # 检查索引是否已存在
            with self.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT EXISTS(
                        SELECT 1 FROM pg_indexes 
                        WHERE indexname = %s
                    ) as exists;
                """, (index_name,))
                result = cur.fetchone()
                if result and result[0]:
                    logger.info(f"索引 {index_name} 已存在")
                    return True
                
                # 创建索引
                if index_type.lower() == "hnsw":
                    create_index_sql = f"""
                    CREATE INDEX {index_name} ON {table_name} 
                    USING hnsw (embedding vector_cosine_ops)
                    WITH (m = {m}, ef_construction = {ef_construction});
                    """
                elif index_type.lower() == "ivfflat":
                    create_index_sql = f"""
                    CREATE INDEX {index_name} ON {table_name} 
                    USING ivfflat (embedding vector_cosine_ops)
                    WITH (lists = 100);
                    """
                else:
                    raise ValueError(f"不支持的索引类型: {index_type}")
                
                cur.execute(create_index_sql)
                conn.commit()
                logger.info(f"索引 {index_name} 创建成功")
                return True
        except Exception as e:
            logger.error(f"创建索引失败: {str(e)}")
            return False
    
    def insert_vector(
        self,
        table_name: str,
        content: str,
        embedding: Union[np.ndarray, List[float]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[int]:
        """
        插入向量数据
        
        Args:
            table_name: 表名
            content: 文本内容
            embedding: 向量（numpy array 或 list）
            metadata: 元数据字典（可选）
        
        Returns:
            Optional[int]: 插入的记录ID，失败返回None
        """
        try:
            # 将向量转换为字符串格式
            if isinstance(embedding, np.ndarray):
                embedding = embedding.tolist()
            vector_str = '[' + ','.join(map(str, embedding)) + ']'
            
            # 处理元数据
            import json
            metadata_json = json.dumps(metadata) if metadata else '{}'
            
            with self.get_connection() as conn:
                cur = conn.cursor()
                insert_sql = f"""
                INSERT INTO {table_name} (content, embedding, metadata)
                VALUES (%s, %s::vector, %s::jsonb)
                RETURNING id;
                """
                cur.execute(insert_sql, (content, vector_str, metadata_json))
                record_id = cur.fetchone()[0]
                conn.commit()
                logger.debug(f"向量插入成功，ID: {record_id}")
                return record_id
        except Exception as e:
            logger.error(f"向量插入失败: {str(e)}")
            return None
    
    def batch_insert(
        self,
        table_name: str,
        contents: List[str],
        embeddings: Union[np.ndarray, List[List[float]]],
        metadata_list: Optional[List[Dict[str, Any]]] = None
    ) -> int:
        """
        批量插入向量数据
        
        Args:
            table_name: 表名
            contents: 文本内容列表
            embeddings: 向量数组（numpy array 或 list of lists）
            metadata_list: 元数据列表（可选）
        
        Returns:
            int: 插入的记录数
        """
        if len(contents) != len(embeddings):
            raise ValueError(f"内容数量({len(contents)})与向量数量({len(embeddings)})不匹配")
        
        try:
            # 转换为列表格式
            if isinstance(embeddings, np.ndarray):
                embeddings = embeddings.tolist()
            
            # 构建向量字符串列表
            vector_strs = ['[' + ','.join(map(str, vec)) + ']' for vec in embeddings]
            
            # 处理元数据
            import json
            if metadata_list is None:
                metadata_list = [{}] * len(contents)
            metadata_jsons = [json.dumps(md) if md else '{}' for md in metadata_list]
            
            with self.get_connection() as conn:
                cur = conn.cursor()
                insert_sql = f"""
                INSERT INTO {table_name} (content, embedding, metadata)
                VALUES (%s, %s::vector, %s::jsonb)
                """
                
                # 批量插入
                params_list = list(zip(contents, vector_strs, metadata_jsons))
                cur.executemany(insert_sql, params_list)
                conn.commit()
                
                inserted_count = cur.rowcount
                logger.info(f"批量插入成功，共插入 {inserted_count} 条记录")
                return inserted_count
        except Exception as e:
            logger.error(f"批量插入失败: {str(e)}")
            raise
    
    def cosine_search(
        self,
        table_name: str,
        query_vector: Union[np.ndarray, List[float]],
        limit: int = 10,
        threshold: Optional[float] = None,
        where_clause: Optional[str] = None
    ) -> List[Dict[str, Any]]:
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
        try:
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
            
            with self.get_connection() as conn:
                cur = conn.cursor(cursor_factory=RealDictCursor)
                cur.execute(query, tuple(params))
                results = cur.fetchall()
                
                # 转换为字典列表
                return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"相似度搜索失败: {str(e)}")
            raise
    
    def update_vector(
        self,
        table_name: str,
        record_id: int,
        content: Optional[str] = None,
        embedding: Optional[Union[np.ndarray, List[float]]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        更新向量数据
        
        Args:
            table_name: 表名
            record_id: 记录ID
            content: 新的文本内容（可选）
            embedding: 新的向量（可选）
            metadata: 新的元数据（可选）
        
        Returns:
            bool: 是否更新成功
        """
        try:
            updates = []
            params = []
            
            if content is not None:
                updates.append("content = %s")
                params.append(content)
            
            if embedding is not None:
                if isinstance(embedding, np.ndarray):
                    embedding = embedding.tolist()
                vector_str = '[' + ','.join(map(str, embedding)) + ']'
                updates.append("embedding = %s::vector")
                params.append(vector_str)
            
            if metadata is not None:
                import json
                metadata_json = json.dumps(metadata)
                updates.append("metadata = %s::jsonb")
                params.append(metadata_json)
            
            if not updates:
                return False
            
            params.append(record_id)
            
            with self.get_connection() as conn:
                cur = conn.cursor()
                query = f"UPDATE {table_name} SET {', '.join(updates)} WHERE id = %s"
                cur.execute(query, tuple(params))
                conn.commit()
                logger.debug(f"向量更新成功，ID: {record_id}")
                return True
        except Exception as e:
            logger.error(f"向量更新失败: {str(e)}")
            return False
    
    def delete_vector(self, table_name: str, record_id: int) -> bool:
        """
        删除向量数据
        
        Args:
            table_name: 表名
            record_id: 记录ID
        
        Returns:
            bool: 是否删除成功
        """
        try:
            with self.get_connection() as conn:
                cur = conn.cursor()
                query = f"DELETE FROM {table_name} WHERE id = %s"
                cur.execute(query, (record_id,))
                conn.commit()
                logger.debug(f"向量删除成功，ID: {record_id}")
                return True
        except Exception as e:
            logger.error(f"向量删除失败: {str(e)}")
            return False


if __name__ == "__main__":
    """
    测试代码
    """
    import sys
    from pathlib import Path
    
    # 添加项目根目录到路径
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    print("=" * 60)
    print("向量数据库操作工具测试")
    print("=" * 60)
    
    # 创建向量存储实例
    store = VectorStore()
    
    # 测试连接
    print("\n测试数据库连接...")
    if store.test_connection():
        print("✅ 数据库连接成功")
    else:
        print("❌ 数据库连接失败")
        exit(1)
    
    # 检查扩展
    print("\n检查pgvector扩展...")
    if store.check_extension('vector'):
        print("✅ pgvector扩展已安装")
    else:
        print("❌ pgvector扩展未安装")
        print("请在数据库中执行: CREATE EXTENSION IF NOT EXISTS vector;")
        exit(1)
    
    print("\n" + "=" * 60)

