
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
地震数据时间序列TSE分析（增强版）
按时间窗口分析地震数据，寻找地震前后的TSE变化模式
新增功能：
- 自适应窗口分析（根据地震密度自动调整）
- 样本量标记和过滤
- 多特征联合分析
"""

import os
import csv
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from collections import defaultdict

def read_earthquake_data(file_path):
    """读取地震数据"""
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['type'] == 'earthquake':
                    try:
                        mag = float(row['mag'])
                        depth = float(row['depth'])
                        lat = float(row['latitude'])
                        lon = float(row['longitude'])
                        time_str = row['time']
                        
                        time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                        timestamp = time.timestamp()
                        
                        data.append({
                            'mag': mag,
                            'depth': depth,
                            'lat': lat,
                            'lon': lon,
                            'time': time,
                            'timestamp': timestamp
                        })
                    except:
                        continue
        print(f"✓ 读取文件: {os.path.basename(file_path)}")
        print(f"  共 {len(data)} 条地震记录")
        return data
    except Exception as e:
        print(f"✗ 读取文件失败: {e}")
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

def time_window_analysis(data, window_hours=24, min_samples=5):
    """时间窗口分析（带样本量过滤）"""
    if not data:
        return []
    
    sorted_data = sorted(data, key=lambda x: x['time'])
    
    start_time = sorted_data[0]['time']
    end_time = sorted_data[-1]['time']
    
    window_results = []
    current_time = start_time
    
    while current_time < end_time:
        window_end = current_time + timedelta(hours=window_hours)
        
        window_data = [d for d in sorted_data if current_time <= d['time'] < window_end]
        
        if window_data and len(window_data) >= min_samples:
            mag_values = [d['mag'] for d in window_data]
            depth_values = [d['depth'] for d in window_data]
            
            mag_binary = data_to_binary(mag_values)
            depth_binary = data_to_binary(depth_values)
            
            mag_tse = calculate_tse(mag_binary) if mag_binary else 0
            depth_tse = calculate_tse(depth_binary) if depth_binary else 0
            
            window_results.append({
                'start_time': current_time,
                'end_time': window_end,
                'count': len(window_data),
                'avg_mag': np.mean(mag_values),
                'max_mag': max(mag_values),
                'min_mag': min(mag_values),
                'avg_depth': np.mean(depth_values),
                'max_depth': max(depth_values),
                'min_depth': min(depth_values),
                'mag_tse': mag_tse,
                'depth_tse': depth_tse,
                'mag_entropy': calculate_entropy(mag_binary) if mag_binary else 0,
                'depth_entropy': calculate_entropy(depth_binary) if depth_binary else 0
            })
        
        current_time = window_end
    
    return window_results

def adaptive_window_analysis(data, target_samples=20, max_hours=168):
    """自适应窗口分析（根据地震密度自动调整窗口大小）"""
    if not data:
        return []
    
    sorted_data = sorted(data, key=lambda x: x['time'])
    start_time = sorted_data[0]['time']
    end_time = sorted_data[-1]['time']
    
    window_results = []
    current_time = start_time
    
    while current_time < end_time:
        window_hours = 1
        window_end = current_time + timedelta(hours=window_hours)
        window_data = [d for d in sorted_data if current_time <= d['time'] < window_end]
        
        while len(window_data) < target_samples and window_hours < max_hours:
            window_hours *= 2
            window_end = current_time + timedelta(hours=window_hours)
            window_data = [d for d in sorted_data if current_time <= d['time'] < window_end]
        
        if window_data:
            mag_values = [d['mag'] for d in window_data]
            depth_values = [d['depth'] for d in window_data]
            
            mag_binary = data_to_binary(mag_values)
            depth_binary = data_to_binary(depth_values)
            
            mag_tse = calculate_tse(mag_binary) if mag_binary else 0
            depth_tse = calculate_tse(depth_binary) if depth_binary else 0
            
            combined_values = []
            for d in window_data:
                combined_values.append(d['mag'] * 10 + d['depth'])
            combined_binary = data_to_binary(combined_values)
            combined_tse = calculate_tse(combined_binary) if combined_binary else 0
            
            window_results.append({
                'start_time': current_time,
                'end_time': window_end,
                'window_hours': window_hours,
                'count': len(window_data),
                'avg_mag': np.mean(mag_values),
                'max_mag': max(mag_values),
                'min_mag': min(mag_values),
                'avg_depth': np.mean(depth_values),
                'max_depth': max(depth_values),
                'min_depth': min(depth_values),
                'mag_tse': mag_tse,
                'depth_tse': depth_tse,
                'combined_tse': combined_tse,
                'mag_entropy': calculate_entropy(mag_binary) if mag_binary else 0,
                'depth_entropy': calculate_entropy(depth_binary) if depth_binary else 0
            })
        
        current_time = window_end
    
    return window_results

def sliding_window_analysis(data, window_hours=24, step_hours=1, min_samples=5):
    """滑动窗口分析（更细粒度的时间分辨率）"""
    if not data:
        return []
    
    sorted_data = sorted(data, key=lambda x: x['time'])
    start_time = sorted_data[0]['time']
    end_time = sorted_data[-1]['time']
    
    window_results = []
    current_time = start_time
    
    while current_time < end_time:
        window_end = current_time + timedelta(hours=window_hours)
        
        window_data = [d for d in sorted_data if current_time <= d['time'] < window_end]
        
        if window_data and len(window_data) >= min_samples:
            mag_values = [d['mag'] for d in window_data]
            depth_values = [d['depth'] for d in window_data]
            
            mag_binary = data_to_binary(mag_values)
            depth_binary = data_to_binary(depth_values)
            
            mag_tse = calculate_tse(mag_binary) if mag_binary else 0
            depth_tse = calculate_tse(depth_binary) if depth_binary else 0
            
            combined_values = []
            for d in window_data:
                combined_values.append(d['mag'] * 10 + d['depth'])
            combined_binary = data_to_binary(combined_values)
            combined_tse = calculate_tse(combined_binary) if combined_binary else 0
            
            window_results.append({
                'start_time': current_time,
                'end_time': window_end,
                'count': len(window_data),
                'avg_mag': np.mean(mag_values),
                'max_mag': max(mag_values),
                'avg_depth': np.mean(depth_values),
                'max_depth': max(depth_values),
                'mag_tse': mag_tse,
                'depth_tse': depth_tse,
                'combined_tse': combined_tse
            })
        
        current_time += timedelta(hours=step_hours)
    
    return window_results

def analyze_earthquake_files():
    """分析地震数据文件"""
    earthquake_dir = os.path.join('data2', 'earthquake')
    files = [f for f in os.listdir(earthquake_dir) if f.endswith('.csv')]
    
    all_results = {}
    
    for file_name in files:
        file_path = os.path.join(earthquake_dir, file_name)
        data = read_earthquake_data(file_path)
        
        if data:
            file_results = {}
            
            print(f"\n分析 {file_name}...")
            
            window_sizes = [1, 6, 24]
            for window_hours in window_sizes:
                print(f"  {window_hours}h窗口分析...")
                results = time_window_analysis(data, window_hours, min_samples=5)
                file_results[f'{window_hours}h'] = results
                print(f"    有效窗口数: {len(results)}")
            
            print(f"  自适应窗口分析...")
            adaptive_results = adaptive_window_analysis(data, target_samples=20)
            file_results['adaptive'] = adaptive_results
            print(f"    有效窗口数: {len(adaptive_results)}")
            
            print(f"  滑动窗口分析...")
            sliding_results = sliding_window_analysis(data, window_hours=6, step_hours=1, min_samples=3)
            file_results['sliding_6h'] = sliding_results
            print(f"    有效窗口数: {len(sliding_results)}")
            
            all_results[file_name] = file_results
    
    return all_results

def plot_time_series(results, output_dir='data2'):
    """绘制时间序列图表"""
    os.makedirs(output_dir, exist_ok=True)
    
    for file_name, file_results in results.items():
        for window, window_results in file_results.items():
            if not window_results:
                continue
            
            times = [r['start_time'] for r in window_results]
            mag_tse = [r['mag_tse'] for r in window_results]
            depth_tse = [r['depth_tse'] for r in window_results]
            counts = [r['count'] for r in window_results]
            max_mag = [r['max_mag'] for r in window_results]
            
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
            
            ax1.plot(times, mag_tse, label='震级TSE', color='blue', marker='o')
            ax1.plot(times, depth_tse, label='深度TSE', color='green', marker='s')
            if 'combined_tse' in window_results[0]:
                combined_tse = [r['combined_tse'] for r in window_results]
                ax1.plot(times, combined_tse, label='联合TSE', color='purple', marker='^')
            ax1.set_ylabel('TSE值')
            ax1.set_title(f'{file_name} - {window}窗口 TSE分析')
            ax1.legend()
            ax1.grid(True)
            
            ax2.bar(times, counts, color='orange', alpha=0.6)
            ax2.set_ylabel('地震次数')
            ax2.grid(True)
            
            ax3.plot(times, max_mag, label='最大震级', color='red', marker='o')
            ax3.set_ylabel('最大震级')
            ax3.set_xlabel('时间')
            ax3.grid(True)
            
            plt.tight_layout()
            output_file = os.path.join(output_dir, f'{os.path.splitext(file_name)[0]}_{window}_tse_analysis.png')
            plt.savefig(output_file)
            plt.close()
            
            print(f"✓ 图表已保存: {output_file}")

def main():
    """主函数"""
    print("=" * 60)
    print("地震数据时间序列TSE分析（增强版）")
    print("新增：自适应窗口、滑动窗口、多特征联合分析")
    print("=" * 60)
    
    results = analyze_earthquake_files()
    
    if not results:
        print("✗ 没有找到地震数据文件")
        return 1
    
    print("\n绘制时间序列图表...")
    plot_time_series(results)
    
    output_file = os.path.join('data2', 'earthquake_time_series_analysis_enhanced.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("地震数据时间序列TSE分析结果（增强版）\n")
        f.write("=" * 60 + "\n")
        
        for file_name, file_results in results.items():
            f.write(f"\n文件: {file_name}\n")
            for window, window_results in file_results.items():
                f.write(f"\n  {window}窗口分析:\n")
                
                sample_counts = [r['count'] for r in window_results]
                mag_tse_values = [r['mag_tse'] for r in window_results]
                depth_tse_values = [r['depth_tse'] for r in window_results]
                
                f.write(f"    窗口数: {len(window_results)}\n")
                f.write(f"    样本量范围: {min(sample_counts)}-{max(sample_counts)}\n")
                f.write(f"    震级TSE范围: {min(mag_tse_values):.4f}-{max(mag_tse_values):.4f}\n")
                f.write(f"    深度TSE范围: {min(depth_tse_values):.4f}-{max(depth_tse_values):.4f}\n")
                
                f.write(f"    详细数据:\n")
                for i, result in enumerate(window_results[:20]):
                    f.write(f"      {i+1}. {result['start_time']} - 地震:{result['count']}次, 震级TSE:{result['mag_tse']:.4f}, 深度TSE:{result['depth_tse']:.4f}\n")
                if len(window_results) > 20:
                    f.write(f"      ... 共 {len(window_results)} 个窗口\n")
    
    print(f"\n✓ 分析结果已保存到: {output_file}")
    print("\n" + "=" * 60)
    print("时间序列分析完成！")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    main()
