﻿# core/predictors/ensemble_predictor.py
# 集成预测引擎

from typing import Dict, List, Any
from core.predictors.base_predictor import BasePredictor
from core.predictors.statistical_predictor import StatisticalPredictor
from core.predictors.pattern_predictor import PatternPredictor
from core.predictors.hybrid_predictor import HybridPredictor
from core.analyzers.composite_analyzer import CompositeAnalyzer

class EnsemblePredictor(BasePredictor):
    """集成预测引擎"""
    
    def __init__(self):
        """初始化集成预测引擎"""
        self.predictors = {
            "statistical": StatisticalPredictor(use_markov=True, markov_order=2),
            "pattern": PatternPredictor(),
            "hybrid": HybridPredictor()
        }
        self.analyzer = CompositeAnalyzer()
        self.strategy_cache = {}
    
    def predict(self, digits: List[int], length: int = 100, constant_type: str = None) -> List[int]:
        """
        智能预测数字序列
        
        Args:
            digits: 输入数字序列
            length: 预测长度
            constant_type: 常数类型（可选）
            
        Returns:
            预测的数字序列
        """
        if not self.validate_input(digits):
            return [0] * length
        
        digits = self.preprocess(digits)
        
        # 分析常数特征
        analysis_result = self.analyzer.analyze(digits)
        
        # 确定最佳预测策略
        best_strategy = self._select_best_strategy(digits, analysis_result, constant_type)
        
        # 生成基础预测
        prediction = self._generate_prediction(digits, length, best_strategy)
        
        # 使用四轨分析结果优化预测
        if "four_track" in analysis_result:
            four_track = analysis_result["four_track"]
            prediction = self._optimize_prediction_using_four_track(prediction, four_track)
        
        return prediction
    
    def _select_best_strategy(self, digits: List[int], analysis_result: Dict[str, Any], constant_type: str = None) -> str:
        """选择最佳预测策略"""
        # 检查缓存
        cache_key = f"{constant_type}_{len(digits)}"
        if cache_key in self.strategy_cache:
            return self.strategy_cache[cache_key]
        
        # 基于常数类型选择策略
        if constant_type:
            return self._select_strategy_by_type(constant_type)
        
        # 基于分析结果选择策略
        return self._select_strategy_by_analysis(analysis_result)
    
    def _select_strategy_by_type(self, constant_type: str) -> str:
        """基于常数类型选择策略"""
        constant_type = constant_type.lower()
        
        # 数学常数
        if constant_type in ["pi", "e", "phi", "sqrt2", "sqrt3", "zeta3", "catalan", "apery"]:
            return "hybrid"  # 混合策略
        
        # 物理常数
        if constant_type == "hubble_constant":
            return "pattern"  # 模式策略
        
        if constant_type == "speed_of_light":
            return "statistical"  # 统计策略
        
        if constant_type in ["light_year", "astronomical_unit"]:
            return "hybrid"  # 混合策略
        
        if constant_type in ["fine_structure_constant", "electron_mass", "planck_constant"]:
            return "hybrid"  # 混合策略
        
        # 默认策略
        return "hybrid"
    
    def _select_strategy_by_analysis(self, analysis_result: Dict[str, Any]) -> str:
        """基于分析结果选择策略"""
        # 获取关键指标
        entropy = analysis_result.get("statistical", {}).get("entropy", 0)
        pattern_density = analysis_result.get("pattern", {}).get("pattern_density", 0)
        total_patterns = analysis_result.get("pattern", {}).get("total_patterns", 0)
        symmetry = analysis_result.get("four_track", {}).get("track1", {}).get("symbol_pairs", {}).get("pair_ratio", 0)
        
        # 基于熵值和模式密度选择策略
        if entropy > 3.2 and pattern_density < 0.1:
            # 高熵值，低模式密度：接近随机
            return "statistical"
        elif pattern_density > 0.3 and total_patterns > 10:
            # 高模式密度，多模式
            return "pattern"
        elif symmetry > 0.15:
            # 高对称性
            return "hybrid"
        else:
            # 其他情况
            return "hybrid"
    
    def _generate_prediction(self, digits: List[int], length: int, strategy: str) -> List[int]:
        """基于选择的策略生成预测"""
        if strategy in self.predictors:
            predictor = self.predictors[strategy]
            
            # 实现迭代预测
            return self._predict_iterative(digits, length, predictor)
        else:
            # 默认使用混合策略
            return self._predict_iterative(digits, length, self.predictors["hybrid"])
    
    def _predict_iterative(self, digits: List[int], length: int, predictor) -> List[int]:
        """迭代预测"""
        # 直接生成完整预测，避免迭代过程中预测结果影响输入数据
        # 这样可以防止预测结果从第二位开始都是0的问题
        prediction = predictor.predict(digits, length)
        return prediction
    
    def _optimize_prediction_using_four_track(self, prediction: List[int], four_track: Dict[str, Any]) -> List[int]:
        """使用四轨分析结果优化预测"""
        # 获取轨道1信息
        track1 = four_track.get("track1", {})
        
        # 使用轨道1的配对信息优化预测
        if "symbol_pairs" in track1:
            symbol_pairs = track1["symbol_pairs"]
            if "pair_ratio" in symbol_pairs and symbol_pairs["pair_ratio"] > 0.1:
                prediction = self._optimize_using_track1_pairs(prediction, track1)
        
        return prediction
    
    def _optimize_using_track1_pairs(self, prediction: List[int], track1: Dict[str, Any]) -> List[int]:
        """使用轨道1的配对信息优化预测"""
        optimized_prediction = []
        
        # 基于九和配对规则优化预测
        nine_sum_pairs = {1: 8, 2: 7, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1, 0: 9, 9: 0}
        
        for i, digit in enumerate(prediction):
            # 对于偶数位置，考虑九和配对
            if i % 2 == 1:  # 从0开始计数，第二个数字（索引1）开始
                if digit in nine_sum_pairs:
                    # 基于前一个数字的九和配对调整
                    if optimized_prediction:
                        prev_digit = optimized_prediction[-1]
                        expected_pair = nine_sum_pairs.get(prev_digit, digit)
                        # 有一定概率使用配对数字
                        import random
                        if random.random() < 0.3:  # 30%的概率使用配对数字
                            digit = expected_pair
            
            optimized_prediction.append(digit)
        
        return optimized_prediction
    
    def evaluate_strategies(self, digits: List[int], actual: List[int]) -> Dict[str, Any]:
        """
        评估所有策略的性能
        
        Args:
            digits: 输入数字序列
            actual: 实际数字序列
            
        Returns:
            各策略的评估结果
        """
        evaluations = {}
        
        for name, predictor in self.predictors.items():
            prediction = predictor.predict(digits, len(actual))
            evaluation = self.evaluate(prediction, actual)
            evaluations[name] = evaluation
        
        # 找出最佳策略
        best_strategy = None
        best_accuracy = 0
        
        for name, eval_result in evaluations.items():
            if eval_result["accuracy"] > best_accuracy:
                best_accuracy = eval_result["accuracy"]
                best_strategy = name
        
        return {
            "evaluations": evaluations,
            "best_strategy": best_strategy,
            "best_accuracy": best_accuracy
        }
    
    def get_name(self) -> str:
        """获取预测器名称"""
        return "EnsemblePredictor"
    
    def get_version(self) -> str:
        """获取预测器版本"""
        return "2.0.0"
    
    def clear_cache(self) -> None:
        """
        清除策略缓存
        """
        self.strategy_cache.clear()
    
    def add_predictor(self, name: str, predictor: BasePredictor) -> None:
        """
        添加自定义预测器
        
        Args:
            name: 预测器名称
            predictor: 预测器实例
        """
        self.predictors[name] = predictor
    
    def remove_predictor(self, name: str) -> None:
        """
        移除预测器
        
        Args:
            name: 预测器名称
        """
        if name in self.predictors:
            del self.predictors[name]
