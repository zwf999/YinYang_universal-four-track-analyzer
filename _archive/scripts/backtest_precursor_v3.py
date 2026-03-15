#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
太仪地震预警系统 - 前兆检测 v3
检测震前各时间窗口的最低TSE值
"""

import os
import csv
import numpy as np
from datetime import datetime, timedelta

def calculate_entropy(binary_string):
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
    if not binary_string:
        return 999
    entropy = calculate_entropy(binary_string)
    tse = 6.0 * entropy / 4.0
    return tse

def read_earthquake_file(filepath):
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
                    data.append({'time': time, 'mag': mag, 'depth': depth})
                except:
                    continue
    except Exception as e:
        print(f"  读取失败: {e}")
    return data

def analyze_windows(data, main_time, max_hours=24):
    results = []
    for hours in range(1, max_hours + 1):
        window_data = [eq for eq in data if main_time - timedelta(hours=hours) <= eq['time'] < main_time]
        if len(window_data) < 3:
            continue
        depths = [eq['depth'] for eq in window_data if eq.get('depth')]
        mags = [eq['mag'] for eq in window_data if eq.get('mag')]
        tse_depth = 999
        tse_mag = 999
        if len(depths) >= 3:
            tse_depth = calculate_tse(data_to_binary(depths))
        if len(mags) >= 3:
            tse_mag = calculate_tse(data_to_binary(mags))
        results.append({'hours': hours, 'tse_depth': tse_depth, 'tse_mag': tse_mag, 'count': len(window_data)})
    return results

def main():
    print("=" * 70)
    print("太仪地震预警系统 - 前兆检测 v3")
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

        windows = analyze_windows(data, main_time, max_hours=24)
        
        if not windows:
            continue

        print("\n各时间窗口TSE:")
        for w in windows:
            d_str = f"{w['tse_depth']:.2f}" if w['tse_depth'] < 100 else "N/A"
            m_str = f"{w['tse_mag']:.2f}" if w['tse_mag'] < 100 else "N/A"
            print(f"  前{w['hours']:2d}h: 深度TSE={d_str}, 震级TSE={m_str}, 次数={w['count']}")

        valid_depth = [w for w in windows if w['tse_depth'] < 100]
        valid_mag = [w for w in windows if w['tse_mag'] < 100]
        
        if valid_depth:
            min_depth = min(valid_depth, key=lambda x: x['tse_depth'])
            normal_tse = 1.5
            depth_drop = (normal_tse - min_depth['tse_depth']) / normal_tse * 100
            print(f"\n最低深度TSE: {min_depth['tse_depth']:.4f} (前{min_depth['hours']}小时, 下降{depth_drop:.1f}%)")
        else:
            min_depth = None
            depth_drop = 0

        if valid_mag:
            min_mag = min(valid_mag, key=lambda x: x['tse_mag'])
            mag_drop = (1.5 - min_mag['tse_mag']) / 1.5 * 100
            print(f"最低震级TSE: {min_mag['tse_mag']:.4f} (前{min_mag['hours']}小时, 下降{mag_drop:.1f}%)")
        else:
            min_mag = None
            mag_drop = 0

        is_depth_precursor = min_depth and depth_drop > 20
        is_mag_precursor = min_mag and mag_drop > 10

        all_results.append({
            'name': name,
            'main_mag': main_mag,
            'min_depth_tse': min_depth['tse_depth'] if min_depth else 999,
            'min_depth_hours': min_depth['hours'] if min_depth else 0,
            'depth_drop': depth_drop,
            'min_mag_tse': min_mag['tse_mag'] if min_mag else 999,
            'min_mag_hours': min_mag['hours'] if min_mag else 0,
            'mag_drop': mag_drop,
            'is_depth_precursor': is_depth_precursor,
            'is_mag_precursor': is_mag_precursor,
        })

    print("\n" + "=" * 70)
    print("统计汇总")
    print("=" * 70)
    
    for r in all_results:
        d_status = "✓" if r['is_depth_precursor'] else "○"
        m_status = "✓" if r['is_mag_precursor'] else "○"
        print(f"\n{r['name']} (M{r['main_mag']}):")
        print(f"  深度TSE: 最低={r['min_depth_tse']:.2f}, 下降={r['depth_drop']:.1f}% {d_status}")
        print(f"  震级TSE: 最低={r['min_mag_tse']:.2f}, 下降={r['mag_drop']:.1f}% {m_status}")

    depth_precursors = [r for r in all_results if r['is_depth_precursor']]
    mag_precursors = [r for r in all_results if r['is_mag_precursor']]
    
    print(f"\n检测到深度TSE前兆: {len(depth_precursors)}/{len(all_results)}")
    print(f"检测到震级TSE前兆: {len(mag_precursors)}/{len(all_results)}")

    if len(depth_precursors) >= 2 or len(mag_precursors) >= 2:
        print("\n✓ 检测到显著前兆信号！")
    elif len(depth_precursors) >= 1 or len(mag_precursors) >= 1:
        print("\n⚠ 检测到潜在前兆")
    else:
        print("\n⚠ 未检测到显著前兆")

    output_file = "data2/results/precursor_v3.csv"
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['名称', '震级', '最低深度TSE', '前X小时', '深度下降%', '最低震级TSE', '前Y小时', '震级下降%'])
        for r in all_results:
            writer.writerow([r['name'], r['main_mag'],
                           f"{r['min_depth_tse']:.4f}", r['min_depth_hours'], f"{r['depth_drop']:.1f}",
                           f"{r['min_mag_tse']:.4f}", r['min_mag_hours'], f"{r['mag_drop']:.1f}"])
    print(f"\n结果已保存到: {output_file}")

if __name__ == "__main__":
    main()
