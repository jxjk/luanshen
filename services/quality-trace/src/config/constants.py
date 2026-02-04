"""
常量定义
"""

# 质量等级枚举
class QualityGradeEnum:
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    ACCEPTABLE = "ACCEPTABLE"
    REJECTED = "REJECTED"

# 追溯状态枚举
class TraceStatusEnum:
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    PAUSED = "PAUSED"
    CANCELLED = "CANCELLED"

# 数据来源枚举
class DataSourceEnum:
    DEVICE = "DEVICE"
    MANUAL = "MANUAL"
    IMPORTED = "IMPORTED"
    INTEGRATED = "INTEGRATED"

# API 响应消息
class APIMessage:
    SUCCESS = "操作成功"
    CREATED = "创建成功"
    UPDATED = "更新成功"
    DELETED = "删除成功"
    NOT_FOUND = "资源不存在"
    INVALID_PARAMS = "参数无效"
    INTERNAL_ERROR = "内部服务器错误"
    TRACE_NOT_FOUND = "追溯记录不存在"
    WORKPIECE_ALREADY_EXISTS = "工件追溯记录已存在"
    TRACE_IN_PROGRESS = "追溯正在进行中"
    INVALID_TIME_RANGE = "无效的时间范围"

# 参数类型
class ParameterTypeEnum:
    SPEED = "speed"
    FEED = "feed"
    CUT_DEPTH = "cut_depth"
    CUT_WIDTH = "cut_width"
    POWER = "power"
    TORQUE = "torque"
    TEMPERATURE = "temperature"
    VIBRATION = "vibration"
    POSITION_X = "position_x"
    POSITION_Y = "position_y"
    POSITION_Z = "position_z"