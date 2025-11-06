"""
数据模型和 Alembic 配置验证测试

本测试脚本用于验证：
1. SQLAlchemy 数据模型是否正确导入和定义
2. 数据库引擎创建和连接是否正常
3. Alembic 迁移配置是否正确

运行方式：
    conda run -n py_311_rag python test/db_models/test_db_models.py
"""
import asyncio
import sys
import os
import logging
from pathlib import Path

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from utils.db.base import Base, get_async_engine
from utils.db.models import BloodPressureRecord, Appointment
from utils.config import Config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_models():
    """测试数据模型导入和定义"""
    logger.info("=" * 60)
    logger.info("测试1：验证数据模型导入")
    logger.info("=" * 60)
    
    try:
        # 检查模型类是否存在
        assert BloodPressureRecord is not None
        assert Appointment is not None
        logger.info("✅ 数据模型导入成功")
        
        # 检查表名
        assert BloodPressureRecord.__tablename__ == "blood_pressure_records"
        assert Appointment.__tablename__ == "appointments"
        logger.info("✅ 表名定义正确")
        
        # 检查 Base.metadata
        assert Base.metadata is not None
        tables = list(Base.metadata.tables.keys())
        logger.info(f"✅ Base.metadata 包含 {len(tables)} 个表: {', '.join(tables)}")
        
        return True
    except Exception as e:
        logger.error(f"❌ 数据模型测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_engine():
    """测试数据库引擎创建"""
    logger.info("\n" + "=" * 60)
    logger.info("测试2：验证数据库引擎创建")
    logger.info("=" * 60)
    
    try:
        engine = get_async_engine()
        assert engine is not None
        logger.info("✅ 数据库引擎创建成功")
        
        # 测试连接
        async with engine.connect() as conn:
            from sqlalchemy import text
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            logger.info(f"✅ 数据库连接成功: {version[:50]}...")
        
        await engine.dispose()
        logger.info("✅ 数据库引擎关闭成功")
        
        return True
    except Exception as e:
        logger.error(f"❌ 数据库引擎测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_alembic_config():
    """测试 Alembic 配置"""
    logger.info("\n" + "=" * 60)
    logger.info("测试3：验证 Alembic 配置")
    logger.info("=" * 60)
    
    try:
        # 检查 alembic 目录是否存在
        project_root_path = Path(project_root)
        alembic_dir = project_root_path / "alembic"
        assert alembic_dir.exists(), "alembic 目录不存在"
        logger.info("✅ alembic 目录存在")
        
        # 检查 alembic.ini 是否存在
        alembic_ini = project_root_path / "alembic.ini"
        assert alembic_ini.exists(), "alembic.ini 文件不存在"
        logger.info("✅ alembic.ini 文件存在")
        
        # 检查 versions 目录是否存在
        versions_dir = alembic_dir / "versions"
        assert versions_dir.exists(), "alembic/versions 目录不存在"
        logger.info("✅ alembic/versions 目录存在")
        
        # 检查迁移脚本
        migration_files = list(versions_dir.glob("*.py"))
        if migration_files:
            logger.info(f"✅ 找到 {len(migration_files)} 个迁移脚本")
            for f in migration_files:
                logger.info(f"   - {f.name}")
        else:
            logger.warning("⚠️  未找到迁移脚本（这是正常的，如果还没有创建）")
        
        return True
    except Exception as e:
        logger.error(f"❌ Alembic 配置测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主函数"""
    logger.info("\n" + "=" * 60)
    logger.info("数据模型和 Alembic 配置验证")
    logger.info("=" * 60 + "\n")
    
    results = []
    
    # 运行测试
    results.append(await test_models())
    results.append(await test_engine())
    results.append(await test_alembic_config())
    
    # 汇总结果
    logger.info("\n" + "=" * 60)
    logger.info("测试结果汇总")
    logger.info("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        logger.info(f"✅ 所有测试通过 ({passed}/{total})")
        return 0
    else:
        logger.error(f"❌ 部分测试失败 ({passed}/{total} 通过)")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

