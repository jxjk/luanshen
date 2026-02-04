"""
报警记录模型
"""
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, Enum
from sqlalchemy.sql import func
import enum

from ..config.database import Base


class AlarmLevelEnum(str, enum.Enum):
    """报警级别枚举"""
    WARNING = "WARNING"
    ALARM = "ALARM"
    CRITICAL = "CRITICAL"


class AlarmStatusEnum(str, enum.Enum):
    """报警状态枚举"""
    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class AlarmRecord(Base):
    """报警记录表"""
    __tablename__ = "alarm_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    device_id = Column(Integer, ForeignKey("machines.id"), nullable=False, index=True, comment="设备ID")
    alarm_level = Column(
        Enum(AlarmLevelEnum),
        nullable=False,
        comment="报警级别"
    )
    alarm_code = Column(String(50), nullable=False, comment="报警代码")
    alarm_message = Column(String(255), nullable=False, comment="报警消息")
    status = Column(
        Enum(AlarmStatusEnum),
        nullable=False,
        default=AlarmStatusEnum.OPEN,
        comment="报警状态"
    )
    acknowledged_by = Column(String(50), nullable=True, comment="确认人")
    acknowledged_at = Column(TIMESTAMP, nullable=True, comment="确认时间")
    resolved_by = Column(String(50), nullable=True, comment="解决人")
    resolved_at = Column(TIMESTAMP, nullable=True, comment="解决时间")
    resolution_note = Column(Text, nullable=True, comment="解决说明")
    created_at = Column(TIMESTAMP, default=func.now(), nullable=False, comment="创建时间")
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "device_id": self.device_id,
            "alarm_level": self.alarm_level.value if self.alarm_level else None,
            "alarm_code": self.alarm_code,
            "alarm_message": self.alarm_message,
            "status": self.status.value if self.status else None,
            "acknowledged_by": self.acknowledged_by,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolved_by": self.resolved_by,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolution_note": self.resolution_note,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }