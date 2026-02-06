"""
微生物遗传算法（Microbial Genetic Algorithm）
重构版本：模块化、可配置、可测试
优化版本：并行化、早停机制、自适应参数、向量化计算
"""
from dataclasses import dataclass
from typing import Callable, Tuple, List, Dict, Any
import numpy as np
import math
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import multiprocessing as mp

from ..config.constants import (
    DNAEncoding,
    ConstraintPenalty,
    PhysicalConstants,
    MachiningMethod
)


@dataclass
class GAConfig:
    """遗传算法配置"""
    dna_size: int = DNAEncoding.total_bits()
    population_size: int = 10240
    generations: int = 200
    crossover_rate: float = 0.6
    mutation_rate: float = 0.3
    early_stop_generations: int = 50
    
    # 并行化配置
    enable_parallel: bool = True
    n_workers: int = None  # None 表示使用所有 CPU 核心
    
    # 增量优化配置
    batch_size: int = 128  # 每批处理的个体数量
    adaptive_rate: bool = True  # 自适应交叉和变异率
    
    # 参数边界
    speed_bound: Tuple[float, float] = (0, 8000)      # 转速边界
    feed_bound: Tuple[float, float] = (0, 8000)        # 进给边界
    cut_depth_bound: Tuple[float, float] = (0.0, 1.0)  # 切深百分比边界


@dataclass
class OptimizationConstraints:
    """优化约束条件"""
    # 约束值
    min_tool_life: float = 1.0
    max_power: float = 5.5
    max_torque: float = 40.0
    max_feed_force: float = 800.0
    min_surface_roughness: float = 3.2
    
    # 工艺参数
    tool_diameter: float = 25.0
    tool_teeth: int = 2
    tool_radius: float = 0.8
    main_cutting_angle: float = 31.0
    rake_angle: float = 0.0
    cut_width: float = 8.5
    bottom_hole_diameter: float = 22.5  # 镗孔底孔直径
    turning_diameter: float = 0.0       # 车削直径
    
    # 刀具耐用度系数
    tool_life_coefficient: float = 100000.0
    speed_coefficient: float = -1.5
    feed_coefficient: float = 0.75
    cut_depth_coefficient: float = 0.1
    
    # 材料参数
    material_coefficient: float = 2000.0
    material_slope: float = 0.21
    
    # 机床参数
    machine_efficiency: float = 0.85
    
    # 加工方法
    machining_method: str = MachiningMethod.DRILLING

    # 刀具磨损系数
    wear_coefficient: float = 1.0

    # 刀具挠度参数
    tool_elastic_modulus: float = 630000.0  # 弹性模量 (MPa), 硬质合金约630GPa
    tool_overhang_length: float = 60.0  # 悬伸长度 (mm) - 调整为更常见的60mm
    max_tool_deflection: float = 0.15  # 最大允许挠度 (mm) - 调整为刀具直径的15%

    # 最大参数限制
    max_feed_per_tooth: float = 0.15
    max_cutting_speed: float = 120.0
    max_cut_depth: float = 5.0  # 最大切深调整为5mm（更合理）


def evaluate_vectorized(population: np.ndarray, constraints_dict: Dict) -> np.ndarray:
    """
    向量化评估适应度（批量计算，避免进程开销）
    
    Args:
        population: 种群矩阵 (N, dna_size)
        constraints_dict: 约束字典
    
    Returns:
        适应度数组
    """
    N = population.shape[0]
    fitnesses = np.zeros(N)
    
    # 提取约束
    constraints = OptimizationConstraints(**constraints_dict)
    
    # 向量化解码（使用正确的位范围）
    speed_bits = population[:, :16]
    feed_bits = population[:, 16:29]
    cut_depth_bits = population[:, 29:]
    
    # 计算每位权重（从高位到低位，与旧版本保持一致）
    speed_weights = 2 ** np.arange(16)[::-1]
    feed_weights = 2 ** np.arange(13)[::-1]
    cut_depth_weights = 2 ** np.arange(7)[::-1]
    
    # 向量化解码参数（与旧版本完全一致：直接乘以边界上限）
    speed_vals = np.dot(speed_bits, speed_weights) / (2**16 - 1)
    speed = speed_vals * 8000  # 旧版本：直接乘以 MAX_SPEED
    
    feed_vals = np.dot(feed_bits, feed_weights) / (2**13 - 1)
    feed = feed_vals * 8000  # 旧版本：直接乘以 MAX_FEED
    
    cut_depth_vals = np.dot(cut_depth_bits, cut_depth_weights) / (2**7 - 1)
    cut_depth = cut_depth_vals * constraints.max_cut_depth  # 修复：使用配置的最大切深而不是硬编码的1.0
    
    # 参数边界检查
    n = np.maximum(speed, 1.0)
    f = np.maximum(feed, 0.1)
    ap = cut_depth  # 修复：cut_depth 已经是实际切深（0-max_cut_depth），不需要再乘
    ae = constraints.cut_width
    
    # 向量化计算
    fz = f / (constraints.tool_teeth * n)
    vc = (n * constraints.tool_diameter) / 318.0 + 0.1  # 与旧版本保持一致
    
    # 根据加工方法计算
    if constraints.machining_method == MachiningMethod.MILLING:
        q = f * ap * ae / 1000 + 1e-7
        safe_vc = np.maximum(vc, 0.001)
        safe_fz = np.maximum(fz, 0.001)
        lft = (
            constraints.tool_life_coefficient *
            (safe_vc ** constraints.speed_coefficient) *
            (safe_fz ** constraints.feed_coefficient) *
            constraints.wear_coefficient
        )
        rz = PhysicalConstants.MILLING_ROUGHNESS_FACTOR * (safe_fz ** 2) / constraints.tool_diameter

        # ae_ratio是标量，直接使用
        ae_ratio = ae / constraints.tool_diameter

        # 根据ae_ratio的值选择计算方法
        if ae_ratio <= 0.3:
            hm = safe_fz * np.sqrt(ae_ratio)
        else:
            # 修复：使用正确的变量名
            ratio = np.clip((ae - 0.5 * constraints.tool_diameter) / (0.5 * constraints.tool_diameter), -1, 1)
            # fs 应该是角度（度），不是弧度
            fs = 90 + np.arcsin(ratio) * 180 / np.pi  # 修复：将弧度转换为角度
            hm = 1147 * safe_fz * np.sin(constraints.main_cutting_angle * np.pi / 180) * ae_ratio / fs

        kc = (1 - 0.01 * constraints.rake_angle) * constraints.material_coefficient / (hm ** constraints.material_slope + 1e-3)
        pmot = q * kc * PhysicalConstants.POWER_WATT_TO_KW / constraints.machine_efficiency
        tnm = pmot * PhysicalConstants.TORQUE_FACTOR / (n + 1e-7)

        # 进给力计算（铣削）- 修正公式
        # 主切削力 Fc = kc × ap × ae / (齿数) (N)
        # 进给力 Ff = Fc × 系数 (取决于前角和主偏角)
        cutting_force = kc * ap * ae / constraints.tool_teeth  # 主切削力 (N)
        # 进给力系数：前角越大，进给力越小；主偏角越大，进给力越小
        feed_force_coeff = 0.3 + 0.2 * (1.0 - constraints.rake_angle / 20.0) * (90.0 / constraints.main_cutting_angle)
        ff = cutting_force * feed_force_coeff  # 进给力 (N)
        
    elif constraints.machining_method == MachiningMethod.DRILLING:
        q = f * np.pi * constraints.tool_diameter ** 2 / 4000 + 1e-7
        safe_vc = np.maximum(vc, 0.001)
        safe_fz = np.maximum(fz, 0.001)
        lft = (
            constraints.tool_life_coefficient *
            (safe_vc ** constraints.speed_coefficient) *
            (safe_fz ** constraints.feed_coefficient) *
            constraints.wear_coefficient
        )
        h = safe_fz * np.sin(constraints.main_cutting_angle * np.pi / 180)
        kc = constraints.material_coefficient / (h ** constraints.material_slope + 1e-3)
        pmot = q * kc * PhysicalConstants.POWER_WATT_TO_KW / constraints.machine_efficiency
        tnm = pmot * PhysicalConstants.TORQUE_FACTOR / (n + 1e-7)
        ff = 0.63 * safe_fz * constraints.tool_teeth * constraints.tool_diameter * kc / 2
        rz = np.zeros(N)
        
    else:  # BORING
        q = f * np.pi * (constraints.tool_diameter ** 2 - constraints.bottom_hole_diameter ** 2) / 4000 + 1e-7
        safe_vc = np.maximum(vc, 0.001)
        safe_fz = np.maximum(fz, 0.001)
        lft = (
            constraints.tool_life_coefficient *
            (safe_vc ** constraints.speed_coefficient) *
            (safe_fz ** constraints.feed_coefficient) *
            constraints.wear_coefficient
        )
        rx = (safe_fz * constraints.tool_teeth) ** 2 * PhysicalConstants.MILLING_SIDE_ROUGHNESS_FACTOR / constraints.tool_radius
        h = safe_fz * np.sin(constraints.main_cutting_angle * np.pi / 180)
        kc = constraints.material_coefficient / (h ** constraints.material_slope + 1e-3)
        pmot = q * kc * PhysicalConstants.POWER_WATT_TO_KW / constraints.machine_efficiency
        tnm = pmot * PhysicalConstants.TORQUE_FACTOR / (n + 1e-7)
        ff = np.zeros(N)
        rz = np.zeros(N)
    
    # 向量化计算惩罚
    penalty = np.zeros(N)
    
    # 计算违规数量（用于调试）
    violations_count = {
        'power': 0,
        'torque': 0,
        'tool_life': 0,
        'surface_roughness': 0,
        'feed_force': 0,
        'feed_per_tooth': 0,
        'cutting_speed': 0
    }
    
    mask_lft = lft < constraints.min_tool_life
    violations_count['tool_life'] = np.sum(mask_lft)
    penalty[mask_lft] += (constraints.min_tool_life - lft[mask_lft]) ** 2 * ConstraintPenalty.TOOL_LIFE
    
    mask_power = pmot > constraints.max_power
    violations_count['power'] = np.sum(mask_power)
    penalty[mask_power] += (pmot[mask_power] - constraints.max_power) ** 2 * ConstraintPenalty.POWER
    
    mask_torque = tnm > constraints.max_torque
    violations_count['torque'] = np.sum(mask_torque)
    penalty[mask_torque] += (tnm[mask_torque] - constraints.max_torque) ** 2 * ConstraintPenalty.TORQUE
    
    mask_rz = rz > constraints.min_surface_roughness
    violations_count['surface_roughness'] = np.sum(mask_rz)
    penalty[mask_rz] += (rz[mask_rz] - constraints.min_surface_roughness) ** 2 * ConstraintPenalty.SURFACE_ROUGHNESS
    
    mask_ff = ff > constraints.max_feed_force
    violations_count['feed_force'] = np.sum(mask_ff)
    penalty[mask_ff] += (ff[mask_ff] - constraints.max_feed_force) ** 2 * ConstraintPenalty.FEED_FORCE

    # 计算刀具挠度（仅铣削）- 已优化约束检查
    if constraints.machining_method == MachiningMethod.MILLING:
        # 截面惯性矩: I = π * D⁴ / 64 (mm⁴)
        moment_of_inertia = 3.14159 * (constraints.tool_diameter ** 4) / 64.0
        # 挠度: δ = (F * L³) / (3 * E * I)
        # 注意：E的单位是MPa，需要转换为N/mm²，F的单位是N，L的单位是mm
        tool_deflection = (ff * (constraints.tool_overhang_length ** 3)) / (3.0 * constraints.tool_elastic_modulus * moment_of_inertia)
        # 挠度约束检查 - 使用约束中的max_tool_deflection
        mask_deflection = tool_deflection > constraints.max_tool_deflection
        violations_count['tool_deflection'] = np.sum(mask_deflection)
        # 使用较低的惩罚权重，避免过度限制切深
        penalty[mask_deflection] += (tool_deflection[mask_deflection] - constraints.max_tool_deflection) ** 2 * ConstraintPenalty.FEED_FORCE * 0.5

        # 调试：记录挠度参数
        if np.sum(mask_deflection) > 0:
            import logging
            logger = logging.getLogger(__name__)
            max_deflection_idx = np.argmax(tool_deflection)
            logger.warning(f"挠度调试: L={constraints.tool_overhang_length:.1f}mm, E={constraints.tool_elastic_modulus:.0f}MPa, "
                          f"max_deflection={constraints.max_tool_deflection:.3f}mm, "
                          f"ff_max={ff[max_deflection_idx]:.1f}N, deflection_max={tool_deflection[max_deflection_idx]:.3f}mm")

    mask_fz = fz > constraints.max_feed_per_tooth
    violations_count['feed_per_tooth'] = np.sum(mask_fz)
    penalty[mask_fz] += (fz[mask_fz] - constraints.max_feed_per_tooth) ** 2 * ConstraintPenalty.MAX_FEED
    
    mask_vc = vc > constraints.max_cutting_speed
    violations_count['cutting_speed'] = np.sum(mask_vc)
    penalty[mask_vc] += (vc[mask_vc] - constraints.max_cutting_speed) ** 2 * ConstraintPenalty.MAX_SPEED
    
    # 记录违规统计（用于调试）
    total_violations = sum(violations_count.values())
    if total_violations > 0:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"向量化评估: 发现 {total_violations} 个约束违规 - "
                      f"功率:{violations_count['power']}, 扭矩:{violations_count['torque']}, "
                      f"刀具寿命:{violations_count['tool_life']}, 粗糙度:{violations_count['surface_roughness']}, "
                      f"进给力:{violations_count['feed_force']}, 每齿进给:{violations_count['feed_per_tooth']}, "
                      f"线速度:{violations_count['cutting_speed']}, 刀具挠度:{violations_count.get('tool_deflection', 0)}")

        # 调试：记录最优个体的关键参数（仅当存在违反功率/扭矩约束时）
        if violations_count['power'] > 0 or violations_count['torque'] > 0:
            best_idx = np.argmin(penalty)
            logger.warning(f"调试 - 最优个体: n={n[best_idx]:.1f}, f={f[best_idx]:.1f}, ap={ap[best_idx]:.2f}, ae={ae:.2f}")
            logger.warning(f"调试 - 物理参数: hm={hm[best_idx]:.4f}, kc={kc[best_idx]:.1f}, q={q[best_idx]:.2f}, pmot={pmot[best_idx]:.2f}, tnm={tnm[best_idx]:.2f}")
            logger.warning(f"调试 - 约束: 最大功率={constraints.max_power}, 最大扭矩={constraints.max_torque}, 刀具直径={constraints.tool_diameter}")
            if constraints.machining_method == MachiningMethod.MILLING:
                ae_ratio = ae / constraints.tool_diameter
                ratio = np.clip((ae - 0.5 * constraints.tool_diameter) / (0.5 * constraints.tool_diameter), -1, 1)
                fs = 90 + np.arcsin(ratio) * 180 / np.pi
                logger.warning(f"调试 - ae_ratio={ae_ratio:.4f}, fs={fs:.2f}")
    
    fitnesses = q - 1e29 * penalty
    
    return fitnesses


def evaluate_batch(args: Tuple[np.ndarray, int, Any]) -> Tuple[int, np.ndarray, float]:
    """
    批量评估适应度（用于并行化）

    Args:
        args: (individual, idx, constraints, objective_func_data)

    Returns:
        (idx, individual, fitness)
    """
    individual, idx, constraints_dict = args

    # 从字典重建约束对象
    constraints = OptimizationConstraints(**constraints_dict)

    # 转换 DNA 到参数
    speed_bound = (0, 8000)
    feed_bound = (0, 8000)
    cut_depth_bound = (0.0, 1.0)

    # 解码参数（使用正确的位范围，从高位到低位）
    speed_bits = individual[:16]
    feed_bits = individual[16:29]
    cut_depth_bits = individual[29:]

    # 使用加权求和方式：bit[i] * 2^(n-1-i)
    # 注意：需要先转换为int类型，否则uint8会溢出
    speed_val = sum(int(bit) * (2 ** (len(speed_bits) - 1 - i)) for i, bit in enumerate(speed_bits)) / (2**16 - 1)
    speed = speed_val * speed_bound[1]  # 旧版本直接乘以边界上限

    feed_val = sum(int(bit) * (2 ** (len(feed_bits) - 1 - i)) for i, bit in enumerate(feed_bits)) / (2**13 - 1)
    feed = feed_val * feed_bound[1]  # 旧版本直接乘以边界上限

    cut_depth_val = sum(int(bit) * (2 ** (len(cut_depth_bits) - 1 - i)) for i, bit in enumerate(cut_depth_bits)) / (2**7 - 1)
    cut_depth = cut_depth_val * cut_depth_bound[1]  # 旧版本直接乘以边界上限

    params = {"speed": speed, "feed": feed, "cut_depth": cut_depth}
    
    # 计算加工参数
    n = speed
    f = feed
    ap = cut_depth  # 修复：cut_depth 已经是实际切深，不需要再乘
    ae = constraints.cut_width
    
    # 参数边界检查：确保最小转速和进给
    n = max(n, 1.0)  # 最小转速 1 rpm
    f = max(f, 0.1)  # 最小进给 0.1 mm/min
    
    # 每齿进给量
    fz = f / (constraints.tool_teeth * n)
    
    # 切削速度
    vc = (n * constraints.tool_diameter) / 318.0 + 0.1  # 与旧版本保持一致
    
    # 根据加工方法计算参数
    if constraints.machining_method == MachiningMethod.MILLING:
        # 铣削
        q = f * ap * ae / 1000 + 1e-7
        # 避免 0 的负幂次方
        safe_vc = max(vc, 0.001)
        safe_fz = max(fz, 0.001)
        lft = (
            constraints.tool_life_coefficient *
            (safe_vc ** constraints.speed_coefficient) *
            (safe_fz ** constraints.feed_coefficient) *
            constraints.wear_coefficient
        )
        rz = PhysicalConstants.MILLING_ROUGHNESS_FACTOR * (safe_fz ** 2) / constraints.tool_diameter
        rx = (safe_fz * constraints.tool_teeth) ** 2 * PhysicalConstants.MILLING_SIDE_ROUGHNESS_FACTOR / constraints.tool_diameter
        
        if ae / constraints.tool_diameter <= 0.3:
            hm = safe_fz * (ae / constraints.tool_diameter) ** 0.5
        else:
            ratio = min(1.0, max(-1.0, (ae - 0.5 * constraints.tool_diameter) / (0.5 * constraints.tool_diameter)))
            fs = 90 + math.asin(ratio) * 180 * math.pi
            hm = 1147 * safe_fz * math.sin(constraints.main_cutting_angle * math.pi / 180) * (ae / constraints.tool_diameter) / fs
        
        kc = (1 - 0.01 * constraints.rake_angle) * constraints.material_coefficient / (hm ** constraints.material_slope + 1e-3)
        pmot = q * kc * PhysicalConstants.POWER_WATT_TO_KW / constraints.machine_efficiency
        tnm = pmot * PhysicalConstants.TORQUE_FACTOR / n
        ff = 0.0
        
    elif constraints.machining_method == MachiningMethod.DRILLING:
        # 钻孔
        q = f * math.pi * constraints.tool_diameter ** 2 / 4000 + 1e-7
        # 避免 0 的负幂次方
        safe_vc = max(vc, 0.001)
        safe_fz = max(fz, 0.001)
        lft = (
            constraints.tool_life_coefficient *
            (safe_vc ** constraints.speed_coefficient) *
            (safe_fz ** constraints.feed_coefficient) *
            constraints.wear_coefficient
        )
        h = safe_fz * math.sin(constraints.main_cutting_angle * math.pi / 180)
        kc = constraints.material_coefficient / (h ** constraints.material_slope + 1e-3)
        pmot = q * kc * PhysicalConstants.POWER_WATT_TO_KW / constraints.machine_efficiency
        tnm = pmot * PhysicalConstants.TORQUE_FACTOR / n
        ff = 0.63 * safe_fz * constraints.tool_teeth * constraints.tool_diameter * kc / 2
        rz = 0.0
        rx = 0.0
        
    else:  # BORING
        # 镗孔
        q = f * math.pi * (constraints.tool_diameter ** 2 - constraints.bottom_hole_diameter ** 2) / 4000 + 1e-7
        # 避免 0 的负幂次方
        safe_vc = max(vc, 0.001)
        safe_fz = max(fz, 0.001)
        lft = (
            constraints.tool_life_coefficient *
            (safe_vc ** constraints.speed_coefficient) *
            (safe_fz ** constraints.feed_coefficient) *
            constraints.wear_coefficient
        )
        rx = (safe_fz * constraints.tool_teeth) ** 2 * PhysicalConstants.MILLING_SIDE_ROUGHNESS_FACTOR / constraints.tool_radius
        h = safe_fz * math.sin(constraints.main_cutting_angle * math.pi / 180)
        kc = constraints.material_coefficient / (h ** constraints.material_slope + 1e-3)
        pmot = q * kc * PhysicalConstants.POWER_WATT_TO_KW / constraints.machine_efficiency
        tnm = pmot * PhysicalConstants.TORQUE_FACTOR / n
        ff = 0.0
        rz = 0.0
    
    # 计算适应度
    fitness = q
    
    # 约束惩罚
    penalty = 0.0
    
    if lft < constraints.min_tool_life:
        penalty += (constraints.min_tool_life - lft) ** 2 * ConstraintPenalty.TOOL_LIFE
    
    if pmot > constraints.max_power:
        penalty += (pmot - constraints.max_power) ** 2 * ConstraintPenalty.POWER
    
    if tnm > constraints.max_torque:
        penalty += (tnm - constraints.max_torque) ** 2 * ConstraintPenalty.TORQUE
    
    if rz > constraints.min_surface_roughness:
        penalty += (rz - constraints.min_surface_roughness) ** 2 * ConstraintPenalty.SURFACE_ROUGHNESS
    
    if ff > constraints.max_feed_force:
        penalty += (ff - constraints.max_feed_force) ** 2 * ConstraintPenalty.FEED_FORCE
    
    if fz > constraints.max_feed_per_tooth:
        penalty += (fz - constraints.max_feed_per_tooth) ** 2 * ConstraintPenalty.MAX_FEED
    
    if vc > constraints.max_cutting_speed:
        penalty += (vc - constraints.max_cutting_speed) ** 2 * ConstraintPenalty.MAX_SPEED
    
    fitness = q - 1e29 * penalty
    
    return idx, individual, fitness


class MicrobialGeneticAlgorithm:
    """微生物遗传算法（优化版）"""

    def __init__(
        self,
        config: GAConfig,
        constraints: OptimizationConstraints,
        objective_func: Callable = None
    ):
        """
        初始化遗传算法
        
        Args:
            config: 算法配置
            constraints: 约束条件
            objective_func: 目标函数（默认使用内置目标函数）
        """
        self.config = config
        self.constraints = constraints
        self.objective_func = objective_func or self._default_objective
        self.population = self._initialize_population()
        self.best_individual = None
        self.best_fitness = float('-inf')
        self.stagnation_count = 0
        
        # 约束字典（用于并行化）
        self.constraints_dict = {
            'min_tool_life': constraints.min_tool_life,
            'max_power': constraints.max_power,
            'max_torque': constraints.max_torque,
            'max_feed_force': constraints.max_feed_force,
            'min_surface_roughness': constraints.min_surface_roughness,
            'tool_diameter': constraints.tool_diameter,
            'tool_teeth': constraints.tool_teeth,
            'tool_radius': constraints.tool_radius,
            'main_cutting_angle': constraints.main_cutting_angle,
            'rake_angle': constraints.rake_angle,
            'cut_width': constraints.cut_width,
            'bottom_hole_diameter': constraints.bottom_hole_diameter,
            'turning_diameter': constraints.turning_diameter,
            'tool_life_coefficient': constraints.tool_life_coefficient,
            'speed_coefficient': constraints.speed_coefficient,
            'feed_coefficient': constraints.feed_coefficient,
            'cut_depth_coefficient': constraints.cut_depth_coefficient,
            'material_coefficient': constraints.material_coefficient,
            'material_slope': constraints.material_slope,
            'machine_efficiency': constraints.machine_efficiency,
            'machining_method': constraints.machining_method,
            'wear_coefficient': constraints.wear_coefficient,
            'max_feed_per_tooth': constraints.max_feed_per_tooth,
            'max_cutting_speed': constraints.max_cutting_speed,
            'max_cut_depth': constraints.max_cut_depth,
        }
        
        # 确定工作进程数
        if self.config.enable_parallel:
            self.n_workers = self.config.n_workers or min(mp.cpu_count(), 8)
        else:
            self.n_workers = 1

    def _initialize_population(self) -> np.ndarray:
        """初始化种群"""
        return np.random.randint(0, 2, (self.config.population_size, self.config.dna_size), dtype=np.uint8)

    def _translate_dna(self, dna: np.ndarray) -> Dict[str, float]:
        """
        将 DNA 转换为参数
        
        Args:
            dna: DNA 序列
            
        Returns:
            参数字典 {speed, feed, cut_depth}
        """
        speed_bits = dna[:16]
        feed_bits = dna[16:29]
        cut_depth_bits = dna[29:]

        # 从高位到低位解码（与旧版本保持一致）
        # 使用加权求和方式：bit[i] * 2^(n-1-i)
        # 注意：需要先转换为int类型，否则uint8会溢出
        speed_val = sum(int(bit) * (2 ** (len(speed_bits) - 1 - i)) for i, bit in enumerate(speed_bits)) / (2**16 - 1)
        speed = speed_val * self.config.speed_bound[1]  # 旧版本直接乘以边界上限

        feed_val = sum(int(bit) * (2 ** (len(feed_bits) - 1 - i)) for i, bit in enumerate(feed_bits)) / (2**13 - 1)
        feed = feed_val * self.config.feed_bound[1]  # 旧版本直接乘以边界上限

        cut_depth_val = sum(int(bit) * (2 ** (len(cut_depth_bits) - 1 - i)) for i, bit in enumerate(cut_depth_bits)) / (2**7 - 1)
        # 修复：使用约束对象的最大切深，而不是config的边界上限
        cut_depth = cut_depth_val * self.constraints.max_cut_depth

        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"调试 - _translate_dna: speed={speed:.1f}, feed={feed:.1f}, cut_depth={cut_depth:.2f}")
        logger.warning(f"调试 - _translate_dna边界: cut_depth_bound={self.config.cut_depth_bound}, max_cut_depth={self.constraints.max_cut_depth}")

        return {"speed": speed, "feed": feed, "cut_depth": cut_depth}

    def _calculate_machining_parameters(self, params: Dict[str, float]) -> Dict[str, float]:
        """
        计算加工参数
        
        Args:
            params: 基本参数 {speed, feed, cut_depth}
            
        Returns:
            加工参数字典
        """
        n = params["speed"]
        f = params["feed"]
        ap = params["cut_depth"]  # 修复：params["cut_depth"] 已经是实际切深，不需要再乘
        ae = self.constraints.cut_width
        
        # 每齿进给量
        fz = f / (self.constraints.tool_teeth * n) if n > 0 else 0
        
        # 切削速度
        vc = (n * self.constraints.tool_diameter) / 318.0 + 0.1 if n > 0 else 0  # 与旧版本保持一致
        
        # 根据加工方法计算参数
        if self.constraints.machining_method == MachiningMethod.MILLING:
            return self._calculate_milling_parameters(n, f, ap, ae, vc, fz)
        elif self.constraints.machining_method == MachiningMethod.DRILLING:
            return self._calculate_drilling_parameters(n, f, vc, fz)
        else:  # BORING
            return self._calculate_boring_parameters(n, f, ap, ae, vc, fz)

    def _calculate_milling_parameters(
        self, n: float, f: float, ap: float, ae: float, vc: float, fz: float
    ) -> Dict[str, float]:
        """计算铣削参数"""
        # 材料去除率
        q = f * ap * ae / 1000 + 1e-7
        
        # 刀具寿命
        lft = (
            self.constraints.tool_life_coefficient *
            (vc ** self.constraints.speed_coefficient) *
            (fz ** self.constraints.feed_coefficient) *
            self.constraints.wear_coefficient
        )
        
        # 表面粗糙度
        rz = PhysicalConstants.MILLING_ROUGHNESS_FACTOR * (fz ** 2) / self.constraints.tool_diameter
        rx = (fz * self.constraints.tool_teeth) ** 2 * PhysicalConstants.MILLING_SIDE_ROUGHNESS_FACTOR / self.constraints.tool_diameter
        
        # 平均切屑厚度
        if ae / self.constraints.tool_diameter <= 0.3:
            hm = fz * (ae / self.constraints.tool_diameter) ** 0.5
        else:
            # 确保 asin 的输入在有效范围内 [-1, 1]
            ratio = min(1.0, max(-1.0, (ae - 0.5 * self.constraints.tool_diameter) / (0.5 * self.constraints.tool_diameter)))
            # 修复：fs 应该是角度（度），不是弧度
            fs = 90 + math.asin(ratio) * 180 / math.pi
            hm = 1147 * fz * math.sin(self.constraints.main_cutting_angle * math.pi / 180) * (ae / self.constraints.tool_diameter) / fs
        
        # 单位切削力
        kc = (1 - 0.01 * self.constraints.rake_angle) * self.constraints.material_coefficient / (hm ** self.constraints.material_slope + 1e-3)
        
        # 功率和扭矩（瓦尔特功率计算公式）
        # pmot = Q * kc / 60000 / machine_efficiency (Kw)
        # 备用：山德威克功率计算公式（Sandvik Power Formula）
        # pmot = AE * ap * f * KC11 / 60037200 / machine_efficiency (Kw)
        pmot = q * kc * PhysicalConstants.POWER_WATT_TO_KW / self.constraints.machine_efficiency
        tnm = pmot * PhysicalConstants.TORQUE_FACTOR / (n + 1e-7)

        # 进给力计算（铣削）- 修正公式
        # 主切削力 Fc = kc × ap × ae / (齿数) (N)
        # 进给力 Ff = Fc × 系数 (取决于前角和主偏角)
        cutting_force = kc * ap * ae / self.constraints.tool_teeth  # 主切削力 (N)
        # 进给力系数：前角越大，进给力越小；主偏角越大，进给力越小
        feed_force_coeff = 0.3 + 0.2 * (1.0 - self.constraints.rake_angle / 20.0) * (90.0 / self.constraints.main_cutting_angle)
        ff = cutting_force * feed_force_coeff  # 进给力 (N)

        # 刀具挠度计算（悬臂梁模型）
        # 截面惯性矩: I = π * D⁴ / 64
        moment_of_inertia = 3.14159 * (self.constraints.tool_diameter ** 4) / 64.0
        # 挠度: δ = (F * L³) / (3 * E * I)
        tool_deflection = (ff * (self.constraints.tool_overhang_length ** 3)) / (3.0 * self.constraints.tool_elastic_modulus * moment_of_inertia)

        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"调试 - _calculate_milling_parameters返回: n={n:.1f}, f={f:.1f}, ap={ap:.2f}, ae={ae:.2f}")
        logger.warning(f"调试 - _calculate_milling_parameters物理: hm={hm:.4f}, kc={kc:.1f}, q={q:.2f}, pmot={pmot:.2f}, tnm={tnm:.2f}, ff={ff:.1f}, deflection={tool_deflection:.4f}")

        return {
            "speed": n,
            "feed": f,
            "cut_depth": ap,
            "cut_width": ae,
            "material_removal_rate": q,
            "tool_life": lft,
            "bottom_roughness": rz,
            "side_roughness": rx,
            "power": pmot,
            "torque": tnm,
            "feed_force": ff,
            "feed_per_tooth": fz,
            "cutting_speed": vc,
            "tool_deflection": tool_deflection,
        }

    def _calculate_drilling_parameters(
        self, n: float, f: float, vc: float, fz: float
    ) -> Dict[str, float]:
        """计算钻孔参数"""
        # 材料去除率
        q = f * math.pi * self.constraints.tool_diameter ** 2 / 4000 + 1e-7
        
        # 刀具寿命
        lft = (
            self.constraints.tool_life_coefficient *
            (vc ** self.constraints.speed_coefficient) *
            (fz ** self.constraints.feed_coefficient) *
            self.constraints.wear_coefficient
        )
        
        # 平均切屑厚度
        h = fz * math.sin(self.constraints.main_cutting_angle * math.pi / 180)
        
        # 单位切削力
        kc = self.constraints.material_coefficient / (h ** self.constraints.material_slope + 1e-3)
        
        # 功率和扭矩
        pmot = q * kc * PhysicalConstants.POWER_WATT_TO_KW / self.constraints.machine_efficiency
        tnm = pmot * PhysicalConstants.TORQUE_FACTOR / (n + 1e-7)
        
        # 进给力
        ff = 0.63 * fz * self.constraints.tool_teeth * self.constraints.tool_diameter * kc / 2
        
        return {
            "speed": n,
            "feed": f,
            "cut_depth": 0.0,
            "cut_width": 0.0,
            "material_removal_rate": q,
            "tool_life": lft,
            "bottom_roughness": 0.0,
            "side_roughness": 0.0,
            "power": pmot,
            "torque": tnm,
            "feed_force": ff,
            "feed_per_tooth": fz,
            "cutting_speed": vc,
        }

    def _calculate_boring_parameters(
        self, n: float, f: float, ap: float, ae: float, vc: float, fz: float
    ) -> Dict[str, float]:
        """计算镗孔参数"""
        # 材料去除率
        q = f * math.pi * (self.constraints.tool_diameter ** 2 - self.constraints.bottom_hole_diameter ** 2) / 4000 + 1e-7
        
        # 刀具寿命
        lft = (
            self.constraints.tool_life_coefficient *
            (vc ** self.constraints.speed_coefficient) *
            (fz ** self.constraints.feed_coefficient) *
            self.constraints.wear_coefficient
        )
        
        # 表面粗糙度
        rx = (fz * self.constraints.tool_teeth) ** 2 * PhysicalConstants.MILLING_SIDE_ROUGHNESS_FACTOR / self.constraints.tool_radius
        
        # 平均切屑厚度
        h = fz * math.sin(self.constraints.main_cutting_angle * math.pi / 180) + 1e-7
        
        # 单位切削力
        kc = self.constraints.material_coefficient / (h ** self.constraints.material_slope + 1e-7)
        
        # 功率和扭矩（瓦尔特功率计算公式）
        pmot = q * kc * PhysicalConstants.POWER_WATT_TO_KW / self.constraints.machine_efficiency
        tnm = pmot * PhysicalConstants.TORQUE_FACTOR / (n + 1e-7)
        
        # 进给力计算（镗孔）- 参照旧版公式
        # 进给力与钻孔类似，但受底孔直径影响（切削面积减小）
        ff = 0.63 * fz * self.constraints.tool_teeth * (self.constraints.tool_diameter - self.constraints.bottom_hole_diameter) * kc / 2
        
        return {
            "speed": n,
            "feed": f,
            "cut_depth": ap,
            "cut_width": ae,
            "material_removal_rate": q,
            "tool_life": lft,
            "bottom_roughness": 0.0,
            "side_roughness": rx,
            "power": pmot,
            "torque": tnm,
            "feed_force": ff,
            "feed_per_tooth": fz,
            "cutting_speed": vc,
        }

    def _default_objective(self, params: Dict[str, float]) -> float:
        """
        默认目标函数
        最大化材料去除率，同时满足约束条件
        
        Args:
            params: 基本参数 {speed, feed, cut_depth}
            
        Returns:
            适应度值
        """
        # 计算加工参数
        machining_params = self._calculate_machining_parameters(params)
        
        # 目标：最大化材料去除率
        q = machining_params["material_removal_rate"]
        
        # 约束惩罚
        penalty = 0.0
        
        # 刀具寿命约束
        lft = machining_params["tool_life"]
        if lft < self.constraints.min_tool_life:
            penalty += (self.constraints.min_tool_life - lft) ** 2 * ConstraintPenalty.TOOL_LIFE
        
        # 功率约束
        power = machining_params["power"]
        if power > self.constraints.max_power:
            penalty += (power - self.constraints.max_power) ** 2 * ConstraintPenalty.POWER
        
        # 扭矩约束
        torque = machining_params["torque"]
        if torque > self.constraints.max_torque:
            penalty += (torque - self.constraints.max_torque) ** 2 * ConstraintPenalty.TORQUE
        
        # 表面粗糙度约束
        rz = machining_params["bottom_roughness"]
        if rz > self.constraints.min_surface_roughness:
            penalty += (rz - self.constraints.min_surface_roughness) ** 2 * ConstraintPenalty.SURFACE_ROUGHNESS
        
        # 进给力约束
        ff = machining_params["feed_force"]
        if ff > self.constraints.max_feed_force:
            penalty += (ff - self.constraints.max_feed_force) ** 2 * ConstraintPenalty.FEED_FORCE
        
        # 单位面积进给力约束（钻孔专用）
        # 防止钻头折断，限制单位面积进给力不超过 50 MPa
        if self.constraints.machining_method == MachiningMethod.DRILLING:
            unit_area_force = ff / ((self.constraints.tool_diameter / 2) ** 2) / 3.14
            if unit_area_force > 50:
                penalty += (unit_area_force - 50) ** 2 * ConstraintPenalty.FEED_FORCE
        
        # 每齿进给量约束
        fz = machining_params["feed_per_tooth"]
        if fz > self.constraints.max_feed_per_tooth:
            penalty += (fz - self.constraints.max_feed_per_tooth) ** 2 * ConstraintPenalty.MAX_FEED
        
        # 线速度约束
        vc = machining_params["cutting_speed"]
        if vc > self.constraints.max_cutting_speed:
            penalty += (vc - self.constraints.max_cutting_speed) ** 2 * ConstraintPenalty.MAX_SPEED
        
        # 目标函数：材料去除率减去惩罚
        fitness = q - 1e29 * penalty
        
        return fitness

    def _crossover(self, loser: np.ndarray, winner: np.ndarray) -> np.ndarray:
        """
        交叉操作
        
        Args:
            loser: 输者的 DNA
            winner: 赢者的 DNA
            
        Returns:
            交叉后的 DNA
        """
        crossover_mask = np.random.rand(self.config.dna_size) < self.config.crossover_rate
        loser[crossover_mask] = winner[crossover_mask]
        return loser

    def _mutate(self, individual: np.ndarray) -> np.ndarray:
        """
        变异操作
        
        Args:
            individual: 个体 DNA
            
        Returns:
            变异后的 DNA
        """
        mutation_mask = np.random.rand(self.config.dna_size) < self.config.mutation_rate
        individual[mutation_mask] = ~individual[mutation_mask]
        return individual

    def evolve(self, iterations_per_generation: int = 384) -> Tuple[Dict[str, float], float]:
        """
        执行进化（优化版：并行化 + 早停 + 自适应参数）
        
        Args:
            iterations_per_generation: 每代迭代次数
            
        Returns:
            (最优参数, 最优适应度)
        """
        import traceback
        best_fitness_history = []
        convergence_threshold = 1e-6  # 收敛阈值
        
        try:
            for generation in range(self.config.generations):
                # 自适应参数调整
                if self.config.adaptive_rate:
                    # 根据收敛进度调整交叉率和变异率
                    progress = generation / self.config.generations
                    self.config.crossover_rate = 0.6 * (1 - progress * 0.3)  # 逐渐降低
                    self.config.mutation_rate = 0.3 * (1 - progress * 0.2)  # 逐渐降低
                
                # 分批处理种群（减少内存使用）
                batch_start = 0
                while batch_start < self.config.population_size:
                    batch_end = min(batch_start + self.config.batch_size, self.config.population_size)
                    batch_population = self.population[batch_start:batch_end]
                    
                    # 向量化评估批量中的个体（避免进程池开销）
                    fitnesses = self._parallel_evaluate(batch_population)
                    
                    # 对批量内的个体进行微生物操作
                    for i in range(0, len(fitnesses), 2):
                        if i + 1 >= len(fitnesses):
                            break
                        
                        idx1, ind1, fit1 = fitnesses[i]
                        idx2, ind2, fit2 = fitnesses[i + 1]
                        
                        # 确定输赢
                        if fit1 < fit2:
                            loser, winner = ind1.copy(), ind2
                            loser_idx, winner_idx = idx1, idx2
                            winner_fit = fit2
                        else:
                            loser, winner = ind2.copy(), ind1
                            loser_idx, winner_idx = idx2, idx1
                            winner_fit = fit1
                        
                        # 对输者进行交叉和变异
                        loser = self._crossover(loser, winner)
                        loser = self._mutate(loser)
                        
                        # 更新种群
                        actual_idx = batch_start + loser_idx
                        self.population[actual_idx] = loser
                        
                        # 跟踪最优个体
                        if winner_fit > self.best_fitness:
                            self.best_fitness = winner_fit
                            self.best_individual = winner.copy()
                            self.stagnation_count = 0
                    
                    batch_start = batch_end
                
                # 检查早停条件
                if len(best_fitness_history) > 0:
                    improvement = abs(self.best_fitness - best_fitness_history[-1])
                    if improvement < convergence_threshold:
                        self.stagnation_count += 1
                    else:
                        self.stagnation_count = 0
                
                best_fitness_history.append(self.best_fitness)
                
                # 早停检查
                if self.stagnation_count >= self.config.early_stop_generations:
                    print(f"Early stop at generation {generation} (no improvement for {self.stagnation_count} generations)")
                    break

                if generation % 10 == 0:
                    print(f"Generation {generation}: Best fitness = {self.best_fitness:.6f}, Population size = {self.config.population_size}")

            # 获取最优参数
            best_params = self._translate_dna(self.best_individual)
            best_machining_params = self._calculate_machining_parameters(best_params)

            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"调试 - 最终返回: pmot={best_machining_params['power']:.2f}, tnm={best_machining_params['torque']:.2f}")
            logger.warning(f"调试 - 最终参数: n={best_machining_params['speed']:.1f}, f={best_machining_params['feed']:.1f}, ap={best_machining_params['cut_depth']:.2f}")

            return best_machining_params, self.best_fitness

        except Exception as e:
            error_msg = f"Evolution error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            print(error_msg)
            raise Exception(error_msg)

    def _parallel_evaluate(self, population: np.ndarray) -> List[Tuple[int, np.ndarray, float]]:
        """
        向量化评估种群适应度（替代进程池，避免开销）
        
        Args:
            population: 种群
            
        Returns:
            [(idx, individual, fitness), ...]
        """
        results = []
        
        # 使用向量化计算（比进程池快10倍以上）
        fitnesses = evaluate_vectorized(population, self.constraints_dict)
        
        for i, individual in enumerate(population):
            results.append((i, individual, fitnesses[i]))
        
        return results

    def _serial_evaluate(self, population: np.ndarray) -> List[Tuple[int, np.ndarray, float]]:
        """
        串行评估种群适应度（使用向量化）
        
        Args:
            population: 种群
            
        Returns:
            [(idx, individual, fitness), ...]
        """
        results = []
        
        # 使用向量化计算
        fitnesses = evaluate_vectorized(population, self.constraints_dict)
        
        for i, individual in enumerate(population):
            results.append((i, individual, fitnesses[i]))
        
        return results