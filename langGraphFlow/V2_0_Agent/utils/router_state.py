"""
路由智能体状态定义（向后兼容层）
此模块已迁移到 domain.router.state，保留此文件以保持向后兼容
建议新代码使用：from domain.router import RouterState, IntentResult
"""
import warnings
from domain.router import RouterState, IntentResult

# 发出警告，提示使用新模块
warnings.warn(
    "utils.router_state 已迁移到 domain.router，"
    "建议使用：from domain.router import RouterState, IntentResult",
    DeprecationWarning,
    stacklevel=2
)

__all__ = ["RouterState", "IntentResult"]

