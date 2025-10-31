"""
数据库配置文件
"""

# PostgreSQL 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'sxl_pg_db1',
    'user': 'postgres',
    'password': 'sxl_pwd_123'
}

# Embedding 模型配置
MODEL_NAME = "moka-ai/m3e-base"
MODEL_DIMENSION = 768

