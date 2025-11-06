"""
数据模型模块
导出所有数据模型类
"""
from .blood_pressure_model import BloodPressureRecord
from .appointment_model import Appointment

__all__ = [
    "BloodPressureRecord",
    "Appointment",
]

