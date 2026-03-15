#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAI v10.0 + 双向扫描升级版
============================
✅ 完全保留原版两次运算：无序随机验证 → 有序色彩解读
✅ 只新增：正向扫描 + 反向扫描（比特流反转）
✅ 无花哨功能、无新增卦象、无共振、无镜像
"""

import os
import random
import numpy as np
import matplotlib.pyplot as plt
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
    MIN_VAL = 0.0016
    MAX_VAL = 0.1200

    @classmethod
    def get(cls, layer: int) -> float:
        return cls.VALUES[layer-1]

    @classmethod
    def get_all(cls) -> np.ndarray:
        return cls.VALUES.copy()

# ==============================================================================
# 数据处理器：新增 正向/反向 比特流
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
# 第一次运算：无序随机验证（已修复漏洞）
# ==============================================================================
class FirstOperation:
    def __init__(self, n_trials: int = 100):
        self.n_trials = n_trials

    def run(self, patterns: List[str]) -> Dict:
        print("\n" + "="*50)
        print("【第一次运算】无序随机验证（真随机 + Z-score）")
        print("="*50)

        all_patterns = list(TruthTable.PATTERN_TO_LAYER.keys())
        total = len(patterns)

        orig_layers = [TruthTable.PATTERN_TO_LAYER[p] for p in patterns]
        orig_cnt = Counter(orig_layers)
        orig_probs = np.array([orig_cnt.get(l, 0) / total for l in range(1, 17)])

        # 基础 TSE
        H = -np.sum(orig_probs[orig_probs > 0] * np.log2(orig_probs[orig_probs > 0]))
        tse_base = 6.0 * H / 4.0

        dev4, dev7, dev12 = [], [], []
        uniform = 1/16

        for _ in range(self.n_trials):
            shuffled = all_patterns.copy()
            random.shuffle(shuffled)
            r_map = {p: (i//4)+1 for i, p in enumerate(shuffled)}
            r_layers = [r_map[p] for p in patterns]
            r_cnt = Counter(r_layers)
            r_probs = np.array([r_cnt.get(l, 0)/total for l in range(1,17)])
            dev4.append(abs(r_probs[3]-uniform))
            dev7.append(abs(r_probs[6]-uniform))
            dev12.append(abs(r_probs[11]-uniform))

        def z(val, lst):
            return (val - np.mean(lst)) / (np.std(lst)+1e-8)

        z4 = z(abs(orig_probs[3]-uniform), dev4)
        z7 = z(abs(orig_probs[6]-uniform), dev7)
        z12 = z(abs(orig_probs[11]-uniform), dev12)

        return {
            'tse_base': tse_base,
            'layer4_z': z4,
            'layer7_z': z7,
            'layer12_z': z12,
            'stable': all(abs(x)>=1 for x in [z4,z7,z12])
        }

# ==============================================================================
# 第二次运算：有序色彩解读（完全不动）
# ==============================================================================
class SecondOperation:
    def __init__(self):
        self.weights = OriginalWeights.get_all()

    def run(self, patterns: List[str]) -> Dict:
        layers_seq = [TruthTable.get_layer(p) for p in patterns]
        cnt = Counter(layers_seq)
        total = len(layers_seq)
        probs = np.array([cnt.get(l,0)/total for l in range(1,17)])

        w = self.weights
        weighted_sum = np.sum(w * probs)
        vis_index = 6.0 * (weighted_sum - w.min()) / (w.max() - w.min())

        p4,p7,p12 = probs[3], probs[6], probs[11]
        w4,w7,w12 = w[3]*p4, w[6]*p7, w[11]*p12

        d4 = YijingDictionary.interpret(4)
        d7 = YijingDictionary.interpret(7)
        d12 = YijingDictionary.interpret(12)

        return {
            'visual_index': vis_index,
            'probs': probs,
            'layer4': {'p':p4,'w':w4,**d4},
            'layer7': {'p':p7,'w':w7,**d7},
            'layer12': {'p':p12,'w':w12,**d12},
            'weights_seq': [self.weights[l-1] for l in layers_seq]
        }

# ==============================================================================
# 统一执行函数：正向 / 反向 共用
# ==============================================================================
def run_both_operations(patterns: List[str], direction_name: str):
    print(f"\n" + "="*60)
    print(f"🔍 方向：{direction_name}")
    print(f"="*60)

    first = FirstOperation(n_trials=100)
    res1 = first.run(patterns)

    second = SecondOperation()
    res2 = second.run(patterns)

    return res1, res2

# ==============================================================================
# 主程序：双向扫描
# ==============================================================================
def main():
    print("="*60)
    print("🚀 TAI v10.0 双向扫描版")
    print("   正向：原始顺序   |   反向：比特流反转")
    print("   两次运算完全保留，无额外花哨功能")
    print("="*60)

    data_dir = Path("data")
    res_dir  = Path("results")
    data_dir.mkdir(exist_ok=True)
    res_dir.mkdir(exist_ok=True)

    if not any(data_dir.iterdir()):
        with open(data_dir/"example.txt", 'w', encoding='utf-8') as f:
            f.write("TAI 10.0 bidirectional test " * 100)

    for fpath in sorted(data_dir.glob("*")):
        if not fpath.is_file():
            continue

        print(f"\n📄 处理文件：{fpath.name}")
        bits = DataProcessor.file_to_bits(str(fpath))

        # ======================
        # 正向
        # ======================
        patterns_forward = DataProcessor.bits_to_patterns(bits)
        f1, f2 = run_both_operations(patterns_forward, "正向")

        # ======================
        # 反向：只反转比特流
        # ======================
        bits_reverse = bits[::-1]
        patterns_reverse = DataProcessor.bits_to_patterns(bits_reverse)
        r1, r2 = run_both_operations(patterns_reverse, "反向")

        # ======================
        # 最终输出对比
        # ======================
        print("\n" + "="*60)
        print("📊 双向扫描最终对比")
        print("="*60)
        print(f"正向 TSE：{f1['tse_base']:.4f}")
        print(f"反向 TSE：{r1['tse_base']:.4f}")
        print()
        print(f"正向 4/7/12 稳定：{f1['stable']}")
        print(f"反向 4/7/12 稳定：{r1['stable']}")
        print("="*60)
        print("✅ 双向扫描完成！")

if __name__ == "__main__":
    main()