"""
刀具数据模型
"""
from sqlalchemy import Column, String, Integer, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Tool(Base):
    """刀具模型"""
    __tablename__ = "tools"

    # 主键
    id = Column(String(8), primary_key=True)
    
    # 基本信息
    name = Column(String(255), nullable=True, comment="刀具名称")
    type = Column(String(8), nullable=True, comment="刀具类型")
    xing_hao = Column(String(32), nullable=True, name="xingHao", comment="型号")
    
    # 几何参数
    zhi_jing = Column(Float, nullable=False, name="zhiJing", comment="刀具直径 mm")
    chi_shu = Column(Integer, nullable=False, name="chiShu", comment="刀具齿数")
    qian_jiao = Column(Float, nullable=False, name="qianJiao", comment="前角")
    zhu_pian_jiao = Column(Float, nullable=False, name="zhuPianJiao", comment="主偏角")
    dao_jian_r = Column(Float, nullable=False, name="daoJianR", comment="刀尖半径 mm")
    
    # 性能参数
    ff_max = Column(Integer, nullable=True, name="Ff_max", comment="最大进给力 N")
    ap_max = Column(Float, nullable=False, name="Ap_Max", comment="最大切深 mm")
    ae_max = Column(Float, nullable=False, name="Ae_max", comment="最大切宽 mm")
    vc_max = Column(Float, nullable=False, name="Vc_max", comment="最大线速度 m/min")
    fz_max = Column(Float, nullable=False, name="fz_max", comment="最大每齿进给量 mm")
    
    # 耐用度系数
    ct = Column(Float, nullable=False, name="Ct", comment="刀具耐用度系数")
    s_xi_shu = Column(Float, nullable=False, name="S_xiShu", comment="转速系数")
    f_xi_shu = Column(Float, nullable=False, name="F_xiShu", comment="进给系数")
    ap_xi_shu = Column(Float, nullable=False, name="Ap_xiShu", comment="切深系数")

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "zhiJing": self.zhi_jing,
            "chiShu": self.chi_shu,
            "vc_max": self.vc_max,
            "fz_max": self.fz_max,
            "ct": self.ct,
            "s_xiShu": self.s_xi_shu,
            "f_xiShu": self.f_xi_shu,
            "ap_xiShu": self.ap_xi_shu,
            "ap_max": self.ap_max,
            "ff_max": self.ff_max,
            "daoJianR": self.dao_jian_r,
            "zhuPianJiao": self.zhu_pian_jiao,
            "qianJiao": self.qian_jiao,
        }

    def __repr__(self) -> str:
        return f"<Tool(id={self.id}, name={self.name}, diameter={self.zhi_jing})>"