import os
from langchain.chat_models import init_chat_model
from typing import Optional, List
from langchain_core.language_models.chat_models import BaseChatModel
from .config import Config
from .llm_callbacks import get_model_interaction_logger


class LLMInitializationError(Exception):
    """自定义异常类用于LLM初始化错误"""
    pass


def get_llm(
    model: str,
    temperature: float = 0,
    base_url: str = "https://api.deepseek.com",
    api_key: Optional[str] = None,
    env_key_name: str = "DEEPSEEK_API_KEY",
    callbacks: Optional[List] = None
) -> BaseChatModel:
    """
    通用的 LLM 初始化方法（基础方法）
    
    Args:
        model (str): 模型名称，例如 "openai:deepseek-chat", "openai:deepseek-v3"
        temperature (float): 温度参数，默认为 0
        base_url (str): API 基础 URL，默认为 "https://api.deepseek.com"
        api_key (Optional[str]): API Key，如果为 None 则从环境变量读取
        env_key_name (str): 环境变量名称，默认为 "DEEPSEEK_API_KEY"
        callbacks (Optional[List]): 回调处理器列表，如果为 None 则使用默认的模型交互日志记录器
    
    Returns:
        BaseChatModel: LLM 实例
    
    Raises:
        LLMInitializationError: 当 API Key 未设置或初始化失败时抛出
    """
    # 获取 API Key
    if api_key is None:
        api_key = os.getenv(env_key_name)
    
    # 检查 API Key
    if not api_key or api_key == "":
        error_msg = f"请设置环境变量 {env_key_name}"
        print(f"{env_key_name}:{api_key}")
        raise LLMInitializationError(error_msg)
    
    print(f"{env_key_name}:{api_key}")
    
    try:
        # 初始化 LLM
        llm = init_chat_model(
            model=model,
            temperature=temperature,
            base_url=base_url,
            api_key=api_key
        )
        
        # ========== 方案2：添加 LangChain 回调处理器 ==========
        # 如果没有提供回调，使用默认的模型交互日志记录器
        if callbacks is None:
            callbacks = [get_model_interaction_logger()]
        
        # 为 LLM 实例设置默认回调处理器
        # 注意：在 LangChain 中，callbacks 通常在调用时通过 config 传递
        # 但我们可以通过设置默认 callbacks 来确保所有调用都被记录
        # 如果 LLM 实例支持 default_callback_manager，则使用它
        if hasattr(llm, 'callbacks') and callbacks:
            # 如果已有 callbacks，合并它们
            existing_callbacks = getattr(llm, 'callbacks', None)
            if existing_callbacks:
                if isinstance(existing_callbacks, list):
                    llm.callbacks = existing_callbacks + callbacks
                else:
                    llm.callbacks = [existing_callbacks] + callbacks
            else:
                llm.callbacks = callbacks
        
        return llm
    except Exception as e:
        error_msg = f"初始化 LLM 失败: {str(e)}"
        raise LLMInitializationError(error_msg) from e


def get_deepseek_llm(
    model: str = "openai:deepseek-chat",
    temperature: float = 0,
    api_key: Optional[str] = None,
    env_key_name: str = "DEEPSEEK_API_KEY",
    callbacks: Optional[List] = None
) -> BaseChatModel:
    """
    便捷方法：初始化 DeepSeek LLM 实例
    
    根据 DeepSeek API 文档: https://api-docs.deepseek.com/zh-cn/
    模型名称: deepseek-chat (非思考模式) 或 deepseek-reasoner (思考模式)
    base_url: https://api.deepseek.com (langchain 会自动添加 /v1 路径)
    
    Args:
        model (str): 模型名称，默认为 "openai:deepseek-chat"
                     可选值: "openai:deepseek-chat", "openai:deepseek-reasoner"
        temperature (float): 温度参数，默认为 0
        api_key (Optional[str]): API Key，如果为 None 则从环境变量读取
        env_key_name (str): 环境变量名称，默认为 "DEEPSEEK_API_KEY"
        callbacks (Optional[List]): 回调处理器列表，如果为 None 则使用默认的模型交互日志记录器
    
    Returns:
        BaseChatModel: DeepSeek LLM 实例
    
    Raises:
        LLMInitializationError: 当 API Key 未设置或初始化失败时抛出
    
    Example:
        >>> llm = get_deepseek_llm()
        >>> llm = get_deepseek_llm(model="openai:deepseek-reasoner", temperature=0.7)
    """
    return get_llm(
        model=model,
        temperature=temperature,
        base_url="https://api.deepseek.com",
        api_key=api_key,
        env_key_name=env_key_name,
        callbacks=callbacks
    )


def get_llm_by_config() -> BaseChatModel:
    """
    根据配置文件中的LLM_TYPE自动选择对应的LLM初始化方法
    所有配置参数从Config类中读取，确保代码安全性
    如果配置未设置，使用合理的默认值
    
    Returns:
        BaseChatModel: LLM 实例
    
    Raises:
        LLMInitializationError: 当 LLM_TYPE 不支持或初始化失败时抛出
    """
    llm_type = Config.LLM_TYPE
    
    # 代码安全：确保LLM_TYPE有效
    if not llm_type or not isinstance(llm_type, str):
        raise LLMInitializationError(f"配置错误: LLM_TYPE 必须是非空字符串")
    
    # LLM_TEMPERATURE 是所有模型都有的参数，默认值为 0
    # 如果配置中存在则使用配置值，否则使用默认值
    temperature = Config.LLM_TEMPERATURE
    if not isinstance(temperature, (int, float)) or temperature < 0 or temperature > 2:
        raise LLMInitializationError(f"配置错误: LLM_TEMPERATURE 必须是0-2之间的数字")
    
    if llm_type == "deepseek-chat":
        # LLM_API_KEY_ENV_NAME 是deepseek专有的，默认值为 "DEEPSEEK_API_KEY"
        # 如果配置中存在则使用配置值，否则使用默认值
        env_key_name = Config.LLM_API_KEY_ENV_NAME
        if not env_key_name or not isinstance(env_key_name, str):
            raise LLMInitializationError(f"配置错误: LLM_API_KEY_ENV_NAME 必须是非空字符串")
        
        # 尝试从环境变量获取API Key
        api_key = os.getenv(env_key_name)
        if not api_key or api_key == "":
            raise LLMInitializationError(f"请设置环境变量 {env_key_name}")
        
        # 调用DeepSeek LLM初始化方法
        return get_deepseek_llm(
            temperature=temperature,
            api_key=api_key,
            env_key_name=env_key_name
        )
    else:
        # 其他情况暂不实现，留白
        raise LLMInitializationError(f"不支持的LLM类型: {llm_type}. 当前仅支持: deepseek-chat")

