"""
设备状态模型
"""
from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, ForeignKey, Enum
from sqlalchemy.sql import func
import enum

from ..config.database import Base


class DeviceStatusEnum(str, enum.Enum):
    """设备状态枚举"""
    RUNNING = "RUNNING"
    IDLE = "IDLE"
    ALARM = "ALARM"
    MAINTENANCE = "MAINTENANCE"
    OFFLINE = "OFFLINE"


class DeviceStatus(Base):
    """设备状态表"""
    __tablename__ = "device_status"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    device_id = Column(Integer, ForeignKey("machines.id"), nullable=False, index=True, comment="设备ID")
    status = Column(
        Enum(DeviceStatusEnum),
        nullable=False,
        default=DeviceStatusEnum.OFFLINE,
        comment="设备状态"
    )
    current_x = Column(DECIMAL(10, 3), nullable=True, comment="X轴当前位置")
    current_y = Column(DECIMAL(10, 3), nullable=True, comment="Y轴当前位置")
    current_z = Column(DECIMAL(10, 3), nullable=True, comment="Z轴当前位置")
    spindle_speed = Column(DECIMAL(10, 2), nullable=True, comment="主轴转速 (r/min)")
    feed_rate = Column(DECIMAL(10, 2), nullable=True, comment="进给率 (mm/min)")
    load_percent = Column(DECIMAL(5, 2), nullable=True, comment="负载百分比 (%)")
    alarm_code = Column(String(50), nullable=True, comment="报警代码")
    alarm_message = Column(String(255), nullable=True, comment="报警消息")
    recorded_at = Column(TIMESTAMP, default=func.now(), nullable=False, comment="记录时间")
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "device_id": self.device_id,
            "status": self.status.value if self.status else None,
            "current_x": float(self.current_x) if self.current_x else None,
            "current_y": float(self.current_y) if self.current_y else None,
            "current_z": float(self.current_z) if self.current_z else None,
            "spindle_speed": float(self.spindle_speed) if self.spindle_speed else None,
            "feed_rate": float(self.feed_rate) if self.feed_rate else None,
            "load_percent": float(self.load_percent) if self.load_percent else None,
            "alarm_code": self.alarm_code,
            "alarm_message": self.alarm_message,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None,
        }