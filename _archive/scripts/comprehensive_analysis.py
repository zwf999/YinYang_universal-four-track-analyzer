#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
太仪v2.0 - 全面深入验证分析
使用42,278条数据和优化阈值进行全面验证
核心算法永不修改
"""

import os
import csv
import numpy as np
from datetime import datetime, timedelta

class ComprehensiveAnalysis:
    def __init__(self):
        # 优化后的阈值（应用层参数）
        self.long_threshold = 0.05   # 5%
        self.short_threshold = 0.10  # 10%
        self.min_samples = 3
    
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
    
    def analyze_tse_distribution(self, data, window_size=50):
        """分析TSE分布"""
        if len(data) < window_size:
            return None
        
        data = sorted(data, key=lambda x: x['time'])
        
        tse_values = []
        
        for i in range(0, len(data) - window_size + 1, window_size // 2):
            window = data[i:i + window_size]
            depths = [eq['depth'] for eq in window if eq.get('depth') and eq['depth'] > 0]
            mags = [eq['mag'] for eq in window if eq.get('mag') and eq['mag'] > 0]
            
            if len(depths) >= 3:
                tse_depth = self.calculate_tse(self.data_to_binary(depths))
                if tse_depth < 100:
                    tse_values.append(tse_depth)
        
        if not tse_values:
            return None
        
        return {
            'mean': np.mean(tse_values),
            'std': np.std(tse_values),
            'min': np.min(tse_values),
            'max': np.max(tse_values),
            'median': np.median(tse_values),
            'count': len(tse_values)
        }
    
    def detect_precursor(self, data, window_size=50):
        """检测前兆信号"""
        if len(data) < window_size * 2:
            return None
        
        data = sorted(data, key=lambda x: x['time'])
        
        # 分成前后两半
        mid_idx = len(data) // 2
        first_half = data[:mid_idx]
        second_half = data[mid_idx:]
        
        # 分析前半段
        first_stats = self.analyze_tse_distribution(first_half, window_size)
        # 分析后半段
        second_stats = self.analyze_tse_distribution(second_half, window_size)
        
        if not first_stats or not second_stats:
            return None
        
        # 计算TSE变化
        depth_change = first_stats['mean'] - second_stats['mean']
        depth_change_rate = depth_change / first_stats['mean'] if first_stats['mean'] > 0 else 0
        
        # 判断是否为前兆
        is_precursor = depth_change_rate > self.long_threshold
        
        return {
            'first_mean': first_stats['mean'],
            'second_mean': second_stats['mean'],
            'change': depth_change,
            'change_rate': depth_change_rate,
            'is_precursor': is_precursor,
            'first_count': first_stats['count'],
            'second_count': second_stats['count']
        }
    
    def analyze_region(self, filepath, region_name):
        """分析单个区域"""
        data = self.read_earthquake_data(filepath)
        
        if len(data) < 100:
            return None
        
        # TSE分布分析
        tse_stats = self.analyze_tse_distribution(data)
        
        # 前兆检测
        precursor = self.detect_precursor(data)
        
        # 震级分布
        mags = [eq['mag'] for eq in data if eq.get('mag') and eq['mag'] > 0]
        mag_stats = {
            'mean': np.mean(mags) if mags else 0,
            'std': np.std(mags) if mags else 0,
            'max': np.max(mags) if mags else 0,
            'min': np.min(mags) if mags else 0
        }
        
        # 深度分布
        depths = [eq['depth'] for eq in data if eq.get('depth') and eq['depth'] > 0]
        depth_stats = {
            'mean': np.mean(depths) if depths else 0,
            'std': np.std(depths) if depths else 0,
            'max': np.max(depths) if depths else 0,
            'min': np.min(depths) if depths else 0
        }
        
        return {
            'region': region_name,
            'count': len(data),
            'tse_stats': tse_stats,
            'precursor': precursor,
            'mag_stats': mag_stats,
            'depth_stats': depth_stats
        }
    
    def run_comprehensive_analysis(self):
        """运行全面分析"""
        print("=" * 70)
        print("太仪v2.0 - 全面深入验证分析")
        print("=" * 70)
        print(f"优化阈值: 长窗{self.long_threshold*100:.0f}%, 短窗{self.short_threshold*100:.0f}%")
        print("=" * 70)
        
        data_dir = "data2/earthquake"
        
        # 分析所有区域数据
        region_files = [
            ('region_日本本州.csv', '日本本州'),
            ('region_智利中部.csv', '智利中部'),
            ('region_印尼苏门答腊.csv', '印尼苏门答腊'),
            ('region_中国西南.csv', '中国西南'),
            ('region_新西兰.csv', '新西兰'),
            ('recent_1year.csv', '全球最近1年'),
        ]
        
        results = []
        
        for filename, region_name in region_files:
            filepath = os.path.join(data_dir, filename)
            if not os.path.exists(filepath):
                continue
            
            print(f"\n分析 {region_name}...")
            result = self.analyze_region(filepath, region_name)
            
            if result:
                results.append(result)
                print(f"  数据量: {result['count']} 条")
                if result['tse_stats']:
                    print(f"  TSE均值: {result['tse_stats']['mean']:.4f}")
                    print(f"  TSE范围: {result['tse_stats']['min']:.4f} - {result['tse_stats']['max']:.4f}")
                if result['precursor']:
                    status = "✓ 检测到前兆" if result['precursor']['is_precursor'] else "○ 无前兆"
                    print(f"  TSE变化率: {result['precursor']['change_rate']*100:.1f}% {status}")
        
        # 统计汇总
        print("\n" + "=" * 70)
        print("统计汇总")
        print("=" * 70)
        
        total_count = sum(r['count'] for r in results)
        print(f"总数据量: {total_count} 条")
        
        # TSE统计
        tse_means = [r['tse_stats']['mean'] for r in results if r['tse_stats']]
        if tse_means:
            print(f"平均TSE均值: {np.mean(tse_means):.4f}")
        
        # 前兆统计
        precursors = [r for r in results if r['precursor'] and r['precursor']['is_precursor']]
        print(f"检测到前兆的区域: {len(precursors)}/{len(results)}")
        
        # 显示前兆详情
        if precursors:
            print("\n前兆详情:")
            for r in precursors:
                print(f"  {r['region']}: TSE变化率 {r['precursor']['change_rate']*100:.1f}%")
        
        # 保存结果
        output_file = "data2/results/comprehensive_analysis.csv"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['区域', '数据量', 'TSE均值', 'TSE最小', 'TSE最大', 'TSE变化率', '前兆'])
            
            for r in results:
                tse_mean = r['tse_stats']['mean'] if r['tse_stats'] else 0
                tse_min = r['tse_stats']['min'] if r['tse_stats'] else 0
                tse_max = r['tse_stats']['max'] if r['tse_stats'] else 0
                change_rate = r['precursor']['change_rate'] if r['precursor'] else 0
                is_precursor = "是" if r['precursor'] and r['precursor']['is_precursor'] else "否"
                
                writer.writerow([
                    r['region'],
                    r['count'],
                    f"{tse_mean:.4f}",
                    f"{tse_min:.4f}",
                    f"{tse_max:.4f}",
                    f"{change_rate*100:.1f}%",
                    is_precursor
                ])
        
        print(f"\n结果已保存到: {output_file}")
        
        return results

if __name__ == "__main__":
    analysis = ComprehensiveAnalysis()
    analysis.run_comprehensive_analysis()
