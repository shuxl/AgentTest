"""
路由工具实现（向后兼容层）
此模块已迁移到 domain.router.tools.router_tools，保留此文件以保持向后兼容
建议新代码使用：from domain.router.tools import identify_intent, clarify_intent, get_router_tools
"""
import warnings
from domain.router.tools import identify_intent, clarify_intent, get_router_tools

# 发出警告，提示使用新模块
warnings.warn(
    "utils.tools.router_tools 已迁移到 domain.router.tools，"
    "建议使用：from domain.router.tools import identify_intent, clarify_intent, get_router_tools",
    DeprecationWarning,
    stacklevel=2
)

__all__ = ["identify_intent", "clarify_intent", "get_router_tools"]
