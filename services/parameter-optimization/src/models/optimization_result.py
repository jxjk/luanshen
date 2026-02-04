"""
优化结果数据模型
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class OptimizationResult(Base):
    """优化结果模型"""
    __tablename__ = "record"

    # 主键
    id = Column(String(20), primary_key=True)
    
    # 输入参数
    ci_liao_id = Column(Integer, nullable=True, name="ciLiaoID", comment="材料ID")
    tool_id = Column(Integer, nullable=True, name="toolID", comment="刀具ID")
    machine_id = Column(Integer, nullable=True, name="machineID", comment="设备ID")
    method_id = Column(Integer, nullable=True, name="methodID", comment="策略ID")
    
    # 优化结果 - 切削参数
    s = Column(Integer, nullable=True, comment="转速 r/min")
    f = Column(Integer, nullable=True, comment="进给量 mm/min")
    ap = Column(Float, nullable=True, comment="切深 mm")
    ae = Column(Float, nullable=True, comment="切宽 mm")
    
    # 优化结果 - 计算参数
    vc = Column(Float, nullable=True, comment="线速度 m/min")
    fz = Column(Float, nullable=True, comment="每齿进给 mm")
    rz = Column(Float, nullable=True, comment="底面粗糙度 um")
    rx = Column(Float, nullable=True, comment="侧面粗糙度 um")
    pw = Column(Float, nullable=True, comment="功率 Kw")
    tnm = Column(Float, nullable=True, comment="扭矩 Nm")
    q = Column(Float, nullable=True, comment="排屑量 cm³/min")
    lft = Column(Float, nullable=True, comment="刀具寿命 min")
    
    # 时间戳
    created_at = Column(DateTime, nullable=True, default=func.now(), comment="创建时间")

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "material_id": self.ci_liao_id,
            "tool_id": self.tool_id,
            "machine_id": self.machine_id,
            "method_id": self.method_id,
            "speed": self.s,
            "feed": self.f,
            "cut_depth": self.ap,
            "cut_width": self.ae,
            "cutting_speed": self.vc,
            "feed_per_tooth": self.fz,
            "bottom_roughness": self.rz,
            "side_roughness": self.rx,
            "power": self.pw,
            "torque": self.tnm,
            "material_removal_rate": self.q,
            "tool_life": self.lft,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<OptimizationResult(id={self.id}, speed={self.s}, feed={self.f})>"