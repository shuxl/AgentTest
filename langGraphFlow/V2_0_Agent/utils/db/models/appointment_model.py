"""
预约记录数据模型
对应数据库表：appointments
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    CheckConstraint,
    Index,
)
from sqlalchemy.sql import func
from ..base import Base


class Appointment(Base):
    """
    预约记录模型
    
    表名：appointments
    
    字段说明：
    - id: 预约ID（主键，自增）
    - user_id: 用户ID（必填）
    - department: 科室（必填）
    - doctor_id: 医生ID（可选）
    - doctor_name: 医生姓名（可选）
    - appointment_date: 预约时间（必填）
    - status: 预约状态（必填，默认：pending）
        - pending: 待处理
        - completed: 已完成
        - cancelled: 已取消
    - notes: 备注（可选）
    - created_at: 创建时间（自动设置）
    - updated_at: 更新时间（自动更新）
    
    约束：
    - status 必须是 'pending', 'completed', 'cancelled' 之一
    """
    __tablename__ = "appointments"
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, comment="预约ID")
    
    # 用户信息
    user_id = Column(String(255), nullable=False, comment="用户ID")
    
    # 预约信息
    department = Column(String(255), nullable=False, comment="科室")
    doctor_id = Column(String(255), nullable=True, comment="医生ID")
    doctor_name = Column(String(255), nullable=True, comment="医生姓名")
    
    # 预约时间
    appointment_date = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="预约时间"
    )
    
    # 状态
    status = Column(
        String(50),
        nullable=False,
        server_default="pending",
        comment="预约状态（pending/completed/cancelled）"
    )
    
    # 备注
    notes = Column(Text, nullable=True, comment="备注")
    
    # 时间戳
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
        comment="创建时间"
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        comment="更新时间"
    )
    
    # 表级约束
    __table_args__ = (
        # 状态值约束
        CheckConstraint(
            "status IN ('pending', 'completed', 'cancelled')",
            name="check_appointment_status"
        ),
        # 索引
        Index("idx_appointments_user_id", "user_id"),
        Index("idx_appointments_appointment_date", "appointment_date"),
        Index("idx_appointments_status", "status"),
        Index("idx_appointments_user_status", "user_id", "status"),
    )
    
    def __repr__(self) -> str:
        """字符串表示"""
        return (
            f"<Appointment(id={self.id}, user_id='{self.user_id}', "
            f"department='{self.department}', doctor_name='{self.doctor_name}', "
            f"appointment_date={self.appointment_date}, status='{self.status}')>"
        )
    
    def to_dict(self) -> dict:
        """
        转换为字典格式
        
        Returns:
            dict: 包含所有字段的字典
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "department": self.department,
            "doctor_id": self.doctor_id,
            "doctor_name": self.doctor_name,
            "appointment_date": self.appointment_date.isoformat() if self.appointment_date else None,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

