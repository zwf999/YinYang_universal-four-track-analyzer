#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
太仪v2.0 - 阈值优化模块
基于真实数据统计优化预警阈值
核心算法永不修改
"""

import os
import csv
import numpy as np
from datetime import datetime, timedelta

class ThresholdOptimizer:
    def __init__(self):
        pass
    
    def calculate_entropy(self, binary_string):
        """计算香农熵 - 核心公式，永不修改"""
        if not binary_string or len(binary_string) < 8:
            return 0.0
        total = len(binary_string)
        counts = {}
        for char in binary_string:
            counts[char] = counts.get(char, 0) + 1
        entropy = 0.0
        for count in counts.values():
            p = count / total
            if p > 0:
                entropy -= p * np.log2(p)
        return min(entropy, 4.0)
    
    def data_to_binary(self, values):
        """将数据转换为二进制序列 - 核心方法，永不修改"""
        if not values or len(values) < 2:
            return ""
        min_val = min(values)
        max_val = max(values)
        if max_val == min_val:
            return ""
        normalized = [(v - min_val) / (max_val - min_val) for v in values]
        binary = []
        for val in normalized:
            byte = int(val * 255)
            binary_str = bin(byte)[2:].zfill(8)
            binary.append(binary_str)
        return ''.join(binary)
    
    def calculate_tse(self, binary_string):
        """计算TSE - 核心公式，永不修改"""
        if not binary_string:
            return 999
        entropy = self.calculate_entropy(binary_string)
        tse = 6.0 * entropy / 4.0
        return tse
    
    def read_earthquake_data(self, filepath):
        """读取地震数据"""
        data = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        time_str = row.get('time', '')
                        if not time_str:
                            continue
                        time_str = time_str.replace('Z', '+00:00')
                        time = datetime.fromisoformat(time_str)
                        time = time.replace(tzinfo=None)
                        mag = float(row.get('mag', 0)) if row.get('mag') else 0
                        depth = float(row.get('depth', 0)) if row.get('depth') else 0
                        data.append({'time': time, 'mag': mag, 'depth': depth})
                    except:
                        continue
        except Exception as e:
            pass
        return data
    
    def calculate_tse_drop(self, data):
        """计算TSE降幅"""
        if len(data) < 10:
            return None
        
        data = sorted(data, key=lambda x: x['time'])
        
        mid_idx = len(data) // 2
        first_half = data[:mid_idx]
        second_half = data[mid_idx:]
        
        depths1 = [eq['depth'] for eq in first_half if eq.get('depth') and eq['depth'] > 0]
        depths2 = [eq['depth'] for eq in second_half if eq.get('depth') and eq['depth'] > 0]
        
        if len(depths1) < 3 or len(depths2) < 3:
            return None
        
        tse1 = self.calculate_tse(self.data_to_binary(depths1))
        tse2 = self.calculate_tse(self.data_to_binary(depths2))
        
        if tse1 < 100 and tse2 < 100 and tse1 > 0:
            drop_rate = (tse1 - tse2) / tse1
            return drop_rate
        
        return None
    
    def optimize_thresholds(self):
        """基于真实数据优化阈值"""
        print("=" * 70)
        print("太仪v2.0 - 阈值优化")
        print("=" * 70)
        
        data_dir = "data2/earthquake"
        
        # 查找所有full.csv文件
        all_files = os.listdir(data_dir)
        files = [f for f in all_files if f.endswith('_full.csv') or f.startswith('m7_')]
        
        print(f"找到 {len(files)} 个数据文件")
        
        all_drops = []
        
        for filename in files:
            filepath = os.path.join(data_dir, filename)
            data = self.read_earthquake_data(filepath)
            
            if len(data) < 20:
                continue
            
            drop = self.calculate_tse_drop(data)
            if drop is not None:
                all_drops.append({
                    'file': filename,
                    'count': len(data),
                    'drop': drop
                })
                print(f"  {filename}: {len(data)}条, 降幅{drop*100:.1f}%")
        
        if not all_drops:
            print("无有效数据")
            return None
        
        drops = [d['drop'] for d in all_drops]
        mean_drop = np.mean(drops)
        std_drop = np.std(drops)
        median_drop = np.median(drops)
        max_drop = np.max(drops)
        min_drop = np.min(drops)
        
        print("\n" + "=" * 70)
        print("统计结果")
        print("=" * 70)
        print(f"样本数: {len(drops)}")
        print(f"平均降幅: {mean_drop*100:.1f}%")
        print(f"标准差: {std_drop*100:.1f}%")
        print(f"中位数: {median_drop*100:.1f}%")
        print(f"最大降幅: {max_drop*100:.1f}%")
        print(f"最小降幅: {min_drop*100:.1f}%")
        
        long_threshold = max(0.05, mean_drop - 0.5 * std_drop)
        short_threshold = max(0.10, mean_drop)
        
        print("\n" + "=" * 70)
        print("优化后的阈值建议")
        print("=" * 70)
        print(f"长窗阈值（宽松）: {long_threshold*100:.1f}%")
        print(f"短窗阈值（严格）: {short_threshold*100:.1f}%")
        
        config_file = "data2/config/optimized_thresholds.conf"
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write("# 太仪v2.0 - 优化后的阈值配置\n")
            f.write(f"# 基于真实数据统计\n")
            f.write(f"# 样本数: {len(drops)}\n")
            f.write(f"long_window_threshold = {long_threshold:.4f}\n")
            f.write(f"short_window_threshold = {short_threshold:.4f}\n")
            f.write(f"mean_drop = {mean_drop:.4f}\n")
            f.write(f"std_drop = {std_drop:.4f}\n")
        
        print(f"\n配置已保存到: {config_file}")
        
        return {
            'long_threshold': long_threshold,
            'short_threshold': short_threshold,
            'mean_drop': mean_drop,
            'std_drop': std_drop
        }

if __name__ == "__main__":
    optimizer = ThresholdOptimizer()
    optimizer.optimize_thresholds()
