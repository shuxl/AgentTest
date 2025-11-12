"""
路由节点实现
包含router_node和route_decision函数
"""
import logging
from typing import Literal
from langchain_core.messages import AIMessage, HumanMessage
from .state import RouterState, IntentResult
from .tools.router_tools import identify_intent, clarify_intent
from core.config import get_settings

logger = logging.getLogger(__name__)


def router_node(state: RouterState) -> RouterState:
    """
    路由节点函数
    每次调用都会经过此节点，识别意图并更新状态
    
    Args:
        state: 路由状态
        
    Returns:
        RouterState: 更新后的路由状态
    """
    # 获取配置
    settings = get_settings()
    
    # 获取最后一条消息
    messages = state.get("messages", [])
    if not messages:
        logger.warning("没有消息，返回未更新状态")
        return state
    
    last_message = messages[-1]
    
    # 关键修复：如果最后一条消息是AI消息，说明没有新的用户消息，应该停止执行
    # 这可以防止无限循环：router -> agent -> router -> ...
    if isinstance(last_message, AIMessage):
        logger.debug("最后一条消息是AI消息，没有新的用户消息，停止路由执行")
        # 直接返回当前状态，不进行路由决策
        return state
    
    # 获取用户查询
    user_query = ""
    if isinstance(last_message, HumanMessage):
        user_query = last_message.content
    else:
        user_query = str(last_message.content) if hasattr(last_message, 'content') else str(last_message)
    
    # 获取当前意图和智能体
    current_intent = state.get("current_intent")
    current_agent = state.get("current_agent")
    
    logger.info(f"路由节点: 用户查询='{user_query}', 当前意图={current_intent}, 当前智能体={current_agent}")
    
    # 准备对话历史（用于上下文）
    conversation_history = []
    for msg in messages[-5:]:  # 只取最近5条消息
        if isinstance(msg, HumanMessage):
            conversation_history.append(f"用户: {msg.content}")
        elif isinstance(msg, AIMessage):
            conversation_history.append(f"助手: {msg.content}")
    
    conversation_history_str = "\n".join(conversation_history) if conversation_history else None
    
    # 调用意图识别工具
    try:
        intent_result_dict = identify_intent.invoke({
            "query": user_query,
            "conversation_history": conversation_history_str,
            "current_intent": current_intent
        })
        
        intent_result = IntentResult(**intent_result_dict)
        
        logger.info(f"意图识别结果: type={intent_result.intent_type}, confidence={intent_result.confidence}, "
                   f"need_clarification={intent_result.need_clarification}")
        
        # 检查是否需要重新路由
        need_reroute = False
        new_intent = intent_result.intent_type
        new_agent = None
        
        # 如果置信度低，需要澄清
        if intent_result.confidence < settings.intent_confidence_threshold:
            logger.info(f"置信度低（{intent_result.confidence} < {settings.intent_confidence_threshold}），需要澄清")
            new_intent = "unclear"
            new_agent = None
        else:
            # 置信度高，检查意图是否变化
            if current_intent != new_intent:
                logger.info(f"检测到意图变化: {current_intent} -> {new_intent}")
                need_reroute = True
            
            # 确定对应的智能体
            intent_to_agent = {
                "blood_pressure": "blood_pressure_agent",
                "appointment": "appointment_agent",
                "internal_medicine_diagnosis": "internal_medicine_diagnosis_agent",
                "diagnosis": "internal_medicine_diagnosis_agent",  # 通用诊断意图也路由到内科诊断智能体（默认）
                "doctor_assistant": "doctor_assistant_agent",
                "unclear": None
            }
            
            # 处理诊断意图的子类型
            sub_intent = intent_result.sub_intent
            if new_intent == "diagnosis" and sub_intent:
                # 如果有子意图，使用子意图对应的智能体
                # 科室诊断智能体映射
                diagnosis_agent_map = {
                    "internal_medicine_diagnosis": "internal_medicine_diagnosis_agent",
                    "surgery_diagnosis": "surgery_diagnosis_agent",
                    "pediatrics_diagnosis": "pediatrics_diagnosis_agent",
                    "gynecology_diagnosis": "gynecology_diagnosis_agent",
                    "cardiology_diagnosis": "cardiology_diagnosis_agent",
                    "general_diagnosis": "general_diagnosis_agent"
                }
                
                if sub_intent in diagnosis_agent_map:
                    new_agent = diagnosis_agent_map[sub_intent]
                    new_intent = sub_intent  # 更新意图为子意图
                else:
                    # 未知的子类型，使用通用诊断智能体
                    logger.warning(f"诊断子类型 {sub_intent} 未映射到具体智能体，使用通用诊断智能体")
                    new_agent = "general_diagnosis_agent"
                    new_intent = "general_diagnosis"
            else:
                new_agent = intent_to_agent.get(new_intent)
        
        # 更新状态
        updated_state = state.copy()
        updated_state["current_intent"] = new_intent
        updated_state["current_agent"] = new_agent
        updated_state["need_reroute"] = need_reroute
        # 保存子意图
        if intent_result.sub_intent:
            updated_state["sub_intent"] = intent_result.sub_intent
        
        logger.info(f"状态更新: current_intent={new_intent}, sub_intent={intent_result.sub_intent}, current_agent={new_agent}, need_reroute={need_reroute}")
        
        return updated_state
        
    except Exception as e:
        logger.error(f"路由节点执行失败: {str(e)}")
        # 返回默认状态，设置为unclear
        updated_state = state.copy()
        updated_state["current_intent"] = "unclear"
        updated_state["need_reroute"] = False
        return updated_state


def clarify_intent_node(state: RouterState) -> RouterState:
    """
    意图澄清节点函数
    当意图不明确时，生成澄清问题
    
    Args:
        state: 路由状态
        
    Returns:
        RouterState: 更新后的路由状态（添加澄清问题消息）
    """
    messages = state.get("messages", [])
    if not messages:
        return state
    
    # 获取最后一条用户消息
    last_message = messages[-1]
    user_query = ""
    
    if isinstance(last_message, HumanMessage):
        user_query = last_message.content
    else:
        user_query = str(last_message.content) if hasattr(last_message, 'content') else str(last_message)
    
    # 调用澄清工具
    try:
        clarification = clarify_intent.invoke({
            "query": user_query,
            "possible_intents": None
        })
        
        logger.info(f"生成澄清问题: {clarification}")
        
        # 添加澄清问题到消息列表
        updated_state = state.copy()
        updated_messages = list(messages)
        updated_messages.append(AIMessage(content=clarification))
        updated_state["messages"] = updated_messages
        
        return updated_state
        
    except Exception as e:
        logger.error(f"意图澄清节点执行失败: {str(e)}")
        # 返回默认澄清问题
        default_clarification = "抱歉，我没有理解您的意图。请告诉我您是想记录血压、预约复诊，还是需要其他帮助？"
        updated_state = state.copy()
        updated_messages = list(state.get("messages", []))
        updated_messages.append(AIMessage(content=default_clarification))
        updated_state["messages"] = updated_messages
        return updated_state


def route_decision(state: RouterState) -> Literal[
    "blood_pressure", "appointment", 
    "internal_medicine_diagnosis", "surgery_diagnosis", "pediatrics_diagnosis",
    "gynecology_diagnosis", "cardiology_diagnosis", "general_diagnosis",
    "doctor_assistant", "unclear", "__end__"
]:
    """
    路由决策函数
    根据当前意图返回路由目标节点名称
    
    Args:
        state: 路由状态
        
    Returns:
        Literal: 路由目标节点名称，如果是"__end__"则停止执行
    """
    # 检查是否有新的用户消息
    messages = state.get("messages", [])
    if messages:
        last_message = messages[-1]
        # 如果最后一条消息是AI消息，停止执行
        if isinstance(last_message, AIMessage):
            logger.info("路由决策: 最后一条消息是AI消息，停止执行")
            return "__end__"  # type: ignore
    
    current_intent = state.get("current_intent", "unclear")
    
    logger.info(f"路由决策: current_intent={current_intent}")
    
    # 如果意图是unclear，路由到clarify_intent节点
    if current_intent == "unclear":
        return "unclear"
    
    # 其他情况直接返回意图类型（对应智能体节点名称）
    return current_intent  # type: ignore

