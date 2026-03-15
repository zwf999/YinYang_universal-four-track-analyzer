#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAI公开版
================================
第一次运算（随机16层）+ 第二次运算（64卦直接映射）

【设计原则】
1. 无权重：纯统计
2. 第一次运算：随机16层映射，测方向性
3. 第二次运算：64模式直接对应64卦
4. 数据编码规则：
   - 数据文件（.dat, .bin等）：原始8-bit字节流
   - 文本文件（.txt, .csv, .json等）：字符ASCII码
5. 必须区分【数据文本】和【人文文本】
"""

import random
import numpy as np
import argparse
from pathlib import Path
from collections import Counter
from typing import List, Dict

HEXAGRAM_NAMES = [
    '乾', '坤', '屯', '蒙', '需', '讼', '师', '比',
    '小畜', '履', '泰', '否', '同人', '大有', '谦', '豫',
    '随', '蛊', '临', '观', '噬嗑', '贲', '剥', '复',
    '无妄', '大畜', '颐', '大过', '坎', '离', '咸', '恒',
    '遯', '大壮', '晋', '明夷', '家人', '睽', '蹇', '解',
    '损', '益', '夬', '姤', '萃', '升', '困', '井',
    '革', '鼎', '震', '艮', '渐', '归妹', '丰', '旅',
    '巽', '兑', '涣', '节', '中孚', '小过', '既济', '未济'
]

HEXAGRAM_PAIRS = [
    ('乾', '坤'), ('屯', '蒙'), ('需', '讼'), ('师', '比'),
    ('小畜', '履'), ('泰', '否'), ('同人', '大有'), ('谦', '豫'),
    ('随', '蛊'), ('临', '观'), ('噬嗑', '贲'), ('剥', '复'),
    ('无妄', '大畜'), ('颐', '大过'), ('坎', '离'), ('咸', '恒'),
    ('遯', '大壮'), ('晋', '明夷'), ('家人', '睽'), ('蹇', '解'),
    ('损', '益'), ('夬', '姤'), ('萃', '升'), ('困', '井'),
    ('革', '鼎'), ('震', '艮'), ('渐', '归妹'), ('丰', '旅'),
    ('巽', '兑'), ('涣', '节'), ('中孚', '小过'), ('既济', '未济')
]

DATA_EXTENSIONS = {'.dat', '.bin', '.raw', '.hex', '.bytes'}
TEXT_EXTENSIONS = {'.txt', '.csv', '.json', '.xml', '.md', '.py', '.c', '.h', '.log'}

def get_pair_index(hexagram_idx: int) -> int:
    return (hexagram_idx - 1) // 2 + 1

BINARY_TO_HEXAGRAM = {
    '111111': 1, '000000': 2, '100010': 3, '010001': 4,
    '111010': 5, '010111': 6, '010000': 7, '000010': 8,
    '111011': 9, '110111': 10, '111000': 11, '000111': 12,
    '101111': 13, '111101': 14, '001000': 15, '000100': 16,
    '100110': 17, '011001': 18, '110000': 19, '000011': 20,
    '100101': 21, '101001': 22, '000001': 23, '100000': 24,
    '100111': 25, '111001': 26, '100001': 27, '011110': 28,
    '010010': 29, '101101': 30, '001110': 31, '011100': 32,
    '001111': 33, '111100': 34, '000101': 35, '101000': 36,
    '101011': 37, '110101': 38, '001010': 39, '010100': 40,
    '110001': 41, '100011': 42, '111110': 43, '011111': 44,
    '000110': 45, '011000': 46, '010110': 47, '011010': 48,
    '101110': 49, '011101': 50, '100100': 51, '001001': 52,
    '001011': 53, '110100': 54, '101100': 55, '001101': 56,
    '011011': 57, '110110': 58, '010011': 59, '110010': 60,
    '110011': 61, '001100': 62, '101010': 63, '010101': 64
}

def is_data_file(filepath: str) -> bool:
    """判断是否为数据文件（使用原始字节流）"""
    path = Path(filepath)
    ext = path.suffix.lower()
    if ext in DATA_EXTENSIONS:
        return True
    if ext in TEXT_EXTENSIONS:
        return False
    filename = path.name.lower()
    if any(kw in filename for kw in ['constant', 'digit', 'sequence', 'earthquake', 'dna']):
        return True
    return False

def file_to_bits(filepath: str) -> List[int]:
    """将文件转换为8-bit二进制数据流"""
    bits = []
    path = Path(filepath)
    is_data = is_data_file(filepath)

    print(f"\n[数据识别]")
    print(f"  文件: {path.name}")
    print(f"  类型: {'数据文件（原始8-bit字节流）' if is_data else '文本文件（字符ASCII码）'}")
    print(f"  编码: 8-bit统一编码")

    if is_data:
        with open(filepath, 'rb') as f:
            data = f.read()
        for byte in data:
            for i in range(7, -1, -1):
                bits.append((byte >> i) & 1)
    else:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        for char in content:
            byte = ord(char)
            for i in range(7, -1, -1):
                bits.append((byte >> i) & 1)

    print(f"  比特数: {len(bits):,}")
    return bits

def bits_to_patterns(bits: List[int]) -> List[str]:
    patterns = []
    for i in range(len(bits) - 5):
        window = bits[i:i+6]
        patterns.append(''.join(str(b) for b in window))
    return patterns

def generate_random_layer_mapping() -> Dict[str, int]:
    all_patterns = [format(i, '06b') for i in range(64)]
    random.shuffle(all_patterns)
    mapping = {}
    for i, p in enumerate(all_patterns):
        mapping[p] = (i // 4) + 1
    return mapping

def calculate_tse(probs: np.ndarray) -> float:
    probs = probs[probs > 0]
    if len(probs) == 0:
        return 0.0
    H = -np.sum(probs * np.log2(probs))
    return 6.0 * H / 4.0

def first_operation(patterns: List[str], n_random: int = 100) -> Dict:
    print("\n" + "="*70)
    print(f"【第一次运算】随机16层映射（{n_random}次）")
    print("="*70)

    total = len(patterns)
    tse_values = []
    delta_tse_values = []

    for trial in range(n_random):
        mapping = generate_random_layer_mapping()

        layers_fwd = [mapping[p] for p in patterns]
        cnt_fwd = Counter(layers_fwd)
        probs_fwd = np.array([cnt_fwd.get(l, 0) / total for l in range(1, 17)])
        tse_fwd = calculate_tse(probs_fwd)

        patterns_rev = [p[::-1].translate(str.maketrans('01', '10')) for p in patterns]
        layers_rev = [mapping[p] for p in patterns_rev]
        cnt_rev = Counter(layers_rev)
        probs_rev = np.array([cnt_rev.get(l, 0) / total for l in range(1, 17)])
        tse_rev = calculate_tse(probs_rev)

        tse_values.append(tse_fwd)
        delta_tse_values.append(abs(tse_fwd - tse_rev))

    mean_tse = np.mean(tse_values)
    std_tse = np.std(tse_values)
    mean_delta = np.mean(delta_tse_values)
    std_delta = np.std(delta_tse_values)

    print(f"  TSE均值: {mean_tse:.4f} ± {std_tse:.4f}")
    print(f"  ΔTSE均值: {mean_delta:.4f} ± {std_delta:.4f}")

    if mean_delta > 0.01:
        print("  方向性: 有时间箭头 ✓")
    else:
        print("  方向性: 无明显时间箭头")

    return {
        'mean_tse': mean_tse,
        'std_tse': std_tse,
        'mean_delta_tse': mean_delta,
        'std_delta_tse': std_delta,
        'has_arrow': mean_delta > 0.01
    }

def second_operation(patterns: List[str]) -> Dict:
    print("\n" + "="*70)
    print("【第二次运算】64模式直接映射64卦（无权重）")
    print("="*70)

    total = len(patterns)

    hexagram_indices = [BINARY_TO_HEXAGRAM[p] for p in patterns]
    cnt = Counter(hexagram_indices)
    probs = np.array([cnt.get(i, 0) / total for i in range(1, 65)])

    probs_valid = probs[probs > 0]
    H_fwd = -np.sum(probs_valid * np.log2(probs_valid))
    tse_fwd = H_fwd

    patterns_rev = [p[::-1].translate(str.maketrans('01', '10')) for p in patterns]
    hexagram_indices_rev = [BINARY_TO_HEXAGRAM[p] for p in patterns_rev]
    cnt_rev = Counter(hexagram_indices_rev)
    probs_rev = np.array([cnt_rev.get(i, 0) / total for i in range(1, 65)])
    probs_rev_valid = probs_rev[probs_rev > 0]
    H_rev = -np.sum(probs_rev_valid * np.log2(probs_rev_valid))
    tse_rev = H_rev

    delta_tse = abs(tse_fwd - tse_rev)

    sorted_items = sorted(cnt.items(), key=lambda x: x[1], reverse=True)
    top_hexagrams = []
    print("  最凸显卦象:")
    for idx, count in sorted_items[:2]:
        prob = count / total
        name = HEXAGRAM_NAMES[idx - 1]
        pair_idx = get_pair_index(idx)
        pair = HEXAGRAM_PAIRS[pair_idx - 1]
        top_hexagrams.append((idx, name, prob, pair_idx, pair))
        print(f"    第{idx}卦 {name} (第{pair_idx}对 {pair[0]}·{pair[1]}): {prob*100:.2f}%")

    print(f"\n  正向TSE: {tse_fwd:.4f}")
    print(f"  反向TSE: {tse_rev:.4f}")
    print(f"  ΔTSE: {delta_tse:.4f}")

    return {
        'tse_forward': tse_fwd,
        'tse_reverse': tse_rev,
        'delta_tse': delta_tse,
        'probs': probs.tolist(),
        'top_hexagrams': top_hexagrams
    }

def run_all_operations(bits: List[int], n_random: int = 100) -> Dict:
    patterns = bits_to_patterns(bits)
    print(f"\n数据统计: {len(patterns)} 个6bit模式")

    first_result = first_operation(patterns, n_random)
    second_result = second_operation(patterns)

    print("\n" + "="*70)
    print("【综合结论】")
    print("="*70)
    print(f"  信息复杂度: {second_result['tse_forward']:.2f}")
    print(f"  时间方向性: {first_result['mean_delta_tse']:.4f}")
    print("="*70)

    return {
        'first_operation': first_result,
        'second_operation': second_result
    }

def main():
    parser = argparse.ArgumentParser(description='TAI公开版')
    parser.add_argument('file', type=str, help='待分析文件路径')
    parser.add_argument('--n-random', type=int, default=100, help='随机映射次数')
    args = parser.parse_args()

    print("="*70)
    print("TAI公开版")
    print("   第一次运算（随机16层）+ 第二次运算（64卦）")
    print("="*70)

    bits = file_to_bits(args.file)
    if len(bits) < 100:
        print("错误: 数据量不足")
        return

    result = run_all_operations(bits, args.n_random)

if __name__ == "__main__":
    main()
