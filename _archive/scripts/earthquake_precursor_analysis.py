
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
历史特大地震TSE预警分析
专注于分析震前TSE变化模式，寻找预警信号
"""

import os
import csv
import numpy as np
from datetime import datetime, timedelta

def read_earthquake_data(file_path):
    """读取地震数据"""
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    time_str = row['time'].replace('Z', '+00:00')
                    time = datetime.fromisoformat(time_str)
                    time_naive = time.replace(tzinfo=None)
                    data.append({
                        'mag': float(row['mag']),
                        'depth': float(row['depth']),
                        'time': time_naive,
                        'timestamp': time.timestamp()
                    })
                except:
                    continue
        return data
    except:
        return []

def data_to_binary(values):
    """将数据转换为二进制序列"""
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

def calculate_entropy(binary_string):
    """计算香农熵"""
    if not binary_string:
        return 0.0
    total = len(binary_string)
    counts = {}
    for bit in binary_string:
        counts[bit] = counts.get(bit, 0) + 1
    entropy = 0.0
    for count in counts.values():
        p = count / total
        entropy -= p * np.log2(p)
    return entropy

def calculate_tse(binary_string):
    """计算TSE"""
    entropy = calculate_entropy(binary_string)
    entropy = min(entropy, 4.0)
    tse = 6.0 * entropy / 4.0
    return tse

def sliding_window_analysis(data, main_shock_time, window_hours=6, step_hours=1, min_samples=3):
    """滑动窗口分析，专注于主震前的时间段"""
    sorted_data = sorted(data, key=lambda x: x['time'])
    
    analysis_start = main_shock_time - timedelta(days=10)
    analysis_end = main_shock_time + timedelta(days=1)
    
    filtered_data = [d for d in sorted_data if analysis_start <= d['time'] <= analysis_end]
    
    if not filtered_data:
        return []
    
    window_results = []
    current_time = analysis_start
    
    while current_time < analysis_end:
        window_end = current_time + timedelta(hours=window_hours)
        
        window_data = [d for d in filtered_data if current_time <= d['time'] < window_end]
        
        if window_data and len(window_data) >= min_samples:
            mag_values = [d['mag'] for d in window_data]
            depth_values = [d['depth'] for d in window_data]
            
            mag_binary = data_to_binary(mag_values)
            depth_binary = data_to_binary(depth_values)
            
            mag_tse = calculate_tse(mag_binary) if mag_binary else 0
            depth_tse = calculate_tse(depth_binary) if depth_binary else 0
            
            hours_before = (main_shock_time - current_time).total_seconds() / 3600
            
            window_results.append({
                'start_time': current_time,
                'hours_before_main_shock': hours_before,
                'count': len(window_data),
                'max_mag': max(mag_values),
                'mag_tse': mag_tse,
                'depth_tse': depth_tse,
                'is_main_shock_day': hours_before < 0
            })
        
        current_time += timedelta(hours=step_hours)
    
    return window_results

def analyze_earthquake_sequence(data_file, main_shock_time, eq_name):
    """分析单个地震序列"""
    print(f"\n{'='*60}")
    print(f"分析: {eq_name}")
    print(f"主震时间: {main_shock_time}")
    print(f"{'='*60}")
    
    data = read_earthquake_data(data_file)
    
    if not data:
        print(f"✗ 无法读取数据: {data_file}")
        return
    
    print(f"总地震数: {len(data)}")
    
    results = sliding_window_analysis(data, main_shock_time, window_hours=6, step_hours=1, min_samples=3)
    
    if not results:
        print("⚠ 有效窗口不足")
        return
    
    print(f"\n时间\t\t\t主震前(小时)\t地震数\t震级TSE\t深度TSE\t最大震级")
    print("-" * 85)
    
    mag_tse_values = []
    depth_tse_values = []
    pre_main_shock = []
    post_main_shock = []
    
    for r in results:
        time_str = r['start_time'].strftime('%m-%d %H:%M')
        hours = r['hours_before_main_shock']
        count = r['count']
        mag_tse = r['mag_tse']
        depth_tse = r['depth_tse']
        max_mag = r['max_mag']
        
        print(f"{time_str}\t{hours:6.1f}\t\t{count}\t{mag_tse:.4f}\t{depth_tse:.4f}\t{max_mag:.1f}")
        
        mag_tse_values.append(mag_tse)
        depth_tse_values.append(depth_tse)
        
        if hours > 0:
            pre_main_shock.append({'mag': mag_tse, 'depth': depth_tse, 'hours': hours})
        else:
            post_main_shock.append({'mag': mag_tse, 'depth': depth_tse, 'hours': hours})
    
    print(f"\n--- 统计摘要 ---")
    print(f"震级TSE范围: {min(mag_tse_values):.4f} - {max(mag_tse_values):.4f}")
    print(f"深度TSE范围: {min(depth_tse_values):.4f} - {max(depth_tse_values):.4f}")
    
    if pre_main_shock:
        pre_mag_tse = [x['mag'] for x in pre_main_shock]
        pre_depth_tse = [x['depth'] for x in pre_main_shock]
        
        print(f"\n主震前平均TSE:")
        print(f"  震级TSE: {np.mean(pre_mag_tse):.4f}")
        print(f"  深度TSE: {np.mean(pre_depth_tse):.4f}")
        
        print(f"\n主震前72小时的TSE趋势:")
        t72 = [x for x in pre_main_shock if x['hours'] <= 72]
        if t72:
            print(f"  平均震级TSE: {np.mean([x['mag'] for x in t72]):.4f}")
            print(f"  平均深度TSE: {np.mean([x['depth'] for x in t72]):.4f}")
        
        t24 = [x for x in pre_main_shock if x['hours'] <= 24]
        if t24:
            print(f"\n主震前24小时的TSE:")
            print(f"  平均震级TSE: {np.mean([x['mag'] for x in t24]):.4f}")
            print(f"  平均深度TSE: {np.mean([x['depth'] for x in t24]):.4f}")
            
            t12 = [x for x in pre_main_shock if x['hours'] <= 12]
            if t12:
                print(f"\n主震前12小时的TSE:")
                print(f"  平均震级TSE: {np.mean([x['mag'] for x in t12]):.4f}")
                print(f"  平均深度TSE: {np.mean([x['depth'] for x in t12]):.4f}")

def main():
    """主函数"""
    print("="*60)
    print("历史特大地震TSE预警分析")
    print("寻找震前TSE异常模式")
    print("="*60)
    
    earthquakes = [
        {
            'name': '日本311地震',
            'file': 'data2/earthquake/japan_311_2011.csv',
            'main_shock': datetime(2011, 3, 11, 5, 46, 0)
        },
        {
            'name': '土耳其双震',
            'file': 'data2/earthquake/turkey_2023.csv',
            'main_shock': datetime(2023, 2, 6, 1, 17, 0)
        },
        {
            'name': '汶川地震',
            'file': 'data2/earthquake/wenchuan_2008.csv',
            'main_shock': datetime(2008, 5, 12, 14, 28, 0)
        }
    ]
    
    for eq in earthquakes:
        if os.path.exists(eq['file']):
            analyze_earthquake_sequence(eq['file'], eq['main_shock'], eq['name'])
        else:
            print(f"\n⚠ 文件不存在: {eq['file']}")
    
    print("\n" + "="*60)
    print("分析完成")
    print("="*60)

if __name__ == "__main__":
    main()
