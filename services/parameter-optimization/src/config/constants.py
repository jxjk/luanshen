"""
常量定义模块
集中管理应用中使用的常量
"""

# 加工方法枚举
class MachiningMethod:
    """加工方法"""
    MILLING = "milling"
    DRILLING = "drilling"
    BORING = "boring"
    TURNING = "turning"

    @classmethod
    def all(cls) -> list[str]:
        return [cls.MILLING, cls.DRILLING, cls.BORING, cls.TURNING]

    @classmethod
    def is_valid(cls, method: str) -> bool:
        return method in cls.all()


# 材料组枚举（基于 ga_tools.sql）
class MaterialGroup:
    """材料组"""
    # 非合金及低合金钢
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"
    P5 = "P5"
    P6 = "P6"
    P7 = "P7"
    P8 = "P8"
    P9 = "P9"
    P10 = "P10"
    P11 = "P11"
    P12 = "P12"
    P13 = "P13"
    P14 = "P14"
    P15 = "P15"
    
    # 不锈钢
    M1 = "M1"
    M2 = "M2"
    M3 = "M3"
    
    # 铸铁
    K1 = "K1"
    K2 = "K2"
    K3 = "K3"
    K4 = "K4"
    K5 = "K5"
    K6 = "K6"
    K7 = "K7"
    
    # 铝合金和铜合金
    N1 = "N1"
    N2 = "N2"
    N3 = "N3"
    N4 = "N4"
    N5 = "N5"
    N7 = "N7"
    N8 = "N8"
    N9 = "N9"
    N10 = "N10"
    
    # 耐热合金
    S1 = "S1"
    S2 = "S2"
    S3 = "S3"
    
    # 淬火钢
    H1 = "H1"
    H2 = "H2"
    H3 = "H3"
    H4 = "H4"
    
    # 硬质材料
    O1 = "O1"
    O2 = "O2"
    O3 = "O3"
    O4 = "O4"
    O5 = "O5"
    O6 = "O6"


# DNA 编码常量
class DNAEncoding:
    """DNA 编码配置"""
    # 基因位分配
    SPEED_BITS = 16      # 转速占 16 位
    FEED_BITS = 13       # 进给占 13 位
    CUT_DEPTH_BITS = 7   # 切深占 7 位
    
    @classmethod
    def total_bits(cls) -> int:
        return cls.SPEED_BITS + cls.FEED_BITS + cls.CUT_DEPTH_BITS
    
    @classmethod
    def get_bit_ranges(cls) -> dict:
        """获取各参数的位范围"""
        speed_end = cls.SPEED_BITS
        feed_end = speed_end + cls.FEED_BITS
        return {
            "speed": (0, speed_end),
            "feed": (speed_end, feed_end),
            "cut_depth": (feed_end, cls.total_bits())
        }


# 优化目标权重
class ObjectiveWeights:
    """优化目标权重"""
    MATERIAL_REMOVAL_RATE = 1.0      # 材料去除率权重
    TOOL_LIFE = 0.5                  # 刀具寿命权重
    SURFACE_QUALITY = 0.3            # 表面质量权重
    ENERGY_EFFICIENCY = 0.2          # 能效权重


# 约束惩罚系数
class ConstraintPenalty:
    """约束惩罚系数"""
    POWER = 1e29          # 功率约束惩罚系数
    TORQUE = 1e29        # 扭矩约束惩罚系数（修复：从1e6改为1e29）
    TOOL_LIFE = 1e29     # 刀具寿命约束惩罚系数
    SURFACE_ROUGHNESS = 1e29  # 表面粗糙度约束惩罚系数
    FEED_FORCE = 1e29    # 进给力约束惩罚系数（修复：从1e6改为1e29）
    MAX_FEED = 1e29      # 最大进给惩罚系数（修复：从1改为1e29）
    MAX_SPEED = 1e29     # 最大转速惩罚系数（修复：从1改为1e29）


# 物理计算常量
class PhysicalConstants:
    """物理计算常量"""
    PI = 3.141592653589793
    SPEED_TO_VC_FACTOR = 1.0 / 318.0  # 转速转线速度系数 (n * D / 318) - 与旧版本保持一致
    VC_FORMULA_DIVISOR = 318.0  # 线速度计算分母，与旧版本保持一致
    POWER_WATT_TO_KW = 1.0 / 60000.0  # 瓦特转千瓦系数
    TORQUE_FACTOR = 9549.0            # 扭矩计算系数
    MILLING_ROUGHNESS_FACTOR = 318.0 / 4.0  # 铣削粗糙度系数
    MILLING_SIDE_ROUGHNESS_FACTOR = 125.0   # 铣削侧壁粗糙度系数
    TURNING_ROUGHNESS_FACTOR = 1000.0 / 8.0 # 车削粗糙度系数