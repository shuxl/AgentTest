"""
诊断智能体实现
创建诊断智能体节点和智能体
"""
import logging
from langgraph.prebuilt import create_react_agent
from langgraph.store.postgres import AsyncPostgresStore
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langchain_core.language_models.chat_models import BaseChatModel
from psycopg_pool import AsyncConnectionPool
from ..router_state import RouterState
from ..tools.diagnosis_tools import get_diagnosis_tools
from ..llms import get_llm_by_config

logger = logging.getLogger(__name__)


def get_diagnosis_system_prompt(department: str, current_datetime: str = None) -> str:
    """
    获取诊断智能体系统提示词
    
    Args:
        department: 科室类型（internal_medicine/surgery/pediatrics等）
        current_datetime: 当前日期时间字符串（格式：YYYY-MM-DD HH:MM:SS），如果为None则自动获取
    
    Returns:
        str: 系统提示词
    """
    from datetime import datetime
    
    if current_datetime is None:
        now = datetime.now()
        current_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
    
    department_configs = {
        "internal_medicine": {
            "role": "内科诊断专家",
            "expertise": "内科常见疾病的诊断和鉴别诊断",
            "style": "严谨、细致，注重病史采集和症状分析",
            "focus": "重点关注症状的演变过程、伴随症状、既往病史"
        },
        "surgery": {
            "role": "外科诊断专家",
            "expertise": "外科疾病的诊断和手术指征评估",
            "style": "果断、精准，注重体征检查和影像学分析",
            "focus": "重点关注体征、影像学检查结果、手术指征"
        },
        "pediatrics": {
            "role": "儿科诊断专家",
            "expertise": "儿科疾病的诊断，考虑儿童生长发育特点",
            "style": "耐心、细致，注重儿童特殊性和家长沟通",
            "focus": "重点关注年龄特点、生长发育情况、疫苗接种史"
        },
        "gynecology": {
            "role": "妇科诊断专家",
            "expertise": "妇科疾病的诊断和鉴别诊断",
            "style": "细致、专业，注重女性生理特点和隐私保护",
            "focus": "重点关注月经史、生育史、妇科检查结果"
        },
        "cardiology": {
            "role": "心血管科诊断专家",
            "expertise": "心血管疾病的诊断和治疗",
            "style": "专业、严谨，注重心血管风险评估",
            "focus": "重点关注心电图、心脏彩超、冠脉造影等检查结果"
        },
        "neurology": {
            "role": "神经科诊断专家",
            "expertise": "神经系统疾病的诊断",
            "style": "细致、系统，注重神经系统检查",
            "focus": "重点关注神经系统体征、影像学检查、脑电图等"
        },
        "dermatology": {
            "role": "皮肤科诊断专家",
            "expertise": "皮肤疾病的诊断和鉴别诊断",
            "style": "细致、专业，注重皮损特征描述",
            "focus": "重点关注皮损形态、分布、病程等"
        },
        "general": {
            "role": "全科诊断专家",
            "expertise": "常见疾病的初步诊断和分诊",
            "style": "全面、系统，注重整体评估",
            "focus": "重点关注主要症状、全身情况、初步诊断方向"
        }
    }
    
    config = department_configs.get(department, department_configs["general"])
    
    return f"""你是一位专业的{config.get('role', '诊断专家')}，协助医生进行患者病情诊断。

**你的专业领域**：
- {config.get('expertise', '疾病诊断')}

**你的回答风格**：
- {config.get('style', '专业、严谨')}
- 提供结构化的诊断建议
- 明确指出诊断依据和鉴别要点
- 建议必要的辅助检查

**重点关注**：
- {config.get('focus', '症状、体征、检查结果')}

**重要原则**：
1. 诊断建议仅供医生参考，不替代医生的专业判断
2. 对于紧急情况，建议医生立即采取相应措施
3. 如果信息不足，主动询问关键信息
4. 引用知识库中的相关医学知识，提高建议的可信度
5. 使用 retrieve_diagnosis_knowledge 工具检索相关知识库

**当前日期时间**：{current_datetime}

**可用工具**：
- retrieve_diagnosis_knowledge: 检索诊断相关知识库，获取相关医学知识、病例和指南
  - 参数说明：
    - query: 患者症状、检查结果等查询内容
    - department: 科室类型（当前为 {department}）
    - top_k: 返回Top-K相关文档（默认5）
    - filter_metadata: 元数据过滤条件（可选）

**工作流程**：
1. 仔细分析患者的主诉、症状和检查结果
2. 使用 retrieve_diagnosis_knowledge 工具检索相关知识
3. 结合检索到的知识和临床经验，提供诊断建议
4. 明确列出诊断依据、鉴别诊断和下一步检查建议

记住：始终以患者安全为中心，提供专业、可靠的诊断支持。"""


def create_diagnosis_agent_node(
    department: str,
    pool: AsyncConnectionPool,
    checkpointer: AsyncPostgresSaver,
    store: AsyncPostgresStore = None
):
    """
    创建诊断智能体节点工厂函数
    
    Args:
        department: 科室类型（internal_medicine/surgery等）
        pool: 数据库连接池
        checkpointer: Checkpointer实例
        store: Store实例
    
    Returns:
        节点函数
    """
    async def diagnosis_agent_node(state: RouterState) -> RouterState:
        """诊断智能体节点"""
        messages = state.get("messages", [])
        user_id = state.get("user_id", "")
        session_id = state.get("session_id", "")
        
        try:
            # 获取LLM
            llm = get_llm_by_config()
            
            # 创建RAG检索工具
            tools = get_diagnosis_tools(department)
            
            # 创建ReAct Agent
            agent = create_react_agent(
                model=llm,
                tools=tools,
                checkpointer=checkpointer
            )
            
            # 获取系统提示词
            from datetime import datetime
            from langchain_core.messages import SystemMessage
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            system_prompt = get_diagnosis_system_prompt(department, current_datetime)
            
            # 构造消息列表，包含系统提示词
            # 如果messages中已经有SystemMessage，则替换；否则添加
            messages_with_system = []
            has_system_message = False
            for msg in messages:
                if isinstance(msg, SystemMessage):
                    # 替换现有的系统消息
                    messages_with_system.append(SystemMessage(content=system_prompt))
                    has_system_message = True
                else:
                    messages_with_system.append(msg)
            
            # 如果没有系统消息，在开头添加
            if not has_system_message:
                messages_with_system.insert(0, SystemMessage(content=system_prompt))
            
            # 调用智能体
            config = {
                "configurable": {
                    "thread_id": session_id
                }
            }
            
            result = await agent.ainvoke(
                {"messages": messages_with_system},
                config=config
            )
            
            # 更新状态
            updated_state = state.copy()
            updated_state["messages"] = result["messages"]
            updated_state["current_agent"] = f"{department}_diagnosis_agent"
            
            logger.info(f"诊断智能体 ({department}) 处理完成，用户: {user_id}, 会话: {session_id}")
            
            return updated_state
            
        except Exception as e:
            logger.error(f"诊断智能体节点执行失败: {e}", exc_info=True)
            # 返回错误消息
            from langchain_core.messages import AIMessage
            error_message = AIMessage(
                content=f"抱歉，诊断智能体处理时出现错误：{str(e)}。请稍后重试或联系技术支持。"
            )
            updated_state = state.copy()
            updated_state["messages"] = state.get("messages", []) + [error_message]
            return updated_state
    
    return diagnosis_agent_node


def create_internal_medicine_diagnosis_agent_node(
    pool: AsyncConnectionPool,
    checkpointer: AsyncPostgresSaver,
    store: AsyncPostgresStore = None
):
    """
    创建内科诊断智能体节点（便捷函数）
    
    Args:
        pool: 数据库连接池
        checkpointer: Checkpointer实例
        store: Store实例
    
    Returns:
        节点函数
    """
    return create_diagnosis_agent_node(
        department="internal_medicine",
        pool=pool,
        checkpointer=checkpointer,
        store=store
    )


def create_surgery_diagnosis_agent_node(
    pool: AsyncConnectionPool,
    checkpointer: AsyncPostgresSaver,
    store: AsyncPostgresStore = None
):
    """
    创建外科诊断智能体节点（便捷函数）
    
    Args:
        pool: 数据库连接池
        checkpointer: Checkpointer实例
        store: Store实例
    
    Returns:
        节点函数
    """
    return create_diagnosis_agent_node(
        department="surgery",
        pool=pool,
        checkpointer=checkpointer,
        store=store
    )


def create_pediatrics_diagnosis_agent_node(
    pool: AsyncConnectionPool,
    checkpointer: AsyncPostgresSaver,
    store: AsyncPostgresStore = None
):
    """
    创建儿科诊断智能体节点（便捷函数）
    
    Args:
        pool: 数据库连接池
        checkpointer: Checkpointer实例
        store: Store实例
    
    Returns:
        节点函数
    """
    return create_diagnosis_agent_node(
        department="pediatrics",
        pool=pool,
        checkpointer=checkpointer,
        store=store
    )


def create_gynecology_diagnosis_agent_node(
    pool: AsyncConnectionPool,
    checkpointer: AsyncPostgresSaver,
    store: AsyncPostgresStore = None
):
    """
    创建妇科诊断智能体节点（便捷函数）
    
    Args:
        pool: 数据库连接池
        checkpointer: Checkpointer实例
        store: Store实例
    
    Returns:
        节点函数
    """
    return create_diagnosis_agent_node(
        department="gynecology",
        pool=pool,
        checkpointer=checkpointer,
        store=store
    )


def create_cardiology_diagnosis_agent_node(
    pool: AsyncConnectionPool,
    checkpointer: AsyncPostgresSaver,
    store: AsyncPostgresStore = None
):
    """
    创建心血管科诊断智能体节点（便捷函数）
    
    Args:
        pool: 数据库连接池
        checkpointer: Checkpointer实例
        store: Store实例
    
    Returns:
        节点函数
    """
    return create_diagnosis_agent_node(
        department="cardiology",
        pool=pool,
        checkpointer=checkpointer,
        store=store
    )


def create_general_diagnosis_agent_node(
    pool: AsyncConnectionPool,
    checkpointer: AsyncPostgresSaver,
    store: AsyncPostgresStore = None
):
    """
    创建通用诊断智能体节点（便捷函数）
    用于无法确定具体科室时的诊断支持
    
    Args:
        pool: 数据库连接池
        checkpointer: Checkpointer实例
        store: Store实例
    
    Returns:
        节点函数
    """
    return create_diagnosis_agent_node(
        department="general",
        pool=pool,
        checkpointer=checkpointer,
        store=store
    )

