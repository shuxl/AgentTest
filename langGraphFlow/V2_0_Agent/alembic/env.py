"""
Alembic 环境配置
支持异步数据库迁移
"""
import asyncio
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine

from alembic import context

# 添加项目根目录到 sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# 导入配置和模型
from utils.config import Config
from utils.db.base import Base, get_async_engine
from utils.db.models import BloodPressureRecord, Appointment  # noqa: F401

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# 导入所有模型以确保 Alembic 能够检测到它们
target_metadata = Base.metadata

# 设置数据库连接 URL（从 Config 读取）
# 将 postgresql:// 转换为 postgresql+psycopg://
db_uri = Config.DB_URI
if db_uri.startswith("postgresql://"):
    sqlalchemy_uri = db_uri.replace("postgresql://", "postgresql+psycopg://", 1)
else:
    sqlalchemy_uri = db_uri

config.set_main_option("sqlalchemy.url", sqlalchemy_uri)


# 定义需要忽略的表（LangGraph 管理的表）
IGNORE_TABLES = {
    'checkpoints',
    'checkpoint_writes',
    'checkpoint_blobs',
    'checkpoint_migrations',
    'store',
    'store_migrations',
    'test_sqlalchemy_setup',  # 测试表
}


def include_name(name: str, type_: str, parent_names: dict) -> bool:
    """
    过滤函数：决定是否包含某个数据库对象
    
    Args:
        name: 对象名称
        type_: 对象类型（'table', 'index', 'column' 等）
        parent_names: 父对象名称字典
        
    Returns:
        bool: True 表示包含，False 表示忽略
    """
    if type_ == 'table':
        # 忽略 LangGraph 管理的表
        return name not in IGNORE_TABLES
    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_name,  # 使用过滤函数
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """执行迁移"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_object=include_name,  # 使用过滤函数
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """在异步模式下运行迁移"""
    # 获取异步引擎
    engine = get_async_engine()

    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await engine.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # 使用异步引擎运行迁移
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
