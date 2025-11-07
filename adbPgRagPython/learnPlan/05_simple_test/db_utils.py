"""
数据库连接工具类
封装 PostgreSQL 数据库连接和基本操作
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Optional, List, Dict, Any


class PgVectorClient:
    """
    PostgreSQL 向量数据库客户端
    """
    
    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        """
        初始化数据库连接参数
        
        Args:
            host: 数据库主机地址
            port: 数据库端口
            database: 数据库名称
            user: 用户名
            password: 密码
        """
        self.conn_params = {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password
        }
    
    @contextmanager
    def get_connection(self):
        """
        获取数据库连接的上下文管理器
        自动处理连接的打开和关闭
        
        Yields:
            psycopg2.connection: 数据库连接对象
        """
        conn = psycopg2.connect(**self.conn_params)
        try:
            yield conn
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        执行查询语句
        
        Args:
            query: SQL 查询语句
            params: 查询参数（元组）
        
        Returns:
            List[Dict]: 查询结果列表，每行是一个字典
        """
        with self.get_connection() as conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(query, params)
            return cur.fetchall()
    
    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """
        执行更新语句（INSERT, UPDATE, DELETE）
        
        Args:
            query: SQL 更新语句
            params: 更新参数（元组）
        
        Returns:
            int: 受影响的行数
        """
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()
            return cur.rowcount
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """
        批量执行更新语句
        
        Args:
            query: SQL 更新语句
            params_list: 参数列表，每个元素是一个元组
        
        Returns:
            int: 受影响的总行数
        """
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.executemany(query, params_list)
            conn.commit()
            return cur.rowcount
    
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
            print(f"❌ 数据库连接失败: {str(e)}")
            return False
    
    def check_extension(self, extension_name: str = 'vector') -> bool:
        """
        检查 pgvector 扩展是否已安装
        
        Args:
            extension_name: 扩展名称，默认 'vector'
        
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
            result = self.execute_query(query, (extension_name,))
            return result[0]['exists'] if result else False
        except Exception as e:
            print(f"❌ 检查扩展失败: {str(e)}")
            return False


if __name__ == "__main__":
    """
    测试数据库连接
    """
    from config import DB_CONFIG
    
    print("="*60)
    print("测试数据库连接")
    print("="*60)
    
    # 创建客户端
    client = PgVectorClient(**DB_CONFIG)
    
    # 测试连接
    print("\n测试数据库连接...")
    if client.test_connection():
        print("✅ 数据库连接成功！")
    else:
        print("❌ 数据库连接失败！")
        exit(1)
    
    # 检查 pgvector 扩展
    print("\n检查 pgvector 扩展...")
    if client.check_extension('vector'):
        print("✅ pgvector 扩展已安装")
    else:
        print("❌ pgvector 扩展未安装")
        print("请在数据库中执行: CREATE EXTENSION IF NOT EXISTS vector;")
    
    print("\n" + "="*60)

