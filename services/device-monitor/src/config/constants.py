"""
常量定义
"""

# 设备状态枚举
class DeviceStatusEnum:
    RUNNING = "RUNNING"
    IDLE = "IDLE"
    ALARM = "ALARM"
    MAINTENANCE = "MAINTENANCE"
    OFFLINE = "OFFLINE"


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


# 传感器类型枚举
class SensorTypeEnum:
    VIBRATION = "VIBRATION"
    TEMPERATURE = "TEMPERATURE"
    CURRENT = "CURRENT"
    PRESSURE = "PRESSURE"
    FLOW = "FLOW"
    POSITION = "POSITION"
    SPEED = "SPEED"
    TORQUE = "TORQUE"


# InfluxDB Measurements
class InfluxMeasurement:
    DEVICE_SENSOR_DATA = "device_sensor_data"
    PROCESS_PARAMETERS = "process_parameters"
    DEVICE_STATUS_SNAPSHOT = "device_status_snapshot"


# WebSocket 消息类型
class WSMessageType:
    DEVICE_STATUS = "device_status"
    SENSOR_DATA = "sensor_data"
    ALARM = "alarm"
    HEARTBEAT = "heartbeat"


# Redis Key 前缀
class RedisKeyPrefix:
    DEVICE_STATUS = "device:status:"
    DEVICE_DATA = "device:data:"
    DEVICE_SUBSCRIBERS = "device:subscribers:"
    ALARM = "alarm:"

# OPC UA 节点配置（示例）
OPCUA_NODE_MAPPING = {
    1: {
        "status": "ns=2;s=Machine1.Status",
        "x_position": "ns=2;s=Machine1.AxisX.Position",
        "y_position": "ns=2;s=Machine1.AxisY.Position",
        "z_position": "ns=2;s=Machine1.AxisZ.Position",
        "spindle_speed": "ns=2;s=Machine1.Spindle.Speed",
        "feed_rate": "ns=2;s=Machine1.Feed.Rate",
        "load": "ns=2;s=Machine1.Load.Percent",
        "alarm_code": "ns=2;s=Machine1.Alarm.Code",
        "alarm_message": "ns=2;s=Machine1.Alarm.Message",
    },
}

# 数据采集间隔（秒）
COLLECTION_INTERVAL = 1.0

# 批量写入大小
BATCH_WRITE_SIZE = 100

# 数据保留策略（天）
DATA_RETENTION_DAYS = 90

# API 响应消息
class APIMessage:
    SUCCESS = "操作成功"
    CREATED = "创建成功"
    UPDATED = "更新成功"
    DELETED = "删除成功"
    NOT_FOUND = "资源不存在"
    INVALID_PARAMS = "参数无效"
    INTERNAL_ERROR = "内部服务器错误"
    DEVICE_NOT_FOUND = "设备不存在"
    DEVICE_ALREADY_STARTED = "设备监控已启动"
    DEVICE_ALREADY_STOPPED = "设备监控已停止"
    COLLECTION_FAILED = "数据采集失败"