"""
常量定义
"""

# 报警级别枚举
class AlarmLevelEnum:
    WARNING = "WARNING"
    ALARM = "ALARM"
    CRITICAL = "CRITICAL"

# 报警状态枚举
class AlarmStatusEnum:
    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

# 通知渠道枚举
class NotificationChannelEnum:
    EMAIL = "EMAIL"
    SMS = "SMS"
    WEBSOCKET = "WEBSOCKET"
    WEBHOOK = "WEBHOOK"

# 报警类型枚举
class AlarmTypeEnum:
    DEVICE_OFFLINE = "DEVICE_OFFLINE"
    DEVICE_ALARM = "DEVICE_ALARM"
    PARAMETER_EXCEED = "PARAMETER_EXCEED"
    VIBRATION_HIGH = "VIBRATION_HIGH"
    TEMPERATURE_HIGH = "TEMPERATURE_HIGH"
    QUALITY_DEVIATION = "QUALITY_DEVIATION"
    TOOL_WEAR = "TOOL_WEAR"
    MAINTENANCE_DUE = "MAINTENANCE_DUE"

# Redis Key 前缀
class RedisKeyPrefix:
    ALARM = "alarm:"
    ALARM_RULE = "alarm:rule:"
    NOTIFICATION_QUEUE = "notification:queue"

# WebSocket 消息类型
class WSMessageType:
    ALARM_CREATED = "alarm_created"
    ALARM_UPDATED = "alarm_updated"
    ALARM_ACKNOWLEDGED = "alarm_acknowledged"
    ALARM_RESOLVED = "alarm_resOLVED"
    HEARTBEAT = "heartbeat"

# RabbitMQ Exchange 和 Queue
class RabbitMQConfig:
    ALARM_EXCHANGE = "alarm.exchange"
    ALARM_QUEUE = "alarm.queue"
    NOTIFICATION_QUEUE = "notification.queue"
    ROUTING_KEY_ALARM = "alarm.created"
    ROUTING_KEY_NOTIFICATION = "notification.send"

# API 响应消息
class APIMessage:
    SUCCESS = "操作成功"
    CREATED = "创建成功"
    UPDATED = "更新成功"
    DELETED = "删除成功"
    ACKNOWLEDGED = "报警已确认"
    RESOLVED = "报警已解决"
    CLOSED = "报警已关闭"
    NOT_FOUND = "资源不存在"
    INVALID_PARAMS = "参数无效"
    INTERNAL_ERROR = "内部服务器错误"
    ALARM_NOT_FOUND = "报警记录不存在"
    ALARM_ALREADY_ACKNOWLEDGED = "报警已被确认"
    ALARM_ALREADY_RESOLVED = "报警已解决"
    NOTIFICATION_FAILED = "通知发送失败"

# 报警规则类型
class RuleTypeEnum:
    THRESHOLD = "THRESHOLD"  # 阈值规则
    RATE_OF_CHANGE = "RATE_OF_CHANGE"  # 变化率规则
    PATTERN = "PATTERN"  # 模式规则
    COMPOSITE = "COMPOSITE"  # 组合规则