# core/classifiers/base_classifier.py
# 分类器基类

from abc import ABC, abstractmethod
from typing import Dict, List, Any

class BaseClassifier(ABC):
    """分类器基类"""
    
    @abstractmethod
    def classify(self, digits: List[int], name: str = None) -> Dict[str, Any]:
        """
        分类数字序列
        
        Args:
            digits: 输入数字序列
            name: 常数名称（可选）
            
        Returns:
            分类结果
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """
        获取分类器名称
        
        Returns:
            分类器名称
        """
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """
        获取分类器版本
        
        Returns:
            分类器版本
        """
        pass
    
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
    
    def evaluate(self, classifications: List[Dict[str, Any]], actual_types: List[str]) -> Dict[str, Any]:
        """
        评估分类器性能
        
        Args:
            classifications: 分类结果列表
            actual_types: 实际类型列表
            
        Returns:
            评估结果
        """
        if not classifications or not actual_types:
            return {
                'accuracy': 0,
                'correct': 0,
                'total': 0,
                'confusion_matrix': {},
                'class_accuracy': {}
            }
        
        correct = 0
        total = min(len(classifications), len(actual_types))
        confusion_matrix = {}
        class_correct = {}
        class_total = {}
        
        for i in range(total):
            predicted_type = classifications[i].get('type', 'unknown')
            actual_type = actual_types[i]
            
            # 更新混淆矩阵
            if actual_type not in confusion_matrix:
                confusion_matrix[actual_type] = {}
            if predicted_type not in confusion_matrix[actual_type]:
                confusion_matrix[actual_type][predicted_type] = 0
            confusion_matrix[actual_type][predicted_type] += 1
            
            # 更新类统计
            if actual_type not in class_correct:
                class_correct[actual_type] = 0
            if actual_type not in class_total:
                class_total[actual_type] = 0
            class_total[actual_type] += 1
            
            # 计算正确分类
            if predicted_type == actual_type:
                correct += 1
                class_correct[actual_type] += 1
        
        accuracy = correct / total if total > 0 else 0
        
        # 计算各类别准确率
        class_accuracy = {}
        for class_type in class_total:
            class_accuracy[class_type] = class_correct.get(class_type, 0) / class_total[class_type]
        
        return {
            'accuracy': accuracy,
            'correct': correct,
            'total': total,
            'confusion_matrix': confusion_matrix,
            'class_accuracy': class_accuracy
        }
