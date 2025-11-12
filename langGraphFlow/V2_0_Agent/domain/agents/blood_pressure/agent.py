"""
血压记录智能体实现
创建血压记录智能体节点和智能体
"""
import logging
from langgraph.prebuilt import create_react_agent
from langgraph.store.postgres import AsyncPostgresStore
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import SystemMessage
from psycopg_pool import AsyncConnectionPool
from domain.router import RouterState
from .tools import create_blood_pressure_tools
from core.llm import get_llm_by_config

logger = logging.getLogger(__name__)

def get_blood_pressure_system_prompt(current_datetime: str = None) -> str:
    """
    获取血压记录智能体系统提示词
    
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
    
    return f"""你是一个专业的血压记录助手，帮助用户记录和管理血压数据。

**重要：当前日期时间信息**
- 当前日期时间：{current_datetime}
- 当前日期：{current_date}
- 今天是：{current_weekday}

**日期时间处理规则（重要）**：
- 当用户提到"今天"、"昨天"、"明天"、"本周一"、"上周一"等相对时间时：
  1. 根据当前日期时间计算具体日期和时间
  2. 将计算后的标准格式时间传递给record_blood_pressure工具的date_time参数（格式：YYYY-MM-DD HH:MM:SS或YYYY-MM-DD）
  3. **必须同时**将用户的原始时间描述传递给original_time_description参数（例如："今天早上8点"、"昨天下午"、"本周一上午"等）
- 示例（假设今天是{current_date}）：
  - 用户说"今天早上8点" → 调用record_blood_pressure(date_time="{current_date} 08:00:00", original_time_description="今天早上8点", ...)
  - 用户说"昨天下午" → 计算昨天的日期，调用record_blood_pressure(date_time="计算的日期 14:00:00", original_time_description="昨天下午", ...)
  - 用户说"本周一上午" → 计算本周一的日期，调用record_blood_pressure(date_time="计算的日期 09:00:00", original_time_description="本周一上午", ...)
  - 用户说"2024-01-15" → 调用record_blood_pressure(date_time="2024-01-15", original_time_description="2024-01-15", ...)
  - 用户没有提供时间 → 调用record_blood_pressure(date_time=None, original_time_description=None, ...)，工具会使用当前时间

你的职责：
1. 引导用户完成血压数据收集（收缩压、舒张压、测量时间）
2. 验证血压数据的合法性
3. 查询用户的历史血压记录
4. 更新已有的血压记录
5. 提供血压统计信息

数据验证规则：
- 收缩压范围：50-300 mmHg
- 舒张压范围：30-200 mmHg
- 收缩压必须大于舒张压

对话策略：
- 主动问候用户，说明你的目的
- 一次只询问一个信息项，避免一次性询问太多
- 使用友好的语言，让用户感到舒适
- 如果用户输入的数据不合理，友好地提示并请求重新输入
- 在收集完所有数据后，向用户确认数据是否正确
- 确认后使用 record_blood_pressure 工具保存数据

日期时间处理示例（重要：必须同时提供原始描述）：
- 用户说"今天早上8点" → 调用record_blood_pressure(date_time="{current_date} 08:00:00", original_time_description="今天早上8点", ...)
- 用户说"昨天下午" → 计算昨天的日期，调用record_blood_pressure(date_time="计算的日期 14:00:00", original_time_description="昨天下午", ...)
- 用户说"本周一上午" → 计算本周一的日期，调用record_blood_pressure(date_time="计算的日期 09:00:00", original_time_description="本周一上午", ...)
- 用户说"2024-01-15" → 调用record_blood_pressure(date_time="2024-01-15", original_time_description="2024-01-15", ...)
- 用户没有提供时间 → 调用record_blood_pressure(date_time=None, original_time_description=None, ...)，工具会使用当前时间

**关键要求**：调用record_blood_pressure或update_blood_pressure工具时，如果用户提供了时间描述，必须同时传递original_time_description参数保存用户的原始描述。

可用工具：
- record_blood_pressure: 记录血压数据（自动处理日期时间转换，支持相对时间和绝对时间）
- query_blood_pressure: 查询历史血压记录
- update_blood_pressure: 更新已存在的血压记录
- info: 查询用户的基础信息（设置信息和血压统计信息）

记住：始终以用户为中心，提供温暖、专业的服务。工具调用会自动执行，无需人工审批。"""


async def create_blood_pressure_agent(
    llm: BaseChatModel,
    pool: AsyncConnectionPool,
    user_id: str,
    checkpointer=None,
    store: AsyncPostgresStore = None
):
    """
    创建血压记录智能体
    
    Args:
        llm: LLM模型实例
        pool: PostgreSQL数据库连接池实例
        user_id: 用户ID
        checkpointer: Checkpointer实例（可选）
        store: PostgreSQL Store实例（可选，用于长期记忆）
        
    Returns:
        CompiledGraph: 编译后的智能体图
    """
    # 创建血压记录工具（使用数据库连接池和store）
    # pool用于访问blood_pressure_records表，store用于查询用户设置信息
    tools = create_blood_pressure_tools(pool, user_id, store)
    
    # 创建ReAct Agent
    agent = create_react_agent(
        model=llm,
        tools=tools,
        checkpointer=checkpointer,
        store=store
    )
    
    logger.info(f"血压记录智能体创建成功，用户ID: {user_id}")
    
    return agent


def create_blood_pressure_agent_node(pool: AsyncConnectionPool, checkpointer: AsyncPostgresSaver, store: AsyncPostgresStore = None):
    """
    创建血压记录智能体节点函数（工厂函数）
    
    使用闭包捕获pool、checkpointer和store，返回符合LangGraph节点签名的函数
    
    Args:
        pool: PostgreSQL数据库连接池实例
        checkpointer: PostgreSQL Checkpointer实例
        store: PostgreSQL Store实例（可选，用于长期记忆）
        
    Returns:
        Callable: 符合(state: RouterState) -> RouterState签名的节点函数
    """
    async def blood_pressure_agent_node(state: RouterState) -> RouterState:
        """
        血压记录智能体节点函数
        
        注意：这个节点执行完后，会返回到router节点
        下次调用时，router节点会重新判断意图
        """
        try:
            messages = state.get("messages", [])
            session_id = state.get("session_id")
            user_id = state.get("user_id")
            
            if not user_id:
                logger.error("blood_pressure_agent_node: user_id为空")
                return state
            
            # 获取LLM
            llm = get_llm_by_config()
            
            # 创建血压记录智能体
            agent = await create_blood_pressure_agent(
                llm=llm,
                pool=pool,
                user_id=user_id,
                checkpointer=checkpointer,
                store=store
            )
            
            # 调用智能体（使用相同的thread_id）
            config = {"configurable": {"thread_id": session_id}} if session_id else {}
            
            # 获取当前日期时间，用于构建系统提示词
            from datetime import datetime
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            system_prompt = get_blood_pressure_system_prompt(current_datetime)
            
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
            
            result = await agent.ainvoke(
                {"messages": messages_with_system},
                config=config
            )
            
            # 更新状态
            updated_state = state.copy()
            updated_state["messages"] = result.get("messages", messages)
            
            logger.info(f"血压记录智能体节点执行完成，用户ID: {user_id}")
            
            return updated_state
            
        except Exception as e:
            logger.error(f"血压记录智能体节点执行失败: {str(e)}")
            import traceback
            traceback.print_exc()
            # 返回未更新的状态
            return state
    
    return blood_pressure_agent_node

