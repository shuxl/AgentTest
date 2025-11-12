"""
路由智能体状态定义
定义RouterState和IntentResult数据结构
"""
from typing import TypedDict, List, Optional, Dict, Any
from langchain_core.messages import BaseMessage
from pydantic import BaseModel


class RouterState(TypedDict):
    """路由状态数据结构"""
    messages: List[BaseMessage]  # 消息列表
    current_intent: Optional[str]  # 当前意图：blood_pressure, appointment, diagnosis, internal_medicine_diagnosis, unclear
    sub_intent: Optional[str]  # 子意图（用于诊断意图的细化，如internal_medicine_diagnosis）
    current_agent: Optional[str]  # 当前活跃的智能体名称
    need_reroute: bool  # 是否需要重新路由
    session_id: str  # 会话ID
    user_id: str  # 用户ID


class IntentResult(BaseModel):
    """意图识别结果"""
    intent_type: str  # "blood_pressure", "appointment", "diagnosis", "unclear"
    sub_intent: Optional[str] = None  # 子意图（用于诊断意图的细化，如internal_medicine_diagnosis）
    confidence: float  # 0.0-1.0
    entities: Dict[str, Any]  # 提取的实体信息
    need_clarification: bool  # 是否需要澄清
    reasoning: Optional[str] = None  # 识别理由（可选）

