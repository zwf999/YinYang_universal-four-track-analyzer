#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAI v10.0 + 双向扫描升级版 - DNA分析扩展（流式处理版）
============================
✅ 完全保留原版两次运算：无序随机验证 → 有序色彩解读
✅ 只新增：正向扫描 + 反向扫描（比特流反转）
✅ 新增DNA分析功能：FASTA/GTF读取、编码区/非编码区分离、ΔTSE验证
✅ 优化：流式处理算法，避免内存溢出
✅ 无花哨功能、无新增卦象、无共振、无镜像
"""

import os
import random
import numpy as np
from pathlib import Path
from collections import Counter
from typing import List, Dict, Tuple
import warnings
import gzip
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

    @staticmethod
    def dna_to_bits(dna_sequence: str) -> List[int]:
        """将DNA序列转换为2-bit编码"""
        dna_map = {'A': '00', 'C': '01', 'G': '10', 'T': '11'}
        bits = []
        for base in dna_sequence:
            if base.upper() in dna_map:
                bits.extend([int(b) for b in dna_map[base.upper()]])
        return bits

# ==============================================================================
# FASTA文件读取器
# ==============================================================================
class FastaReader:
    @staticmethod
    def read_fasta(fasta_path: str) -> str:
        """读取FASTA文件，返回完整的DNA序列"""
        sequence = []
        if fasta_path.endswith('.gz'):
            open_func = gzip.open
            mode = 'rt'
        else:
            open_func = open
            mode = 'r'
        
        with open_func(fasta_path, mode) as f:
            for line in f:
                line = line.strip()
                if not line.startswith('>'):
                    sequence.append(line.upper())
        
        return ''.join(sequence)

# ==============================================================================
# GTF文件读取器
# ==============================================================================
class GtfReader:
    @staticmethod
    def read_gtf(gtf_path: str, chromosome: str = '22') -> List[Tuple[int, int]]:
        """读取GTF文件，返回排序后的编码区位置列表"""
        coding_regions = []
        
        if gtf_path.endswith('.gz'):
            open_func = gzip.open
            mode = 'rt'
        else:
            open_func = open
            mode = 'r'
        
        with open_func(gtf_path, mode) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split('\t')
                if len(parts) < 9:
                    continue
                
                chrom = parts[0]
                feature = parts[2]
                start = int(parts[3])
                end = int(parts[4])
                
                if chrom == chromosome and feature == 'CDS':
                    coding_regions.append((start, end))
        
        # 按起始位置排序
        coding_regions.sort()
        return coding_regions

    @staticmethod
    def separate_coding_non_coding(dna_sequence: str, coding_regions: List[Tuple[int, int]]) -> Tuple[str, str]:
        """分离编码区和非编码区，使用优化算法"""
        coding_sequence = []
        non_coding_sequence = []
        
        n = len(dna_sequence)
        region_index = 0
        num_regions = len(coding_regions)
        
        i = 0
        while i < n:
            current_pos = i + 1
            
            in_coding = False
            while region_index < num_regions:
                start, end = coding_regions[region_index]
                if current_pos < start:
                    break
                elif start <= current_pos <= end:
                    in_coding = True
                    end_in_sequence = min(end, n)
                    coding_sequence.append(dna_sequence[i:end_in_sequence])
                    i = end_in_sequence
                    current_pos = end_in_sequence + 1
                    region_index += 1
                    break
                else:
                    region_index += 1
            
            if not in_coding and i < n:
                next_coding_start = n + 1
                if region_index < num_regions:
                    next_coding_start = coding_regions[region_index][0]
                non_coding_end = min(next_coding_start - 1, n)
                non_coding_sequence.append(dna_sequence[i:non_coding_end])
                i = non_coding_end
        
        return ''.join(coding_sequence), ''.join(non_coding_sequence)

# ==============================================================================
# 流式TSE计算器
# ==============================================================================
class StreamingTSECalculator:
    def __init__(self):
        self.layer_counts = np.zeros(16, dtype=np.int64)
        self.total_patterns = 0
    
    def process_pattern(self, pattern: str):
        layer = TruthTable.PATTERN_TO_LAYER[pattern]
        self.layer_counts[layer - 1] += 1
        self.total_patterns += 1
    
    def get_tse(self):
        if self.total_patterns == 0:
            return 0.0
        
        probs = self.layer_counts / self.total_patterns
        H = -np.sum(probs[probs > 0] * np.log2(probs[probs > 0]))
        # 确保H不超过4.0（16层的最大熵）
        H = min(H, 4.0)
        tse = 6.0 * H / 4.0
        return tse

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
            'layer12': {'p':p12,'w':w12,**d12}
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
# DNA分析函数
# ==============================================================================
def analyze_dna(fasta_path: str, gtf_path: str, chromosome: str = '22', sample_size: int = 10000000, start_from_coding: bool = True):
    print("="*60)
    print("🧬 DNA序列分析")
    print("="*60)
    
    # 读取FASTA文件
    print(f"📖 读取FASTA文件：{os.path.basename(fasta_path)}")
    dna_sequence = FastaReader.read_fasta(fasta_path)
    print(f"✅ 读取完成，序列长度：{len(dna_sequence):,} bp")
    
    # 读取GTF文件，找到第一个编码区的位置
    print(f"📖 读取GTF文件：{os.path.basename(gtf_path)}")
    coding_regions = GtfReader.read_gtf(gtf_path, chromosome)
    print(f"✅ 读取完成，编码区数量：{len(coding_regions)}")
    
    # 确定采样起始位置
    start_pos = 0
    if start_from_coding and coding_regions:
        # 从第一个编码区开始采样，这样能确保有编码区
        first_coding_start = coding_regions[0][0]
        start_pos = first_coding_start
        print(f"🔄 从第一个编码区开始采样：位置 {start_pos:,}")
    
    # 采样处理（避免内存问题）
    end_pos = min(start_pos + sample_size, len(dna_sequence))
    if end_pos - start_pos < sample_size:
        start_pos = max(0, len(dna_sequence) - sample_size)
        end_pos = len(dna_sequence)
    
    dna_sequence = dna_sequence[start_pos:end_pos]
    print(f"✅ 采样区间：{start_pos:,} - {end_pos:,}，长度：{len(dna_sequence):,} bp")
    
    # 调整编码区位置，使其相对于采样序列
    adjusted_coding_regions = []
    for (orig_start, orig_end) in coding_regions:
        # 计算相对于采样序列的位置
        rel_start = orig_start - start_pos
        rel_end = orig_end - start_pos
        # 只保留与采样序列有重叠的区域
        if rel_end > 0 and rel_start < len(dna_sequence):
            # 调整到采样序列范围内
            adj_start = max(0, rel_start)
            adj_end = min(len(dna_sequence), rel_end)
            adjusted_coding_regions.append((adj_start + 1, adj_end))  # +1 因为DNA位置从1开始
    
    coding_regions = adjusted_coding_regions
    
    # 分离编码区和非编码区
    print("\n🔄 分离编码区和非编码区...")
    coding_seq_str, non_coding_seq_str = GtfReader.separate_coding_non_coding(dna_sequence, coding_regions)
    
    print(f"✅ 编码区长度：{len(coding_seq_str):,} bp")
    print(f"✅ 非编码区长度：{len(non_coding_seq_str):,} bp")
    
    # 如果编码区或非编码区太短，警告
    if len(coding_seq_str) < 1000:
        print("⚠️  警告：编码区序列太短，可能影响分析结果")
    if len(non_coding_seq_str) < 1000:
        print("⚠️  警告：非编码区序列太短，可能影响分析结果")
    
    # 转换为比特流
    print("\n🔄 转换为比特流...")
    coding_bits = DataProcessor.dna_to_bits(coding_seq_str)
    non_coding_bits = DataProcessor.dna_to_bits(non_coding_seq_str)
    
    print(f"✅ 编码区比特数：{len(coding_bits):,}")
    print(f"✅ 非编码区比特数：{len(non_coding_bits):,}")
    
    # 生成模式
    print("\n🔄 生成6-bit模式...")
    coding_patterns = DataProcessor.bits_to_patterns(coding_bits)
    non_coding_patterns = DataProcessor.bits_to_patterns(non_coding_bits)
    
    print(f"✅ 编码区模式数：{len(coding_patterns):,}")
    print(f"✅ 非编码区模式数：{len(non_coding_patterns):,}")
    
    # 分析编码区
    if len(coding_patterns) > 0:
        print("\n" + "="*60)
        print("🔬 编码区分析")
        print("="*60)
        coding_f1, coding_f2 = run_both_operations(coding_patterns, "正向")
        
        # 反向分析编码区
        coding_bits_reverse = coding_bits[::-1]
        coding_patterns_reverse = DataProcessor.bits_to_patterns(coding_bits_reverse)
        coding_r1, coding_r2 = run_both_operations(coding_patterns_reverse, "反向")
    else:
        print("\n⚠️  编码区模式数为0，跳过编码区分析")
        coding_f1 = {'tse_base': 0}
        coding_r1 = {'tse_base': 0}
    
    # 分析非编码区
    if len(non_coding_patterns) > 0:
        print("\n" + "="*60)
        print("🔬 非编码区分析")
        print("="*60)
        non_coding_f1, non_coding_f2 = run_both_operations(non_coding_patterns, "正向")
        
        # 反向分析非编码区
        non_coding_bits_reverse = non_coding_bits[::-1]
        non_coding_patterns_reverse = DataProcessor.bits_to_patterns(non_coding_bits_reverse)
        non_coding_r1, non_coding_r2 = run_both_operations(non_coding_patterns_reverse, "反向")
    else:
        print("\n⚠️  非编码区模式数为0，跳过非编码区分析")
        non_coding_f1 = {'tse_base': 0}
        non_coding_r1 = {'tse_base': 0}
    
    # 计算ΔTSE
    print("\n" + "="*60)
    print("📊 ΔTSE 验证")
    print("="*60)
    
    # 正向ΔTSE
    delta_tse_forward = abs(coding_f1['tse_base'] - non_coding_f1['tse_base'])
    # 反向ΔTSE
    delta_tse_reverse = abs(coding_r1['tse_base'] - non_coding_r1['tse_base'])
    # 平均ΔTSE
    avg_delta_tse = (delta_tse_forward + delta_tse_reverse) / 2
    
    # 理论值
    theoretical_delta = 5/64  # 0.078125
    
    print(f"正向编码区 TSE：{coding_f1['tse_base']:.4f}")
    print(f"正向非编码区 TSE：{non_coding_f1['tse_base']:.4f}")
    print(f"正向 ΔTSE：{delta_tse_forward:.4f}")
    print()
    print(f"反向编码区 TSE：{coding_r1['tse_base']:.4f}")
    print(f"反向非编码区 TSE：{non_coding_r1['tse_base']:.4f}")
    print(f"反向 ΔTSE：{delta_tse_reverse:.4f}")
    print()
    print(f"平均 ΔTSE：{avg_delta_tse:.4f}")
    print(f"理论 ΔTSE：{theoretical_delta:.4f}")
    print(f"误差：{abs(avg_delta_tse - theoretical_delta):.4f}")
    
    # 验证结果
    if len(coding_patterns) > 0 and len(non_coding_patterns) > 0:
        if abs(avg_delta_tse - theoretical_delta) < 0.01:
            print("✅ 验证成功！ΔTSE 接近理论值 5/64")
        else:
            print("⚠️  验证结果与理论值有差异")
    else:
        print("⚠️  无法完成验证：编码区或非编码区模式数不足")
    
    return {
        'coding_tse_forward': coding_f1['tse_base'],
        'non_coding_tse_forward': non_coding_f1['tse_base'],
        'coding_tse_reverse': coding_r1['tse_base'],
        'non_coding_tse_reverse': non_coding_r1['tse_base'],
        'delta_tse_forward': delta_tse_forward,
        'delta_tse_reverse': delta_tse_reverse,
        'avg_delta_tse': avg_delta_tse,
        'theoretical_delta': theoretical_delta
    }

# ==============================================================================
# 主程序：双向扫描 + DNA分析
# ==============================================================================
def main():
    print("="*60)
    print("🚀 TAI v10.0 双向扫描版 - DNA分析扩展（流式处理版）")
    print("   正向：原始顺序   |   反向：比特流反转")
    print("   两次运算完全保留，无额外花哨功能")
    print("   新增：DNA序列分析、编码区/非编码区分离、ΔTSE验证")
    print("   优化：流式处理 + 采样模式，避免内存溢出")
    print("="*60)

    data_dir = Path("data")
    res_dir  = Path("results")
    data_dir.mkdir(exist_ok=True)
    res_dir.mkdir(exist_ok=True)

    # 检查是否有DNA数据文件
    fasta_files = list(Path(".").glob("*.fa.gz")) + list(Path(".").glob("*.fasta.gz"))
    gtf_files = list(Path(".").glob("*.gtf.gz"))
    
    if fasta_files and gtf_files:
        print("\n🔍 发现DNA数据文件，开始分析...")
        fasta_path = str(fasta_files[0])
        gtf_path = str(gtf_files[0])
        # 使用采样模式，采样1000万碱基
        analyze_dna(fasta_path, gtf_path, sample_size=10000000)
    else:
        print("\n📁 处理常规数据文件...")
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