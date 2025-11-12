"""
LangChain 回调处理器模块（向后兼容层）
此模块已迁移到 core.llm.callbacks，保留此文件以保持向后兼容
建议新代码使用：from core.llm.callbacks import ModelInteractionLogger, get_model_interaction_logger
"""
import warnings
from core.llm.callbacks import (
    ModelInteractionLogger,
    get_model_interaction_logger as _get_model_interaction_logger
)

# 发出警告，提示使用新模块
warnings.warn(
    "utils.llm_callbacks 已迁移到 core.llm.callbacks，"
    "建议使用：from core.llm.callbacks import ModelInteractionLogger, get_model_interaction_logger",
    DeprecationWarning,
    stacklevel=2
)

# 向后兼容：重新导出
__all__ = ["ModelInteractionLogger", "get_model_interaction_logger"]


def get_model_interaction_logger():
    """
    获取模型交互日志记录器实例（向后兼容）
    
    Returns:
        ModelInteractionLogger: 回调处理器实例
    
    Note:
        此函数是为了向后兼容而保留的，建议新代码使用 core.llm.callbacks.get_model_interaction_logger
    """
    return _get_model_interaction_logger()
