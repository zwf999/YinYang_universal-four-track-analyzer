# core/classifiers/ensemble_classifier.py
# 集成分类器

from typing import Dict, List, Any
from collections import defaultdict
from core.classifiers.base_classifier import BaseClassifier
from core.classifiers.rule_based_classifier import RuleBasedClassifier
from core.classifiers.feature_based_classifier import FeatureBasedClassifier

class EnsembleClassifier(BaseClassifier):
    """集成分类器"""
    
    def __init__(self):
        """初始化集成分类器"""
        self.classifiers = {
            'rule_based': RuleBasedClassifier(),
            'feature_based': FeatureBasedClassifier()
        }
        self.weights = {
            'rule_based': 0.6,  # 基于规则的分类器权重较高
            'feature_based': 0.4  # 基于特征的分类器权重
        }
    
    def classify(self, digits: List[int], name: str = None) -> Dict[str, Any]:
        """
        集成多个分类器的结果
        
        Args:
            digits: 输入数字序列
            name: 常数名称（可选）
            
        Returns:
            集成分类结果
        """
        if not self.validate_input(digits):
            return {
                'type': 'unknown',
                'subtype': 'unknown',
                'description': '未知常数',
                'confidence': 0.0,
                'classifications': {}
            }
        
        digits = self.preprocess(digits)
        
        # 获取所有分类器的结果
        classifications = {}
        for classifier_name, classifier in self.classifiers.items():
            classifications[classifier_name] = classifier.classify(digits, name)
        
        # 集成分类结果
        ensemble_result = self._ensemble_classifications(classifications)
        
        # 整合结果
        result = {
            'type': ensemble_result['type'],
            'subtype': ensemble_result['subtype'],
            'description': ensemble_result['description'],
            'confidence': ensemble_result['confidence'],
            'classifications': classifications,
            'ensemble_summary': {
                'best_classifier': ensemble_result['best_classifier'],
                'weighted_votes': ensemble_result['weighted_votes'],
                'consensus_strength': ensemble_result['consensus_strength']
            }
        }
        
        return result
    
    def _ensemble_classifications(self, classifications: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """集成多个分类结果"""
        # 计算类型投票
        type_votes = defaultdict(float)
        subtype_votes = defaultdict(float)
        
        # 收集所有分类器的投票
        for classifier_name, classification in classifications.items():
            weight = self.weights.get(classifier_name, 1.0)
            confidence = classification.get('confidence', 0.5)
            effective_weight = weight * confidence
            
            # 类型投票
            type_name = classification.get('type', 'unknown')
            type_votes[type_name] += effective_weight
            
            # 子类型投票
            subtype_name = classification.get('subtype', 'unknown')
            subtype_votes[subtype_name] += effective_weight
        
        # 确定最佳类型
        if type_votes:
            best_type = max(type_votes.items(), key=lambda x: x[1])[0]
            best_type_score = type_votes[best_type]
        else:
            best_type = 'unknown'
            best_type_score = 0
        
        # 确定最佳子类型
        if subtype_votes:
            best_subtype = max(subtype_votes.items(), key=lambda x: x[1])[0]
        else:
            best_subtype = 'unknown'
        
        # 计算共识强度
        total_weight = sum(type_votes.values())
        consensus_strength = best_type_score / total_weight if total_weight > 0 else 0
        
        # 确定最佳分类器
        best_classifier = None
        best_classifier_score = 0
        
        for classifier_name, classification in classifications.items():
            classification_score = classification.get('confidence', 0)
            if classification_score > best_classifier_score:
                best_classifier_score = classification_score
                best_classifier = classifier_name
        
        # 获取描述
        description = self._get_description(best_type, best_subtype)
        
        return {
            'type': best_type,
            'subtype': best_subtype,
            'description': description,
            'confidence': consensus_strength,
            'best_classifier': best_classifier,
            'weighted_votes': dict(type_votes),
            'consensus_strength': consensus_strength
        }
    
    def _get_description(self, type_name: str, subtype: str) -> str:
        """获取类别描述"""
        descriptions = {
            'mathematical': {
                'irrational': '无理数学常数',
                'transcendental': '超越数学常数',
                'algebraic': '代数数学常数',
                'unknown': '数学常数'
            },
            'physical': {
                'exact': '精确物理常数',
                'fundamental': '基本物理常数',
                'derived': '导出物理常数',
                'experimental': '实验物理常数',
                'unknown': '物理常数'
            },
            'unknown': {
                'unknown': '未知常数'
            }
        }
        
        return descriptions.get(type_name, {}).get(subtype, '未知常数')
    
    def evaluate(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        评估集成分类器性能
        
        Args:
            test_cases: 测试用例列表，每个测试用例包含'digits'、'name'和'actual_type'
            
        Returns:
            评估结果
        """
        if not test_cases:
            return {
                'accuracy': 0,
                'correct': 0,
                'total': 0,
                'classifier_accuracies': {},
                'confusion_matrix': {}
            }
        
        correct = 0
        total = len(test_cases)
        classifier_correct = defaultdict(int)
        classifier_total = defaultdict(int)
        confusion_matrix = defaultdict(lambda: defaultdict(int))
        
        for test_case in test_cases:
            digits = test_case.get('digits', [])
            name = test_case.get('name', None)
            actual_type = test_case.get('actual_type', 'unknown')
            
            # 获取集成分类结果
            result = self.classify(digits, name)
            predicted_type = result.get('type', 'unknown')
            
            # 更新混淆矩阵
            confusion_matrix[actual_type][predicted_type] += 1
            
            # 检查是否正确
            if predicted_type == actual_type:
                correct += 1
            
            # 检查每个分类器的结果
            for classifier_name, classification in result.get('classifications', {}).items():
                classifier_predicted = classification.get('type', 'unknown')
                classifier_total[classifier_name] += 1
                if classifier_predicted == actual_type:
                    classifier_correct[classifier_name] += 1
        
        # 计算准确率
        accuracy = correct / total if total > 0 else 0
        
        # 计算每个分类器的准确率
        classifier_accuracies = {}
        for classifier_name in self.classifiers:
            if classifier_total.get(classifier_name, 0) > 0:
                classifier_accuracies[classifier_name] = classifier_correct.get(classifier_name, 0) / classifier_total[classifier_name]
            else:
                classifier_accuracies[classifier_name] = 0
        
        return {
            'accuracy': accuracy,
            'correct': correct,
            'total': total,
            'classifier_accuracies': classifier_accuracies,
            'confusion_matrix': dict(confusion_matrix),
            'improvement': self._calculate_improvement(accuracy, classifier_accuracies)
        }
    
    def _calculate_improvement(self, ensemble_accuracy: float, classifier_accuracies: Dict[str, float]) -> float:
        """计算集成分类器相对于单个分类器的改进"""
        if not classifier_accuracies:
            return 0
        
        # 计算单个分类器的平均准确率
        avg_classifier_accuracy = sum(classifier_accuracies.values()) / len(classifier_accuracies)
        
        # 计算改进百分比
        if avg_classifier_accuracy > 0:
            improvement = (ensemble_accuracy - avg_classifier_accuracy) / avg_classifier_accuracy
        else:
            improvement = ensemble_accuracy
        
        return improvement
    
    def set_weights(self, weights: Dict[str, float]) -> None:
        """
        设置分类器权重
        
        Args:
            weights: 分类器权重字典
        """
        for classifier_name, weight in weights.items():
            if classifier_name in self.classifiers:
                self.weights[classifier_name] = weight
    
    def add_classifier(self, name: str, classifier: BaseClassifier, weight: float = 0.3) -> None:
        """
        添加自定义分类器
        
        Args:
            name: 分类器名称
            classifier: 分类器实例
            weight: 分类器权重
        """
        self.classifiers[name] = classifier
        self.weights[name] = weight
    
    def remove_classifier(self, name: str) -> None:
        """
        移除分类器
        
        Args:
            name: 分类器名称
        """
        if name in self.classifiers:
            del self.classifiers[name]
        if name in self.weights:
            del self.weights[name]
    
    def get_name(self) -> str:
        """获取分类器名称"""
        return "EnsembleClassifier"
    
    def get_version(self) -> str:
        """获取分类器版本"""
        return "2.0.0"
