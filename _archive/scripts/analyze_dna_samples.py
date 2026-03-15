#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专门分析data/dna/目录中的癌症和健康样本
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
# 第一次运算：无序随机验证
# ==============================================================================
class FirstOperation:
    def __init__(self, n_trials: int = 100):
        self.n_trials = n_trials

    def run(self, patterns: List[str]) -> Dict:
        if len(patterns) == 0:
            return {'tse_base': 0, 'stable': False}

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
    patterns = DataProcessor.bits_to_patterns(bits)
    
    first = FirstOperation(n_trials=100)
    res = first.run(patterns)
    
    return {
        'tse': res['tse_base'],
        'num_patterns': len(patterns),
        'num_bits': len(bits)
    }

# ==============================================================================
# 主程序
# ==============================================================================
def main():
    print("="*60)
    print("🧬 DNA样本分析")
    print("="*60)
    
    dna_dir = Path("data/dna")
    
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
    
    healthy_tse = []
    for fpath in healthy_files:
        result = analyze_file(str(fpath))
        healthy_tse.append(result['tse'])
        print(f"{fpath.name}: TSE = {result['tse']:.4f}")
    
    # 分析癌症样本
    print("\n" + "="*60)
    print("🔴 癌症样本分析")
    print("="*60)
    
    cancer_tse = []
    for fpath in cancer_files:
        result = analyze_file(str(fpath))
        cancer_tse.append(result['tse'])
        print(f"{fpath.name}: TSE = {result['tse']:.4f}")
    
    # 统计分析
    print("\n" + "="*60)
    print("📊 统计结果")
    print("="*60)
    
    if healthy_tse:
        print(f"健康样本：")
        print(f"  样本数：{len(healthy_tse)}")
        print(f"  平均 TSE：{np.mean(healthy_tse):.4f}")
        print(f"  最小 TSE：{np.min(healthy_tse):.4f}")
        print(f"  最大 TSE：{np.max(healthy_tse):.4f}")
        print(f"  标准差：{np.std(healthy_tse):.4f}")
    
    if cancer_tse:
        print(f"\n癌症样本：")
        print(f"  样本数：{len(cancer_tse)}")
        print(f"  平均 TSE：{np.mean(cancer_tse):.4f}")
        print(f"  最小 TSE：{np.min(cancer_tse):.4f}")
        print(f"  最大 TSE：{np.max(cancer_tse):.4f}")
        print(f"  标准差：{np.std(cancer_tse):.4f}")
    
    if healthy_tse and cancer_tse:
        diff = abs(np.mean(healthy_tse) - np.mean(cancer_tse))
        print(f"\n健康 vs 癌症平均差异：{diff:.4f}")
    
    print("\n✅ 分析完成！")

if __name__ == "__main__":
    main()