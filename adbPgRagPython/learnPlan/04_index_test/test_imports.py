"""
测试所有模块导入是否正常
"""

import sys
from pathlib import Path

print("="*60)
print("测试模块导入")
print("="*60)

# 测试基本依赖
print("\n1. 测试基本依赖包...")
try:
    import psycopg2
    print("   ✅ psycopg2")
except ImportError as e:
    print(f"   ❌ psycopg2: {e}")

try:
    import numpy
    print("   ✅ numpy")
except ImportError as e:
    print(f"   ❌ numpy: {e}")

try:
    from tqdm import tqdm
    print("   ✅ tqdm")
except ImportError as e:
    print(f"   ❌ tqdm: {e}")

# 测试项目模块
print("\n2. 测试项目模块...")
try:
    from config import DB_CONFIG, MODEL_DIMENSION, TEST_TABLE_NAME
    print("   ✅ config")
    print(f"      数据库: {DB_CONFIG['database']}")
    print(f"      向量维度: {MODEL_DIMENSION}")
except ImportError as e:
    print(f"   ❌ config: {e}")

try:
    from db_utils import PgVectorClient
    print("   ✅ db_utils (PgVectorClient)")
except ImportError as e:
    print(f"   ❌ db_utils: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("导入测试完成")
print("="*60)

