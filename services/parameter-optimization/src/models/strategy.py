"""
加工策略数据模型
"""
from sqlalchemy import Column, String, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Strategy(Base):
    """加工策略模型"""
    __tablename__ = "methods"

    # 主键
    id = Column(String(20), primary_key=True)
    
    # 基本信息
    name = Column(String(255), nullable=True, comment="策略名称")
    type = Column(String(32), nullable=True, comment="加工类型")
    
    # 质量要求
    rx_min = Column(Float, nullable=False, name="Rx_min", comment="最小侧面粗糙度 um")
    rz_min = Column(Float, nullable=False, name="Rz_min", comment="最小底面粗糙度 um")
    
    # 工艺参数
    lft_min = Column(Float, nullable=False, name="lfT_min", comment="最小刀具寿命 min")
    ae = Column(Float, nullable=False, comment="切削宽度 mm")
    mo_sun_xi_shu = Column(Float, nullable=False, name="moSun_xiShu", comment="刀具磨损系数")

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "rx_min": self.rx_min,
            "rz_min": self.rz_min,
            "lft_min": self.lft_min,
            "ae": self.ae,
            "moSunXiShu": self.mo_sun_xi_shu,
        }

    def __repr__(self) -> str:
        return f"<Strategy(id={self.id}, name={self.name}, type={self.type})>"