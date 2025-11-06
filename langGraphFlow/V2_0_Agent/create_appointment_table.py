"""
复诊管理数据库表结构
创建appointments表
"""
import asyncio
import sys
import os

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from utils.database import get_db_pool
from utils.config import Config


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS appointments (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    department VARCHAR(255) NOT NULL,
    doctor_id VARCHAR(255),
    doctor_name VARCHAR(255),
    appointment_date TIMESTAMP NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'cancelled')),
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""

# 索引SQL语句（分开执行）
CREATE_INDEX_SQLS = [
    "CREATE INDEX IF NOT EXISTS idx_appointments_user_id ON appointments(user_id)",
    "CREATE INDEX IF NOT EXISTS idx_appointments_appointment_date ON appointments(appointment_date)",
    "CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status)",
    "CREATE INDEX IF NOT EXISTS idx_appointments_user_status ON appointments(user_id, status)"
]


async def create_appointment_table():
    """创建复诊预约表"""
    print("=" * 50)
    print("创建复诊预约数据库表")
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
                    print("✓ 复诊预约表创建成功")
                    
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
                            WHERE table_name = 'appointments'
                        )
                    """)
                    exists = await cur.fetchone()
                    if exists and exists.get('exists'):
                        print("\n✓ 表验证成功：appointments表已存在")
                    else:
                        print("\n✗ 表验证失败：appointments表不存在")
                        return False
                    
                    # 检查索引
                    await cur.execute("""
                        SELECT indexname FROM pg_indexes 
                        WHERE tablename = 'appointments'
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
    success = asyncio.run(create_appointment_table())
    sys.exit(0 if success else 1)

