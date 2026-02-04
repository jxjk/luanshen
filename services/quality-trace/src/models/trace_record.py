"""
质量追溯记录模型
"""
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, Enum, DECIMAL
from sqlalchemy.sql import func
import enum

from ..config.database import Base


class QualityGradeEnum(str, enum.Enum):
    """质量等级枚举"""
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    ACCEPTABLE = "ACCEPTABLE"
    REJECTED = "REJECTED"


class QualityTraceRecord(Base):
    """质量追溯记录表"""
    __tablename__ = "quality_trace_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    workpiece_id = Column(String(100), unique=True, nullable=False, index=True, comment="工件ID")
    workpiece_name = Column(String(255), nullable=True, comment="工件名称")
    production_order_id = Column(String(50), nullable=True, index=True, comment="生产订单ID")
    material_id = Column(String(50), nullable=True, comment="材料ID")
    tool_id = Column(Integer, ForeignKey("tools.id"), nullable=True, comment="刀具ID")
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=True, index=True, comment="设备ID")
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=True, comment="策略ID")
    start_time = Column(TIMESTAMP, nullable=True, comment="开始时间")
    end_time = Column(TIMESTAMP, nullable=True, comment="结束时间")
    total_duration = Column(Integer, nullable=True, comment="总耗时（秒）")
    nc_program_path = Column(String(500), nullable=True, comment="NC程序路径")
    operator = Column(String(50), nullable=True, comment="操作员")
    quality_grade = Column(
        Enum(QualityGradeEnum),
        nullable=True,
        comment="质量等级"
    )
    inspection_result = Column(Text, nullable=True, comment="检测结果")
    created_at = Column(TIMESTAMP, default=func.now(), nullable=False, comment="创建时间")
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "workpiece_id": self.workpiece_id,
            "workpiece_name": self.workpiece_name,
            "production_order_id": self.production_order_id,
            "material_id": self.material_id,
            "tool_id": self.tool_id,
            "machine_id": self.machine_id,
            "strategy_id": self.strategy_id,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "total_duration": self.total_duration,
            "nc_program_path": self.nc_program_path,
            "operator": self.operator,
            "quality_grade": self.quality_grade.value if self.quality_grade else None,
            "inspection_result": self.inspection_result,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class QualityTraceParameter(Base):
    """质量追溯参数明细表"""
    __tablename__ = "quality_trace_parameters"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    trace_record_id = Column(Integer, ForeignKey("quality_trace_records.id"), nullable=False, index=True, comment="追溯记录ID")
    parameter_name = Column(String(50), nullable=False, comment="参数名称")
    parameter_value = Column(DECIMAL(15, 4), nullable=True, comment="参数值")
    timestamp = Column(TIMESTAMP, default=func.now(), nullable=False, comment="时间戳")
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "trace_record_id": self.trace_record_id,
            "parameter_name": self.parameter_name,
            "parameter_value": float(self.parameter_value) if self.parameter_value else None,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }