"""
数据模型定义模块
包含所有业务数据模型
"""
from .blood_pressure import BloodPressureRecord
from .appointment import Appointment

__all__ = [
    "BloodPressureRecord",
    "Appointment",
]

