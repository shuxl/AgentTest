"""
API模块
包含API路由定义和数据模型
"""
from .models import ChatRequest, ChatResponse
from .routes import router

__all__ = [
    "ChatRequest",
    "ChatResponse",
    "router",
]

