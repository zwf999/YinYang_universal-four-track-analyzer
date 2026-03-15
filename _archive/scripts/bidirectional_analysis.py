#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
太仪v2.0 - 双向比较分析
核心创新：正向TSE vs 反向TSE
这是太仪系统的核心能力！
"""

import os
import csv
import numpy as np
from datetime import datetime, timedelta

class BidirectionalAnalysis:
    def __init__(self):
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
    
    def reverse_binary(self, binary_string):
        """反转二进制序列 - 双向比较的核心"""
        if not binary_string:
            return ""
        return binary_string[::-1]
    
    def calculate_tse(self, binary_string):
        """计算TSE - 核心公式，永不修改"""
        if not binary_string:
            return 999
        entropy = self.calculate_entropy(binary_string)
        tse = 6.0 * entropy / 4.0
        return tse
    
    def bidirectional_tse(self, values):
        """双向TSE计算 - 太仪核心创新"""
        if len(values) < 3:
            return None, None, None
        
        binary = self.data_to_binary(values)
        if not binary:
            return None, None, None
        
        # 正向TSE
        tse_forward = self.calculate_tse(binary)
        
        # 反向TSE（比特流反转）
        binary_reversed = self.reverse_binary(binary)
        tse_reverse = self.calculate_tse(binary_reversed)
        
        # ΔTSE（方向性指标）
        delta_tse = abs(tse_forward - tse_reverse)
        
        return tse_forward, tse_reverse, delta_tse
    
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
    
    def analyze_with_bidirectional(self, data, window_size=50):
        """使用双向比较分析数据"""
        if len(data) < window_size:
            return None
        
        data = sorted(data, key=lambda x: x['time'])
        
        results = []
        
        for i in range(0, len(data) - window_size + 1, window_size // 2):
            window = data[i:i + window_size]
            
            depths = [eq['depth'] for eq in window if eq.get('depth') and eq['depth'] > 0]
            mags = [eq['mag'] for eq in window if eq.get('mag') and eq['mag'] > 0]
            
            if len(depths) >= 3:
                tse_fwd, tse_rev, delta_tse = self.bidirectional_tse(depths)
                
                if tse_fwd is not None and tse_fwd < 100:
                    results.append({
                        'time': window[0]['time'],
                        'tse_forward': tse_fwd,
                        'tse_reverse': tse_rev,
                        'delta_tse': delta_tse,
                        'has_direction': delta_tse > 0.3,  # 方向性阈值
                        'count': len(depths)
                    })
        
        return results
    
    def analyze_earthquake_sequence(self, data):
        """分析地震序列的双向特性"""
        if len(data) < 100:
            return None
        
        data = sorted(data, key=lambda x: x['time'])
        
        # 分成三段：前震、主震、余震
        total = len(data)
        pre_shock = data[:total//3]
        main_shock = data[total//3:2*total//3]
        after_shock = data[2*total//3:]
        
        results = {}
        
        # 分析前震
        if len(pre_shock) >= 30:
            depths = [eq['depth'] for eq in pre_shock if eq.get('depth') and eq['depth'] > 0]
            if len(depths) >= 3:
                tse_fwd, tse_rev, delta = self.bidirectional_tse(depths)
                results['pre_shock'] = {
                    'tse_forward': tse_fwd,
                    'tse_reverse': tse_rev,
                    'delta_tse': delta,
                    'has_direction': delta > 0.3 if delta else False
                }
        
        # 分析主震
        if len(main_shock) >= 30:
            depths = [eq['depth'] for eq in main_shock if eq.get('depth') and eq['depth'] > 0]
            if len(depths) >= 3:
                tse_fwd, tse_rev, delta = self.bidirectional_tse(depths)
                results['main_shock'] = {
                    'tse_forward': tse_fwd,
                    'tse_reverse': tse_rev,
                    'delta_tse': delta,
                    'has_direction': delta > 0.3 if delta else False
                }
        
        # 分析余震
        if len(after_shock) >= 30:
            depths = [eq['depth'] for eq in after_shock if eq.get('depth') and eq['depth'] > 0]
            if len(depths) >= 3:
                tse_fwd, tse_rev, delta = self.bidirectional_tse(depths)
                results['after_shock'] = {
                    'tse_forward': tse_fwd,
                    'tse_reverse': tse_rev,
                    'delta_tse': delta,
                    'has_direction': delta > 0.3 if delta else False
                }
        
        return results
    
    def run_bidirectional_analysis(self):
        """运行双向比较分析"""
        print("=" * 70)
        print("太仪v2.0 - 双向比较分析（核心创新）")
        print("=" * 70)
        print("正向TSE vs 反向TSE → ΔTSE（方向性指标）")
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
        
        all_results = []
        
        for filename, region_name in region_files:
            filepath = os.path.join(data_dir, filename)
            if not os.path.exists(filepath):
                continue
            
            print(f"\n分析 {region_name}...")
            data = self.read_earthquake_data(filepath)
            print(f"  数据量: {len(data)} 条")
            
            if len(data) < 100:
                print("  数据不足，跳过")
                continue
            
            # 地震序列分析
            seq_results = self.analyze_earthquake_sequence(data)
            
            if seq_results:
                print(f"\n  地震序列双向分析:")
                
                if 'pre_shock' in seq_results:
                    r = seq_results['pre_shock']
                    print(f"    前震: 正向TSE={r['tse_forward']:.4f}, 反向TSE={r['tse_reverse']:.4f}, ΔTSE={r['delta_tse']:.4f}")
                    print(f"          方向性: {'✓ 有' if r['has_direction'] else '○ 无'}")
                
                if 'main_shock' in seq_results:
                    r = seq_results['main_shock']
                    print(f"    主震: 正向TSE={r['tse_forward']:.4f}, 反向TSE={r['tse_reverse']:.4f}, ΔTSE={r['delta_tse']:.4f}")
                    print(f"          方向性: {'✓ 有' if r['has_direction'] else '○ 无'}")
                
                if 'after_shock' in seq_results:
                    r = seq_results['after_shock']
                    print(f"    余震: 正向TSE={r['tse_forward']:.4f}, 反向TSE={r['tse_reverse']:.4f}, ΔTSE={r['delta_tse']:.4f}")
                    print(f"          方向性: {'✓ 有' if r['has_direction'] else '○ 无'}")
                
                all_results.append({
                    'region': region_name,
                    'count': len(data),
                    'sequence': seq_results
                })
        
        # 统计汇总
        print("\n" + "=" * 70)
        print("双向比较统计汇总")
        print("=" * 70)
        
        # 统计方向性
        pre_with_dir = sum(1 for r in all_results if r['sequence'].get('pre_shock', {}).get('has_direction', False))
        main_with_dir = sum(1 for r in all_results if r['sequence'].get('main_shock', {}).get('has_direction', False))
        after_with_dir = sum(1 for r in all_results if r['sequence'].get('after_shock', {}).get('has_direction', False))
        
        print(f"\n方向性统计:")
        print(f"  前震有方向性: {pre_with_dir}/{len(all_results)}")
        print(f"  主震有方向性: {main_with_dir}/{len(all_results)}")
        print(f"  余震有方向性: {after_with_dir}/{len(all_results)}")
        
        # ΔTSE统计
        pre_deltas = [r['sequence']['pre_shock']['delta_tse'] for r in all_results if r['sequence'].get('pre_shock')]
        main_deltas = [r['sequence']['main_shock']['delta_tse'] for r in all_results if r['sequence'].get('main_shock')]
        after_deltas = [r['sequence']['after_shock']['delta_tse'] for r in all_results if r['sequence'].get('after_shock')]
        
        if pre_deltas:
            print(f"\n前震ΔTSE: 平均={np.mean(pre_deltas):.4f}, 最大={np.max(pre_deltas):.4f}")
        if main_deltas:
            print(f"主震ΔTSE: 平均={np.mean(main_deltas):.4f}, 最大={np.max(main_deltas):.4f}")
        if after_deltas:
            print(f"余震ΔTSE: 平均={np.mean(after_deltas):.4f}, 最大={np.max(after_deltas):.4f}")
        
        # 保存结果
        output_file = "data2/results/bidirectional_analysis.csv"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['区域', '数据量', '前震正向TSE', '前震反向TSE', '前震ΔTSE', '前震方向性',
                           '主震正向TSE', '主震反向TSE', '主震ΔTSE', '主震方向性',
                           '余震正向TSE', '余震反向TSE', '余震ΔTSE', '余震方向性'])
            
            for r in all_results:
                seq = r['sequence']
                pre = seq.get('pre_shock', {})
                main = seq.get('main_shock', {})
                after = seq.get('after_shock', {})
                
                writer.writerow([
                    r['region'],
                    r['count'],
                    f"{pre.get('tse_forward', 0):.4f}",
                    f"{pre.get('tse_reverse', 0):.4f}",
                    f"{pre.get('delta_tse', 0):.4f}",
                    "是" if pre.get('has_direction') else "否",
                    f"{main.get('tse_forward', 0):.4f}",
                    f"{main.get('tse_reverse', 0):.4f}",
                    f"{main.get('delta_tse', 0):.4f}",
                    "是" if main.get('has_direction') else "否",
                    f"{after.get('tse_forward', 0):.4f}",
                    f"{after.get('tse_reverse', 0):.4f}",
                    f"{after.get('delta_tse', 0):.4f}",
                    "是" if after.get('has_direction') else "否"
                ])
        
        print(f"\n结果已保存到: {output_file}")
        print("\n双向比较分析完成！")
        
        return all_results

if __name__ == "__main__":
    analysis = BidirectionalAnalysis()
    analysis.run_bidirectional_analysis()
