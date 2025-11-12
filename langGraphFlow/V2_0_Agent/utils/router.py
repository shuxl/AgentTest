"""
路由节点实现（向后兼容层）
此模块已迁移到 domain.router.node，保留此文件以保持向后兼容
建议新代码使用：from domain.router import router_node, clarify_intent_node, route_decision
"""
import warnings
from domain.router import router_node, clarify_intent_node, route_decision

# 发出警告，提示使用新模块
warnings.warn(
    "utils.router 已迁移到 domain.router，"
    "建议使用：from domain.router import router_node, clarify_intent_node, route_decision",
    DeprecationWarning,
    stacklevel=2
)

__all__ = ["router_node", "clarify_intent_node", "route_decision"]
