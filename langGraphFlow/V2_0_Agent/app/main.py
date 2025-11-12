"""
FastAPI后端服务入口
实现最小可用的后端API，支持路由智能体的基本对话功能测试
"""
import logging
import sys
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.postgres import AsyncPostgresStore

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from core.config import get_settings
from core.database import get_db_pool
from core.cache import get_redis_manager
from domain.router import create_router_agent
from core.logging import setup_logging
from app.api.routes import router

# 设置统一的日志配置（必须在导入其他模块之前调用）
setup_logging()

# 获取日志记录器
logger = logging.getLogger(__name__)

# 获取配置
settings = get_settings()


# 生命周期函数：应用初始化
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    try:
        # 初始化数据库连接池（统一管理 LangGraph 和 SQLAlchemy）
        db_pool = get_db_pool(settings)
        await db_pool.initialize()  # 初始化连接池和引擎
        app.state.db_pool = db_pool  # 保存 db_pool 实例以便后续访问
        app.state.pool = await db_pool.create_pool()  # LangGraph 使用的连接池
        
        # 记录连接池统计信息
        pool_stats = db_pool.get_pool_stats()
        logger.info(f"数据库连接池初始化成功")
        logger.info(f"连接池统计信息: {pool_stats}")

        # 初始化checkpointer（短期记忆）
        app.state.checkpointer = AsyncPostgresSaver(app.state.pool)
        await app.state.checkpointer.setup()
        logger.info("Checkpointer初始化成功")

        # 初始化store（长期记忆）
        app.state.store = AsyncPostgresStore(app.state.pool)
        await app.state.store.setup()
        logger.info("Store初始化成功")

        # 初始化Redis连接管理器
        app.state.redis_manager = get_redis_manager(settings)
        await app.state.redis_manager.initialize()  # 初始化Redis连接池
        # 测试Redis连接
        if await app.state.redis_manager.ping():
            logger.info("Redis连接初始化成功")
        else:
            logger.warning("Redis连接测试失败，但继续运行")

        # 创建路由智能体（使用checkpointer、pool和store）
        app.state.router_agent = await create_router_agent(
            checkpointer=app.state.checkpointer,
            pool=app.state.pool,
            store=app.state.store
        )
        logger.info("路由智能体初始化成功")

        logger.info("服务完成初始化并启动服务")
        yield

    except Exception as e:
        logger.error(f"初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise RuntimeError(f"服务初始化失败: {str(e)}")

    # 清理资源
    finally:
        # 关闭Redis连接
        if hasattr(app.state, 'redis_manager'):
            await app.state.redis_manager.close()
        # 关闭数据库连接池（统一关闭 LangGraph 和 SQLAlchemy 连接池）
        if hasattr(app.state, 'db_pool'):
            await app.state.db_pool.close()
        logger.info("关闭服务并完成资源清理")


# 实例化FastAPI应用
app = FastAPI(
    title="多智能体路由系统后端API",
    description="基于LangGraph提供多智能体路由服务，支持血压记录、复诊管理、医生助手等功能",
    lifespan=lifespan
)

# 注册路由
app.include_router(router)

# 启动服务器
if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=settings.port)

