"""
血压记录数据库表结构
创建blood_pressure_records表
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from utils.database import get_db_pool
from utils.config import Config


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS blood_pressure_records (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    systolic INTEGER NOT NULL CHECK (systolic >= 50 AND systolic <= 300),
    diastolic INTEGER NOT NULL CHECK (diastolic >= 30 AND diastolic <= 200),
    measurement_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    original_time_description TEXT,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_systolic_gt_diastolic CHECK (systolic > diastolic)
)
"""

# 索引SQL语句（分开执行）
CREATE_INDEX_SQLS = [
    "CREATE INDEX IF NOT EXISTS idx_blood_pressure_user_id ON blood_pressure_records(user_id)",
    "CREATE INDEX IF NOT EXISTS idx_blood_pressure_measurement_time ON blood_pressure_records(measurement_time)",
    "CREATE INDEX IF NOT EXISTS idx_blood_pressure_user_time ON blood_pressure_records(user_id, measurement_time)"
]


async def create_blood_pressure_table():
    """创建血压记录表"""
    print("=" * 50)
    print("创建血压记录数据库表")
    print("=" * 50)
    
    try:
        db_pool = get_db_pool()
        await db_pool.create_pool()
        
        pool = db_pool.pool
        if pool:
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    # 执行创建表SQL
                    await cur.execute(CREATE_TABLE_SQL)
                    print("✓ 血压记录表创建成功")
                    
                    # 创建索引（逐个执行）
                    for index_sql in CREATE_INDEX_SQLS:
                        try:
                            await cur.execute(index_sql)
                            index_name = index_sql.split("idx_")[1].split(" ON")[0] if "idx_" in index_sql else "未知"
                            print(f"✓ 索引创建成功: {index_name}")
                        except Exception as e:
                            print(f"⚠ 索引创建警告: {str(e)}")
                    
                    # 验证表是否存在
                    await cur.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = 'blood_pressure_records'
                        )
                    """)
                    exists = await cur.fetchone()
                    if exists and exists.get('exists'):
                        print("\n✓ 表验证成功：blood_pressure_records表已存在")
                    else:
                        print("\n✗ 表验证失败：blood_pressure_records表不存在")
                        return False
                    
                    # 检查索引
                    await cur.execute("""
                        SELECT indexname FROM pg_indexes 
                        WHERE tablename = 'blood_pressure_records'
                    """)
                    indexes = await cur.fetchall()
                    print(f"\n✓ 索引数量: {len(indexes)}")
                    for idx in indexes:
                        print(f"  - {idx.get('indexname')}")
        
        await db_pool.close()
        print("\n✓ 数据库表创建完成")
        return True
        
    except Exception as e:
        print(f"\n✗ 创建表失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(create_blood_pressure_table())
    sys.exit(0 if success else 1)

