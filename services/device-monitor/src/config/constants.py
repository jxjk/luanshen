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

# OPC UA 节点配置（真实设备连接示例）
# 详见文档: docs/deployment/NC设备连接配置指南.md
OPCUA_NODE_MAPPING = {
    # FANUC设备示例
    1: {
        "device_name": "FANUC_5AX_VM",
        "controller_type": "FANUC",
        "server_url": "opc.tcp://192.168.1.100:4840",
        "description": "FANUC Series 30i-MB 五轴加工中心",
        "status": "ns=2;s=Channel1.Stat.Mode",
        "x_position": "ns=2;s=AxisX.Act.Position",
        "y_position": "ns=2;s=AxisY.Act.Position",
        "z_position": "ns=2;s=AxisZ.Act.Position",
        "spindle_speed": "ns=2;s=Spindle.Act.Speed",
        "feed_rate": "ns=2;s=Channel1.Stat.Feed",
        "load": "ns=2;s=Spindle.Act.Load",
        "alarm_code": "ns=2;s=Alarm.Code",
        "alarm_message": "ns=2;s=Alarm.Message",
    },
    
    # SIEMENS设备示例
    2: {
        "device_name": "SIEMENS_840D",
        "controller_type": "SIEMENS",
        "server_url": "opc.tcp://192.168.1.101:4840",
        "description": "SIEMENS SINUMERIK 840D sl 五轴加工中心",
        "status": "ns=2;s=PLC.Blocks.DB10.OperatingState",
        "x_position": "ns=2;s=PLC.Blocks.DB10.AxisX.ActPos",
        "y_position": "ns=2;s=PLC.Blocks.DB10.AxisY.ActPos",
        "z_position": "ns=2;s=PLC.Blocks.DB10.AxisZ.ActPos",
        "spindle_speed": "ns=2;s=PLC.Blocks.DB10.Spindle.ActSpeed",
        "feed_rate": "ns=2;s=PLC.Blocks.DB10.Channel.ActFeed",
        "load": "ns=2;s=PLC.Blocks.DB10.Spindle.ActLoad",
        "alarm_code": "ns=2;s=PLC.Blocks.DB10.Alarm.Code",
        "alarm_message": "ns=2;s=PLC.Blocks.DB10.Alarm.Message",
    },
    
    # HEIDENHAIN设备示例
    3: {
        "device_name": "HEIDENHAIN_TNC640",
        "controller_type": "HEIDENHAIN",
        "server_url": "opc.tcp://192.168.1.102:4840",
        "description": "HEIDENHAIN TNC 640 五轴加工中心",
        "status": "ns=2;s=Machine.Status",
        "x_position": "ns=2;s=AxisX.ActPosition",
        "y_position": "ns=2;s=AxisY.ActPosition",
        "z_position": "ns=2;s=AxisZ.ActPosition",
        "spindle_speed": "ns=2;s=Spindle.ActSpeed",
        "feed_rate": "ns=2;s=Path.ActFeed",
        "load": "ns=2;s=Spindle.ActLoad",
        "alarm_code": "ns=2;s=Alarm.Number",
        "alarm_message": "ns=2;s=Alarm.Text",
    },
    
    # MITSUBISHI设备示例
    4: {
        "device_name": "MITSUBISHI_M800",
        "controller_type": "MITSUBISHI",
        "server_url": "opc.tcp://192.168.1.103:4840",
        "description": "MITSUBISHI M800/M80 Series 五轴加工中心",
        "status": "ns=2;s=Machine.OperationMode",
        "x_position": "ns=2;s=AxisX.ActPosition",
        "y_position": "ns=2;s=AxisY.ActPosition",
        "z_position": "ns=2;s=AxisZ.ActPosition",
        "spindle_speed": "ns=2;s=Spindle.ActSpeed",
        "feed_rate": "ns=2;s=Path.ActFeed",
        "load": "ns=2;s=Spindle.ActLoad",
        "alarm_code": "ns=2;s=Alarm.Code",
        "alarm_message": "ns=2;s=Alarm.Message",
    },
    
    # KEPServerEX网关连接示例
    5: {
        "device_name": "FANUC_Via_KEPServer",
        "controller_type": "FANUC",
        "server_url": "opc.tcp://192.168.1.200:49380",
        "description": "通过KEPServerEX网关连接的FANUC设备",
        "status": "ns=2;s=Channel1.Device1.Tag_Status",
        "x_position": "ns=2;s=Channel1.Device1.Tag_X",
        "y_position": "ns=2;s=Channel1.Device1.Tag_Y",
        "z_position": "ns=2;s=Channel1.Device1.Tag_Z",
        "spindle_speed": "ns=2;s=Channel1.Device1.Tag_SpindleSpeed",
        "feed_rate": "ns=2;s=Channel1.Device1.Tag_FeedRate",
        "load": "ns=2;s=Channel1.Device1.Tag_Load",
        "alarm_code": "ns=2;s=Channel1.Device1.Tag_AlarmCode",
        "alarm_message": "ns=2;s=Channel1.Device1.Tag_AlarmMessage",
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