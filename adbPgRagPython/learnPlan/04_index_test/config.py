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

# 测试表配置
TEST_TABLE_NAME = 'index_test_items'

# 索引测试配置
INDEX_TEST_CONFIG = {
    'hnsw_m_values': [8, 16, 32, 64],  # HNSW m 参数测试值
    'hnsw_ef_construction_values': [32, 64, 128, 200],  # HNSW ef_construction 测试值
    'hnsw_ef_search_values': [20, 40, 100, 200],  # HNSW ef_search 测试值
    'ivfflat_lists_ratios': [1000, 500, 100],  # IVFFlat lists = rows / ratio
    'ivfflat_probes_values': [1, 10, 50, 100],  # IVFFlat probes 测试值
}

