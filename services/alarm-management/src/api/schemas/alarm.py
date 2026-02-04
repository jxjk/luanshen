"""
报警相关 Schema
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AlarmLevelEnum(str, Enum):
    """报警级别枚举"""
    WARNING = "WARNING"
    ALARM = "ALARM"
    CRITICAL = "CRITICAL"


class AlarmStatusEnum(str, Enum):
    """报警状态枚举"""
    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class AlarmTypeEnum(str, Enum):
    """报警类型枚举"""
    DEVICE_OFFLINE = "DEVICE_OFFLINE"
    DEVICE_ALARM = "DEVICE_ALARM"
    PARAMETER_EXCEED = "PARAMETER_EXCEED"
    VIBRATION_HIGH = "VIBRATION_HIGH"
    TEMPERATURE_HIGH = "TEMPERATURE_HIGH"
    QUALITY_DEVIATION = "QUALITY_DEVIATION"
    TOOL_WEAR = "TOOL_WEAR"
    MAINTENANCE_DUE = "MAINTENANCE_DUE"


class NotificationChannelEnum(str, Enum):
    """通知渠道枚举"""
    EMAIL = "EMAIL"
    SMS = "SMS"
    WEBSOCKET = "WEBSOCKET"
    WEBHOOK = "WEBHOOK"


class AlarmResponse(BaseModel):
    """报警响应"""
    id: int
    device_id: int
    alarm_level: AlarmLevelEnum
    alarm_type: AlarmTypeEnum
    alarm_code: str
    alarm_message: str
    status: AlarmStatusEnum
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolution_note: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AlarmCreateRequest(BaseModel):
    """创建报警请求"""
    device_id: int = Field(..., description="设备ID", gt=0)
    alarm_level: AlarmLevelEnum = Field(..., description="报警级别")
    alarm_type: AlarmTypeEnum = Field(..., description="报警类型")
    alarm_code: str = Field(..., description="报警代码", max_length=50)
    alarm_message: str = Field(..., description="报警消息", max_length=255)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="元数据")


class AlarmAcknowledgeRequest(BaseModel):
    """确认报警请求"""
    acknowledged_by: str = Field(..., description="确认人")
    note: Optional[str] = Field(None, description="确认备注", max_length=500)


class AlarmResolveRequest(BaseModel):
    """解决报警请求"""
    resolved_by: str = Field(..., description="解决人")
    resolution_note: str = Field(..., description="解决说明", max_length=1000)


class AlarmCloseRequest(BaseModel):
    """关闭报警请求"""
    closed_by: str = Field(..., description="关闭人")
    note: Optional[str] = Field(None, description="关闭备注", max_length=500)


class AlarmQueryParams(BaseModel):
    """报警查询参数"""
    device_id: Optional[int] = Field(None, description="设备ID")
    alarm_level: Optional[AlarmLevelEnum] = Field(None, description="报警级别")
    alarm_type: Optional[AlarmTypeEnum] = Field(None, description="报警类型")
    status: Optional[AlarmStatusEnum] = Field(None, description="报警状态")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")


class AlarmStatisticsResponse(BaseModel):
    """报警统计响应"""
    total: int = Field(..., description="总数")
    open: int = Field(..., description="未处理")
    acknowledged: int = Field(..., description="已确认")
    resolved: int = Field(..., description="已解决")
    closed: int = Field(..., description="已关闭")
    by_level: Dict[str, int] = Field(default_factory=dict, description="按级别统计")
    by_type: Dict[str, int] = Field(default_factory=dict, description="按类型统计")


class NotificationRequest(BaseModel):
    """通知请求"""
    alarm_id: int = Field(..., description="报警ID")
    channels: List[NotificationChannelEnum] = Field(..., description="通知渠道")
    recipients: List[str] = Field(..., description="接收人（邮箱或手机号）")
    message: Optional[str] = Field(None, description="自定义消息")


class NotificationResponse(BaseModel):
    """通知响应"""
    success: bool
    message: str
    channel: NotificationChannelEnum
    recipient: str
    sent_at: Optional[datetime] = None


class AlarmRuleBase(BaseModel):
    """报警规则基础"""
    device_id: int = Field(..., description="设备ID")
    rule_name: str = Field(..., description="规则名称", max_length=100)
    rule_type: str = Field(..., description="规则类型")
    condition: Dict[str, Any] = Field(..., description="条件配置")
    alarm_level: AlarmLevelEnum = Field(..., description="报警级别")
    alarm_type: AlarmTypeEnum = Field(..., description="报警类型")
    is_enabled: bool = Field(True, description="是否启用")


class AlarmRuleCreate(AlarmRuleBase):
    """创建报警规则"""
    pass


class AlarmRuleUpdate(BaseModel):
    """更新报警规则"""
    rule_name: Optional[str] = Field(None, max_length=100)
    condition: Optional[Dict[str, Any]] = None
    alarm_level: Optional[AlarmLevelEnum] = None
    alarm_type: Optional[AlarmTypeEnum] = None
    is_enabled: Optional[bool] = None


class AlarmRuleResponse(AlarmRuleBase):
    """报警规则响应"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class WSAlarmMessage(BaseModel):
    """WebSocket 报警消息"""
    type: str = Field(..., description="消息类型")
    alarm: AlarmResponse = Field(..., description="报警信息")
    timestamp: datetime = Field(default_factory=datetime.now)