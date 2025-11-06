"""
路由工具实现
包含意图识别工具和意图澄清工具
"""
import json
import logging
from typing import Optional, Dict, Any
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from ..router_state import IntentResult
from ..llms import get_llm_by_config
from ..config import Config

logger = logging.getLogger(__name__)

# 意图识别系统提示词
INTENT_IDENTIFICATION_PROMPT = """你是一个智能路由助手，负责识别用户的真实意图。

支持的意图类型：
1. blood_pressure: 用户想要记录、查询或管理血压数据
   - 关键词：血压、收缩压、舒张压、记录血压、查询血压、血压记录、血压数据
   - 示例："我想记录血压"、"查询我的血压记录"、"更新血压数据"

2. appointment: 用户想要预约、查询或管理复诊
   - 关键词：预约、复诊、挂号、就诊、门诊、预约医生、预约时间
   - 示例："我想预约复诊"、"查询我的预约"、"取消预约"

3. doctor_assistant: 医生需要助手处理咨询、病历、处方等
   - 关键词：病历、处方、患者、咨询、诊断、开具处方、查看病历
   - 示例："查询患者病历"、"开具处方"、"处理患者咨询"

4. unclear: 意图不明确，需要进一步澄清
   - 当用户的消息无法明确归类到上述三种意图时
   - 示例："你好"、"在吗"、"有什么功能"

请分析用户消息，返回JSON格式的意图识别结果：
{{
    "intent_type": "意图类型（blood_pressure/appointment/doctor_assistant/unclear）",
    "confidence": 置信度（0.0-1.0之间的浮点数）,
    "entities": {{}},
    "need_clarification": 是否需要澄清（true/false）,
    "reasoning": "识别理由"
}}

规则：
- 如果意图明确且置信度>0.8，设置need_clarification=false
- 如果意图不明确（置信度<0.8），设置need_clarification=true
- 如果用户同时提及多个意图，按优先级选择（优先级：doctor_assistant > appointment > blood_pressure）
- 如果用户的消息很短（如"你好"、"在吗"），且当前有活跃的智能体，可能继续当前意图
"""


def _parse_intent_result(llm_response: str) -> IntentResult:
    """
    解析LLM返回的意图识别结果
    
    Args:
        llm_response: LLM返回的文本
        
    Returns:
        IntentResult: 解析后的意图识别结果
    """
    try:
        # 尝试提取JSON部分
        json_start = llm_response.find('{')
        json_end = llm_response.rfind('}') + 1
        
        if json_start == -1 or json_end == 0:
            logger.warning(f"无法找到JSON部分，返回默认结果。响应: {llm_response}")
            return IntentResult(
                intent_type="unclear",
                confidence=0.0,
                entities={},
                need_clarification=True,
                reasoning="无法解析LLM响应"
            )
        
        json_str = llm_response[json_start:json_end]
        data = json.loads(json_str)
        
        # 验证并创建IntentResult
        intent_type = data.get("intent_type", "unclear")
        if intent_type not in ["blood_pressure", "appointment", "doctor_assistant", "unclear"]:
            logger.warning(f"无效的意图类型: {intent_type}，使用unclear")
            intent_type = "unclear"
        
        confidence = float(data.get("confidence", 0.0))
        confidence = max(0.0, min(1.0, confidence))  # 限制在0-1之间
        
        return IntentResult(
            intent_type=intent_type,
            confidence=confidence,
            entities=data.get("entities", {}),
            need_clarification=data.get("need_clarification", confidence < 0.8),
            reasoning=data.get("reasoning", "")
        )
    except json.JSONDecodeError as e:
        logger.error(f"JSON解析失败: {str(e)}，响应: {llm_response}")
        return IntentResult(
            intent_type="unclear",
            confidence=0.0,
            entities={},
            need_clarification=True,
            reasoning=f"JSON解析失败: {str(e)}"
        )
    except Exception as e:
        logger.error(f"解析意图识别结果失败: {str(e)}")
        return IntentResult(
            intent_type="unclear",
            confidence=0.0,
            entities={},
            need_clarification=True,
            reasoning=f"解析失败: {str(e)}"
        )


@tool
def identify_intent(
    query: str,
    conversation_history: Optional[str] = None,
    current_intent: Optional[str] = None
) -> Dict[str, Any]:
    """
    识别用户意图
    
    Args:
        query: 用户查询内容
        conversation_history: 对话历史（可选，JSON字符串格式）
        current_intent: 当前意图（可选）
        
    Returns:
        Dict: 意图识别结果，包含intent_type、confidence、entities、need_clarification等字段
    """
    try:
        # 构建提示词
        prompt = ChatPromptTemplate.from_messages([
            ("system", INTENT_IDENTIFICATION_PROMPT),
            ("human", """用户消息: {query}

对话历史: {history}

当前意图: {current_intent}

请识别用户的真实意图，返回JSON格式的结果。""")
        ])
        
        # 准备输入
        history_text = conversation_history if conversation_history else "无"
        current_intent_text = current_intent if current_intent else "无"
        
        # 调用LLM
        llm = get_llm_by_config()
        chain = prompt | llm
        response = chain.invoke({
            "query": query,
            "history": history_text,
            "current_intent": current_intent_text
        })
        
        # 解析响应
        llm_text = response.content if hasattr(response, 'content') else str(response)
        intent_result = _parse_intent_result(llm_text)
        
        logger.info(f"意图识别结果: {intent_result.intent_type}, 置信度: {intent_result.confidence}")
        
        # 返回字典格式（工具需要返回可序列化的字典）
        return intent_result.model_dump()
        
    except Exception as e:
        logger.error(f"意图识别失败: {str(e)}")
        # 返回默认结果
        default_result = IntentResult(
            intent_type="unclear",
            confidence=0.0,
            entities={},
            need_clarification=True,
            reasoning=f"意图识别异常: {str(e)}"
        )
        return default_result.model_dump()


@tool
def clarify_intent(
    query: str,
    possible_intents: Optional[str] = None
) -> str:
    """
    生成意图澄清问题
    
    Args:
        query: 用户查询内容
        possible_intents: 可能的意图列表（可选，JSON字符串格式）
        
    Returns:
        str: 澄清问题文本
    """
    try:
        clarify_prompt = """你是一个友好的助手，当用户的意图不明确时，你需要友好地引导用户说明他们的需求。

可能的意图类型：
1. blood_pressure: 记录、查询或管理血压数据
2. appointment: 预约、查询或管理复诊
3. doctor_assistant: 处理咨询、病历、处方等医生助手功能

用户消息: {query}

请生成一个友好的澄清问题，引导用户说明他们的具体需求。问题应该简洁明了，不超过50字。"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", clarify_prompt),
            ("human", "用户消息: {query}\n\n请生成澄清问题。")
        ])
        
        llm = get_llm_by_config()
        chain = prompt | llm
        response = chain.invoke({"query": query})
        
        clarification = response.content if hasattr(response, 'content') else str(response)
        clarification = clarification.strip()
        
        logger.info(f"生成澄清问题: {clarification}")
        
        return clarification
        
    except Exception as e:
        logger.error(f"生成澄清问题失败: {str(e)}")
        return "抱歉，我没有理解您的意图。请告诉我您是想记录血压、预约复诊，还是需要其他帮助？"


def get_router_tools():
    """
    获取路由工具列表
    
    Returns:
        List: 路由工具列表
    """
    return [identify_intent, clarify_intent]

