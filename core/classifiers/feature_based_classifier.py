# core/classifiers/feature_based_classifier.py
# 基于特征的分类器

from typing import Dict, List, Any
from collections import Counter
import numpy as np
from core.classifiers.base_classifier import BaseClassifier
from core.analyzers.composite_analyzer import CompositeAnalyzer

class FeatureBasedClassifier(BaseClassifier):
    """基于特征的分类器"""
    
    def __init__(self):
        """初始化基于特征的分类器"""
        self.analyzer = CompositeAnalyzer()
        self.thresholds = {
            'mathematical': {
                'min_entropy': 2.5,
                'min_pattern_density': 0.05,
                'min_unique_digits': 8,
                'min_length': 100
            },
            'physical': {
                'max_entropy': 3.0,
                'min_pattern_density': 0.1,
                'min_length': 10
            }
        }
    
    def classify(self, digits: List[int], name: str = None) -> Dict[str, Any]:
        """
        基于数字特征分类数字序列
        
        Args:
            digits: 输入数字序列
            name: 常数名称（可选）
            
        Returns:
            分类结果
        """
        if not self.validate_input(digits):
            return {
                'type': 'unknown',
                'subtype': 'unknown',
                'description': '未知常数',
                'confidence': 0.0,
                'features': {}
            }
        
        digits = self.preprocess(digits)
        
        # 分析数字特征
        analysis_result = self.analyzer.analyze(digits)
        
        # 提取特征
        features = self._extract_features(digits, analysis_result)
        
        # 基于特征分类
        classification = self._classify_based_on_features(features)
        
        # 整合结果
        result = {
            'type': classification['type'],
            'subtype': classification['subtype'],
            'description': classification['description'],
            'confidence': classification['confidence'],
            'features': features,
            'analysis_summary': {
                'entropy': features.get('entropy', 0),
                'pattern_density': features.get('pattern_density', 0),
                'symmetry': features.get('symmetry', 0),
                'digit_coverage': features.get('digit_coverage', 0)
            }
        }
        
        return result
    
    def _extract_features(self, digits: List[int], analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """提取数字序列特征"""
        # 基本特征
        length = len(digits)
        digit_counter = Counter(digits)
        unique_digits = len(digit_counter)
        digit_coverage = unique_digits / 10.0
        
        # 统计特征
        entropy = analysis_result.get('statistical', {}).get('entropy', 0)
        mean = analysis_result.get('statistical', {}).get('mean', 0)
        std = analysis_result.get('statistical', {}).get('std', 0)
        correlation = analysis_result.get('statistical', {}).get('correlation', 0)
        
        # 模式特征
        pattern_density = analysis_result.get('pattern', {}).get('pattern_density', 0)
        total_patterns = analysis_result.get('pattern', {}).get('total_patterns', 0)
        repetition_score = analysis_result.get('pattern', {}).get('repetition_score', 0)
        pair_score = analysis_result.get('pattern', {}).get('pair_score', 0)
        sequential_score = analysis_result.get('pattern', {}).get('sequential_score', 0)
        
        # 四轨道特征
        symmetry = analysis_result.get('four_track', {}).get('track1', {}).get('nine_sum_pairs', {}).get('pair_ratio', 0)
        yinyang_ratio = analysis_result.get('four_track', {}).get('track1', {}).get('yinyang', {}).get('ratio', 0)
        yang_percent = analysis_result.get('four_track', {}).get('track1', {}).get('yinyang', {}).get('yang_percent', 0)
        
        # 数字分布特征
        digit_distribution = analysis_result.get('statistical', {}).get('digit_distribution', {})
        distribution_uniformity = self._calculate_distribution_uniformity(digit_distribution, length)
        
        # 复杂度特征
        complexity_score = analysis_result.get('summary', {}).get('complexity_score', 0)
        randomness_score = analysis_result.get('scores', {}).get('randomness', 0)
        pattern_complexity_score = analysis_result.get('scores', {}).get('pattern_complexity', 0)
        
        features = {
            'length': length,
            'unique_digits': unique_digits,
            'digit_coverage': digit_coverage,
            'entropy': entropy,
            'mean': mean,
            'std': std,
            'correlation': correlation,
            'pattern_density': pattern_density,
            'total_patterns': total_patterns,
            'repetition_score': repetition_score,
            'pair_score': pair_score,
            'sequential_score': sequential_score,
            'symmetry': symmetry,
            'yinyang_ratio': yinyang_ratio,
            'yang_percent': yang_percent,
            'distribution_uniformity': distribution_uniformity,
            'complexity_score': complexity_score,
            'randomness_score': randomness_score,
            'pattern_complexity_score': pattern_complexity_score,
            'digit_distribution': digit_distribution
        }
        
        return features
    
    def _calculate_distribution_uniformity(self, digit_distribution: Dict[int, float], length: int) -> float:
        """计算数字分布均匀性"""
        if length == 0:
            return 0
        
        # 期望均匀分布
        expected_prob = 0.1
        
        # 计算与均匀分布的偏差
        deviation = 0
        for digit in range(10):
            actual_prob = digit_distribution.get(digit, 0)
            deviation += abs(actual_prob - expected_prob)
        
        # 归一化到0-1，值越大越均匀
        uniformity = 1 - (deviation / 2)  # 最大偏差为2（所有概率都为0或1）
        
        return max(0, uniformity)
    
    def _classify_based_on_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """基于特征分类"""
        # 计算各类别得分
        scores = {
            'mathematical': self._calculate_mathematical_score(features),
            'physical': self._calculate_physical_score(features),
            'unknown': 0.1  # 默认未知得分
        }
        
        # 选择得分最高的类别
        best_type = max(scores.items(), key=lambda x: x[1])[0]
        best_score = scores[best_type]
        
        # 计算置信度
        confidence = min(best_score / max(sum(scores.values()), 1), 1.0)
        
        # 确定子类型
        subtype = self._determine_subtype(best_type, features)
        description = self._get_description(best_type, subtype)
        
        return {
            'type': best_type,
            'subtype': subtype,
            'description': description,
            'confidence': confidence,
            'scores': scores
        }
    
    def _calculate_mathematical_score(self, features: Dict[str, Any]) -> float:
        """计算数学常数得分"""
        score = 0
        
        # 高熵值
        if features.get('entropy', 0) > 3.0:
            score += 0.3
        elif features.get('entropy', 0) > 2.5:
            score += 0.2
        
        # 均匀分布
        if features.get('distribution_uniformity', 0) > 0.8:
            score += 0.2
        
        # 高数字覆盖率
        if features.get('digit_coverage', 0) > 0.8:
            score += 0.2
        
        # 长序列
        if features.get('length', 0) > 1000:
            score += 0.15
        elif features.get('length', 0) > 100:
            score += 0.1
        
        # 低模式密度（数学常数通常更随机）
        if features.get('pattern_density', 0) < 0.2:
            score += 0.15
        
        return score
    
    def _calculate_physical_score(self, features: Dict[str, Any]) -> float:
        """计算物理常数得分"""
        score = 0
        
        # 中等熵值
        if 2.0 < features.get('entropy', 0) < 3.0:
            score += 0.3
        
        # 高模式密度
        if features.get('pattern_density', 0) > 0.2:
            score += 0.25
        elif features.get('pattern_density', 0) > 0.1:
            score += 0.15
        
        # 高对称性
        if features.get('symmetry', 0) > 0.3:
            score += 0.2
        elif features.get('symmetry', 0) > 0.2:
            score += 0.1
        
        # 中等长度
        if 10 < features.get('length', 0) < 1000:
            score += 0.15
        
        # 高相关性
        if abs(features.get('correlation', 0)) > 0.1:
            score += 0.1
        
        return score
    
    def _determine_subtype(self, type_name: str, features: Dict[str, Any]) -> str:
        """确定子类型"""
        if type_name == 'mathematical':
            if features.get('entropy', 0) > 3.2:
                return 'transcendental'
            elif features.get('pattern_density', 0) > 0.1:
                return 'algebraic'
            else:
                return 'irrational'
        
        elif type_name == 'physical':
            if features.get('length', 0) < 50 and features.get('pattern_density', 0) > 0.3:
                return 'exact'
            elif features.get('symmetry', 0) > 0.3:
                return 'fundamental'
            elif features.get('pattern_density', 0) > 0.2:
                return 'derived'
            else:
                return 'experimental'
        
        else:
            return 'unknown'
    
    def _get_description(self, type_name: str, subtype: str) -> str:
        """获取类别描述"""
        descriptions = {
            'mathematical': {
                'irrational': '无理数学常数',
                'transcendental': '超越数学常数',
                'algebraic': '代数数学常数'
            },
            'physical': {
                'exact': '精确物理常数',
                'fundamental': '基本物理常数',
                'derived': '导出物理常数',
                'experimental': '实验物理常数'
            },
            'unknown': {
                'unknown': '未知常数'
            }
        }
        
        return descriptions.get(type_name, {}).get(subtype, '未知常数')
    
    def get_name(self) -> str:
        """获取分类器名称"""
        return "FeatureBasedClassifier"
    
    def get_version(self) -> str:
        """获取分类器版本"""
        return "2.0.0"
