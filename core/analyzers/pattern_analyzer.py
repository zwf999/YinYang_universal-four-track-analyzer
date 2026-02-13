# core/analyzers/pattern_analyzer.py
# 模式分析器

from typing import Dict, List, Any, Tuple
from collections import Counter
import numpy as np
from core.analyzers.base_analyzer import BaseAnalyzer

class PatternAnalyzer(BaseAnalyzer):
    """模式分析器"""
    
    def __init__(self):
        """初始化模式分析器"""
        self.max_pattern_length = 20
        self.min_pattern_length = 2
        self.min_repetitions = 2
    
    def analyze(self, digits: List[int]) -> Dict[str, Any]:
        """
        分析数字序列中的模式
        
        Args:
            digits: 数字序列
            
        Returns:
            分析结果
        """
        if not self.validate_input(digits):
            return {
                'error': 'Invalid input',
                'patterns': [],
                'repetition_score': 0,
                'pair_score': 0,
                'sequential_score': 0,
                'pattern_density': 0
            }
        
        digits = self.preprocess(digits)
        
        # 检测模式
        patterns = self._detect_patterns(digits)
        
        # 计算模式特征
        repetition_score = self._calculate_repetition_score(digits)
        pair_score = self._calculate_pair_score(digits)
        sequential_score = self._calculate_sequential_score(digits)
        pattern_density = self._calculate_pattern_density(patterns, len(digits))
        
        # 分析模式分布
        pattern_distribution = self._analyze_pattern_distribution(patterns)
        
        return {
            'patterns': patterns,
            'repetition_score': repetition_score,
            'pair_score': pair_score,
            'sequential_score': sequential_score,
            'pattern_density': pattern_density,
            'pattern_distribution': pattern_distribution,
            'total_patterns': len(patterns)
        }
    
    def _detect_patterns(self, digits: List[int]) -> List[Dict[str, Any]]:
        """检测数字序列中的模式"""
        patterns = []
        
        # 检测重复模式
        repetition_patterns = self._detect_repetition_patterns(digits)
        patterns.extend(repetition_patterns)
        
        # 检测序列模式
        sequential_patterns = self._detect_sequential_patterns(digits)
        patterns.extend(sequential_patterns)
        
        # 检测配对模式
        pair_patterns = self._detect_pair_patterns(digits)
        patterns.extend(pair_patterns)
        
        return patterns
    
    def _detect_repetition_patterns(self, digits: List[int]) -> List[Dict[str, Any]]:
        """检测重复模式"""
        patterns = []
        
        for pattern_length in range(self.min_pattern_length, min(self.max_pattern_length, len(digits) // 2) + 1):
            pattern_counts = Counter()
            
            for i in range(len(digits) - pattern_length + 1):
                pattern = tuple(digits[i:i+pattern_length])
                pattern_counts[pattern] += 1
            
            # 找出重复次数足够的模式
            for pattern, count in pattern_counts.items():
                if count >= self.min_repetitions:
                    # 找到所有出现位置
                    positions = []
                    for i in range(len(digits) - pattern_length + 1):
                        if tuple(digits[i:i+pattern_length]) == pattern:
                            positions.append(i)
                    
                    patterns.append({
                        'type': 'repetition',
                        'pattern': list(pattern),
                        'length': pattern_length,
                        'count': count,
                        'positions': positions,
                        'score': count * pattern_length
                    })
        
        return patterns
    
    def _detect_sequential_patterns(self, digits: List[int]) -> List[Dict[str, Any]]:
        """检测序列模式"""
        patterns = []
        
        # 检测递增/递减序列
        i = 0
        while i < len(digits) - 2:
            # 检查递增序列
            if i + 2 < len(digits) and digits[i+1] == digits[i] + 1 and digits[i+2] == digits[i] + 2:
                start = i
                while i + 1 < len(digits) and digits[i+1] == digits[i] + 1:
                    i += 1
                end = i
                pattern_length = end - start + 1
                
                if pattern_length >= 3:
                    pattern = digits[start:end+1]
                    patterns.append({
                        'type': 'sequential_increasing',
                        'pattern': pattern,
                        'length': pattern_length,
                        'start': start,
                        'end': end,
                        'score': pattern_length
                    })
            
            # 检查递减序列
            elif i + 2 < len(digits) and digits[i+1] == digits[i] - 1 and digits[i+2] == digits[i] - 2:
                start = i
                while i + 1 < len(digits) and digits[i+1] == digits[i] - 1:
                    i += 1
                end = i
                pattern_length = end - start + 1
                
                if pattern_length >= 3:
                    pattern = digits[start:end+1]
                    patterns.append({
                        'type': 'sequential_decreasing',
                        'pattern': pattern,
                        'length': pattern_length,
                        'start': start,
                        'end': end,
                        'score': pattern_length
                    })
            else:
                i += 1
        
        return patterns
    
    def _detect_pair_patterns(self, digits: List[int]) -> List[Dict[str, Any]]:
        """检测配对模式"""
        patterns = []
        
        # 检测连续配对
        pair_counts = Counter()
        for i in range(len(digits) - 1):
            pair = (digits[i], digits[i+1])
            pair_counts[pair] += 1
        
        # 找出高频配对
        for pair, count in pair_counts.most_common(10):  # 只取前10个
            if count >= 3:  # 至少出现3次
                # 找到所有出现位置
                positions = []
                for i in range(len(digits) - 1):
                    if (digits[i], digits[i+1]) == pair:
                        positions.append(i)
                
                patterns.append({
                    'type': 'pair',
                    'pattern': list(pair),
                    'length': 2,
                    'count': count,
                    'positions': positions,
                    'score': count * 2
                })
        
        return patterns
    
    def _calculate_repetition_score(self, digits: List[int]) -> float:
        """计算重复得分"""
        max_repetition = 0
        for pattern_length in range(2, 11):
            for i in range(len(digits) - pattern_length * 2 + 1):
                pattern = tuple(digits[i:i+pattern_length])
                next_pattern = tuple(digits[i+pattern_length:i+pattern_length*2])
                if pattern == next_pattern:
                    max_repetition = max(max_repetition, pattern_length)
        return max_repetition
    
    def _calculate_pair_score(self, digits: List[int]) -> int:
        """计算配对得分"""
        pairs = []
        for i in range(len(digits) - 1):
            pairs.append((digits[i], digits[i+1]))
        pair_counts = Counter(pairs)
        most_common = pair_counts.most_common(1)
        return most_common[0][1] if most_common else 0
    
    def _calculate_sequential_score(self, digits: List[int]) -> int:
        """计算序列得分"""
        sequential_count = 0
        for i in range(len(digits) - 2):
            if abs(digits[i] - digits[i+1]) == 1 and abs(digits[i+1] - digits[i+2]) == 1:
                sequential_count += 1
        return sequential_count
    
    def _calculate_pattern_density(self, patterns: List[Dict[str, Any]], total_length: int) -> float:
        """计算模式密度"""
        if total_length == 0:
            return 0
        
        total_pattern_length = sum(p['length'] * p.get('count', 1) for p in patterns)
        return total_pattern_length / total_length
    
    def _analyze_pattern_distribution(self, patterns: List[Dict[str, Any]]) -> Dict[str, int]:
        """分析模式分布"""
        distribution = Counter()
        for pattern in patterns:
            distribution[pattern['type']] += 1
        return dict(distribution)
    
    def get_name(self) -> str:
        """获取分析器名称"""
        return "PatternAnalyzer"
    
    def get_version(self) -> str:
        """获取分析器版本"""
        return "2.0.0"
