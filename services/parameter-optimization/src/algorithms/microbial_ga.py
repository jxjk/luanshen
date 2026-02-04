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
    
    # 最大参数限制
    max_feed_per_tooth: float = 0.15
    max_cutting_speed: float = 120.0
    max_cut_depth: float = 0.68


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
    cut_depth = cut_depth_vals * 1.0  # 旧版本：直接乘以 1.0
    
    # 参数边界检查
    n = np.maximum(speed, 1.0)
    f = np.maximum(feed, 0.1)
    ap = cut_depth * constraints.max_cut_depth
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
        ff = np.zeros(N)
        
        # ae_ratio是标量，直接使用
        ae_ratio = ae / constraints.tool_diameter
        
        # 根据ae_ratio的值选择计算方法
        if ae_ratio <= 0.3:
            hm = safe_fz * np.sqrt(ae_ratio)
        else:
            # 确保asin输入在有效范围内
            ratio = np.clip((ae - 0.5 * constraints.tool_diameter) / (0.5 * constraints.tool_diameter), -1, 1)
            fs = 90 + np.arcsin(ratio) * 180 * np.pi
            hm = 1147 * safe_fz * np.sin(constraints.main_cutting_angle * np.pi / 180) * ae_ratio / fs
        
        kc = (1 - 0.01 * constraints.rake_angle) * constraints.material_coefficient / (hm ** constraints.material_slope + 1e-3)
        pmot = q * kc * PhysicalConstants.POWER_WATT_TO_KW / constraints.machine_efficiency
        tnm = pmot * PhysicalConstants.TORQUE_FACTOR / (n + 1e-7)
        
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
    
    mask_lft = lft < constraints.min_tool_life
    penalty[mask_lft] += (constraints.min_tool_life - lft[mask_lft]) ** 2 * ConstraintPenalty.TOOL_LIFE
    
    mask_power = pmot > constraints.max_power
    penalty[mask_power] += (pmot[mask_power] - constraints.max_power) ** 2 * ConstraintPenalty.POWER
    
    mask_torque = tnm > constraints.max_torque
    penalty[mask_torque] += (tnm[mask_torque] - constraints.max_torque) ** 2 * ConstraintPenalty.TORQUE
    
    mask_rz = rz > constraints.min_surface_roughness
    penalty[mask_rz] += (rz[mask_rz] - constraints.min_surface_roughness) ** 2 * ConstraintPenalty.SURFACE_ROUGHNESS
    
    mask_ff = ff > constraints.max_feed_force
    penalty[mask_ff] += (ff[mask_ff] - constraints.max_feed_force) ** 2 * ConstraintPenalty.FEED_FORCE
    
    mask_fz = fz > constraints.max_feed_per_tooth
    penalty[mask_fz] += (fz[mask_fz] - constraints.max_feed_per_tooth) ** 2
    
    mask_vc = vc > constraints.max_cutting_speed
    penalty[mask_vc] += (vc[mask_vc] - constraints.max_cutting_speed) ** 2
    
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
    ap = cut_depth * constraints.max_cut_depth
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
        penalty += (fz - constraints.max_feed_per_tooth) ** 2
    
    if vc > constraints.max_cutting_speed:
        penalty += (vc - constraints.max_cutting_speed) ** 2
    
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
        cut_depth = cut_depth_val * self.config.cut_depth_bound[1]  # 旧版本直接乘以边界上限

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
        ap = params["cut_depth"] * self.constraints.max_cut_depth
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
            fs = 90 + math.asin(ratio) * 180 * math.pi
            hm = 1147 * fz * math.sin(self.constraints.main_cutting_angle * math.pi / 180) * (ae / self.constraints.tool_diameter) / fs
        
        # 单位切削力
        kc = (1 - 0.01 * self.constraints.rake_angle) * self.constraints.material_coefficient / (hm ** self.constraints.material_slope + 1e-3)
        
        # 功率和扭矩
        pmot = q * kc * PhysicalConstants.POWER_WATT_TO_KW / self.constraints.machine_efficiency
        tnm = pmot * PhysicalConstants.TORQUE_FACTOR / (n + 1e-7)
        
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
            "feed_force": 0.0,
            "feed_per_tooth": fz,
            "cutting_speed": vc,
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
        
        # 功率和扭矩
        pmot = q * kc * PhysicalConstants.POWER_WATT_TO_KW / self.constraints.machine_efficiency
        tnm = pmot * PhysicalConstants.TORQUE_FACTOR / (n + 1e-7)
        
        # 进给力
        ff = 0.0
        
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
        
        # 每齿进给量约束
        fz = machining_params["feed_per_tooth"]
        if fz > self.constraints.max_feed_per_tooth:
            penalty += (fz - self.constraints.max_feed_per_tooth) ** 2
        
        # 线速度约束
        vc = machining_params["cutting_speed"]
        if vc > self.constraints.max_cutting_speed:
            penalty += (vc - self.constraints.max_cutting_speed) ** 2
        
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