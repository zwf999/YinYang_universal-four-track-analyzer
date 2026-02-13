# core/analyzers/composite_analyzer.py
# 复合分析器

from typing import Dict, List, Any
from core.analyzers.base_analyzer import BaseAnalyzer
from core.analyzers.four_track_analyzer import FourTrackAnalyzer
from core.analyzers.pattern_analyzer import PatternAnalyzer
from core.analyzers.statistical_analyzer import StatisticalAnalyzer

class CompositeAnalyzer(BaseAnalyzer):
    """复合分析器"""
    
    def __init__(self):
        """初始化复合分析器"""
        self.analyzers = {
            'four_track': FourTrackAnalyzer(),
            'pattern': PatternAnalyzer(),
            'statistical': StatisticalAnalyzer()
        }
    
    def analyze(self, digits: List[int]) -> Dict[str, Any]:
        """
        综合分析数字序列
        
        Args:
            digits: 数字序列
            
        Returns:
            综合分析结果
        """
        if not self.validate_input(digits):
            return {
                'error': 'Invalid input',
                'four_track': {},
                'pattern': {},
                'statistical': {},
                'summary': {}
            }
        
        digits = self.preprocess(digits)
        
        # 运行所有分析器
        results = {}
        for name, analyzer in self.analyzers.items():
            results[name] = analyzer.analyze(digits)
        
        # 生成综合摘要
        summary = self._generate_summary(results)
        
        # 生成综合评分
        scores = self._calculate_scores(results)
        
        # 生成综合指纹
        fingerprint = self._generate_composite_fingerprint(results)
        
        # 分析一致性
        consistency = self._analyze_consistency(results)
        
        return {
            'four_track': results['four_track'],
            'pattern': results['pattern'],
            'statistical': results['statistical'],
            'summary': summary,
            'scores': scores,
            'fingerprint': fingerprint,
            'consistency': consistency,
            'analyzers': {
                name: {
                    'version': analyzer.get_version()
                }
                for name, analyzer in self.analyzers.items()
            }
        }
    
    def _generate_summary(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """生成综合摘要"""
        summary = {
            'entropy': results['statistical'].get('entropy', 0),
            'pattern_density': results['pattern'].get('pattern_density', 0),
            'total_patterns': results['pattern'].get('total_patterns', 0),
            'four_track_pair_ratio': results['four_track'].get('track1', {}).get('symbol_pairs', {}).get('pair_ratio', 0),
            'yinyang_ratio': results['four_track'].get('track1', {}).get('yinyang', {}).get('ratio', 0),
            'digit_distribution': results['statistical'].get('digit_distribution', {}),
            'correlation': results['statistical'].get('correlation', 0)
        }
        
        # 计算综合复杂度评分
        summary['complexity_score'] = self._calculate_complexity_score(summary)
        
        return summary
    
    def _calculate_complexity_score(self, summary: Dict[str, Any]) -> float:
        """计算复杂度评分"""
        # 熵值归一化 (0-3.32范围归一到0-1)
        entropy_normalized = min(summary['entropy'] / 3.32, 1.0)
        
        # 模式密度归一化
        pattern_density_normalized = min(summary['pattern_density'] * 10, 1.0)
        
        # 四轨道配对率归一化
        pair_ratio_normalized = summary['four_track_pair_ratio'] * 2  # 最大可能为0.5
        
        # 相关性绝对值归一化
        correlation_normalized = abs(summary['correlation'])
        
        # 加权平均
        weights = {
            'entropy': 0.4,
            'pattern_density': 0.3,
            'pair_ratio': 0.2,
            'correlation': 0.1
        }
        
        complexity_score = (
            entropy_normalized * weights['entropy'] +
            pattern_density_normalized * weights['pattern_density'] +
            pair_ratio_normalized * weights['pair_ratio'] +
            correlation_normalized * weights['correlation']
        )
        
        return complexity_score
    
    def _calculate_scores(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """计算综合评分"""
        scores = {
            'randomness': self._calculate_randomness_score(results),
            'pattern_complexity': self._calculate_pattern_complexity_score(results),
            'symmetry': self._calculate_symmetry_score(results),
            'predictability': self._calculate_predictability_score(results),
            'overall': 0
        }
        
        # 计算总体评分
        scores['overall'] = (
            scores['randomness'] * 0.25 +
            scores['pattern_complexity'] * 0.25 +
            scores['symmetry'] * 0.25 +
            scores['predictability'] * 0.25
        )
        
        return scores
    
    def _calculate_randomness_score(self, results: Dict[str, Dict[str, Any]]) -> float:
        """计算随机性评分"""
        entropy = results['statistical'].get('entropy', 0)
        # 熵值最大约为3.32 (均匀分布)
        randomness = min(entropy / 3.32, 1.0)
        return randomness
    
    def _calculate_pattern_complexity_score(self, results: Dict[str, Dict[str, Any]]) -> float:
        """计算模式复杂度评分"""
        pattern_density = results['pattern'].get('pattern_density', 0)
        total_patterns = results['pattern'].get('total_patterns', 0)
        
        # 模式密度归一化
        density_score = min(pattern_density * 10, 1.0)
        
        # 模式数量归一化
        patterns_score = min(total_patterns / 100, 1.0)
        
        return (density_score + patterns_score) / 2
    
    def _calculate_symmetry_score(self, results: Dict[str, Dict[str, Any]]) -> float:
        """计算对称性评分"""
        pair_ratio = results['four_track'].get('track1', {}).get('symbol_pairs', {}).get('pair_ratio', 0)
        # 配对率最大可能为0.5
        symmetry = min(pair_ratio * 2, 1.0)
        return symmetry
    
    def _calculate_predictability_score(self, results: Dict[str, Dict[str, Any]]) -> float:
        """计算可预测性评分"""
        correlation = abs(results['statistical'].get('correlation', 0))
        pattern_density = results['pattern'].get('pattern_density', 0)
        
        # 相关性越高，可预测性越高
        # 模式密度越高，可预测性越高
        predictability = (correlation + min(pattern_density * 10, 1.0)) / 2
        return min(predictability, 1.0)
    
    def _generate_composite_fingerprint(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """生成综合指纹"""
        fingerprint = {
            'statistical': {
                'entropy': results['statistical'].get('entropy', 0),
                'mean': results['statistical'].get('mean', 0),
                'std': results['statistical'].get('std', 0),
                'skewness': results['statistical'].get('skewness', 0),
                'kurtosis': results['statistical'].get('kurtosis', 0)
            },
            'pattern': {
                'repetition_score': results['pattern'].get('repetition_score', 0),
                'pair_score': results['pattern'].get('pair_score', 0),
                'sequential_score': results['pattern'].get('sequential_score', 0),
                'pattern_density': results['pattern'].get('pattern_density', 0)
            },
            'four_track': {
                'track1_pair_ratio': results['four_track'].get('track1', {}).get('symbol_pairs', {}).get('pair_ratio', 0),
                'track2_pair_ratio': results['four_track'].get('track2', {}).get('symbol_pairs', {}).get('pair_ratio', 0),
                'track3_pair_ratio': results['four_track'].get('track3', {}).get('symbol_pairs', {}).get('pair_ratio', 0),
                'track4_pair_ratio': results['four_track'].get('track4', {}).get('symbol_pairs', {}).get('pair_ratio', 0),
                'yinyang_ratio': results['four_track'].get('track1', {}).get('yinyang', {}).get('ratio', 0)
            }
        }
        
        return fingerprint
    
    def _analyze_consistency(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """分析一致性"""
        # 分析随机性与模式密度的一致性
        entropy = results['statistical'].get('entropy', 0)
        pattern_density = results['pattern'].get('pattern_density', 0)
        
        # 高熵值通常意味着低模式密度
        expected_pattern_density = max(0, 1 - entropy / 3.32)
        pattern_consistency = 1 - abs(pattern_density - expected_pattern_density)
        
        # 分析四轨道配对率与统计相关性的一致性
        pair_ratio = results['four_track'].get('track1', {}).get('symbol_pairs', {}).get('pair_ratio', 0)
        correlation = abs(results['statistical'].get('correlation', 0))
        
        # 高配对率通常意味着高相关性
        expected_correlation = pair_ratio * 2
        correlation_consistency = 1 - abs(correlation - expected_correlation)
        
        return {
            'pattern_consistency': pattern_consistency,
            'correlation_consistency': correlation_consistency,
            'overall_consistency': (pattern_consistency + correlation_consistency) / 2
        }
    
    def get_name(self) -> str:
        """获取分析器名称"""
        return "CompositeAnalyzer"
    
    def get_version(self) -> str:
        """获取分析器版本"""
        return "2.0.0"
    
    def add_analyzer(self, name: str, analyzer: BaseAnalyzer) -> None:
        """
        添加自定义分析器
        
        Args:
            name: 分析器名称
            analyzer: 分析器实例
        """
        self.analyzers[name] = analyzer
    
    def remove_analyzer(self, name: str) -> None:
        """
        移除分析器
        
        Args:
            name: 分析器名称
        """
        if name in self.analyzers:
            del self.analyzers[name]
    
    def get_analyzer(self, name: str) -> BaseAnalyzer:
        """
        获取分析器
        
        Args:
            name: 分析器名称
            
        Returns:
            分析器实例
        """
        return self.analyzers.get(name)
