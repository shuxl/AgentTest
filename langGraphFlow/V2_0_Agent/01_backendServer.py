"""
FastAPI后端服务
实现最小可用的后端API，支持路由智能体的基本对话功能测试
"""
import logging
import sys
import os
from pydantic import BaseModel, Field
import time
from fastapi import FastAPI, HTTPException
from typing import Dict, Any, Optional
import uvicorn
from contextlib import asynccontextmanager
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.postgres import AsyncPostgresStore

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from core.config import get_settings
from core.database import get_db_pool
from core.cache import get_redis_manager
from domain.router import create_router_agent
from core.logging import setup_logging

# 设置统一的日志配置（必须在导入其他模块之前调用）
setup_logging()

# 获取日志记录器
logger = logging.getLogger(__name__)


# 定义数据模型：客户端发起的对话请求
class ChatRequest(BaseModel):
    """对话请求数据模型"""
    message: str = Field(..., description="用户消息内容")
    session_id: str = Field(..., description="会话ID")
    user_id: str = Field(..., description="用户ID")


# 定义数据模型：对话响应
class ChatResponse(BaseModel):
    """对话响应数据模型"""
    response: str = Field(..., description="智能体回复内容")
    current_intent: str = Field(..., description="当前意图（blood_pressure/appointment/doctor_assistant/unclear）")
    current_agent: Optional[str] = Field(None, description="当前活跃的智能体名称")


# 生命周期函数：应用初始化
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    try:
        # 初始化数据库连接池（统一管理 LangGraph 和 SQLAlchemy）
        db_pool = get_db_pool()
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
        app.state.redis_manager = get_redis_manager()
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


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    对话接口
    统一的对话入口，内部调用路由智能体
    
    Args:
        request: 对话请求，包含message、session_id、user_id
        
    Returns:
        ChatResponse: 包含response、current_intent、current_agent的响应
    """
    try:
        logger.info(f"收到对话请求: user_id={request.user_id}, session_id={request.session_id}, message={request.message[:50]}...")
        
        # 获取路由智能体
        router_agent = app.state.router_agent
        
        # 构造输入消息
        messages = [HumanMessage(content=request.message)]
        
        # 构造配置（使用session_id作为thread_id）
        # 设置递归限制，防止无限循环（默认25，我们设置为50以提供更多空间）
        config = {
            "configurable": {
                "thread_id": request.session_id,
                "recursion_limit": 50  # 增加递归限制，防止超时
            }
        }
        
        # 构造状态（包含user_id和session_id）
        state_input = {
            "messages": messages,
            "user_id": request.user_id,
            "session_id": request.session_id,
            "current_intent": None,
            "current_agent": None,
            "need_reroute": False
        }
        
        # 调用路由智能体
        # 注意：LangGraph会自动从checkpointer读取历史状态
        # 我们只需要传入新的用户消息，LangGraph会自动合并到历史中
        result = await router_agent.ainvoke(state_input, config=config)
        
        # 提取最后一条AI消息作为回复
        messages_result = result.get("messages", [])
        response_text = ""
        if messages_result:
            # 找到最后一条AI消息
            for msg in reversed(messages_result):
                if isinstance(msg, AIMessage):
                    if hasattr(msg, 'content'):
                        response_text = msg.content
                    else:
                        response_text = str(msg)
                    break
        
        # 如果没有找到AI消息，使用最后一条消息
        if not response_text and messages_result:
            last_message = messages_result[-1]
            if hasattr(last_message, 'content'):
                response_text = last_message.content
            else:
                response_text = str(last_message)
        
        # 获取当前意图和智能体
        current_intent = result.get("current_intent", "unclear")
        current_agent = result.get("current_agent")
        
        logger.info(f"对话完成: current_intent={current_intent}, current_agent={current_agent}, response_length={len(response_text)}")
        
        # 返回响应
        return ChatResponse(
            response=response_text,
            current_intent=current_intent,
            current_agent=current_agent
        )
        
    except Exception as e:
        logger.error(f"处理对话请求时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"处理请求时出错: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok", "message": "服务运行正常"}


@app.get("/health/db")
async def db_health_check():
    """数据库连接池健康检查接口"""
    try:
        db_pool = app.state.db_pool
        pool_stats = db_pool.get_pool_stats()
        
        # 检查连接池状态
        langgraph_ok = db_pool.pool is not None
        sqlalchemy_ok = db_pool.sqlalchemy_engine is not None
        
        status = "ok" if (langgraph_ok and sqlalchemy_ok) else "degraded"
        
        return {
            "status": status,
            "langgraph_pool": "ok" if langgraph_ok else "not_initialized",
            "sqlalchemy_engine": "ok" if sqlalchemy_ok else "not_initialized",
            "pool_stats": pool_stats
        }
    except Exception as e:
        logger.error(f"数据库健康检查失败: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }


# 启动服务器
if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(app, host=settings.host, port=settings.port)

