"""
数据库连接工具类
封装 PostgreSQL 数据库连接和基本操作
复用 05_simple_test 中的代码
"""

import sys
import importlib.util
from pathlib import Path

# 使用 importlib 直接加载 05_simple_test/db_utils.py 模块，避免循环导入
_05_simple_test_path = Path(__file__).parent.parent / '05_simple_test' / 'db_utils.py'
spec = importlib.util.spec_from_file_location("_db_utils_05", _05_simple_test_path)
_db_utils_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_db_utils_module)

# 导出 PgVectorClient
PgVectorClient = _db_utils_module.PgVectorClient

__all__ = ['PgVectorClient']

