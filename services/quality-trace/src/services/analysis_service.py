"""
质量追溯分析服务
"""
from typing import List, Dict, Any
import numpy as np
from loguru import logger


class AnalysisService:
    """分析服务"""
    
    @staticmethod
    def detect_anomalies(
        data: List[float],
        threshold: float = None,
        method: str = "std"
    ) -> List[Dict[str, Any]]:
        """
        检测异常值
        
        Args:
            data: 数据列表
            threshold: 阈值
            method: 检测方法 (std, iqr, zscore)
        
        Returns:
            异常值列表
        """
        if not data or len(data) < 3:
            return []
        
        anomalies = []
        data_array = np.array(data)
        
        if method == "std":
            # 标准差方法
            mean = np.mean(data_array)
            std = np.std(data_array)
            
            if threshold is None:
                threshold = 3 * std  # 3倍标准差
            
            for i, value in enumerate(data):
                if abs(value - mean) > threshold:
                    anomalies.append({
                        "index": i,
                        "value": value,
                        "type": "outlier",
                        "threshold": threshold
                    })
        
        elif method == "iqr":
            # IQR方法
            q1 = np.percentile(data_array, 25)
            q3 = np.percentile(data_array, 75)
            iqr = q3 - q1
            
            if threshold is None:
                threshold = 1.5 * iqr
            
            lower_bound = q1 - threshold
            upper_bound = q3 + threshold
            
            for i, value in enumerate(data):
                if value < lower_bound or value > upper_bound:
                    anomalies.append({
                        "index": i,
                        "value": value,
                        "type": "outlier",
                        "bounds": (lower_bound, upper_bound)
                    })
        
        elif method == "zscore":
            # Z-score方法
            mean = np.mean(data_array)
            std = np.std(data_array)
            
            if threshold is None:
                threshold = 3  # Z-score阈值
            
            for i, value in enumerate(data):
                zscore = (value - mean) / std if std > 0 else 0
                if abs(zscore) > threshold:
                    anomalies.append({
                        "index": i,
                        "value": value,
                        "type": "outlier",
                        "zscore": zscore
                    })
        
        return anomalies
    
    @staticmethod
    def calculate_correlation(
        x: List[float],
        y: List[float]
    ) -> float:
        """
        计算相关系数
        
        Args:
            x: 数据列表1
            y: 数据列表2
        
        Returns:
            相关系数
        """
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        try:
            return float(np.corrcoef(x, y)[0, 1])
        except:
            return 0.0
    
    @staticmethod
    def calculate_trend(data: List[float]) -> Dict[str, Any]:
        """
        计算趋势
        
        Args:
            data: 数据列表
        
        Returns:
            趋势信息
        """
        if not data or len(data) < 2:
            return {"trend": "unknown", "slope": 0.0}
        
        # 线性回归计算趋势
        x = np.arange(len(data))
        y = np.array(data)
        
        try:
            slope, intercept = np.polyfit(x, y, 1)
            
            if abs(slope) < 0.01:
                trend = "stable"
            elif slope > 0:
                trend = "increasing"
            else:
                trend = "decreasing"
            
            return {
                "trend": trend,
                "slope": float(slope),
                "intercept": float(intercept)
            }
        except:
            return {"trend": "unknown", "slope": 0.0}
    
    @staticmethod
    def analyze_parameter_correlation(
        parameter_data: Dict[str, List[float]]
    ) -> Dict[str, Dict[str, float]]:
        """
        分析参数之间的相关性
        
        Args:
            parameter_data: 参数数据字典 {参数名: [值列表]}
        
        Returns:
            相关系数矩阵
        """
        correlations = {}
        param_names = list(parameter_data.keys())
        
        for i, name1 in enumerate(param_names):
            correlations[name1] = {}
            for name2 in param_names:
                if name1 == name2:
                    correlations[name1][name2] = 1.0
                else:
                    correlations[name1][name2] = AnalysisService.calculate_correlation(
                        parameter_data[name1],
                        parameter_data[name2]
                    )
        
        return correlations
    
    @staticmethod
    def generate_insights(
        parameter_data: Dict[str, List[float]],
        anomalies: Dict[str, List[Dict[str, Any]]]
    ) -> List[str]:
        """
        生成分析洞察
        
        Args:
            parameter_data: 参数数据
            anomalies: 异常数据
        
        Returns:
            洞察列表
        """
        insights = []
        
        # 异常数量洞察
        for param_name, param_anomalies in anomalies.items():
            if param_anomalies:
                insights.append(
                    f"参数 '{param_name}' 检测到 {len(param_anomalies)} 个异常值"
                )
        
        # 趋势洞察
        for param_name, values in parameter_data.items():
            trend_info = AnalysisService.calculate_trend(values)
            if trend_info["trend"] != "stable":
                insights.append(
                    f"参数 '{param_name}' 呈现 {trend_info['trend']} 趋势"
                )
        
        # 相关性洞察
        correlations = AnalysisService.analyze_parameter_correlation(parameter_data)
        for param1, corr_dict in correlations.items():
            for param2, corr in corr_dict.items():
                if param1 < param2 and abs(corr) > 0.8:
                    insights.append(
                        f"参数 '{param1}' 和 '{param2}' 存在强相关性 (r={corr:.2f})"
                    )
        
        return insights