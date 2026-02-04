"""
材料数据模型
"""
from sqlalchemy import Column, String, Integer, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Material(Base):
    """材料模型"""
    __tablename__ = "cailiao"

    # 主键
    cai_liao_zu = Column(String(3), primary_key=True, name="caiLiaoZu")
    
    # 基本信息
    name = Column(String(255), nullable=True, comment="材料名称")
    
    # 力学性能
    rm_min = Column(Integer, nullable=True, comment="最小强度 Rm_min")
    rm_max = Column(Integer, nullable=True, comment="最大强度 Rm_max")
    
    # 切削参数
    kc11 = Column(Integer, nullable=True, comment="单位切削力 N/mm²")
    mc = Column(Float, nullable=True, comment="坡度值")

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.cai_liao_zu,
            "caiLiaoZu": self.cai_liao_zu,
            "name": self.name,
            "rm_min": self.rm_min,
            "rm_max": self.rm_max,
            "kc11": self.kc11,
            "mc": self.mc,
        }

    def __repr__(self) -> str:
        return f"<Material(id={self.cai_liao_zu}, name={self.name})>"