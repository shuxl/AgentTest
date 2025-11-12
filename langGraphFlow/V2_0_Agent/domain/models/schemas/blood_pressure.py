"""
血压记录数据模型
对应数据库表：blood_pressure_records
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
from domain.models.base import Base


class BloodPressureRecord(Base):
    """
    血压记录模型
    
    表名：blood_pressure_records
    
    字段说明：
    - id: 记录ID（主键，自增）
    - user_id: 用户ID（必填）
    - systolic: 收缩压（必填，范围：50-300）
    - diastolic: 舒张压（必填，范围：30-200）
    - measurement_time: 测量时间（必填，默认当前时间）
    - original_time_description: 原始时间描述（可选）
    - notes: 备注（可选）
    - created_at: 创建时间（自动设置）
    - updated_at: 更新时间（自动更新）
    
    约束：
    - 收缩压必须大于舒张压（CHECK constraint）
    - 收缩压范围：50-300
    - 舒张压范围：30-200
    """
    __tablename__ = "blood_pressure_records"
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, comment="记录ID")
    
    # 用户信息
    user_id = Column(String(255), nullable=False, comment="用户ID")
    
    # 血压数据
    systolic = Column(
        Integer,
        nullable=False,
        comment="收缩压（范围：50-300）"
    )
    diastolic = Column(
        Integer,
        nullable=False,
        comment="舒张压（范围：30-200）"
    )
    
    # 时间信息
    measurement_time = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
        comment="测量时间"
    )
    original_time_description = Column(
        Text,
        nullable=True,
        comment="原始时间描述（用户输入的时间描述）"
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
        # 收缩压范围约束
        CheckConstraint(
            "systolic >= 50 AND systolic <= 300",
            name="check_systolic_range"
        ),
        # 舒张压范围约束
        CheckConstraint(
            "diastolic >= 30 AND diastolic <= 200",
            name="check_diastolic_range"
        ),
        # 收缩压必须大于舒张压
        CheckConstraint(
            "systolic > diastolic",
            name="check_systolic_gt_diastolic"
        ),
        # 索引
        Index("idx_blood_pressure_user_id", "user_id"),
        Index("idx_blood_pressure_measurement_time", "measurement_time"),
        Index("idx_blood_pressure_user_time", "user_id", "measurement_time"),
    )
    
    def __repr__(self) -> str:
        """字符串表示"""
        return (
            f"<BloodPressureRecord(id={self.id}, user_id='{self.user_id}', "
            f"systolic={self.systolic}, diastolic={self.diastolic}, "
            f"measurement_time={self.measurement_time})>"
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
            "systolic": self.systolic,
            "diastolic": self.diastolic,
            "measurement_time": self.measurement_time.isoformat() if self.measurement_time else None,
            "original_time_description": self.original_time_description,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

