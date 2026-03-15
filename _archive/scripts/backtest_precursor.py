#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
太仪地震预警系统 - 精确前兆检测
分析震前特定时间窗口 vs 之前时间窗口的TSE变化
"""

import os
import csv
import numpy as np
from datetime import datetime, timedelta

def calculate_entropy(binary_string):
    """计算香农熵"""
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

def calculate_tse(binary_string):
    """计算TSE"""
    if not binary_string:
        return 999
    entropy = calculate_entropy(binary_string)
    tse = 6.0 * entropy / 4.0
    return tse

def read_earthquake_file(filepath):
    """读取地震CSV文件"""
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

                    mag = float(row.get('mag', 0))
                    depth = float(row.get('depth', 0))

                    data.append({
                        'time': time,
                        'mag': mag,
                        'depth': depth,
                        'lat': float(row.get('latitude', 0)),
                        'lon': float(row.get('longitude', 0)),
                    })
                except:
                    continue
    except Exception as e:
        print(f"  读取失败: {e}")
    return data

def analyze_precursor(data, main_time, window_hours=24, pre_hours=168):
    """分析震前TSE前兆"""
    pre_data = [eq for eq in data if main_time - timedelta(hours=pre_hours) <= eq['time'] < main_time]
    
    if len(pre_data) < 10:
        return None
    
    pre_data = sorted(pre_data, key=lambda x: x['time'])
    
    window_minutes = window_hours * 60
    pre_minutes = pre_hours * 60
    
    min_tse_depth = 999
    min_tse_mag = 999
    min_time = None
    
    for i in range(len(pre_data)):
        window_data = []
        for eq in pre_data[i:]:
            if (eq['time'] - pre_data[i]['time']).total_seconds() / 60 <= window_minutes:
                window_data.append(eq)
            else:
                break
        
        if len(window_data) < 5:
            continue
        
        depths = [eq['depth'] for eq in window_data if eq.get('depth')]
        mags = [eq['mag'] for eq in window_data if eq.get('mag')]
        
        if len(depths) >= 5:
            bin_depth = data_to_binary(depths)
            tse_depth = calculate_tse(bin_depth)
            
            if tse_depth < min_tse_depth:
                min_tse_depth = tse_depth
                min_time = window_data[0]['time']
        
        if len(mags) >= 5:
            bin_mag = data_to_binary(mags)
            tse_mag = calculate_tse(bin_mag)
            
            if tse_mag < min_tse_mag:
                min_tse_mag = tse_mag
    
    baseline_start = main_time - timedelta(hours=pre_hours*2)
    baseline_end = main_time - timedelta(hours=pre_hours)
    baseline_data = [eq for eq in data if baseline_start <= eq['time'] < baseline_end]
    
    baseline_depths = [eq['depth'] for eq in baseline_data if eq.get('depth')]
    baseline_mags = [eq['mag'] for eq in baseline_data if eq.get('mag')]
    
    baseline_tse_depth = 999
    baseline_tse_mag = 999
    
    if len(baseline_depths) >= 10:
        bin_depth = data_to_binary(baseline_depths)
        baseline_tse_depth = calculate_tse(bin_depth)
    
    if len(baseline_mags) >= 10:
        bin_mag = data_to_binary(baseline_mags)
        baseline_tse_mag = calculate_tse(bin_mag)
    
    return {
        'min_depth_tse': min_tse_depth,
        'min_mag_tse': min_tse_mag,
        'baseline_depth_tse': baseline_tse_depth,
        'baseline_mag_tse': baseline_tse_mag,
        'depth_drop': baseline_tse_depth - min_tse_depth if baseline_tse_depth < 100 else 0,
        'mag_drop': baseline_tse_mag - min_tse_mag if baseline_tse_mag < 100 else 0,
        'min_time': min_time,
        'pre_count': len(pre_data),
    }

def main():
    print("=" * 70)
    print("太仪地震预警系统 - 精确前兆检测")
    print("=" * 70)

    earthquake_files = [
        ("data2/earthquake/wenchuan_2008.csv", "汶川2008"),
        ("data2/earthquake/japan_311_2011.csv", "日本311"),
        ("data2/earthquake/turkey_2023.csv", "土耳其2023"),
    ]

    results = []

    for filepath, name in earthquake_files:
        if not os.path.exists(filepath):
            continue

        print(f"\n{'='*50}")
        print(f"分析: {name}")
        print(f"{'='*50}")
        
        data = read_earthquake_file(filepath)
        print(f"总记录数: {len(data)}")

        if len(data) < 20:
            continue

        data = sorted(data, key=lambda x: x['time'])
        main_time = data[-1]['time']
        main_mag = data[-1]['mag']
        main_depth = data[-1]['depth']

        print(f"主震: {main_time}, M{main_mag}, 深度{main_depth}km")

        for pre_hours in [168, 72, 24]:
            result = analyze_precursor(data, main_time, window_hours=6, pre_hours=pre_hours)
            
            if result and result['min_depth_tse'] < 100:
                drop_pct = result['depth_drop'] / max(result['baseline_depth_tse'], 0.1) * 100
                
                print(f"\n  前{pre_hours}小时窗口分析:")
                print(f"    基线深度TSE: {result['baseline_depth_tse']:.4f}")
                print(f"    最低深度TSE: {result['min_depth_tse']:.4f}")
                print(f"    下降量: {result['depth_drop']:.4f} ({drop_pct:.1f}%)")
                
                if result['baseline_mag_tse'] < 100:
                    mag_drop_pct = result['mag_drop'] / max(result['baseline_mag_tse'], 0.1) * 100
                    print(f"    基线震级TSE: {result['baseline_mag_tse']:.4f}")
                    print(f"    最低震级TSE: {result['min_mag_tse']:.4f}")
                    print(f"    下降量: {result['mag_drop']:.4f} ({mag_drop_pct:.1f}%)")
                
                is_precursor = result['depth_drop'] > 0.3 and drop_pct > 20
                
                results.append({
                    'name': name,
                    'main_time': main_time,
                    'main_mag': main_mag,
                    'pre_hours': pre_hours,
                    'baseline_tse': result['baseline_depth_tse'],
                    'min_tse': result['min_depth_tse'],
                    'drop': result['depth_drop'],
                    'drop_pct': drop_pct,
                    'is_precursor': is_precursor,
                })

    print("\n" + "=" * 70)
    print("统计结果")
    print("=" * 70)

    if not results:
        print("无有效结果")
        return

    precursors = [r for r in results if r['is_precursor']]
    print(f"\n检测到前兆信号: {len(precursors)}/{len(results)}")

    print("\n详细结果:")
    for r in results:
        status = "✓ 前兆" if r['is_precursor'] else "○ 无"
        print(f"  {r['name']} (前{r['pre_hours']}h): M{r['main_mag']:.1f}, 下降{r['drop_pct']:.1f}% {status}")

    print("\n" + "=" * 70)
    print("结论")
    print("=" * 70)

    if len(precursors) >= 2:
        print("✓ 检测到显著的前兆信号！")
    elif len(precursors) >= 1:
        print("⚠ 检测到潜在前兆")
    else:
        print("⚠ 未检测到显著前兆")

    output_file = "data2/results/precursor_exact.csv"
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['名称', '主震时间', '主震震级', '分析窗口', '基线TSE', '最低TSE', '下降', '下降%', '前兆'])
        for r in results:
            writer.writerow([r['name'], r['main_time'], r['main_mag'], f"前{r['pre_hours']}h",
                           f"{r['baseline_tse']:.4f}", f"{r['min_tse']:.4f}",
                           f"{r['drop']:.4f}", f"{r['drop_pct']:.1f}", "是" if r['is_precursor'] else "否"])

    print(f"\n结果已保存到: {output_file}")

if __name__ == "__main__":
    main()
