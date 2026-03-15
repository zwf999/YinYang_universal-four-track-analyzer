#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整分析data/dna/目录中的癌症和健康样本，包含双向扫描和两次运算
"""

import os
import random
import numpy as np
from pathlib import Path
from collections import Counter
from typing import List, Dict
import warnings
warnings.filterwarnings('ignore')

# ==============================================================================
# 固定映射表（完全不动）
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

# ==============================================================================
# 易经字典（完全不动）
# ==============================================================================
class YijingDictionary:
    LAYER4  = {'卦象': ['晋', '明夷', '师', '比'],    '语义': '底层秩序初现、内外边界形成、状态跃迁受阻'}
    LAYER7  = {'卦象': ['随', '蛊', '渐', '归妹'],  '语义': '新旧交替、渐进演化与突变共生、信息交互核心'}
    LAYER12 = {'卦象': ['临', '观', '萃', '升'],    '语义': '整体秩序显现、聚合升发、宏观形态稳定'}

    @classmethod
    def interpret(cls, layer: int) -> Dict:
        if layer == 4:  return cls.LAYER4
        if layer == 7:  return cls.LAYER7
        if layer == 12: return cls.LAYER12
        return {'卦象': [], '语义': '非关键节点'}

# ==============================================================================
# 权重：0.12 * 0.75^(l-1) 严格原版（完全不动）
# ==============================================================================
class OriginalWeights:
    VALUES = np.array([
        0.1200, 0.0900, 0.0675, 0.0506, 0.0380, 0.0285, 0.0214, 0.0160,
        0.0120, 0.0090, 0.0068, 0.0051, 0.0038, 0.0029, 0.0021, 0.0016
    ])

    @classmethod
    def get_all(cls) -> np.ndarray:
        return cls.VALUES.copy()

# ==============================================================================
# 第一次运算：无序随机验证
# ==============================================================================
class FirstOperation:
    def __init__(self, n_trials: int = 100):
        self.n_trials = n_trials

    def run(self, patterns: List[str]) -> Dict:
        if len(patterns) == 0:
            return {'tse_base': 0}

        all_patterns = list(TruthTable.PATTERN_TO_LAYER.keys())
        total = len(patterns)

        orig_layers = [TruthTable.PATTERN_TO_LAYER[p] for p in patterns]
        orig_cnt = Counter(orig_layers)
        orig_probs = np.array([orig_cnt.get(l, 0) / total for l in range(1, 17)])

        H = -np.sum(orig_probs[orig_probs > 0] * np.log2(orig_probs[orig_probs > 0]))
        # 确保H不超过4.0（16层的最大熵）
        H = min(H, 4.0)
        tse_base = 6.0 * H / 4.0

        return {
            'tse_base': tse_base
        }

# ==============================================================================
# 第二次运算：有序色彩解读
# ==============================================================================
class SecondOperation:
    def __init__(self):
        self.weights = OriginalWeights.get_all()

    def run(self, patterns: List[str]) -> Dict:
        if len(patterns) == 0:
            return {'visual_index': 0}

        layers_seq = [TruthTable.get_layer(p) for p in patterns]
        cnt = Counter(layers_seq)
        total = len(layers_seq)
        probs = np.array([cnt.get(l,0)/total for l in range(1,17)])

        w = self.weights
        weighted_sum = np.sum(w * probs)
        vis_index = 6.0 * (weighted_sum - w.min()) / (w.max() - w.min())

        return {
            'visual_index': vis_index
        }

# ==============================================================================
# 数据处理器
# ==============================================================================
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

# ==============================================================================
# 分析单个文件
# ==============================================================================
def analyze_file(filepath: str):
    bits = DataProcessor.file_to_bits(filepath)
    patterns_forward = DataProcessor.bits_to_patterns(bits)
    
    # 正向
    first_forward = FirstOperation(n_trials=100)
    res1_forward = first_forward.run(patterns_forward)
    
    second_forward = SecondOperation()
    res2_forward = second_forward.run(patterns_forward)
    
    # 反向
    bits_reverse = bits[::-1]
    patterns_reverse = DataProcessor.bits_to_patterns(bits_reverse)
    
    first_reverse = FirstOperation(n_trials=100)
    res1_reverse = first_reverse.run(patterns_reverse)
    
    second_reverse = SecondOperation()
    res2_reverse = second_reverse.run(patterns_reverse)
    
    return {
        'forward_tse': res1_forward['tse_base'],
        'forward_vis': res2_forward['visual_index'],
        'reverse_tse': res1_reverse['tse_base'],
        'reverse_vis': res2_reverse['visual_index'],
        'num_patterns': len(patterns_forward),
        'num_bits': len(bits)
    }

# ==============================================================================
# 主程序
# ==============================================================================
def main():
    print("="*60)
    print("🧬 DNA样本完整分析（双向扫描 + 两次运算）")
    print("="*60)
    
    dna_dir = Path(r"e:\8终究是8bit的16层世界\_archive\dna\dna")
    
    if not dna_dir.exists():
        print("❌ data/dna目录不存在")
        return
    
    # 收集所有文件
    healthy_files = []
    cancer_files = []
    
    for fpath in sorted(dna_dir.glob("*.txt")):
        if not fpath.is_file():
            continue
        
        filename = fpath.name.lower()
        if 'healthy' in filename:
            healthy_files.append(fpath)
        elif 'cancer' in filename:
            cancer_files.append(fpath)
    
    print(f"✅ 找到 {len(healthy_files)} 个健康样本")
    print(f"✅ 找到 {len(cancer_files)} 个癌症样本")
    
    # 分析健康样本
    print("\n" + "="*60)
    print("🟢 健康样本分析")
    print("="*60)
    
    healthy_results = []
    for fpath in healthy_files:
        result = analyze_file(str(fpath))
        healthy_results.append(result)
        print(f"\n{fpath.name}:")
        print(f"  正向 TSE：{result['forward_tse']:.4f}")
        print(f"  正向 VI：{result['forward_vis']:.4f}")
        print(f"  反向 TSE：{result['reverse_tse']:.4f}")
        print(f"  反向 VI：{result['reverse_vis']:.4f}")
    
    # 分析癌症样本
    print("\n" + "="*60)
    print("🔴 癌症样本分析")
    print("="*60)
    
    cancer_results = []
    for fpath in cancer_files:
        result = analyze_file(str(fpath))
        cancer_results.append(result)
        print(f"\n{fpath.name}:")
        print(f"  正向 TSE：{result['forward_tse']:.4f}")
        print(f"  正向 VI：{result['forward_vis']:.4f}")
        print(f"  反向 TSE：{result['reverse_tse']:.4f}")
        print(f"  反向 VI：{result['reverse_vis']:.4f}")
    
    # 统计分析
    print("\n" + "="*60)
    print("📊 统计结果")
    print("="*60)
    
    if healthy_results:
        print(f"\n健康样本：")
        print(f"  样本数：{len(healthy_results)}")
        
        forward_tse = [r['forward_tse'] for r in healthy_results]
        reverse_tse = [r['reverse_tse'] for r in healthy_results]
        forward_vis = [r['forward_vis'] for r in healthy_results]
        reverse_vis = [r['reverse_vis'] for r in healthy_results]
        
        print(f"  正向 TSE：平均 {np.mean(forward_tse):.4f} ± {np.std(forward_tse):.4f}")
        print(f"            范围 {np.min(forward_tse):.4f} - {np.max(forward_tse):.4f}")
        print(f"  反向 TSE：平均 {np.mean(reverse_tse):.4f} ± {np.std(reverse_tse):.4f}")
        print(f"            范围 {np.min(reverse_tse):.4f} - {np.max(reverse_tse):.4f}")
        print(f"  正向 VI：平均 {np.mean(forward_vis):.4f} ± {np.std(forward_vis):.4f}")
        print(f"  反向 VI：平均 {np.mean(reverse_vis):.4f} ± {np.std(reverse_vis):.4f}")
    
    if cancer_results:
        print(f"\n癌症样本：")
        print(f"  样本数：{len(cancer_results)}")
        
        forward_tse = [r['forward_tse'] for r in cancer_results]
        reverse_tse = [r['reverse_tse'] for r in cancer_results]
        forward_vis = [r['forward_vis'] for r in cancer_results]
        reverse_vis = [r['reverse_vis'] for r in cancer_results]
        
        print(f"  正向 TSE：平均 {np.mean(forward_tse):.4f} ± {np.std(forward_tse):.4f}")
        print(f"            范围 {np.min(forward_tse):.4f} - {np.max(forward_tse):.4f}")
        print(f"  反向 TSE：平均 {np.mean(reverse_tse):.4f} ± {np.std(reverse_tse):.4f}")
        print(f"            范围 {np.min(reverse_tse):.4f} - {np.max(reverse_tse):.4f}")
        print(f"  正向 VI：平均 {np.mean(forward_vis):.4f} ± {np.std(forward_vis):.4f}")
        print(f"  反向 VI：平均 {np.mean(reverse_vis):.4f} ± {np.std(reverse_vis):.4f}")
    
    if healthy_results and cancer_results:
        h_forward_tse = np.mean([r['forward_tse'] for r in healthy_results])
        c_forward_tse = np.mean([r['forward_tse'] for r in cancer_results])
        h_reverse_tse = np.mean([r['reverse_tse'] for r in healthy_results])
        c_reverse_tse = np.mean([r['reverse_tse'] for r in cancer_results])
        
        diff_forward = abs(h_forward_tse - c_forward_tse)
        diff_reverse = abs(h_reverse_tse - c_reverse_tse)
        diff_avg = (diff_forward + diff_reverse) / 2
        
        print(f"\n健康 vs 癌症差异：")
        print(f"  正向 TSE差异：{diff_forward:.4f}")
        print(f"  反向 TSE差异：{diff_reverse:.4f}")
        print(f"  平均差异：{diff_avg:.4f}")
    
    print("\n✅ 完整分析完成！")

if __name__ == "__main__":
    main()