"""
API数据模型
定义FastAPI接口的请求和响应数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    """对话请求数据模型"""
    message: str = Field(..., description="用户消息内容")
    session_id: str = Field(..., description="会话ID")
    user_id: str = Field(..., description="用户ID")


class ChatResponse(BaseModel):
    """对话响应数据模型"""
    response: str = Field(..., description="智能体回复内容")
    current_intent: str = Field(..., description="当前意图（blood_pressure/appointment/doctor_assistant/unclear）")
    current_agent: Optional[str] = Field(None, description="当前活跃的智能体名称")

