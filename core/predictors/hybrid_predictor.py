# core/predictors/hybrid_predictor.py
# 混合预测器

from typing import Dict, List, Any
from collections import defaultdict
from core.predictors.base_predictor import BasePredictor
from core.predictors.statistical_predictor import StatisticalPredictor
from core.predictors.pattern_predictor import PatternPredictor

class HybridPredictor(BasePredictor):
    """混合预测器"""
    
    def __init__(self):
        """初始化混合预测器"""
        self.predictors = {
            'statistical': StatisticalPredictor(use_markov=True, markov_order=2),
            'pattern': PatternPredictor()
        }
        self.weights = {
            'statistical': 0.5,
            'pattern': 0.5
        }
    
    def predict(self, digits: List[int], length: int = 100) -> List[int]:
        """
        混合多个预测器的结果
        
        Args:
            digits: 输入数字序列
            length: 预测长度
            
        Returns:
            预测的数字序列
        """
        if not self.validate_input(digits):
            return [0] * length
        
        digits = self.preprocess(digits)
        
        # 获取所有预测器的预测结果
        predictions = {}
        for name, predictor in self.predictors.items():
            predictions[name] = predictor.predict(digits, length)
        
        # 混合预测结果
        hybrid_prediction = self._combine_predictions(predictions, length)
        
        return hybrid_prediction
    
    def _combine_predictions(self, predictions: Dict[str, List[int]], length: int) -> List[int]:
        """混合多个预测结果"""
        hybrid_prediction = []
        
        for i in range(length):
            # 收集所有预测器在当前位置的预测
            position_predictions = {}
            for name, pred in predictions.items():
                if i < len(pred):
                    position_predictions[name] = pred[i]
            
            if not position_predictions:
                hybrid_prediction.append(0)
                continue
            
            # 使用加权投票选择最佳预测
            best_digit = self._weighted_vote(position_predictions, i)
            hybrid_prediction.append(best_digit)
        
        return hybrid_prediction
    
    def _weighted_vote(self, position_predictions: Dict[str, int], position: int) -> int:
        """加权投票选择最佳预测"""
        votes = defaultdict(float)
        
        for name, digit in position_predictions.items():
            weight = self.weights.get(name, 1.0)
            votes[digit] += weight
        
        # 选择得票最高的数字
        if votes:
            best_digit = max(votes.items(), key=lambda x: x[1])[0]
            return best_digit
        else:
            return 0
    
    def _adaptive_weighting(self, predictions: Dict[str, List[int]], actual: List[int]) -> None:
        """基于实际结果自适应调整权重"""
        if not actual:
            return
        
        # 评估每个预测器的性能
        performances = {}
        for name, pred in predictions.items():
            evaluator = BasePredictor()
            evaluation = evaluator.evaluate(pred, actual)
            performances[name] = evaluation['accuracy']
        
        # 基于性能调整权重
        total_performance = sum(performances.values())
        if total_performance > 0:
            for name, performance in performances.items():
                self.weights[name] = performance / total_performance
    
    def set_weights(self, weights: Dict[str, float]) -> None:
        """
        设置预测器权重
        
        Args:
            weights: 预测器权重字典
        """
        for name, weight in weights.items():
            if name in self.predictors:
                self.weights[name] = weight
    
    def add_predictor(self, name: str, predictor: BasePredictor, weight: float = 1.0) -> None:
        """
        添加自定义预测器
        
        Args:
            name: 预测器名称
            predictor: 预测器实例
            weight: 预测器权重
        """
        self.predictors[name] = predictor
        self.weights[name] = weight
    
    def remove_predictor(self, name: str) -> None:
        """
        移除预测器
        
        Args:
            name: 预测器名称
        """
        if name in self.predictors:
            del self.predictors[name]
        if name in self.weights:
            del self.weights[name]
    
    def get_predictions(self, digits: List[int], length: int = 100) -> Dict[str, List[int]]:
        """
        获取所有预测器的预测结果
        
        Args:
            digits: 输入数字序列
            length: 预测长度
            
        Returns:
            所有预测器的预测结果
        """
        predictions = {}
        for name, predictor in self.predictors.items():
            predictions[name] = predictor.predict(digits, length)
        return predictions
    
    def get_name(self) -> str:
        """获取预测器名称"""
        return "HybridPredictor"
    
    def get_version(self) -> str:
        """获取预测器版本"""
        return "2.0.0"
    
    def get_weights(self) -> Dict[str, float]:
        """
        获取预测器权重
        
        Returns:
            预测器权重字典
        """
        return self.weights.copy()
    
    def get_predictors(self) -> Dict[str, BasePredictor]:
        """
        获取所有预测器
        
        Returns:
            预测器字典
        """
        return self.predictors.copy()
