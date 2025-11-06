"""
复诊管理智能体实现
创建复诊管理智能体节点和智能体
"""
import logging
from langgraph.prebuilt import create_react_agent
from langgraph.store.postgres import AsyncPostgresStore
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import SystemMessage
from psycopg_pool import AsyncConnectionPool
from ..router_state import RouterState
from ..tools.appointment_tools import create_appointment_tools
from ..llms import get_llm_by_config

logger = logging.getLogger(__name__)


def get_appointment_system_prompt(current_datetime: str = None) -> str:
    """
    获取复诊管理智能体系统提示词
    
    Args:
        current_datetime: 当前日期时间字符串（格式：YYYY-MM-DD HH:MM:SS），如果为None则自动获取
    
    Returns:
        str: 系统提示词
    """
    from datetime import datetime
    
    if current_datetime is None:
        now = datetime.now()
        current_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
        current_date = now.strftime("%Y-%m-%d")
        current_weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][now.weekday()]
    else:
        dt = datetime.strptime(current_datetime, "%Y-%m-%d %H:%M:%S")
        current_date = dt.strftime("%Y-%m-%d")
        current_weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][dt.weekday()]
    
    return f"""你是一个专业的复诊管理助手，帮助用户预约和管理复诊。

**重要：当前日期时间信息**
- 当前日期时间：{current_datetime}
- 当前日期：{current_date}
- 今天是：{current_weekday}

**日期时间处理规则（重要）**：
- 当用户提到"今天"、"明天"、"本周一"、"下周三"等相对时间时：
  1. 根据当前日期时间计算具体日期和时间
  2. 将计算后的标准格式时间传递给appointment_booking工具的appointment_date参数（格式：YYYY-MM-DD HH:MM:SS或YYYY-MM-DD）
- 示例（假设今天是{current_date}）：
  - 用户说"明天下午2点" → 调用appointment_booking(appointment_date="计算的日期 14:00:00", ...)
  - 用户说"本周一上午" → 计算本周一的日期，调用appointment_booking(appointment_date="计算的日期 09:00:00", ...)
  - 用户说"2024-01-15 14:30" → 调用appointment_booking(appointment_date="2024-01-15 14:30:00", ...)
  - 用户说"明天" → 计算明天的日期，调用appointment_booking(appointment_date="计算的日期 09:00:00", ...)

你的职责：
1. 引导用户完成复诊预约（科室、医生、时间）
2. 查询用户的复诊预约记录
3. 更新已有的复诊预约信息

数据验证规则：
- 预约时间不能是过去时间
- 科室名称必填
- 预约状态：pending（待处理）、completed（已完成）、cancelled（已取消）

对话策略：
- 主动问候用户，说明你的目的
- 一次只询问一个信息项，避免一次性询问太多
- 使用友好的语言，让用户感到舒适
- 如果用户输入的数据不合理，友好地提示并请求重新输入
- 在收集完所有数据后，向用户确认数据是否正确
- 确认后使用 appointment_booking 工具保存预约

可用工具：
- appointment_booking: 创建复诊预约（自动处理日期时间转换，支持相对时间和绝对时间）
- query_appointment: 查询用户的复诊预约记录，支持按状态和时间范围过滤
- update_appointment: 更新已存在的复诊预约信息

记住：始终以用户为中心，提供温暖、专业的服务。工具调用会自动执行，无需人工审批。"""


async def create_appointment_agent(
    llm: BaseChatModel,
    pool: AsyncConnectionPool,
    user_id: str,
    checkpointer=None,
    store: AsyncPostgresStore = None
):
    """
    创建复诊管理智能体
    
    Args:
        llm: LLM模型实例
        pool: PostgreSQL数据库连接池实例
        user_id: 用户ID
        checkpointer: Checkpointer实例（可选）
        store: PostgreSQL Store实例（可选，用于长期记忆）
        
    Returns:
        CompiledGraph: 编译后的智能体图
    """
    # 创建复诊管理工具（使用数据库连接池）
    tools = create_appointment_tools(pool, user_id, store)
    
    # 创建ReAct Agent
    agent = create_react_agent(
        model=llm,
        tools=tools,
        checkpointer=checkpointer,
        store=store
    )
    
    logger.info(f"复诊管理智能体创建成功，用户ID: {user_id}")
    
    return agent


def create_appointment_agent_node(pool: AsyncConnectionPool, checkpointer: AsyncPostgresSaver, store: AsyncPostgresStore = None):
    """
    创建复诊管理智能体节点函数（工厂函数）
    
    使用闭包捕获pool、checkpointer和store，返回符合LangGraph节点签名的函数
    
    Args:
        pool: PostgreSQL数据库连接池实例
        checkpointer: PostgreSQL Checkpointer实例
        store: PostgreSQL Store实例（可选，用于长期记忆）
        
    Returns:
        Callable: 符合(state: RouterState) -> RouterState签名的节点函数
    """
    async def appointment_agent_node(state: RouterState) -> RouterState:
        """
        复诊管理智能体节点函数
        
        注意：这个节点执行完后，会返回到router节点
        下次调用时，router节点会重新判断意图
        """
        try:
            messages = state.get("messages", [])
            session_id = state.get("session_id")
            user_id = state.get("user_id")
            
            if not user_id:
                logger.error("appointment_agent_node: user_id为空")
                return state
            
            # 获取LLM
            llm = get_llm_by_config()
            
            # 创建复诊管理智能体
            agent = await create_appointment_agent(
                llm=llm,
                pool=pool,
                user_id=user_id,
                checkpointer=checkpointer,
                store=store
            )
            
            # 调用智能体（使用相同的thread_id）
            config = {"configurable": {"thread_id": session_id}} if session_id else {}
            
            logger.info(f"[appointment_agent_node] 准备调用智能体，user_id={user_id}, session_id={session_id}")
            logger.info(f"[appointment_agent_node] 当前消息数量: {len(messages)}")
            
            # 获取当前日期时间，用于构建系统提示词
            from datetime import datetime
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            system_prompt = get_appointment_system_prompt(current_datetime)
            
            # 构造消息列表，包含系统提示词
            # 注意：LangGraph会自动从checkpointer读取历史消息，我们只需要添加系统提示词
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
            
            logger.info(f"[appointment_agent_node] 调用智能体，消息数量: {len(messages_with_system)}")
            logger.info(f"[appointment_agent_node] 最后一条用户消息: {messages[-1].content if messages else 'None'}")
            
            result = await agent.ainvoke(
                {"messages": messages_with_system},
                config=config
            )
            
            result_messages = result.get("messages", messages)
            logger.info(f"[appointment_agent_node] 智能体执行完成，返回消息数量: {len(result_messages)}")
            
            # 检查是否有工具调用
            tool_calls = []
            for msg in result_messages:
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    tool_calls.extend(msg.tool_calls)
                    logger.info(f"[appointment_agent_node] 检测到工具调用: {msg.tool_calls}")
            
            if tool_calls:
                logger.info(f"[appointment_agent_node] 共检测到 {len(tool_calls)} 个工具调用")
            else:
                logger.warning(f"[appointment_agent_node] 警告：未检测到工具调用！")
            
            # 更新状态
            updated_state = state.copy()
            updated_state["messages"] = result_messages
            
            logger.info(f"[appointment_agent_node] 复诊管理智能体节点执行完成，用户ID: {user_id}")
            
            return updated_state
            
        except Exception as e:
            logger.error(f"复诊管理智能体节点执行失败: {str(e)}")
            import traceback
            traceback.print_exc()
            # 返回未更新的状态
            return state
    
    return appointment_agent_node

