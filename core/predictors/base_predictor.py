# core/predictors/base_predictor.py
# 预测器基类

from abc import ABC, abstractmethod
from typing import Dict, List, Any

class BasePredictor(ABC):
    """预测器基类"""
    
    @abstractmethod
    def predict(self, digits: List[int], length: int = 100) -> List[int]:
        """
        预测数字序列
        
        Args:
            digits: 输入数字序列
            length: 预测长度
            
        Returns:
            预测的数字序列
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """
        获取预测器名称
        
        Returns:
            预测器名称
        """
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """
        获取预测器版本
        
        Returns:
            预测器版本
        """
        pass
    
    def evaluate(self, prediction: List[int], actual: List[int]) -> Dict[str, Any]:
        """
        评估预测结果
        
        Args:
            prediction: 预测的数字序列
            actual: 实际的数字序列
            
        Returns:
            评估结果
        """
        if not prediction or not actual:
            return {
                'accuracy': 0,
                'correct': 0,
                'total': 0,
                'position_accuracy': [],
                'first_20_accuracy': 0,
                'middle_40_accuracy': 0,
                'last_40_accuracy': 0
            }
        
        # 计算基本准确率
        correct = 0
        total = min(len(prediction), len(actual))
        position_accuracy = []
        
        for i in range(total):
            if prediction[i] == actual[i]:
                correct += 1
                position_accuracy.append(1)
            else:
                position_accuracy.append(0)
        
        accuracy = correct / total if total > 0 else 0
        
        # 计算位置准确率
        first_20_accuracy = 0
        middle_40_accuracy = 0
        last_40_accuracy = 0
        
        if position_accuracy:
            # 前20位准确率
            if len(position_accuracy) >= 20:
                first_20_accuracy = sum(position_accuracy[:20]) / 20
            else:
                first_20_accuracy = sum(position_accuracy) / len(position_accuracy)
            
            # 中间40位准确率
            if len(position_accuracy) >= 60:
                middle_40_accuracy = sum(position_accuracy[20:60]) / 40
            elif len(position_accuracy) > 20:
                middle_40_accuracy = sum(position_accuracy[20:]) / (len(position_accuracy) - 20)
            
            # 后40位准确率
            if len(position_accuracy) >= 60:
                last_40_accuracy = sum(position_accuracy[60:]) / min(40, len(position_accuracy) - 60)
        
        # 计算连续正确长度
        max_consecutive_correct = 0
        current_consecutive = 0
        for acc in position_accuracy:
            if acc == 1:
                current_consecutive += 1
                max_consecutive_correct = max(max_consecutive_correct, current_consecutive)
            else:
                current_consecutive = 0
        
        return {
            'accuracy': accuracy,
            'correct': correct,
            'total': total,
            'position_accuracy': position_accuracy,
            'first_20_accuracy': first_20_accuracy,
            'middle_40_accuracy': middle_40_accuracy,
            'last_40_accuracy': last_40_accuracy,
            'max_consecutive_correct': max_consecutive_correct
        }
    
    def validate_input(self, digits: List[int]) -> bool:
        """
        验证输入数据
        
        Args:
            digits: 数字序列
            
        Returns:
            是否有效
        """
        if not isinstance(digits, list):
            return False
        
        if not all(isinstance(d, int) and 0 <= d <= 9 for d in digits):
            return False
        
        return len(digits) > 0
    
    def preprocess(self, digits: List[int]) -> List[int]:
        """
        预处理数据
        
        Args:
            digits: 数字序列
            
        Returns:
            预处理后的数字序列
        """
        return digits
