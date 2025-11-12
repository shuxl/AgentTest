"""
路由图创建（向后兼容层）
此模块已迁移到 domain.router.graph，保留此文件以保持向后兼容
建议新代码使用：from domain.router import create_router_graph, create_router_agent
"""
import warnings
from domain.router import create_router_graph, create_router_agent, placeholder_agent_node

# 发出警告，提示使用新模块
warnings.warn(
    "utils.router_graph 已迁移到 domain.router，"
    "建议使用：from domain.router import create_router_graph, create_router_agent",
    DeprecationWarning,
    stacklevel=2
)

__all__ = ["create_router_graph", "create_router_agent", "placeholder_agent_node"]
