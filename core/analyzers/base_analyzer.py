# core/analyzers/base_analyzer.py
# 分析器基类

from abc import ABC, abstractmethod
from typing import Dict, List, Any

class BaseAnalyzer(ABC):
    """分析器基类"""
    
    @abstractmethod
    def analyze(self, digits: List[int]) -> Dict[str, Any]:
        """
        分析数字序列
        
        Args:
            digits: 数字序列
            
        Returns:
            分析结果
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """
        获取分析器名称
        
        Returns:
            分析器名称
        """
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """
        获取分析器版本
        
        Returns:
            分析器版本
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
