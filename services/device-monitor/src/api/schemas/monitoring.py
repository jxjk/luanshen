"""
监控相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class MonitoringStatsResponse(BaseModel):
    """监控统计响应"""
    total_devices: int
    running_devices: int
    idle_devices: int
    alarm_devices: int
    maintenance_devices: int
    offline_devices: int


class DeviceMetrics(BaseModel):
    """设备指标"""
    device_id: int
    device_name: str
    status: str
    availability: float = Field(..., ge=0, le=100, description="设备可用率 (%)")
    performance: float = Field(..., ge=0, le=100, description="设备性能 (%)")
    quality: float = Field(..., ge=0, le=100, description="质量指数 (%)")
    oee: float = Field(..., ge=0, le=100, description="OEE (%)")
    uptime: float = Field(..., description="运行时间 (小时)")
    downtime: float = Field(..., description="停机时间 (小时)")


class SensorConfig(BaseModel):
    """传感器配置"""
    sensor_id: str
    sensor_type: str
    node_id: str
    unit: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    warning_threshold: Optional[float] = None
    alarm_threshold: Optional[float] = None


class DeviceConfigResponse(BaseModel):
    """设备配置响应"""
    device_id: int
    device_name: str
    device_type: str
    opcua_enabled: bool
    opcua_url: Optional[str] = None
    polling_interval: float
    sensors: List[SensorConfig] = Field(default_factory=list)


class TimeSeriesData(BaseModel):
    """时序数据"""
    timestamp: datetime
    value: float
    quality: Optional[str] = "good"


class TimeSeriesQuery(BaseModel):
    """时序查询"""
    device_id: int
    field: str
    start_time: datetime
    end_time: datetime
    aggregation: Optional[str] = None  # mean, max, min, sum
    window: Optional[str] = None  # 1m, 5m, 1h