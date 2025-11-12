"""
统一的日志配置模块（向后兼容层）
此模块已迁移到 core.logging，保留此文件以保持向后兼容
建议新代码使用：from core.logging import setup_logging
"""
import warnings
from core.logging import setup_logging as _setup_logging

# 发出警告，提示使用新模块
warnings.warn(
    "utils.logging_config 已迁移到 core.logging，"
    "建议使用：from core.logging import setup_logging",
    DeprecationWarning,
    stacklevel=2
)

# 向后兼容：重新导出
__all__ = ["setup_logging"]


def setup_logging():
    """
    设置统一的日志配置（向后兼容）
    
    Note:
        此函数是为了向后兼容而保留的，建议新代码使用 core.logging.setup_logging
    """
    _setup_logging()
