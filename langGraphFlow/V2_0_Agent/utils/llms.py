"""
LLM初始化模块（向后兼容层）
此模块已迁移到 core.llm，保留此文件以保持向后兼容
建议新代码使用：from core.llm import LLMFactory, get_llm_by_config
"""
import warnings
from core.llm import get_llm_by_config as _get_llm_by_config, LLMFactory, InitializationError

# 发出警告，提示使用新模块
warnings.warn(
    "utils.llms 已迁移到 core.llm，"
    "建议使用：from core.llm import LLMFactory, get_llm_by_config",
    DeprecationWarning,
    stacklevel=2
)

# 向后兼容：重新导出
__all__ = ["get_llm_by_config", "LLMFactory", "LLMInitializationError"]

# 向后兼容：LLMInitializationError别名
LLMInitializationError = InitializationError


def get_llm_by_config():
    """
    根据配置创建LLM实例（向后兼容）
    
    Returns:
        BaseChatModel: LLM实例
    
    Note:
        此函数是为了向后兼容而保留的，建议新代码使用 core.llm.get_llm_by_config
    """
    return _get_llm_by_config()
