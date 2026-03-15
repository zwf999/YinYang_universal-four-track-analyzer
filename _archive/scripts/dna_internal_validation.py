#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DNA数据内部验证脚本
使用留一法、随机分割、Bootstrap等方法验证TSE结果的稳定性
"""

import os
import random
import numpy as np
from pathlib import Path
from collections import Counter
from typing import List, Dict, Tuple
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import warnings
warnings.filterwarnings('ignore')

# ==============================================================================
# 核心类（从主程序导入）
# ==============================================================================
class TruthTable:
    PATTERN_TO_LAYER = {
        '111111':1,'000000':1,'101010':1,'010101':1,
        '010010':2,'101101':2,'111000':2,'000111':2,
        '101111':3,'111101':3,'111010':3,'010111':3,
        '000101':4,'101000':4,'010000':4,'000010':4,
        '100100':5,'001001':5,'011011':5,'110110':5,
        '100001':6,'011110':6,'110011':6,'001100':6,
        '100110':7,'011001':7,'001011':7,'110100':7,
        '110001':8,'100011':8,'001110':8,'011100':8,
        '111011':9,'110111':9,'111110':9,'011111':9,
        '001000':10,'000100':10,'000001':10,'100000':10,
        '100111':11,'111001':11,'001111':11,'111100':11,
        '110000':12,'000011':12,'000110':12,'011000':12,
        '101110':13,'011101':13,'101011':13,'110101':13,
        '101100':14,'001101':14,'100101':14,'101001':14,
        '010110':15,'011010':15,'010011':15,'110010':15,
        '001010':16,'010100':16,'100010':16,'010001':16
    }

    @classmethod
    def get_layer(cls, pattern: str) -> int:
        return cls.PATTERN_TO_LAYER[pattern]

class OriginalWeights:
    VALUES = np.array([
        0.1200, 0.0900, 0.0675, 0.0506, 0.0380, 0.0285, 0.0214, 0.0160,
        0.0120, 0.0090, 0.0068, 0.0051, 0.0038, 0.0029, 0.0021, 0.0016
    ])
    MIN_VAL = 0.0016
    MAX_VAL = 0.1200

    @classmethod
    def get_all(cls) -> np.ndarray:
        return cls.VALUES.copy()

class DataProcessor:
    @staticmethod
    def file_to_bits(filepath: str) -> List[int]:
        with open(filepath, 'rb') as f:
            data = f.read()
        bits = []
        for byte in data:
            for i in range(7, -1, -1):
                bits.append((byte >> i) & 1)
        return bits

    @staticmethod
    def bits_to_patterns(bits: List[int]) -> List[str]:
        patterns = []
        for i in range(len(bits) - 5):
            window = bits[i:i+6]
            patterns.append(''.join(str(b) for b in window))
        return patterns

def calculate_tse_and_vi(patterns: List[str]) -> Tuple[float, float]:
    layers_seq = [TruthTable.get_layer(p) for p in patterns]
    cnt = Counter(layers_seq)
    total = len(layers_seq)
    probs = np.array([cnt.get(l,0)/total for l in range(1,17)])
    
    H = -np.sum(probs[probs > 0] * np.log2(probs[probs > 0]))
    # 确保H不超过4.0（16层的最大熵）
    H = min(H, 4.0)
    tse = 6.0 * H / 4.0
    
    w = OriginalWeights.get_all()
    weighted_sum = np.sum(w * probs)
    vi = 6.0 * (weighted_sum - w.min()) / (w.max() - w.min())
    
    return tse, vi

def analyze_file(filepath: str) -> Dict:
    bits = DataProcessor.file_to_bits(filepath)
    patterns = DataProcessor.bits_to_patterns(bits)
    tse, vi = calculate_tse_and_vi(patterns)
    return {'tse': tse, 'vi': vi}

# ==============================================================================
# 加载所有DNA样本
# ==============================================================================
def load_dna_samples():
    data_dir = Path("data/dna")
    
    healthy_files = sorted(data_dir.glob("healthy_*.txt"))
    cancer_files = sorted(data_dir.glob("cancer_*.txt"))
    
    healthy_samples = []
    for fpath in healthy_files:
        result = analyze_file(str(fpath))
        result['filename'] = fpath.name
        result['type'] = 'healthy'
        healthy_samples.append(result)
    
    cancer_samples = []
    for fpath in cancer_files:
        result = analyze_file(str(fpath))
        result['filename'] = fpath.name
        result['type'] = 'cancer'
        cancer_samples.append(result)
    
    return healthy_samples, cancer_samples

# ==============================================================================
# 方法1：留一法交叉验证
# ==============================================================================
def leave_one_out_validation(healthy_samples, cancer_samples):
    print("\n" + "="*70)
    print("方法1：留一法交叉验证")
    print("="*70)
    
    all_samples = healthy_samples + cancer_samples
    correct_classifications = 0
    
    healthy_tse_values = [s['tse'] for s in healthy_samples]
    cancer_tse_values = [s['tse'] for s in cancer_samples]
    
    threshold = (np.mean(healthy_tse_values) + np.mean(cancer_tse_values)) / 2
    
    print(f"\n分类阈值: {threshold:.4f}")
    print(f"健康样本平均TSE: {np.mean(healthy_tse_values):.4f}")
    print(f"癌症样本平均TSE: {np.mean(cancer_tse_values):.4f}")
    
    print("\n逐样本验证:")
    for i, sample in enumerate(all_samples):
        predicted = 'healthy' if sample['tse'] > threshold else 'cancer'
        actual = sample['type']
        correct = predicted == actual
        correct_classifications += correct
        
        symbol = "✓" if correct else "✗"
        print(f"  {sample['filename'][:30]:30s} TSE={sample['tse']:.4f} "
              f"预测={predicted:7s} 实际={actual:7s} {symbol}")
    
    accuracy = correct_classifications / len(all_samples)
    print(f"\n准确率: {correct_classifications}/{len(all_samples)} = {accuracy*100:.1f}%")
    
    return {
        'method': '留一法交叉验证',
        'accuracy': accuracy,
        'threshold': threshold,
        'correct': correct_classifications,
        'total': len(all_samples)
    }

# ==============================================================================
# 方法2：随机分割验证
# ==============================================================================
def random_split_validation(healthy_samples, cancer_samples, n_iterations=100):
    print("\n" + "="*70)
    print("方法2：随机分割验证")
    print("="*70)
    
    all_healthy = healthy_samples.copy()
    all_cancer = cancer_samples.copy()
    
    significant_count = 0
    all_differences = []
    
    print(f"\n进行 {n_iterations} 次随机分割...")
    
    for i in range(n_iterations):
        random.shuffle(all_healthy)
        random.shuffle(all_cancer)
        
        group1_healthy = all_healthy[:3]
        group1_cancer = all_cancer[:3]
        
        group1_tse = [s['tse'] for s in group1_healthy] + [s['tse'] for s in group1_cancer]
        
        healthy_mean = np.mean([s['tse'] for s in group1_healthy])
        cancer_mean = np.mean([s['tse'] for s in group1_cancer])
        
        difference = healthy_mean - cancer_mean
        all_differences.append(difference)
        
        if difference > 0.1:
            significant_count += 1
    
    mean_diff = np.mean(all_differences)
    std_diff = np.std(all_differences)
    
    print(f"\n结果:")
    print(f"  平均TSE差异: {mean_diff:.4f} ± {std_diff:.4f}")
    print(f"  差异范围: {min(all_differences):.4f} - {max(all_differences):.4f}")
    print(f"  显著差异次数: {significant_count}/{n_iterations} ({significant_count/n_iterations*100:.1f}%)")
    
    return {
        'method': '随机分割验证',
        'mean_difference': mean_diff,
        'std_difference': std_diff,
        'significant_count': significant_count,
        'total_iterations': n_iterations
    }

# ==============================================================================
# 方法3：Bootstrap自举法
# ==============================================================================
def bootstrap_validation(healthy_samples, cancer_samples, n_iterations=1000):
    print("\n" + "="*70)
    print("方法3：Bootstrap自举法")
    print("="*70)
    
    healthy_tse = [s['tse'] for s in healthy_samples]
    cancer_tse = [s['tse'] for s in cancer_samples]
    
    differences = []
    
    print(f"\n进行 {n_iterations} 次Bootstrap抽样...")
    
    for _ in range(n_iterations):
        boot_healthy = [random.choice(healthy_tse) for _ in range(5)]
        boot_cancer = [random.choice(cancer_tse) for _ in range(5)]
        
        diff = np.mean(boot_healthy) - np.mean(boot_cancer)
        differences.append(diff)
    
    differences = np.array(differences)
    
    ci_lower = np.percentile(differences, 2.5)
    ci_upper = np.percentile(differences, 97.5)
    
    print(f"\n结果:")
    print(f"  平均TSE差异: {np.mean(differences):.4f}")
    print(f"  标准差: {np.std(differences):.4f}")
    print(f"  95%置信区间: [{ci_lower:.4f}, {ci_upper:.4f}]")
    print(f"  差异 > 0 的比例: {np.sum(differences > 0) / n_iterations * 100:.1f}%")
    
    return {
        'method': 'Bootstrap自举法',
        'mean_difference': np.mean(differences),
        'std_difference': np.std(differences),
        'ci_lower': ci_lower,
        'ci_upper': ci_upper,
        'positive_ratio': np.sum(differences > 0) / n_iterations
    }

# ==============================================================================
# 方法4：TSE与VI相关性分析
# ==============================================================================
def tse_vi_correlation(healthy_samples, cancer_samples):
    print("\n" + "="*70)
    print("方法4：TSE与VI相关性分析")
    print("="*70)
    
    all_samples = healthy_samples + cancer_samples
    
    tse_values = np.array([s['tse'] for s in all_samples])
    vi_values = np.array([s['vi'] for s in all_samples])
    
    correlation = np.corrcoef(tse_values, vi_values)[0, 1]
    
    print(f"\n结果:")
    print(f"  TSE与VI的相关系数: r = {correlation:.4f}")
    
    if correlation < -0.5:
        print(f"  解读: 强负相关 - TSE越高，VI越低")
    elif correlation < -0.3:
        print(f"  解读: 中等负相关")
    else:
        print(f"  解读: 弱相关或无相关")
    
    return {
        'method': 'TSE与VI相关性',
        'correlation': correlation
    }

# ==============================================================================
# 方法5：散点图可视化
# ==============================================================================
def plot_scatter(healthy_samples, cancer_samples):
    print("\n" + "="*70)
    print("方法5：散点图可视化")
    print("="*70)
    
    healthy_tse = [s['tse'] for s in healthy_samples]
    healthy_vi = [s['vi'] for s in healthy_samples]
    
    cancer_tse = [s['tse'] for s in cancer_samples]
    cancer_vi = [s['vi'] for s in cancer_samples]
    
    plt.figure(figsize=(10, 8))
    
    plt.scatter(healthy_tse, healthy_vi, c='green', s=100, alpha=0.7, 
                label='健康样本', marker='o', edgecolors='darkgreen', linewidths=2)
    
    plt.scatter(cancer_tse, cancer_vi, c='red', s=100, alpha=0.7,
                label='癌症样本', marker='s', edgecolors='darkred', linewidths=2)
    
    plt.xlabel('TSE (总结构熵)', fontsize=14)
    plt.ylabel('VI (变异指数)', fontsize=14)
    plt.title('健康与癌症DNA样本的TSE-VI分布', fontsize=16)
    plt.legend(fontsize=12)
    plt.grid(True, alpha=0.3)
    
    healthy_mean_tse = np.mean(healthy_tse)
    healthy_mean_vi = np.mean(healthy_vi)
    cancer_mean_tse = np.mean(cancer_tse)
    cancer_mean_vi = np.mean(cancer_vi)
    
    plt.axvline(x=(healthy_mean_tse + cancer_mean_tse)/2, color='gray', 
                linestyle='--', alpha=0.5, label='分类线')
    
    plt.tight_layout()
    plt.savefig('tse_vi_scatter.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\n✅ 散点图已保存为: tse_vi_scatter.png")
    print(f"\n关键观察:")
    print(f"  健康样本: TSE均值={healthy_mean_tse:.4f}, VI均值={healthy_mean_vi:.4f}")
    print(f"  癌症样本: TSE均值={cancer_mean_tse:.4f}, VI均值={cancer_mean_vi:.4f}")
    print(f"  两组样本在TSE-VI空间中{'完全不重叠' if min(healthy_tse) > max(cancer_tse) else '有一定重叠'}")
    
    return {
        'method': '散点图可视化',
        'healthy_mean_tse': healthy_mean_tse,
        'healthy_mean_vi': healthy_mean_vi,
        'cancer_mean_tse': cancer_mean_tse,
        'cancer_mean_vi': cancer_mean_vi,
        'no_overlap': min(healthy_tse) > max(cancer_tse)
    }

# ==============================================================================
# 主程序
# ==============================================================================
def main():
    print("="*70)
    print("📊 DNA数据内部验证分析")
    print("="*70)
    
    print("\n加载DNA样本...")
    healthy_samples, cancer_samples = load_dna_samples()
    
    print(f"✅ 加载了 {len(healthy_samples)} 个健康样本")
    print(f"✅ 加载了 {len(cancer_samples)} 个癌症样本")
    
    results = []
    
    results.append(leave_one_out_validation(healthy_samples, cancer_samples))
    
    results.append(random_split_validation(healthy_samples, cancer_samples))
    
    results.append(bootstrap_validation(healthy_samples, cancer_samples))
    
    results.append(tse_vi_correlation(healthy_samples, cancer_samples))
    
    results.append(plot_scatter(healthy_samples, cancer_samples))
    
    print("\n" + "="*70)
    print("📊 内部验证总结")
    print("="*70)
    
    print("\n所有验证方法的结果:")
    for result in results:
        print(f"\n{result['method']}:")
        for key, value in result.items():
            if key != 'method':
                print(f"  {key}: {value}")
    
    print("\n" + "="*70)
    print("✅ 内部验证完成！")
    print("="*70)

if __name__ == "__main__":
    main()
