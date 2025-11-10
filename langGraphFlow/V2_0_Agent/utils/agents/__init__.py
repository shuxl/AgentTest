"""
专门智能体模块
包含血压记录智能体、复诊管理智能体、诊断智能体等
"""
from .blood_pressure_agent import create_blood_pressure_agent_node
from .appointment_agent import create_appointment_agent_node
from .diagnosis_agent import (
    create_diagnosis_agent_node,
    create_internal_medicine_diagnosis_agent_node,
    create_surgery_diagnosis_agent_node,
    create_pediatrics_diagnosis_agent_node,
    create_gynecology_diagnosis_agent_node,
    create_cardiology_diagnosis_agent_node,
    create_general_diagnosis_agent_node,
    get_diagnosis_system_prompt
)

__all__ = [
    "create_blood_pressure_agent_node",
    "create_appointment_agent_node",
    "create_diagnosis_agent_node",
    "create_internal_medicine_diagnosis_agent_node",
    "create_surgery_diagnosis_agent_node",
    "create_pediatrics_diagnosis_agent_node",
    "create_gynecology_diagnosis_agent_node",
    "create_cardiology_diagnosis_agent_node",
    "create_general_diagnosis_agent_node",
    "get_diagnosis_system_prompt"
]
