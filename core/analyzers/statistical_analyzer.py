# core/analyzers/statistical_analyzer.py
# 统计分析器

from typing import Dict, List, Any
from collections import Counter
import numpy as np
from core.analyzers.base_analyzer import BaseAnalyzer

class StatisticalAnalyzer(BaseAnalyzer):
    """统计分析器"""
    
    def __init__(self):
        """初始化统计分析器"""
        pass
    
    def analyze(self, digits: List[int]) -> Dict[str, Any]:
        """
        分析数字序列的统计特性
        
        Args:
            digits: 数字序列
            
        Returns:
            分析结果
        """
        if not self.validate_input(digits):
            return {
                'error': 'Invalid input',
                'digit_distribution': {},
                'entropy': 0,
                'mean': 0,
                'std': 0,
                'variance': 0
            }
        
        digits = self.preprocess(digits)
        
        # 计算数字分布
        digit_distribution = self._calculate_digit_distribution(digits)
        
        # 计算熵值
        entropy = self._calculate_entropy(digits)
        
        # 计算基本统计量
        mean = self._calculate_mean(digits)
        std = self._calculate_std(digits)
        variance = self._calculate_variance(digits)
        
        # 计算高阶统计量
        skewness = self._calculate_skewness(digits)
        kurtosis = self._calculate_kurtosis(digits)
        
        # 计算相邻数字相关性
        correlation = self._calculate_correlation(digits)
        
        # 计算运行统计
        runs_analysis = self._calculate_runs_analysis(digits)
        
        # 计算分位数
        percentiles = self._calculate_percentiles(digits)
        
        return {
            'digit_distribution': digit_distribution,
            'entropy': entropy,
            'mean': mean,
            'std': std,
            'variance': variance,
            'skewness': skewness,
            'kurtosis': kurtosis,
            'correlation': correlation,
            'runs_analysis': runs_analysis,
            'percentiles': percentiles,
            'total_digits': len(digits)
        }
    
    def _calculate_digit_distribution(self, digits: List[int]) -> Dict[int, float]:
        """计算数字分布"""
        counter = Counter(digits)
        total = len(digits)
        distribution = {}
        for digit in range(10):
            distribution[digit] = counter.get(digit, 0) / total if total > 0 else 0
        return distribution
    
    def _calculate_entropy(self, digits: List[int]) -> float:
        """计算熵值"""
        if not digits:
            return 0
        distribution = self._calculate_digit_distribution(digits)
        entropy = 0
        for probability in distribution.values():
            if probability > 0:
                entropy -= probability * np.log2(probability)
        return entropy
    
    def _calculate_mean(self, digits: List[int]) -> float:
        """计算均值"""
        return np.mean(digits) if digits else 0
    
    def _calculate_std(self, digits: List[int]) -> float:
        """计算标准差"""
        return np.std(digits) if digits else 0
    
    def _calculate_variance(self, digits: List[int]) -> float:
        """计算方差"""
        return np.var(digits) if digits else 0
    
    def _calculate_skewness(self, digits: List[int]) -> float:
        """计算偏度"""
        if len(digits) < 3:
            return 0
        mean = self._calculate_mean(digits)
        std = self._calculate_std(digits)
        if std == 0:
            return 0
        skewness = np.mean([(x - mean) ** 3 for x in digits]) / (std ** 3)
        return skewness
    
    def _calculate_kurtosis(self, digits: List[int]) -> float:
        """计算峰度"""
        if len(digits) < 4:
            return 0
        mean = self._calculate_mean(digits)
        std = self._calculate_std(digits)
        if std == 0:
            return 0
        kurtosis = np.mean([(x - mean) ** 4 for x in digits]) / (std ** 4) - 3  # 减去3使正态分布峰度为0
        return kurtosis
    
    def _calculate_correlation(self, digits: List[int]) -> float:
        """计算相邻数字相关性"""
        if len(digits) < 2:
            return 0
        x = digits[:-1]
        y = digits[1:]
        if len(x) < 2:
            return 0
        correlation = np.corrcoef(x, y)[0, 1]
        return correlation if not np.isnan(correlation) else 0
    
    def _calculate_runs_analysis(self, digits: List[int]) -> Dict[str, Any]:
        """计算运行分析"""
        if len(digits) < 2:
            return {
                'runs': 0,
                'expected_runs': 0,
                'z_score': 0
            }
        
        # 计算实际运行数
        runs = 1
        for i in range(1, len(digits)):
            if digits[i] != digits[i-1]:
                runs += 1
        
        # 计算期望运行数
        n = len(digits)
        p = self._calculate_digit_distribution(digits)
        expected_runs = 1 + 2 * n * sum(p_i * (1 - p_i) for p_i in p.values())
        
        # 计算方差
        variance = 2 * (2 * n - 3) * sum(p_i ** 2 * (1 - p_i) ** 2 for p_i in p.values())
        variance -= (expected_runs - 1) ** 2 / (n - 1)
        variance = max(variance, 0)  # 确保方差非负
        
        # 计算z分数
        std_runs = np.sqrt(variance)
        z_score = (runs - expected_runs) / std_runs if std_runs > 0 else 0
        
        return {
            'runs': runs,
            'expected_runs': expected_runs,
            'z_score': z_score,
            'std_runs': std_runs
        }
    
    def _calculate_percentiles(self, digits: List[int]) -> Dict[str, float]:
        """计算分位数"""
        if not digits:
            return {
                'p10': 0,
                'p25': 0,
                'p50': 0,
                'p75': 0,
                'p90': 0
            }
        
        sorted_digits = sorted(digits)
        n = len(sorted_digits)
        
        percentiles = {
            'p10': sorted_digits[int(n * 0.1)] if n > 0 else 0,
            'p25': sorted_digits[int(n * 0.25)] if n > 0 else 0,
            'p50': sorted_digits[int(n * 0.5)] if n > 0 else 0,
            'p75': sorted_digits[int(n * 0.75)] if n > 0 else 0,
            'p90': sorted_digits[int(n * 0.9)] if n > 0 else 0
        }
        
        return percentiles
    
    def get_name(self) -> str:
        """获取分析器名称"""
        return "StatisticalAnalyzer"
    
    def get_version(self) -> str:
        """获取分析器版本"""
        return "2.0.0"
