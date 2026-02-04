"""
设备状态仓储
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from ..models.device_status import DeviceStatus, DeviceStatusEnum


class DeviceStatusRepository:
    """设备状态仓储类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, device_id: int, status_data: dict) -> DeviceStatus:
        """创建设备状态记录"""
        device_status = DeviceStatus(
            device_id=device_id,
            status=status_data.get("status", DeviceStatusEnum.OFFLINE),
            current_x=status_data.get("current_x"),
            current_y=status_data.get("current_y"),
            current_z=status_data.get("current_z"),
            spindle_speed=status_data.get("spindle_speed"),
            feed_rate=status_data.get("feed_rate"),
            load_percent=status_data.get("load_percent"),
            alarm_code=status_data.get("alarm_code"),
            alarm_message=status_data.get("alarm_message"),
        )
        self.db.add(device_status)
        self.db.commit()
        self.db.refresh(device_status)
        return device_status
    
    def get_latest(self, device_id: int) -> Optional[DeviceStatus]:
        """获取设备最新状态"""
        return (
            self.db.query(DeviceStatus)
            .filter(DeviceStatus.device_id == device_id)
            .order_by(DeviceStatus.recorded_at.desc())
            .first()
        )
    
    def get_history(
        self,
        device_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[DeviceStatus]:
        """获取设备历史状态"""
        query = self.db.query(DeviceStatus).filter(DeviceStatus.device_id == device_id)
        
        if start_time:
            query = query.filter(DeviceStatus.recorded_at >= start_time)
        if end_time:
            query = query.filter(DeviceStatus.recorded_at <= end_time)
        
        return (
            query.order_by(DeviceStatus.recorded_at.desc())
            .limit(limit)
            .all()
        )
    
    def get_all_latest(self) -> List[DeviceStatus]:
        """获取所有设备的最新状态"""
        # 使用子查询获取每个设备的最新记录
        latest_ids = (
            self.db.query(
                DeviceStatus.device_id,
                self.db.func.max(DeviceStatus.id).label("max_id")
            )
            .group_by(DeviceStatus.device_id)
            .subquery()
        )
        
        return (
            self.db.query(DeviceStatus)
            .join(latest_ids, DeviceStatus.id == latest_ids.c.max_id)
            .all()
        )
    
    def update_latest_status(
        self,
        device_id: int,
        status: DeviceStatusEnum
    ) -> Optional[DeviceStatus]:
        """更新设备最新状态"""
        latest = self.get_latest(device_id)
        if latest:
            latest.status = status
            self.db.commit()
            self.db.refresh(latest)
            return latest
        return None
    
    def count_by_status(self, status: DeviceStatusEnum) -> int:
        """统计指定状态的设备数量"""
        latest_records = self.get_all_latest()
        return sum(1 for record in latest_records if record.status == status)