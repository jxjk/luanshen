"""
质量追溯记录仓储
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from ..models.trace_record import QualityTraceRecord, QualityTraceParameter, QualityGradeEnum


class TraceRecordRepository:
    """质量追溯记录仓储类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, trace_data: dict) -> QualityTraceRecord:
        """创建追溯记录"""
        record = QualityTraceRecord(
            workpiece_id=trace_data["workpiece_id"],
            workpiece_name=trace_data.get("workpiece_name"),
            production_order_id=trace_data.get("production_order_id"),
            material_id=trace_data.get("material_id"),
            tool_id=trace_data.get("tool_id"),
            machine_id=trace_data.get("machine_id"),
            strategy_id=trace_data.get("strategy_id"),
            nc_program_path=trace_data.get("nc_program_path"),
            operator=trace_data.get("operator"),
            start_time=datetime.now(),
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record
    
    def get(self, trace_id: int) -> Optional[QualityTraceRecord]:
        """获取追溯记录"""
        return self.db.query(QualityTraceRecord).filter(QualityTraceRecord.id == trace_id).first()
    
    def get_by_workpiece_id(self, workpiece_id: str) -> Optional[QualityTraceRecord]:
        """根据工件ID获取追溯记录"""
        return self.db.query(QualityTraceRecord).filter(
            QualityTraceRecord.workpiece_id == workpiece_id
        ).first()
    
    def get_all(
        self,
        production_order_id: Optional[str] = None,
        machine_id: Optional[int] = None,
        quality_grade: Optional[QualityGradeEnum] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[QualityTraceRecord]:
        """获取追溯记录列表"""
        query = self.db.query(QualityTraceRecord)
        
        if production_order_id:
            query = query.filter(QualityTraceRecord.production_order_id == production_order_id)
        if machine_id:
            query = query.filter(QualityTraceRecord.machine_id == machine_id)
        if quality_grade:
            query = query.filter(QualityTraceRecord.quality_grade == quality_grade)
        if start_time:
            query = query.filter(QualityTraceRecord.start_time >= start_time)
        if end_time:
            query = query.filter(QualityTraceRecord.start_time <= end_time)
        
        return (
            query.order_by(QualityTraceRecord.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def update(self, trace_id: int, update_data: dict) -> Optional[QualityTraceRecord]:
        """更新追溯记录"""
        record = self.get(trace_id)
        if record:
            for key, value in update_data.items():
                if hasattr(record, key):
                    setattr(record, key, value)
            
            # 计算总耗时
            if record.start_time and record.end_time:
                record.total_duration = int((record.end_time - record.start_time).total_seconds())
            
            self.db.commit()
            self.db.refresh(record)
        return record
    
    def append_parameters(self, trace_id: int, parameters: List[dict]) -> int:
        """追加参数数据"""
        count = 0
        for param in parameters:
            trace_param = QualityTraceParameter(
                trace_record_id=trace_id,
                parameter_name=param["parameter_name"],
                parameter_value=param["parameter_value"],
                timestamp=param.get("timestamp") or datetime.now()
            )
            self.db.add(trace_param)
            count += 1
        
        self.db.commit()
        return count
    
    def get_parameters(
        self,
        trace_id: int,
        parameter_name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[QualityTraceParameter]:
        """获取参数数据"""
        query = self.db.query(QualityTraceParameter).filter(
            QualityTraceParameter.trace_record_id == trace_id
        )
        
        if parameter_name:
            query = query.filter(QualityTraceParameter.parameter_name == parameter_name)
        if start_time:
            query = query.filter(QualityTraceParameter.timestamp >= start_time)
        if end_time:
            query = query.filter(QualityTraceParameter.timestamp <= end_time)
        
        return query.order_by(QualityTraceParameter.timestamp).all()
    
    def get_timeline(self, trace_id: int) -> Dict[str, Any]:
        """获取时间轴数据"""
        record = self.get(trace_id)
        if not record:
            return None
        
        parameters = self.get_parameters(trace_id)
        
        # 按时间分组参数
        timeline = {}
        for param in parameters:
            time_key = param.timestamp.isoformat()
            if time_key not in timeline:
                timeline[time_key] = {}
            timeline[time_key][param.parameter_name] = float(param.parameter_value) if param.parameter_value else None
        
        return {
            "record": record.to_dict(),
            "timeline": timeline,
            "parameters": [p.to_dict() for p in parameters]
        }
    
    def get_statistics(self, trace_id: int) -> Dict[str, Any]:
        """获取追溯统计信息"""
        parameters = self.get_parameters(trace_id)
        
        # 按参数名分组统计
        param_stats = {}
        for param in parameters:
            name = param.parameter_name
            value = float(param.parameter_value) if param.parameter_value else None
            
            if name not in param_stats:
                param_stats[name] = {
                    "count": 0,
                    "min": float('inf'),
                    "max": float('-inf'),
                    "sum": 0.0,
                    "values": []
                }
            
            if value is not None:
                param_stats[name]["count"] += 1
                param_stats[name]["min"] = min(param_stats[name]["min"], value)
                param_stats[name]["max"] = max(param_stats[name]["max"], value)
                param_stats[name]["sum"] += value
                param_stats[name]["values"].append(value)
        
        # 计算平均值
        for name, stats in param_stats.items():
            if stats["count"] > 0:
                stats["avg"] = stats["sum"] / stats["count"]
            else:
                stats["min"] = None
                stats["max"] = None
        
        return {
            "total_parameters": len(parameters),
            "parameter_count": len(param_stats),
            "parameter_statistics": param_stats
        }