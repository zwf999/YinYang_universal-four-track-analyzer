# core/predictors/statistical_predictor.py
# 统计预测器

from typing import Dict, List, Any
import numpy as np
from collections import Counter
from core.predictors.base_predictor import BasePredictor

class StatisticalPredictor(BasePredictor):
    """统计预测器"""
    
    def __init__(self, use_markov: bool = True, markov_order: int = 2):
        """初始化统计预测器
        
        Args:
            use_markov: 是否使用马尔可夫链
            markov_order: 马尔可夫链阶数
        """
        self.use_markov = use_markov
        self.markov_order = markov_order
        self.markov_chains = {}
    
    def predict(self, digits: List[int], length: int = 100) -> List[int]:
        """
        基于统计分布预测数字序列
        
        Args:
            digits: 输入数字序列
            length: 预测长度
            
        Returns:
            预测的数字序列
        """
        if not self.validate_input(digits):
            return [0] * length
        
        digits = self.preprocess(digits)
        
        if len(digits) < self.markov_order + 1 and self.use_markov:
            # 数据不足，使用简单统计
            return self._predict_simple_statistical(digits, length)
        
        if self.use_markov:
            # 使用马尔可夫链预测
            return self._predict_markov(digits, length)
        else:
            # 使用简单统计预测
            return self._predict_simple_statistical(digits, length)
    
    def _predict_simple_statistical(self, digits: List[int], length: int) -> List[int]:
        """使用简单统计分布预测"""
        # 计算数字分布
        digit_counts = Counter(digits)
        total = len(digits)
        
        if total == 0:
            return [0] * length
        
        # 构建概率分布
        digits_list = list(digit_counts.keys())
        probs_list = [count / total for count in digit_counts.values()]
        
        # 基于概率生成预测
        prediction = np.random.choice(digits_list, size=length, p=probs_list).tolist()
        
        return prediction
    
    def _predict_markov(self, digits: List[int], length: int) -> List[int]:
        """使用马尔可夫链预测"""
        # 构建马尔可夫链
        self._build_markov_chain(digits)
        
        # 初始化预测
        prediction = []
        current_state = tuple(digits[-self.markov_order:]) if len(digits) >= self.markov_order else tuple([0] * self.markov_order)
        
        for _ in range(length):
            next_digit = self._get_next_digit(current_state)
            prediction.append(next_digit)
            
            # 更新当前状态
            current_state = tuple(list(current_state[1:]) + [next_digit])
        
        return prediction
    
    def _build_markov_chain(self, digits: List[int]) -> None:
        """构建马尔可夫链"""
        self.markov_chains = {}
        
        for i in range(len(digits) - self.markov_order):
            state = tuple(digits[i:i+self.markov_order])
            next_digit = digits[i+self.markov_order]
            
            if state not in self.markov_chains:
                self.markov_chains[state] = Counter()
            
            self.markov_chains[state][next_digit] += 1
    
    def _get_next_digit(self, state: tuple) -> int:
        """基于当前状态获取下一个数字"""
        if state in self.markov_chains:
            # 使用状态转移概率
            transitions = self.markov_chains[state]
            digits_list = list(transitions.keys())
            probs_list = [count / sum(transitions.values()) for count in transitions.values()]
            return np.random.choice(digits_list, p=probs_list)
        else:
            # 状态不存在，使用均匀分布
            return np.random.randint(0, 10)
    
    def _calculate_digit_distribution(self, digits: List[int]) -> Dict[int, float]:
        """计算数字分布"""
        counter = Counter(digits)
        total = len(digits)
        distribution = {}
        for digit in range(10):
            distribution[digit] = counter.get(digit, 0) / total if total > 0 else 0
        return distribution
    
    def _calculate_pair_distribution(self, digits: List[int]) -> Dict[tuple, float]:
        """计算数字对分布"""
        if len(digits) < 2:
            return {}
        
        pairs = []
        for i in range(len(digits) - 1):
            pairs.append((digits[i], digits[i+1]))
        
        counter = Counter(pairs)
        total = len(pairs)
        distribution = {}
        for pair, count in counter.items():
            distribution[pair] = count / total
        
        return distribution
    
    def get_name(self) -> str:
        """获取预测器名称"""
        if self.use_markov:
            return f"MarkovPredictor(order={self.markov_order})"
        else:
            return "StatisticalPredictor"
    
    def get_version(self) -> str:
        """获取预测器版本"""
        return "2.0.0"
    
    def set_markov_order(self, order: int) -> None:
        """
        设置马尔可夫链阶数
        
        Args:
            order: 马尔可夫链阶数
        """
        self.markov_order = max(1, order)
    
    def set_use_markov(self, use_markov: bool) -> None:
        """
        设置是否使用马尔可夫链
        
        Args:
            use_markov: 是否使用马尔可夫链
        """
        self.use_markov = use_markov
