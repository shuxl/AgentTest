"""
API路由定义
定义FastAPI的路由端点
"""
import logging
from fastapi import APIRouter, HTTPException, Request
from langchain_core.messages import HumanMessage, AIMessage

from .models import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

# 创建路由实例
router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, req: Request):
    """
    对话接口
    统一的对话入口，内部调用路由智能体
    
    Args:
        request: 对话请求，包含message、session_id、user_id
        req: FastAPI请求对象（用于访问app.state）
        
    Returns:
        ChatResponse: 包含response、current_intent、current_agent的响应
    """
    try:
        logger.info(f"收到对话请求: user_id={request.user_id}, session_id={request.session_id}, message={request.message[:50]}...")
        
        # 获取路由智能体（从app.state）
        router_agent = req.app.state.router_agent
        
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


@router.get("/health")
async def health_check(req: Request):
    """健康检查接口"""
    return {"status": "ok", "message": "服务运行正常"}


@router.get("/health/db")
async def db_health_check(req: Request):
    """数据库连接池健康检查接口"""
    try:
        db_pool = req.app.state.db_pool
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

