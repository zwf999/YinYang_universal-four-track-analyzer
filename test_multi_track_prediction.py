#!/usr/bin/env python3
# 测试多轨道协同预测方法

import sys
import os
from core.predictors.pattern_predictor import PatternPredictor
from core.analyzers.four_track_analyzer import FourTrackAnalyzer

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_multi_track_prediction():
    """测试多轨道协同预测方法"""
    print("测试多轨道协同预测方法...")
    
    # 测试数据：π的前100位数字
    pi_digits = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9, 3, 2, 3, 8, 4, 6, 2, 6, 4, 3, 3, 8, 3, 2, 7, 9, 5, 0, 2, 8, 8, 4, 1, 9, 7, 1, 6, 9, 3, 9, 9, 3, 7, 5, 1, 0, 5, 8, 2, 0, 9, 7, 4, 9, 4, 4, 5, 9, 2, 3, 0, 7, 8, 1, 6, 4, 0, 6, 2, 8, 6, 2, 0, 8, 9, 9, 8, 6, 2, 8, 0, 3, 4, 8, 2, 5, 3, 4, 2, 1, 1, 7, 0, 6, 7, 9]
    
    # 创建预测器和分析器
    predictor = PatternPredictor()
    four_track_analyzer = FourTrackAnalyzer()
    
    # 测试不同长度的预测
    test_lengths = [10, 20, 30]
    
    for length in test_lengths:
        print(f"\n测试预测长度: {length}")
        
        # 分割数据：使用前80位作为训练数据，预测后20位
        train_data = pi_digits[:80]
        test_data = pi_digits[80:80+length]
        
        # 预测数字序列
        prediction = predictor.predict(train_data, length)
        
        # 打印预测结果和真实结果
        print(f"预测结果: {prediction}")
        print(f"真实结果: {test_data}")
        
        # 分析预测结果的质量
        # 1. 数字多样性
        unique_digits = len(set(prediction))
        print(f"数字多样性: {unique_digits}/10")
        
        # 2. 九和配对比例
        analysis_result = four_track_analyzer.analyze(prediction)
        if 'direct_pairing' in analysis_result and 'track2' in analysis_result['direct_pairing']:
            track2_result = analysis_result['direct_pairing']['track2']
            forward_pair_ratio = track2_result['forward']['pair_ratio']
            print(f"九和配对比例: {forward_pair_ratio:.4f}")
        else:
            print("九和配对比例: 无法计算")
        
        # 3. 连续重复数字的比例
        repeat_count = 0
        for i in range(len(prediction) - 1):
            if prediction[i] == prediction[i+1]:
                repeat_count += 1
        repeat_ratio = repeat_count / (len(prediction) - 1) if len(prediction) > 1 else 0
        print(f"连续重复比例: {repeat_ratio:.4f}")
        
        # 4. 与测试数据的匹配率
        if test_data:
            match_count = 0
            for i in range(min(len(prediction), len(test_data))):
                if prediction[i] == test_data[i]:
                    match_count += 1
            match_ratio = match_count / min(len(prediction), len(test_data))
            print(f"与测试数据的匹配率: {match_ratio:.4f}")
        
        # 5. 计算所有轨道的配对比例
        print("各轨道配对比例:")
        for track in ['track2', 'track3', 'track4']:
            if 'direct_pairing' in analysis_result and track in analysis_result['direct_pairing']:
                track_result = analysis_result['direct_pairing'][track]
                forward_pair_ratio = track_result['forward']['pair_ratio']
                print(f"  {track}: {forward_pair_ratio:.4f}")
        
        # 6. 计算预测结果的对称性
        if 'reverse_analysis' in analysis_result:
            symmetry = analysis_result['reverse_analysis']['overall_symmetry']
            print(f"预测结果对称性: {symmetry:.4f}")

if __name__ == "__main__":
    test_multi_track_prediction()
