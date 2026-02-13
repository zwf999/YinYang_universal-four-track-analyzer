# tests/test_predictors_and_classifiers.py
# 测试预测器和分类器组件

import unittest
from core.predictors.ensemble_predictor import EnsemblePredictor
from core.predictors.statistical_predictor import StatisticalPredictor
from core.predictors.pattern_predictor import PatternPredictor
from core.classifiers.ensemble_classifier import EnsembleClassifier
from core.classifiers.rule_based_classifier import RuleBasedClassifier
from core.classifiers.feature_based_classifier import FeatureBasedClassifier

class TestPredictorsAndClassifiers(unittest.TestCase):
    """测试预测器和分类器组件"""
    
    def setUp(self):
        """设置测试环境"""
        self.ensemble_predictor = EnsemblePredictor()
        self.statistical_predictor = StatisticalPredictor()
        self.pattern_predictor = PatternPredictor()
        self.ensemble_classifier = EnsembleClassifier()
        self.rule_based_classifier = RuleBasedClassifier()
        self.feature_based_classifier = FeatureBasedClassifier()
        
        # 测试数据
        self.test_digits = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3, 4, 5]
        self.pi_digits = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9]
        self.e_digits = [2, 7, 1, 8, 2, 8, 1, 8, 2, 8, 4, 5, 9, 0, 4]
    
    def test_ensemble_predictor(self):
        """测试集成预测器"""
        # 预测数据
        prediction = self.ensemble_predictor.predict(self.pi_digits, length=5)
        
        # 验证预测长度
        self.assertEqual(len(prediction), 5)
        
        # 验证预测数字范围
        for digit in prediction:
            self.assertGreaterEqual(digit, 0)
            self.assertLessEqual(digit, 9)
    
    def test_statistical_predictor(self):
        """测试统计预测器"""
        # 预测数据
        prediction = self.statistical_predictor.predict(self.test_digits, length=3)
        
        # 验证预测长度
        self.assertEqual(len(prediction), 3)
        
        # 验证预测数字范围
        for digit in prediction:
            self.assertGreaterEqual(digit, 0)
            self.assertLessEqual(digit, 9)
    
    def test_pattern_predictor(self):
        """测试模式预测器"""
        # 创建有模式的数据
        pattern_digits = [1, 2, 3, 1, 2, 3, 1, 2, 3]
        
        # 预测数据
        prediction = self.pattern_predictor.predict(pattern_digits, length=3)
        
        # 验证预测长度
        self.assertEqual(len(prediction), 3)
        
        # 验证预测数字范围
        for digit in prediction:
            self.assertGreaterEqual(digit, 0)
            self.assertLessEqual(digit, 9)
    
    def test_ensemble_classifier(self):
        """测试集成分类器"""
        # 分类常数
        pi_classification = self.ensemble_classifier.classify('pi', self.pi_digits)
        e_classification = self.ensemble_classifier.classify('e', self.e_digits)
        
        # 验证结果结构
        for classification in [pi_classification, e_classification]:
            self.assertIn('type', classification)
            self.assertIn('confidence', classification)
        
        # 验证置信度范围
        self.assertGreaterEqual(pi_classification['confidence'], 0)
        self.assertLessEqual(pi_classification['confidence'], 1)
        self.assertGreaterEqual(e_classification['confidence'], 0)
        self.assertLessEqual(e_classification['confidence'], 1)
    
    def test_rule_based_classifier(self):
        """测试基于规则的分类器"""
        # 分类已知常数
        pi_classification = self.rule_based_classifier.classify('pi', self.pi_digits)
        e_classification = self.rule_based_classifier.classify('e', self.e_digits)
        
        # 验证结果结构
        self.assertIn('type', pi_classification)
        self.assertIn('confidence', pi_classification)
        
        # 验证分类结果不为空
        self.assertIsNotNone(pi_classification['type'])
        self.assertIsNotNone(e_classification['type'])
    
    def test_feature_based_classifier(self):
        """测试基于特征的分类器"""
        # 分类数据
        classification = self.feature_based_classifier.classify('test_constant', self.test_digits)
        
        # 验证结果结构
        self.assertIn('type', classification)
        self.assertIn('confidence', classification)
        
        # 验证置信度范围
        self.assertGreaterEqual(classification['confidence'], 0)
        self.assertLessEqual(classification['confidence'], 1)
    
    def test_classification_consistency(self):
        """测试分类一致性"""
        # 对同一数据进行多次分类
        classifications = []
        for _ in range(3):
            classification = self.ensemble_classifier.classify('pi', self.pi_digits)
            classifications.append(classification['type'])
        
        # 验证分类结果一致
        self.assertEqual(len(set(classifications)), 1)
    
    def test_prediction_consistency(self):
        """测试预测一致性"""
        # 对同一数据进行多次预测
        predictions = []
        for _ in range(3):
            prediction = self.ensemble_predictor.predict(self.pi_digits, length=3)
            predictions.append(tuple(prediction))
        
        # 验证预测结果应该有一定的一致性（但可能不完全相同）
        # 这里我们只验证预测长度和范围，不要求完全相同
        for pred in predictions:
            self.assertEqual(len(pred), 3)
            for digit in pred:
                self.assertGreaterEqual(digit, 0)
                self.assertLessEqual(digit, 9)
    
    def test_edge_cases(self):
        """测试边界情况"""
        # 空数据预测
        empty_prediction = self.ensemble_predictor.predict([], length=3)
        self.assertEqual(len(empty_prediction), 3)
        
        # 空数据分类
        empty_classification = self.ensemble_classifier.classify('unknown', [])
        self.assertIn('type', empty_classification)
        self.assertIn('confidence', empty_classification)
        
        # 短数据预测
        short_digits = [1, 2, 3]
        short_prediction = self.ensemble_predictor.predict(short_digits, length=5)
        self.assertEqual(len(short_prediction), 5)

if __name__ == '__main__':
    unittest.main()