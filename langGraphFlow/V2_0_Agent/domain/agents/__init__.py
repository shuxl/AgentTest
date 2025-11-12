"""
智能体业务模块
包含血压记录、复诊管理、诊断等各业务智能体
"""
# 血压记录智能体
from .blood_pressure.agent import (
    create_blood_pressure_agent_node,
    create_blood_pressure_agent,
    get_blood_pressure_system_prompt
)

# 复诊管理智能体
from .appointment.agent import (
    create_appointment_agent_node,
    create_appointment_agent,
    get_appointment_system_prompt
)

# 诊断智能体
from .diagnosis.agent import (
    create_internal_medicine_diagnosis_agent_node,
    create_surgery_diagnosis_agent_node,
    create_pediatrics_diagnosis_agent_node,
    create_gynecology_diagnosis_agent_node,
    create_cardiology_diagnosis_agent_node,
    create_general_diagnosis_agent_node,
    get_diagnosis_system_prompt
)

__all__ = [
    # 血压记录智能体
    "create_blood_pressure_agent_node",
    "create_blood_pressure_agent",
    "get_blood_pressure_system_prompt",
    # 复诊管理智能体
    "create_appointment_agent_node",
    "create_appointment_agent",
    "get_appointment_system_prompt",
    # 诊断智能体
    "create_internal_medicine_diagnosis_agent_node",
    "create_surgery_diagnosis_agent_node",
    "create_pediatrics_diagnosis_agent_node",
    "create_gynecology_diagnosis_agent_node",
    "create_cardiology_diagnosis_agent_node",
    "create_general_diagnosis_agent_node",
    "get_diagnosis_system_prompt",
]

