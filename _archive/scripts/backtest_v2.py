#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
太仪地震预警系统 - 回溯验证（实用版）
分析各地区地震数据，检测TSE前兆信号
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

def analyze_earthquake_sequence(data, window_days=10):
    """分析地震序列的TSE变化"""
    if len(data) < 10:
        return None

    data = sorted(data, key=lambda x: x['time'])

    mid_idx = len(data) // 2
    first_half = data[:mid_idx]
    second_half = data[mid_idx:]

    depths1 = [eq['depth'] for eq in first_half if eq.get('depth')]
    depths2 = [eq['depth'] for eq in second_half if eq.get('depth')]
    mags1 = [eq['mag'] for eq in first_half if eq.get('mag')]
    mags2 = [eq['mag'] for eq in second_half if eq.get('mag')]

    if len(depths1) < 3 or len(depths2) < 3:
        return None

    bin_depth1 = data_to_binary(depths1)
    bin_depth2 = data_to_binary(depths2)
    bin_mag1 = data_to_binary(mags1)
    bin_mag2 = data_to_binary(mags2)

    tse_depth1 = calculate_tse(bin_depth1)
    tse_depth2 = calculate_tse(bin_depth2)
    tse_mag1 = calculate_tse(bin_mag1)
    tse_mag2 = calculate_tse(bin_mag2)

    return {
        'first_half_tse_depth': tse_depth1,
        'second_half_tse_depth': tse_depth2,
        'first_half_tse_mag': tse_mag1,
        'second_half_tse_mag': tse_mag2,
        'depth_change': tse_depth1 - tse_depth2,
        'mag_change': tse_mag1 - tse_mag2,
        'count_first': len(first_half),
        'count_second': len(second_half),
    }

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

def main():
    print("=" * 70)
    print("太仪地震预警系统 - 第一阶段：回溯验证")
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

        print(f"\n分析: {name}...")
        data = read_earthquake_file(filepath)
        print(f"  加载 {len(data)} 条记录")

        if len(data) < 20:
            print(f"  数据不足，跳过")
            continue

        data = sorted(data, key=lambda x: x['time'])
        main_time = data[-1]['time']
        main_mag = data[-1]['mag']

        pre_data = [eq for eq in data[:-1] if eq['time'] >= main_time - timedelta(days=30)]
        if len(pre_data) < 20:
            print(f"  前30天数据不足，只用所有数据")
            pre_data = data[:-1]

        analysis = analyze_earthquake_sequence(pre_data)
        if analysis:
            print(f"  前半段深度TSE: {analysis['first_half_tse_depth']:.4f}")
            print(f"  后半段深度TSE: {analysis['second_half_tse_depth']:.4f}")
            print(f"  深度TSE变化: {analysis['depth_change']:.4f} ({analysis['depth_change']/max(analysis['first_half_tse_depth'], 0.1)*100:.1f}%)")

            results.append({
                'name': name,
                'main_time': main_time,
                'main_mag': main_mag,
                'total_events': len(data),
                'pre_events': len(pre_data),
                'first_tse_depth': analysis['first_half_tse_depth'],
                'second_tse_depth': analysis['second_half_tse_depth'],
                'depth_change': analysis['depth_change'],
                'depth_drop_pct': analysis['depth_change'] / max(analysis['first_half_tse_depth'], 0.1) * 100,
            })

    print("\n" + "=" * 70)
    print("统计结果")
    print("=" * 70)

    if not results:
        print("无有效结果")
        return

    drops = [r['depth_drop_pct'] for r in results if r['depth_drop_pct'] > 0]
    print(f"\n分析的地震事件: {len(results)}")
    print(f"检测到TSE下降的事件: {len(drops)}")
    print(f"下降比例: {len(drops)/len(results)*100:.1f}%")

    if drops:
        print(f"平均下降幅度: {np.mean(drops):.1f}%")
        print(f"最大下降幅度: {np.max(drops):.1f}%")

    for r in results:
        status = "✓ 下降" if r['depth_drop_pct'] > 10 else "○ 无显著变化"
        print(f"  {r['name']}: M{r['main_mag']:.1f}, {r['depth_drop_pct']:.1f}% {status}")

    print("\n" + "=" * 70)
    print("结论")
    print("=" * 70)

    if len(drops) >= 2 and np.mean(drops) > 20:
        print("✓ 检测到显著的前兆信号！")
        print("  - 多个地震事件显示震前TSE下降")
    elif len(drops) >= 1 and np.mean(drops) > 10:
        print("⚠ 检测到一定前兆信号")
    else:
        print("⚠ 需要更多数据验证")

    output_file = "data2/results/precursor_stats.csv"
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['名称', '主震时间', '主震震级', '前半段TSE', '后半段TSE', '变化%'])
        for r in results:
            writer.writerow([r['name'], r['main_time'], r['main_mag'],
                           r['first_tse_depth'], r['second_tse_depth'], f"{r['depth_drop_pct']:.1f}"])

    print(f"\n结果已保存到: {output_file}")
    print("\n回溯验证完成！")

if __name__ == "__main__":
    main()
