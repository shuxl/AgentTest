"""
数据库模块（向后兼容层）
此模块已迁移到 domain.models，保留此文件以保持向后兼容
建议新代码使用：from domain.models import ...
"""
import warnings
from domain.models import (
    Base,
    get_async_session,
    get_async_engine,
    get_db_session,
    BloodPressureRecord,
    Appointment,
    CRUDBase,
    QueryBuilder
)

# 发出警告，提示使用新模块
warnings.warn(
    "utils.db 已迁移到 domain.models，"
    "建议使用：from domain.models import ...",
    DeprecationWarning,
    stacklevel=2
)

__all__ = [
    "Base",
    "get_async_session",
    "get_async_engine",
    "get_db_session",
    "BloodPressureRecord",
    "Appointment",
    "CRUDBase",
    "QueryBuilder",
]

