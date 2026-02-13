#!/usr/bin/env python3
# analyze_prediction_performance.py
# 分析预测器性能并提出改进方案

import sys
import os
from typing import List, Dict, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.predictors.ensemble_predictor import EnsemblePredictor
from core.analyzers.composite_analyzer import CompositeAnalyzer
from core.data.data_manager import DataManager

def load_constant(constant_name: str, length: int = 10000) -> List[int]:
    """加载常数数据"""
    manager = DataManager()
    return manager.load_constant(constant_name, length)

def analyze_predictor_performance(constant_name: str, training_length: int = 10000, test_length: int = 100) -> Dict[str, Any]:
    """分析预测器性能"""
    print(f"\n分析 {constant_name} 的预测性能...")
    
    # 加载数据
    data = load_constant(constant_name, training_length + test_length)
    training_data = data[:training_length]
    test_data = data[training_length:training_length + test_length]
    
    print(f"训练数据长度: {len(training_data)}")
    print(f"测试数据长度: {len(test_data)}")
    print(f"训练数据的最后20位: {' '.join(map(str, training_data[-20:]))}")
    
    # 初始化分析器和预测器
    analyzer = CompositeAnalyzer()
    predictor = EnsemblePredictor()
    
    # 分析训练数据
    analysis_result = analyzer.analyze(training_data)
    print("\n数据分析结果:")
    print(f"熵值: {analysis_result.get('statistical', {}).get('entropy', 'N/A'):.4f}")
    print(f"模式密度: {analysis_result.get('pattern', {}).get('pattern_density', 'N/A'):.4f}")
    print(f"总模式数: {analysis_result.get('pattern', {}).get('total_patterns', 'N/A')}")
    
    # 检查四轨分析结果
    four_track = analysis_result.get('four_track', {})
    print("\n四轨分析结果:")
    for track in ['track1', 'track2', 'track3', 'track4']:
        track_data = four_track.get(track, {})
        pair_ratio = track_data.get('symbol_pairs', {}).get('pair_ratio', 0)
        print(f"{track} 配对比例: {pair_ratio:.4f}")
    
    # 生成预测
    prediction = predictor.predict(training_data, test_length, constant_name)
    
    # 评估预测
    evaluation = predictor.evaluate(prediction, test_data)
    
    print("\n预测结果 (前30位):")
    print(' '.join(map(str, prediction[:30])) + ('...' if len(prediction) > 30 else ''))
    
    print("\n真实数据 (前30位):")
    print(' '.join(map(str, test_data[:30])) + ('...' if len(test_data) > 30 else ''))
    
    print(f"\n预测准确性: {evaluation['accuracy']:.2f}% ({evaluation['correct']}/{evaluation['total']})")
    
    # 分析错误
    errors = []
    for i, (pred, actual) in enumerate(zip(prediction, test_data)):
        if pred != actual:
            errors.append((i, pred, actual))
    
    print(f"\n错误分析:")
    print(f"错误总数: {len(errors)}")
    print(f"错误率: {len(errors)/len(test_data)*100:.2f}%")
    
    print("前10个错误:")
    for i, pred, actual in errors[:10]:
        print(f"  位置 {i+1}: 预测={pred}, 真实={actual}")
    if len(errors) > 10:
        print(f"  ... 还有 {len(errors)-10} 个错误")
    
    # 多样性分析
    pred_unique = len(set(prediction))
    actual_unique = len(set(test_data))
    print(f"\n多样性分析:")
    print(f"预测结果唯一数字: {pred_unique}")
    print(f"真实结果唯一数字: {actual_unique}")
    print(f"预测多样性: {'高' if pred_unique >= 8 else '中' if pred_unique >= 5 else '低'}")
    
    return {
        'constant': constant_name,
        'accuracy': evaluation['accuracy'],
        'errors': len(errors),
        'prediction_diversity': pred_unique,
        'analysis_result': analysis_result,
        'prediction': prediction,
        'actual': test_data
    }

def main():
    """主函数"""
    print("预测器性能分析工具")
    print("=" * 50)
    
    # 分析主要常数
    constants = ['pi', 'e', 'phi', 'sqrt2', 'sqrt3']
    results = []
    
    for constant in constants:
        result = analyze_predictor_performance(constant)
        results.append(result)
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("性能汇总")
    print("=" * 50)
    
    for result in results:
        print(f"{result['constant']}: {result['accuracy']:.2f}% 准确率, 多样性={result['prediction_diversity']}")
    
    # 计算平均准确率
    avg_accuracy = sum(r['accuracy'] for r in results) / len(results)
    print(f"\n平均准确率: {avg_accuracy:.2f}%")
    
    # 分析四轨分析的使用情况
    print("\n四轨分析使用情况:")
    for result in results:
        four_track = result['analysis_result'].get('four_track', {})
        track1_ratio = four_track.get('track1', {}).get('symbol_pairs', {}).get('pair_ratio', 0)
        print(f"{result['constant']}: 轨道1配对比例={track1_ratio:.4f}, {'使用九和配对优化' if track1_ratio > 0.1 else '未使用九和配对优化'}")

if __name__ == "__main__":
    main()
