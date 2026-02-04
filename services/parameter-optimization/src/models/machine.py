"""
设备数据模型
"""
from sqlalchemy import Column, String, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Machine(Base):
    """设备模型"""
    __tablename__ = "machines"

    # 主键
    id = Column(String(20), primary_key=True)
    
    # 基本信息
    name = Column(String(255), nullable=True, comment="设备名称")
    type = Column(String(20), nullable=True, comment="设备类型")
    xing_hao = Column(String(255), nullable=True, name="xingHao", comment="型号")
    
    # 性能参数
    pw_max = Column(Float, nullable=False, name="Pw_max", comment="最大功率 Kw")
    rp_max = Column(Float, nullable=False, name="Rp_max", comment="最大转速 r/min")
    tnm_max = Column(Float, nullable=False, name="Tnm_max", comment="最大扭矩 Nm")
    xiao_lv = Column(Float, nullable=False, name="xiaoLv", comment="机床效率")
    f_max = Column(Float, nullable=False, name="F_max", comment="最大进给量 mm/min")

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "pw_max": self.pw_max,
            "rp_max": self.rp_max,
            "tnm_max": self.tnm_max,
            "xiaoLv": self.xiao_lv,
            "f_max": self.f_max,
        }

    def __repr__(self) -> str:
        return f"<Machine(id={self.id}, name={self.name}, type={self.type})>"