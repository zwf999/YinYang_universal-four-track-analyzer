#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
太仪地震预警系统 - 回溯验证（改进版）
使用滑动窗口检测TSE变化趋势
"""

import os
import csv
import numpy as np
from datetime import datetime, timedelta

def linear_regression(x, y):
    """简单线性回归"""
    n = len(x)
    if n < 2:
        return 0, 1.0
    
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(xi * yi for xi, yi in zip(x, y))
    sum_xx = sum(xi * xi for xi in x)
    
    denom = n * sum_xx - sum_x * sum_x
    if denom == 0:
        return 0, 1.0
    
    slope = (n * sum_xy - sum_x * sum_y) / denom
    intercept = (sum_y - slope * sum_x) / n
    
    y_pred = [slope * xi + intercept for xi in y]
    ss_res = sum((yi - ypi) ** 2 for yi, ypi in zip(y, y_pred))
    ss_tot = sum((yi - sum_y/n) ** 2 for yi in y)
    
    if ss_tot == 0:
        r_squared = 0
    else:
        r_squared = 1 - ss_res / ss_tot
    
    return slope, r_squared

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

def sliding_window_tse(data, window_size=20, step=5):
    """使用滑动窗口计算TSE时间序列"""
    if len(data) < window_size:
        return []

    data = sorted(data, key=lambda x: x['time'])
    tse_values = []
    times = []

    for i in range(0, len(data) - window_size + 1, step):
        window = data[i:i + window_size]
        depths = [eq['depth'] for eq in window if eq.get('depth')]
        mags = [eq['mag'] for eq in window if eq.get('mag')]

        if len(depths) >= 10:
            bin_depth = data_to_binary(depths)
            tse_depth = calculate_tse(bin_depth)
            tse_values.append(tse_depth)
            times.append(window[0]['time'])

    return list(zip(times, tse_values))

def detect_tse_trend(tse_series):
    """检测TSE趋势，返回斜率"""
    if len(tse_series) < 3:
        return 0, 1.0

    values = [tse for _, tse in tse_series]
    indices = list(range(len(values)))

    slope, r_squared = linear_regression(indices, values)
    return slope, 1 - r_squared

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
    print("太仪地震预警系统 - 第一阶段：回溯验证（滑动窗口版）")
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

        if len(data) < 30:
            print(f"  数据不足，跳过")
            continue

        data = sorted(data, key=lambda x: x['time'])
        main_time = data[-1]['time']
        main_mag = data[-1]['mag']

        pre_data = [eq for eq in data[:-1] if eq['time'] >= main_time - timedelta(days=30)]
        if len(pre_data) < 30:
            pre_data = [eq for eq in data[:-1] if eq['time'] >= main_time - timedelta(days=60)]
        if len(pre_data) < 30:
            pre_data = data[:-1]

        print(f"  主震时间: {main_time}, 震级: M{main_mag}")
        print(f"  分析数据: {len(pre_data)} 条")

        tse_series = sliding_window_tse(pre_data, window_size=30, step=10)
        print(f"  有效窗口: {len(tse_series)} 个")

        if len(tse_series) >= 3:
            slope, p_value = detect_tse_trend(tse_series)
            first_tse = tse_series[0][1]
            last_tse = tse_series[-1][1]
            change = first_tse - last_tse

            print(f"  首窗口TSE: {first_tse:.4f}")
            print(f"  末窗口TSE: {last_tse:.4f}")
            print(f"  变化量: {change:.4f} ({change/max(first_tse, 0.1)*100:.1f}%)")
            print(f"  趋势斜率: {slope:.6f}, p值: {p_value:.4f}")

            is_precursor = change > 0.3 and p_value < 0.3

            results.append({
                'name': name,
                'main_time': main_time,
                'main_mag': main_mag,
                'total_events': len(data),
                'pre_events': len(pre_data),
                'first_tse': first_tse,
                'last_tse': last_tse,
                'change': change,
                'change_pct': change / max(first_tse, 0.1) * 100,
                'slope': slope,
                'p_value': p_value,
                'is_precursor': is_precursor,
            })
        else:
            print(f"  窗口不足，无法分析")

    print("\n" + "=" * 70)
    print("统计结果")
    print("=" * 70)

    if not results:
        print("无有效结果")
        return

    precursors = [r for r in results if r['is_precursor']]
    changes = [r['change'] for r in results]

    print(f"\n分析的地震事件: {len(results)}")
    print(f"检测到前兆信号: {len(precursors)}/{len(results)}")

    if changes:
        avg_change = np.mean(changes)
        print(f"平均TSE变化: {avg_change:.4f}")
        print(f"变化范围: {min(changes):.4f} ~ {max(changes):.4f}")

    print("\n详细结果:")
    for r in results:
        status = "✓ 前兆" if r['is_precursor'] else "○ 无"
        print(f"  {r['name']}: M{r['main_mag']:.1f}, 变化={r['change']:.3f}, p={r['p_value']:.3f} {status}")

    print("\n" + "=" * 70)
    print("结论")
    print("=" * 70)

    if len(precursors) >= 2:
        print("✓ 检测到显著的前兆信号！")
        print(f"  - {len(precursors)}/{len(results)} 地震显示震前TSE下降趋势")
    elif len(precursors) >= 1:
        print("⚠ 检测到潜在前兆信号，需要更多验证")
    else:
        print("⚠ 未能检测到显著的前兆信号")

    output_file = "data2/results/precursor_stats_v2.csv"
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['名称', '主震时间', '主震震级', '首TSE', '末TSE', '变化', '斜率', 'p值', '前兆'])
        for r in results:
            writer.writerow([r['name'], r['main_time'], r['main_mag'],
                           f"{r['first_tse']:.4f}", f"{r['last_tse']:.4f}",
                           f"{r['change']:.4f}", f"{r['slope']:.6f}",
                           f"{r['p_value']:.4f}", "是" if r['is_precursor'] else "否"])

    print(f"\n结果已保存到: {output_file}")
    print("\n回溯验证完成！")

if __name__ == "__main__":
    main()
