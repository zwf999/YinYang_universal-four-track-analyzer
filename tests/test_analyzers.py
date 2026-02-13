# tests/test_analyzers.py
# 测试分析器组件

import unittest
from core.analyzers.composite_analyzer import CompositeAnalyzer
from core.analyzers.four_track_analyzer import FourTrackAnalyzer
from core.analyzers.statistical_analyzer import StatisticalAnalyzer
from core.analyzers.pattern_analyzer import PatternAnalyzer

class TestAnalyzers(unittest.TestCase):
    """测试分析器组件"""
    
    def setUp(self):
        """设置测试环境"""
        self.composite_analyzer = CompositeAnalyzer()
        self.four_track_analyzer = FourTrackAnalyzer()
        self.statistical_analyzer = StatisticalAnalyzer()
        self.pattern_analyzer = PatternAnalyzer()
        
        # 测试数据
        self.test_digits = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3, 4, 5]
        self.pi_digits = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9]
    
    def test_composite_analyzer(self):
        """测试复合分析器"""
        # 分析数据
        result = self.composite_analyzer.analyze(self.test_digits)
        
        # 验证结果结构
        self.assertIn('four_track', result)
        self.assertIn('pattern', result)
        self.assertIn('statistical', result)
        self.assertIn('summary', result)
        self.assertIn('scores', result)
        self.assertIn('fingerprint', result)
        self.assertIn('consistency', result)
        
        # 验证四轨分析
        four_track = result['four_track']
        self.assertIn('track1', four_track)
        self.assertIn('track2', four_track)
        self.assertIn('track3', four_track)
        self.assertIn('track4', four_track)
        
        # 验证模式分析
        pattern = result['pattern']
        self.assertIn('patterns', pattern)
        self.assertIn('pattern_density', pattern)
        self.assertIn('total_patterns', pattern)
        
        # 验证统计分析
        statistical = result['statistical']
        self.assertIn('entropy', statistical)
        self.assertIn('mean', statistical)
        self.assertIn('std', statistical)
        self.assertIn('digit_distribution', statistical)
    
    def test_four_track_analyzer(self):
        """测试四轨分析器"""
        # 分析数据
        result = self.four_track_analyzer.analyze(self.test_digits)
        
        # 验证结果结构
        self.assertIn('track1', result)
        self.assertIn('track2', result)
        self.assertIn('track3', result)
        self.assertIn('track4', result)
        self.assertIn('direct_pairing', result)
        self.assertIn('fingerprint', result)
        
        # 验证轨道数据结构（包含正向和反向）
        for track_name in ['track1', 'track2', 'track3', 'track4']:
            track = result[track_name]
            self.assertIn('forward', track)
            self.assertIn('backward', track)
            self.assertIn('symmetry', track)
            
            # 验证正向分析结果
            forward = track['forward']
            self.assertIn('window_count', forward)
            self.assertIn('nine_sum_pairs', forward)
            self.assertIn('yinyang', forward)
            
            # 验证反向分析结果
            backward = track['backward']
            self.assertIn('window_count', backward)
            self.assertIn('nine_sum_pairs', backward)
            self.assertIn('yinyang', backward)
            
            # 验证对称性结果
            symmetry = track['symmetry']
            self.assertIn('pair_ratio_diff', symmetry)
            self.assertIn('pair_ratio_similarity', symmetry)
            self.assertIn('yang_percent_diff', symmetry)
            self.assertIn('yang_percent_similarity', symmetry)
            self.assertIn('overall_symmetry', symmetry)
            
            # 验证九和配对结构
            nine_sum = forward['nine_sum_pairs']
            self.assertIn('valid_pairs', nine_sum)
            self.assertIn('total_pairs', nine_sum)
            self.assertIn('pair_ratio', nine_sum)
            
            # 验证阴阳结构
            yinyang = forward['yinyang']
            self.assertIn('yang_count', yinyang)
            self.assertIn('yin_count', yinyang)
            self.assertIn('ratio', yinyang)
            self.assertIn('yang_percent', yinyang)
    
    def test_statistical_analyzer(self):
        """测试统计分析器"""
        # 分析数据
        result = self.statistical_analyzer.analyze(self.test_digits)
        
        # 验证结果结构
        self.assertIn('digit_distribution', result)
        self.assertIn('entropy', result)
        self.assertIn('mean', result)
        self.assertIn('std', result)
        self.assertIn('variance', result)
        self.assertIn('skewness', result)
        self.assertIn('kurtosis', result)
        self.assertIn('correlation', result)
        self.assertIn('runs_analysis', result)
        self.assertIn('percentiles', result)
        self.assertIn('total_digits', result)
        
        # 验证统计值范围
        self.assertGreaterEqual(result['mean'], 0)
        self.assertLessEqual(result['mean'], 9)
        self.assertGreaterEqual(result['std'], 0)
        self.assertGreaterEqual(result['entropy'], 0)
        self.assertLessEqual(result['entropy'], 4)
        
        # 验证数字分布
        digit_dist = result['digit_distribution']
        for digit in range(10):
            self.assertIn(digit, digit_dist)
            self.assertGreaterEqual(digit_dist[digit], 0)
    
    def test_pattern_analyzer(self):
        """测试模式分析器"""
        # 创建有模式的数据
        pattern_digits = [1, 2, 3, 1, 2, 3, 4, 5, 4, 5, 6, 7, 6, 7]
        
        # 分析数据
        result = self.pattern_analyzer.analyze(pattern_digits)
        
        # 验证结果结构
        self.assertIn('patterns', result)
        self.assertIn('repetition_score', result)
        self.assertIn('pair_score', result)
        self.assertIn('sequential_score', result)
        self.assertIn('pattern_density', result)
        self.assertIn('pattern_distribution', result)
        self.assertIn('total_patterns', result)
        
        # 验证模式检测
        patterns = result['patterns']
        self.assertGreater(len(patterns), 0)
        
        # 验证模式结构
        for pattern in patterns:
            self.assertIn('type', pattern)
            self.assertIn('pattern', pattern)
            self.assertIn('length', pattern)
            self.assertIn('score', pattern)
    
    def test_sliding_window_analysis(self):
        """测试滑动窗口分析"""
        # 分析数据
        result = self.composite_analyzer.analyze(self.pi_digits)
        
        # 验证结果包含统计信息
        self.assertIn('statistical', result)
        statistical = result['statistical']
        
        # 验证统计分析包含必要的字段
        self.assertIn('entropy', statistical)
        self.assertIn('mean', statistical)
        self.assertIn('std', statistical)
        self.assertIn('runs_analysis', statistical)
        self.assertIn('percentiles', statistical)
    
    def test_edge_cases(self):
        """测试边界情况"""
        # 空数据
        empty_digits = []
        empty_result = self.composite_analyzer.analyze(empty_digits)
        self.assertIn('error', empty_result)
        self.assertEqual(empty_result['error'], 'Invalid input')
        
        # 单数字
        single_digit = [5]
        single_result = self.composite_analyzer.analyze(single_digit)
        self.assertIn('statistical', single_result)
        self.assertIn('total_digits', single_result['statistical'])
        self.assertEqual(single_result['statistical']['total_digits'], 1)
        
        # 重复数字
        repeated_digits = [1, 1, 1, 1, 1, 1]
        repeated_result = self.composite_analyzer.analyze(repeated_digits)
        self.assertIn('statistical', repeated_result)
        self.assertIn('entropy', repeated_result['statistical'])
        self.assertLess(repeated_result['statistical']['entropy'], 1)  # 低熵值

if __name__ == '__main__':
    unittest.main()