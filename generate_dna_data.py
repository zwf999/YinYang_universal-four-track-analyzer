# generate_dna_data.py
# 生成健康和癌变的DNA数据

import random
import time


class DNAGenerator:
    """DNA数据生成器"""
    
    def __init__(self):
        """初始化DNA生成器"""
        self.bases = ['A', 'C', 'G', 'T']
        
        # 健康DNA的碱基频率（基于人类基因组）
        self.healthy_frequencies = {
            'A': 0.29,  # 腺嘌呤
            'C': 0.21,  # 胞嘧啶
            'G': 0.21,  # 鸟嘌呤
            'T': 0.29   # 胸腺嘧啶
        }
        
        # 癌变DNA的碱基频率（模拟突变特征）
        self.cancer_frequencies = {
            'A': 0.32,  # 腺嘌呤增加
            'C': 0.18,  # 胞嘧啶减少
            'G': 0.18,  # 鸟嘌呤减少
            'T': 0.32   # 胸腺嘧啶增加
        }
        
        # 常见的突变模式
        self.mutations = {
            'C>T': 0.3,  # 胞嘧啶突变为胸腺嘧啶（最常见的点突变）
            'G>A': 0.25,  # 鸟嘌呤突变为腺嘌呤
            'A>T': 0.15,  # 腺嘌呤突变为胸腺嘧啶
            'T>A': 0.1,   # 胸腺嘧啶突变为腺嘌呤
            'C>G': 0.1,   # 胞嘧啶突变为鸟嘌呤
            'G>C': 0.1    # 鸟嘌呤突变为胞嘧啶
        }
    
    def generate_healthy_dna(self, length):
        """生成健康的DNA序列"""
        print(f"正在生成健康的DNA序列，长度: {length}...")
        start_time = time.time()
        
        # 基于频率生成健康DNA
        dna = []
        bases = list(self.healthy_frequencies.keys())
        weights = list(self.healthy_frequencies.values())
        
        for _ in range(length):
            base = random.choices(bases, weights=weights)[0]
            dna.append(base)
        
        dna_sequence = ''.join(dna)
        end_time = time.time()
        print(f"生成健康DNA序列完成，耗时: {end_time - start_time:.2f}秒")
        
        return dna_sequence
    
    def generate_cancer_dna(self, length):
        """生成癌变的DNA序列"""
        print(f"正在生成癌变的DNA序列，长度: {length}...")
        start_time = time.time()
        
        # 先生成健康DNA作为基础
        healthy_dna = self.generate_healthy_dna(length)
        
        # 引入突变
        dna = list(healthy_dna)
        mutation_rate = 0.05  # 5%的突变率
        
        for i in range(length):
            if random.random() < mutation_rate:
                # 随机选择一个突变
                mutation = random.choices(
                    list(self.mutations.keys()),
                    weights=list(self.mutations.values())
                )[0]
                original, mutated = mutation.split('>')
                
                if dna[i] == original:
                    dna[i] = mutated
        
        dna_sequence = ''.join(dna)
        end_time = time.time()
        print(f"生成癌变DNA序列完成，耗时: {end_time - start_time:.2f}秒")
        
        return dna_sequence
    
    def save_dna_data(self, dna_sequence, filename):
        """保存DNA数据到文件"""
        print(f"正在保存DNA数据到文件: {filename}...")
        
        # 保存完整序列
        with open(filename, 'w') as f:
            f.write(dna_sequence