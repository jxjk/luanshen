"""
报警记录仓储
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from ..models.alarm_record import AlarmRecord, AlarmLevelEnum, AlarmStatusEnum


class AlarmRepository:
    """报警记录仓储类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, alarm_data: dict) -> AlarmRecord:
        """创建报警记录"""
        alarm = AlarmRecord(
            device_id=alarm_data["device_id"],
            alarm_level=alarm_data["alarm_level"],
            alarm_code=alarm_data["alarm_code"],
            alarm_message=alarm_data["alarm_message"],
            status=AlarmStatusEnum.OPEN,
        )
        self.db.add(alarm)
        self.db.commit()
        self.db.refresh(alarm)
        return alarm
    
    def get(self, alarm_id: int) -> Optional[AlarmRecord]:
        """获取报警记录"""
        return self.db.query(AlarmRecord).filter(AlarmRecord.id == alarm_id).first()
    
    def get_by_code(self, device_id: int, alarm_code: str) -> Optional[AlarmRecord]:
        """根据设备ID和报警代码获取最新的未解决报警"""
        return (
            self.db.query(AlarmRecord)
            .filter(
                AlarmRecord.device_id == device_id,
                AlarmRecord.alarm_code == alarm_code,
                AlarmRecord.status.in_([AlarmStatusEnum.OPEN, AlarmStatusEnum.ACKNOWLEDGED])
            )
            .order_by(AlarmRecord.created_at.desc())
            .first()
        )
    
    def get_all(
        self,
        device_id: Optional[int] = None,
        alarm_level: Optional[AlarmLevelEnum] = None,
        status: Optional[AlarmStatusEnum] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[AlarmRecord]:
        """获取报警记录列表"""
        query = self.db.query(AlarmRecord)
        
        if device_id:
            query = query.filter(AlarmRecord.device_id == device_id)
        if alarm_level:
            query = query.filter(AlarmRecord.alarm_level == alarm_level)
        if status:
            query = query.filter(AlarmRecord.status == status)
        if start_time:
            query = query.filter(AlarmRecord.created_at >= start_time)
        if end_time:
            query = query.filter(AlarmRecord.created_at <= end_time)
        
        return (
            query.order_by(AlarmRecord.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_active_alarms(self, device_id: int) -> List[AlarmRecord]:
        """获取设备的活跃报警"""
        return (
            self.db.query(AlarmRecord)
            .filter(
                AlarmRecord.device_id == device_id,
                AlarmRecord.status.in_([AlarmStatusEnum.OPEN, AlarmStatusEnum.ACKNOWLEDGED])
            )
            .order_by(AlarmRecord.created_at.desc())
            .all()
        )
    
    def acknowledge(self, alarm_id: int, acknowledged_by: str) -> Optional[AlarmRecord]:
        """确认报警"""
        alarm = self.get(alarm_id)
        if alarm and alarm.status == AlarmStatusEnum.OPEN:
            alarm.status = AlarmStatusEnum.ACKNOWLEDGED
            alarm.acknowledged_by = acknowledged_by
            alarm.acknowledged_at = datetime.now()
            self.db.commit()
            self.db.refresh(alarm)
        return alarm
    
    def resolve(self, alarm_id: int, resolved_by: str, resolution_note: str) -> Optional[AlarmRecord]:
        """解决报警"""
        alarm = self.get(alarm_id)
        if alarm and alarm.status in [AlarmStatusEnum.OPEN, AlarmStatusEnum.ACKNOWLEDGED]:
            alarm.status = AlarmStatusEnum.RESOLVED
            alarm.resolved_by = resolved_by
            alarm.resolved_at = datetime.now()
            alarm.resolution_note = resolution_note
            self.db.commit()
            self.db.refresh(alarm)
        return alarm
    
    def close(self, alarm_id: int) -> Optional[AlarmRecord]:
        """关闭报警"""
        alarm = self.get(alarm_id)
        if alarm:
            alarm.status = AlarmStatusEnum.CLOSED
            self.db.commit()
            self.db.refresh(alarm)
        return alarm
    
    def count_by_status(self, status: AlarmStatusEnum) -> int:
        """统计指定状态的报警数量"""
        return self.db.query(AlarmRecord).filter(AlarmRecord.status == status).count()
    
    def count_by_level(self, level: AlarmLevelEnum) -> int:
        """统计指定级别的报警数量"""
        return self.db.query(AlarmRecord).filter(AlarmRecord.alarm_level == level).count()
    
    def get_statistics(self) -> dict:
        """获取报警统计信息"""
        return {
            "total": self.db.query(AlarmRecord).count(),
            "open": self.count_by_status(AlarmStatusEnum.OPEN),
            "acknowledged": self.count_by_status(AlarmStatusEnum.ACKNOWLEDGED),
            "resolved": self.count_by_status(AlarmStatusEnum.RESOLVED),
            "closed": self.count_by_status(AlarmStatusEnum.CLOSED),
            "by_level": {
                "WARNING": self.count_by_level(AlarmLevelEnum.WARNING),
                "ALARM": self.count_by_level(AlarmLevelEnum.ALARM),
                "CRITICAL": self.count_by_level(AlarmLevelEnum.CRITICAL),
            }
        }