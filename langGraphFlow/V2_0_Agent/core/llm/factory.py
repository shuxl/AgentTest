"""
LLM工厂模块
提供LLM实例的创建和管理功能
"""
import os
import logging
from typing import Optional, List
from langchain.chat_models import init_chat_model
from langchain_core.language_models.chat_models import BaseChatModel

from core.config import Settings, get_settings
from .callbacks import get_model_interaction_logger
from .exceptions import InitializationError, APIError

logger = logging.getLogger(__name__)


class LLMFactory:
    """LLM工厂类，用于创建和管理LLM实例"""
    
    def __init__(self, settings: Settings):
        """
        初始化LLM工厂
        
        Args:
            settings: 配置实例
        """
        self.settings = settings
    
    def _get_api_key(self, env_key_name: Optional[str] = None) -> str:
        """
        获取API Key
        
        Args:
            env_key_name: 环境变量名称，如果为None则使用配置中的值
        
        Returns:
            str: API Key
        
        Raises:
            InitializationError: 当API Key未设置时抛出
        """
        if env_key_name is None:
            env_key_name = self.settings.llm_api_key_env_name
        
        api_key = os.getenv(env_key_name)
        
        if not api_key or api_key == "":
            raise InitializationError(f"请设置环境变量 {env_key_name}")
        
        return api_key
    
    def create(
        self,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        env_key_name: Optional[str] = None,
        callbacks: Optional[List] = None
    ) -> BaseChatModel:
        """
        创建LLM实例
        
        Args:
            model: 模型名称，如果为None则使用配置中的值
            temperature: 温度参数，如果为None则使用配置中的值
            base_url: API基础URL，如果为None则使用默认值
            api_key: API Key，如果为None则从环境变量读取
            env_key_name: 环境变量名称，如果为None则使用配置中的值
            callbacks: 回调处理器列表，如果为None则使用默认的模型交互日志记录器
        
        Returns:
            BaseChatModel: LLM实例
        
        Raises:
            InitializationError: 当初始化失败时抛出
            APIError: 当API调用失败时抛出
        """
        # 使用配置中的默认值
        if model is None:
            model = self.settings.llm_type
        if temperature is None:
            temperature = self.settings.llm_temperature
        if base_url is None:
            base_url = "https://api.deepseek.com"
        
        # 获取API Key
        if api_key is None:
            try:
                api_key = self._get_api_key(env_key_name)
            except InitializationError as e:
                raise InitializationError(f"获取API Key失败: {str(e)}")
        
        # 如果没有提供回调，使用默认的模型交互日志记录器
        if callbacks is None:
            callbacks = [get_model_interaction_logger()]
        
        try:
            # 初始化LLM
            llm = init_chat_model(
                model=model,
                temperature=temperature,
                base_url=base_url,
                api_key=api_key
            )
            
            # 为LLM实例设置默认回调处理器
            if hasattr(llm, 'callbacks') and callbacks:
                existing_callbacks = getattr(llm, 'callbacks', None)
                if existing_callbacks:
                    if isinstance(existing_callbacks, list):
                        llm.callbacks = existing_callbacks + callbacks
                    else:
                        llm.callbacks = [existing_callbacks] + callbacks
                else:
                    llm.callbacks = callbacks
            
            logger.info(f"LLM实例创建成功: model={model}, temperature={temperature}")
            return llm
            
        except Exception as e:
            error_msg = f"初始化LLM失败: {str(e)}"
            logger.error(error_msg)
            raise InitializationError(error_msg) from e
    
    def create_by_config(self) -> BaseChatModel:
        """
        根据配置创建LLM实例（便捷方法）
        
        Returns:
            BaseChatModel: LLM实例
        
        Raises:
            InitializationError: 当LLM_TYPE不支持或初始化失败时抛出
        """
        llm_type = self.settings.llm_type
        
        # 代码安全：确保LLM_TYPE有效
        if not llm_type or not isinstance(llm_type, str):
            raise InitializationError(f"配置错误: LLM_TYPE 必须是非空字符串")
        
        # LLM_TEMPERATURE 是所有模型都有的参数
        temperature = self.settings.llm_temperature
        if not isinstance(temperature, (int, float)) or temperature < 0 or temperature > 2:
            raise InitializationError(f"配置错误: LLM_TEMPERATURE 必须是0-2之间的数字")
        
        if llm_type == "deepseek-chat":
            # 使用工厂方法创建DeepSeek LLM
            return self.create(
                model="openai:deepseek-chat",
                temperature=temperature
            )
        else:
            # 其他情况暂不实现
            raise InitializationError(
                f"不支持的LLM类型: {llm_type}. 当前仅支持: deepseek-chat"
            )


# 全局LLM工厂实例
_llm_factory: Optional[LLMFactory] = None


def get_llm_factory(settings: Settings = None) -> LLMFactory:
    """
    获取全局LLM工厂实例（单例模式）
    
    Args:
        settings: 配置实例（可选，如果不提供则从get_settings获取）
    
    Returns:
        LLMFactory: LLM工厂实例
    """
    global _llm_factory
    if _llm_factory is None:
        if settings is None:
            settings = get_settings()
        _llm_factory = LLMFactory(settings=settings)
    return _llm_factory


# 向后兼容：提供get_llm_by_config函数
def get_llm_by_config() -> BaseChatModel:
    """
    根据配置创建LLM实例（向后兼容函数）
    
    Returns:
        BaseChatModel: LLM实例
    
    Note:
        此函数是为了向后兼容而保留的，建议新代码使用LLMFactory
    """
    factory = get_llm_factory()
    return factory.create_by_config()

