#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
太仪地震预警系统 - 精确前兆检测 v2
按时间分段：比较主震前X小时 vs 更早时间的TSE
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

def analyze_time_windows(data, main_time, hours_before_list=[1, 2, 3, 4, 5, 6, 8, 12, 24]):
    """分析不同时间窗口"""
    results = []
    
    for hours in hours_before_list:
        window_data = [eq for eq in data if main_time - timedelta(hours=hours) <= eq['time'] < main_time]
        
        if len(window_data) < 3:
            continue
        
        depths = [eq['depth'] for eq in window_data if eq.get('depth')]
        mags = [eq['mag'] for eq in window_data if eq.get('mag')]
        
        tse_depth = 999
        tse_mag = 999
        
        if len(depths) >= 3:
            bin_depth = data_to_binary(depths)
            tse_depth = calculate_tse(bin_depth)
        
        if len(mags) >= 3:
            bin_mag = data_to_binary(mags)
            tse_mag = calculate_tse(bin_mag)
        
        results.append({
            'hours_before': hours,
            'tse_depth': tse_depth,
            'tse_mag': tse_mag,
            'count': len(window_data),
        })
    
    return results

def analyze_baseline_vs_precursor(data, main_time, precursor_hours=6, baseline_days=7):
    """比较基线期 vs 前兆期"""
    precursor_start = main_time - timedelta(hours=precursor_hours)
    precursor_data = [eq for eq in data if precursor_start <= eq['time'] < main_time]
    
    baseline_start = main_time - timedelta(days=baseline_days)
    baseline_end = main_time - timedelta(hours=precursor_hours * 2)
    baseline_data = [eq for eq in data if baseline_start <= eq['time'] < baseline_end]
    
    if len(precursor_data) < 3 or len(baseline_data) < 5:
        return None
    
    prec_depths = [eq['depth'] for eq in precursor_data if eq.get('depth')]
    prec_mags = [eq['mag'] for eq in precursor_data if eq.get('mag')]
    
    base_depths = [eq['depth'] for eq in baseline_data if eq.get('depth')]
    base_mags = [eq['mag'] for eq in baseline_data if eq.get('mag')]
    
    prec_tse_depth = 999
    prec_tse_mag = 999
    base_tse_depth = 999
    base_tse_mag = 999
    
    if len(prec_depths) >= 3:
        prec_tse_depth = calculate_tse(data_to_binary(prec_depths))
    if len(prec_mags) >= 3:
        prec_tse_mag = calculate_tse(data_to_binary(prec_mags))
    if len(base_depths) >= 5:
        base_tse_depth = calculate_tse(data_to_binary(base_depths))
    if len(base_mags) >= 5:
        base_tse_mag = calculate_tse(data_to_binary(base_mags))
    
    depth_drop = 0
    mag_drop = 0
    
    if base_tse_depth < 100 and prec_tse_depth < 100:
        depth_drop = base_tse_depth - prec_tse_depth
    
    if base_tse_mag < 100 and prec_tse_mag < 100:
        mag_drop = base_tse_mag - prec_tse_mag
    
    return {
        'precursor_depth_tse': prec_tse_depth,
        'precursor_mag_tse': prec_tse_mag,
        'baseline_depth_tse': base_tse_depth,
        'baseline_mag_tse': base_tse_mag,
        'depth_drop': depth_drop,
        'mag_drop': mag_drop,
        'precursor_count': len(precursor_data),
        'baseline_count': len(baseline_data),
    }

def main():
    print("=" * 70)
    print("太仪地震预警系统 - 前兆检测")
    print("=" * 70)

    earthquake_files = [
        ("data2/earthquake/wenchuan_2008.csv", "汶川2008"),
        ("data2/earthquake/japan_311_2011.csv", "日本311"),
        ("data2/earthquake/turkey_2023.csv", "土耳其2023"),
    ]

    all_results = []

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

        time_windows = analyze_time_windows(data, main_time)
        
        print("\n按时间窗口的TSE:")
        for r in time_windows:
            depth_str = f"{r['tse_depth']:.2f}" if r['tse_depth'] < 100 else "N/A"
            mag_str = f"{r['tse_mag']:.2f}" if r['tse_mag'] < 100 else "N/A"
            print(f"  前{r['hours_before']:2d}小时: 深度TSE={depth_str}, 震级TSE={mag_str}, 次数={r['count']}")
        
        baseline_analysis = analyze_baseline_vs_precursor(data, main_time, precursor_hours=6, baseline_days=7)
        
        if baseline_analysis:
            print("\n基线 vs 前兆期对比 (前6小时 vs 7天前):")
            base_depth = f"{baseline_analysis['baseline_depth_tse']:.4f}" if baseline_analysis['baseline_depth_tse'] < 100 else "N/A"
            prec_depth = f"{baseline_analysis['precursor_depth_tse']:.4f}" if baseline_analysis['precursor_depth_tse'] < 100 else "N/A"
            base_mag = f"{baseline_analysis['baseline_mag_tse']:.4f}" if baseline_analysis['baseline_mag_tse'] < 100 else "N/A"
            prec_mag = f"{baseline_analysis['precursor_mag_tse']:.4f}" if baseline_analysis['precursor_mag_tse'] < 100 else "N/A"
            
            print(f"  深度TSE: 基线={base_depth}, 前兆期={prec_depth}, 下降={baseline_analysis['depth_drop']:.4f}")
            print(f"  震级TSE: 基线={base_mag}, 前兆期={prec_mag}, 下降={baseline_analysis['mag_drop']:.4f}")
            
            all_results.append({
                'name': name,
                'main_mag': main_mag,
                'main_time': main_time,
                'baseline_depth_tse': baseline_analysis['baseline_depth_tse'],
                'precursor_depth_tse': baseline_analysis['precursor_depth_tse'],
                'depth_drop': baseline_analysis['depth_drop'],
                'baseline_mag_tse': baseline_analysis['baseline_mag_tse'],
                'precursor_mag_tse': baseline_analysis['precursor_mag_tse'],
                'mag_drop': baseline_analysis['mag_drop'],
            })

    print("\n" + "=" * 70)
    print("统计汇总")
    print("=" * 70)
    
    for r in all_results:
        depth_drop_pct = r['depth_drop'] / max(r['baseline_depth_tse'], 0.1) * 100 if r['baseline_depth_tse'] < 100 else 0
        mag_drop_pct = r['mag_drop'] / max(r['baseline_mag_tse'], 0.1) * 100 if r['baseline_mag_tse'] < 100 else 0
        
        depth_status = "✓" if depth_drop_pct > 10 else "○"
        mag_status = "✓" if mag_drop_pct > 5 else "○"
        
        print(f"\n{r['name']} (M{r['main_mag']}):")
        print(f"  深度TSE下降: {depth_drop_pct:.1f}% {depth_status}")
        print(f"  震级TSE下降: {mag_drop_pct:.1f}% {mag_status}")

    depth_precursors = [r for r in all_results if r['baseline_depth_tse'] < 100 and r['precursor_depth_tse'] < 100 and r['depth_drop'] / max(r['baseline_depth_tse'], 0.1) > 10]
    mag_precursors = [r for r in all_results if r['baseline_mag_tse'] < 100 and r['precursor_mag_tse'] < 100 and r['mag_drop'] / max(r['baseline_mag_tse'], 0.1) > 5]

    print(f"\n检测到深度TSE前兆: {len(depth_precursors)}/{len(all_results)}")
    print(f"检测到震级TSE前兆: {len(mag_precursors)}/{len(all_results)}")

    if len(depth_precursors) >= 2 or len(mag_precursors) >= 2:
        print("\n✓ 检测到显著前兆信号！")
    elif len(depth_precursors) >= 1 or len(mag_precursors) >= 1:
        print("\n⚠ 检测到潜在前兆")
    else:
        print("\n⚠ 未检测到显著前兆")

    output_file = "data2/results/precursor_v2.csv"
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['名称', '震级', '基线深度TSE', '前兆深度TSE', '深度下降%', '基线震级TSE', '前兆震级TSE', '震级下降%'])
        for r in all_results:
            depth_pct = r['depth_drop'] / max(r['baseline_depth_tse'], 0.1) * 100 if r['baseline_depth_tse'] < 100 else 0
            mag_pct = r['mag_drop'] / max(r['baseline_mag_tse'], 0.1) * 100 if r['baseline_mag_tse'] < 100 else 0
            writer.writerow([r['name'], r['main_mag'],
                           format_tse(r['baseline_depth_tse']),
                           format_tse(r['precursor_depth_tse']),
                           f"{depth_pct:.1f}",
                           format_tse(r['baseline_mag_tse']),
                           format_tse(r['precursor_mag_tse']),
                           f"{mag_pct:.1f}"])

    print(f"\n结果已保存到: {output_file}")

def format_tse(val):
    if val < 100:
        return f"{val:.4f}"
    return "N/A"

if __name__ == "__main__":
    main()
