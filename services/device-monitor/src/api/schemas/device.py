"""
设备相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class DeviceStatusEnum(str, Enum):
    """设备状态枚举"""
    RUNNING = "RUNNING"
    IDLE = "IDLE"
    ALARM = "ALARM"
    MAINTENANCE = "MAINTENANCE"
    OFFLINE = "OFFLINE"


class DeviceStatusResponse(BaseModel):
    """设备状态响应"""
    id: int
    device_id: int
    status: DeviceStatusEnum
    current_x: Optional[float] = None
    current_y: Optional[float] = None
    current_z: Optional[float] = None
    spindle_speed: Optional[float] = None
    feed_rate: Optional[float] = None
    load_percent: Optional[float] = None
    alarm_code: Optional[str] = None
    alarm_message: Optional[str] = None
    recorded_at: datetime
    
    class Config:
        from_attributes = True


class DeviceStartRequest(BaseModel):
    """启动设备监控请求"""
    device_id: int = Field(..., description="设备ID", gt=0)
    opcua_url: Optional[str] = Field(None, description="OPC UA 服务器地址")


class DeviceStopRequest(BaseModel):
    """停止设备监控请求"""
    device_id: int = Field(..., description="设备ID", gt=0)


class RealtimeDataResponse(BaseModel):
    """实时数据响应"""
    device_id: int
    status: DeviceStatusEnum
    coordinates: dict = Field(default_factory=dict)
    parameters: dict = Field(default_factory=dict)
    sensors: dict = Field(default_factory=dict)
    timestamp: datetime


class HistoryDataRequest(BaseModel):
    """历史数据查询请求"""
    device_id: int = Field(..., description="设备ID", gt=0)
    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")
    measurement: str = Field(default="device_sensor_data", description="测量名称")
    limit: Optional[int] = Field(1000, ge=1, le=10000, description="返回数量限制")


class HistoryDataResponse(BaseModel):
    """历史数据响应"""
    device_id: int
    measurement: str
    data_points: list
    count: int


class SensorDataPoint(BaseModel):
    """传感器数据点"""
    device_id: int
    sensor_type: str
    value: float
    unit: str
    timestamp: datetime


class WSMessage(BaseModel):
    """WebSocket 消息"""
    type: str = Field(..., description="消息类型")
    device_id: int = Field(..., description="设备ID")
    data: dict = Field(default_factory=dict, description="消息数据")
    timestamp: datetime = Field(default_factory=datetime.now)