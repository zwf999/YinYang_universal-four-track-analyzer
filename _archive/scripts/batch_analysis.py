#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量数据分析脚本
使用TAI v10.0双向扫描版分析所有数据文件
"""

import os
import random
import numpy as np
from pathlib import Path
from collections import Counter
from typing import List, Dict
import json
import warnings
warnings.filterwarnings('ignore')

# ==============================================================================
# 从主程序导入核心类
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
    def get(cls, layer: int) -> float:
        return cls.VALUES[layer-1]

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

class FirstOperation:
    def __init__(self, n_trials: int = 100):
        self.n_trials = n_trials

    def run(self, patterns: List[str]) -> Dict:
        all_patterns = list(TruthTable.PATTERN_TO_LAYER.keys())
        total = len(patterns)

        orig_layers = [TruthTable.PATTERN_TO_LAYER[p] for p in patterns]
        orig_cnt = Counter(orig_layers)
        orig_probs = np.array([orig_cnt.get(l, 0) / total for l in range(1, 17)])

        H = -np.sum(orig_probs[orig_probs > 0] * np.log2(orig_probs[orig_probs > 0]))
        # 确保H不超过4.0（16层的最大熵）
        H = min(H, 4.0)
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

        return {
            'visual_index': vis_index,
            'probs': probs
        }

# ==============================================================================
# 分析单个文件
# ==============================================================================
def analyze_file(filepath: str) -> Dict:
    bits = DataProcessor.file_to_bits(filepath)
    
    patterns_forward = DataProcessor.bits_to_patterns(bits)
    first_forward = FirstOperation(n_trials=100)
    res1_forward = first_forward.run(patterns_forward)
    
    second_forward = SecondOperation()
    res2_forward = second_forward.run(patterns_forward)
    
    bits_reverse = bits[::-1]
    patterns_reverse = DataProcessor.bits_to_patterns(bits_reverse)
    
    first_reverse = FirstOperation(n_trials=100)
    res1_reverse = first_reverse.run(patterns_reverse)
    
    second_reverse = SecondOperation()
    res2_reverse = second_reverse.run(patterns_reverse)
    
    return {
        'filename': os.path.basename(filepath),
        'forward': {
            'tse': res1_forward['tse_base'],
            'vi': res2_forward['visual_index'],
            'stable': res1_forward['stable'],
            'layer4_z': res1_forward['layer4_z'],
            'layer7_z': res1_forward['layer7_z'],
            'layer12_z': res1_forward['layer12_z']
        },
        'reverse': {
            'tse': res1_reverse['tse_base'],
            'vi': res2_reverse['visual_index'],
            'stable': res1_reverse['stable'],
            'layer4_z': res1_reverse['layer4_z'],
            'layer7_z': res1_reverse['layer7_z'],
            'layer12_z': res1_reverse['layer12_z']
        },
        'tse_diff': abs(res1_forward['tse_base'] - res1_reverse['tse_base']),
        'vi_diff': abs(res2_forward['visual_index'] - res2_reverse['visual_index'])
    }

# ==============================================================================
# 数据分类
# ==============================================================================
def categorize_file(filename: str) -> str:
    filename_lower = filename.lower()
    
    if 'pi' in filename_lower:
        return '数学常数 - π'
    elif 'e_' in filename_lower or 'e_100k' in filename_lower:
        return '数学常数 - e'
    elif 'phi' in filename_lower:
        return '数学常数 - φ'
    elif 'sqrt2' in filename_lower:
        return '数学常数 - √2'
    elif 'sqrt3' in filename_lower:
        return '数学常数 - √3'
    elif 'catalan' in filename_lower:
        return '数学常数 - Catalan'
    elif 'champernowne' in filename_lower:
        return '数学常数 - Champernowne'
    elif 'zeta3' in filename_lower or 'apery' in filename_lower:
        return '数学常数 - ζ(3)'
    elif 'rational' in filename_lower:
        return '有理数'
    elif 'planck' in filename_lower:
        return '物理常数 - Planck'
    elif 'avogadro' in filename_lower:
        return '物理常数 - Avogadro'
    elif 'boltzmann' in filename_lower:
        return '物理常数 - Boltzmann'
    elif 'bohr' in filename_lower:
        return '物理常数 - Bohr'
    elif 'electron' in filename_lower:
        return '物理常数 - Electron'
    elif 'proton' in filename_lower:
        return '物理常数 - Proton'
    elif 'neutron' in filename_lower:
        return '物理常数 - Neutron'
    elif 'fine_structure' in filename_lower or 'alpha' in filename_lower:
        return '物理常数 - Fine Structure'
    elif 'rydberg' in filename_lower:
        return '物理常数 - Rydberg'
    elif 'gravitational' in filename_lower:
        return '物理常数 - Gravitational'
    elif 'hubble' in filename_lower:
        return '物理常数 - Hubble'
    elif 'light_year' in filename_lower:
        return '物理常数 - Light Year'
    elif 'speed_of_light' in filename_lower:
        return '物理常数 - Speed of Light'
    elif 'elementary_charge' in filename_lower:
        return '物理常数 - Elementary Charge'
    elif 'compton' in filename_lower:
        return '物理常数 - Compton'
    elif 'classical_electron' in filename_lower:
        return '物理常数 - Classical Electron'
    elif 'impedance' in filename_lower:
        return '物理常数 - Impedance'
    elif 'vacuum' in filename_lower:
        return '物理常数 - Vacuum'
    elif 'standard_gravity' in filename_lower:
        return '物理常数 - Standard Gravity'
    elif 'astronomical' in filename_lower:
        return '物理常数 - Astronomical Unit'
    elif 'b001620' in filename_lower:
        return '序列 - B001620'
    else:
        return '其他'

# ==============================================================================
# 主程序
# ==============================================================================
def main():
    print("="*70)
    print("📊 TAI v10.0 批量数据分析")
    print("="*70)
    
    data_dir = Path("data")
    
    all_files = []
    for fpath in sorted(data_dir.glob("*.txt")):
        all_files.append(str(fpath))
    
    print(f"\n✅ 找到 {len(all_files)} 个数据文件")
    
    results = []
    categories = {}
    
    for i, filepath in enumerate(all_files, 1):
        filename = os.path.basename(filepath)
        print(f"\n[{i}/{len(all_files)}] 分析: {filename}")
        
        try:
            result = analyze_file(filepath)
            category = categorize_file(filename)
            result['category'] = category
            
            if category not in categories:
                categories[category] = []
            categories[category].append(result)
            
            results.append(result)
            
            print(f"  正向 TSE: {result['forward']['tse']:.4f}, VI: {result['forward']['vi']:.4f}")
            print(f"  反向 TSE: {result['reverse']['tse']:.4f}, VI: {result['reverse']['vi']:.4f}")
            print(f"  TSE差异: {result['tse_diff']:.6f}")
            
        except Exception as e:
            print(f"  ❌ 错误: {e}")
    
    print("\n" + "="*70)
    print("📊 分析完成！")
    print("="*70)
    
    with open('analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'results': results,
            'categories': categories
        }, f, ensure_ascii=False, indent=2)
    
    print("\n✅ 结果已保存到 analysis_results.json")
    
    print("\n" + "="*70)
    print("📈 分类统计")
    print("="*70)
    
    for category, items in sorted(categories.items()):
        tse_values = [item['forward']['tse'] for item in items]
        avg_tse = np.mean(tse_values)
        std_tse = np.std(tse_values)
        print(f"\n{category}:")
        print(f"  样本数: {len(items)}")
        print(f"  平均TSE: {avg_tse:.4f} ± {std_tse:.4f}")
        print(f"  TSE范围: {min(tse_values):.4f} - {max(tse_values):.4f}")

if __name__ == "__main__":
    main()
