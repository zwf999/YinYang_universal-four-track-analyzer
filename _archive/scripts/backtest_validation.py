
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
太仪地震预警系统 - 第一阶段：回溯验证（改进版）
使用M≥4.0地震数据分析主震前的微震活动
"""

import os
import csv
import numpy as np
from datetime import datetime, timedelta
import random

def download_earthquake_data(min_mag=4.0, output_file="data2/earthquake/usgs_m4_full.csv"):
    """下载M≥指定震级的地震数据"""
    import urllib.request
    
    url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv&starttime=2000-01-01&endtime=2024-12-31&minmagnitude={min_mag}"
    
    print(f"下载M≥{min_mag}地震数据...")
    try:
        with urllib.request.urlopen(url, timeout=300) as response:
            content = response.read().decode('utf-8')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        lines = content.strip().split('\n')
        print(f"✓ 下载完成: {len(lines)-1} 条记录")
        return output_file
    except Exception as e:
        print(f"✗ 下载失败: {e}")
        return None

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
                        'lat': float(row['latitude']),
                        'lon': float(row['longitude']),
                        'time': time_naive,
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

def analyze_time_window(window_data, min_samples=5):
    """分析单个时间窗口的TSE"""
    if not window_data or len(window_data) < min_samples:
        return None
    
    mag_values = [d['mag'] for d in window_data]
    depth_values = [d['depth'] for d in window_data]
    
    mag_binary = data_to_binary(mag_values)
    depth_binary = data_to_binary(depth_values)
    
    mag_tse = calculate_tse(mag_binary) if mag_binary else 0
    depth_tse = calculate_tse(depth_binary) if depth_binary else 0
    
    return {
        'count': len(window_data),
        'mag_tse': mag_tse,
        'depth_tse': depth_tse,
    }

def find_main_shocks(data, min_mag=7.0, min_days_between=30):
    """识别主震时间点"""
    main_shocks = []
    sorted_data = sorted(data, key=lambda x: x['time'])
    
    for i, eq in enumerate(sorted_data):
        if eq['mag'] >= min_mag:
            is_separate = True
            for ms in main_shocks:
                if abs((eq['time'] - ms['time']).days) < min_days_between:
                    if eq['mag'] > ms['mag']:
                        ms['time'] = eq['time']
                        ms['mag'] = eq['mag']
                    is_separate = False
                    break
            
            if is_separate:
                main_shocks.append({
                    'time': eq['time'],
                    'mag': eq['mag'],
                    'lat': eq['lat'],
                    'lon': eq['lon'],
                })
    
    return main_shocks

def get_window_data(data, start_time, window_hours=6):
    """获取时间窗口内的地震数据"""
    end_time = start_time + timedelta(hours=window_hours)
    return [d for d in data if start_time <= d['time'] < end_time]

def test_precursor_detection(data, main_shock_time, window_hours=6, hours_before=168, min_samples=5):
    """测试主震前的TSE异常（10天=240小时）"""
    analysis_start = main_shock_time - timedelta(hours=hours_before)
    analysis_end = main_shock_time
    
    all_results = []
    current_time = analysis_start
    
    while current_time < analysis_end:
        window_data = get_window_data(data, current_time, window_hours)
        result = analyze_time_window(window_data, min_samples=min_samples)
        
        if result:
            hours_before = (main_shock_time - current_time).total_seconds() / 3600
            result['hours_before'] = hours_before
            result['time'] = current_time
            all_results.append(result)
        
        current_time += timedelta(hours=1)
    
    return all_results

def test_control_period(data, start_time, window_hours=6, hours_test=168, min_samples=5):
    """测试对照期间的TSE"""
    all_results = []
    current_time = start_time
    end_time = start_time + timedelta(hours=hours_test)
    
    while current_time < end_time:
        window_data = get_window_data(data, current_time, window_hours)
        result = analyze_time_window(window_data, min_samples=min_samples)
        
        if result:
            result['time'] = current_time
            all_results.append(result)
        
        current_time += timedelta(hours=1)
    
    return all_results

def generate_random_control_periods(data, n_periods=30, days_before=10):
    """生成随机对照时间段"""
    sorted_data = sorted(data, key=lambda x: x['time'])
    
    if len(sorted_data) < 2:
        return []
    
    main_shocks = find_main_shocks(data, min_mag=7.0)
    main_shock_times = set()
    for ms in main_shocks:
        for h in range(-30, 30):
            main_shock_times.add(ms['time'] + timedelta(days=h))
    
    time_range_start = sorted_data[0]['time'] + timedelta(days=60)
    time_range_end = sorted_data[-1]['time'] - timedelta(days=30)
    
    if time_range_end < time_range_start:
        return []
    
    control_periods = []
    attempts = 0
    max_attempts = n_periods * 10
    
    while len(control_periods) < n_periods and attempts < max_attempts:
        attempts += 1
        days_offset = random.randint(0, int((time_range_end - time_range_start).days))
        start_time = time_range_start + timedelta(days=days_offset)
        
        if start_time in main_shock_times:
            continue
        
        has_large_eq = False
        for eq in sorted_data:
            if start_time <= eq['time'] < start_time + timedelta(days=days_before + 1):
                if eq['mag'] >= 7.0:
                    has_large_eq = True
                    break
        
        if not has_large_eq:
            control_periods.append(start_time)
    
    return control_periods

def main():
    """主函数"""
    print("=" * 70)
    print("太仪地震预警系统 - 第一阶段：回溯验证")
    print("=" * 70)
    
    os.makedirs('data2/earthquake', exist_ok=True)
    os.makedirs('data2/results', exist_ok=True)
    
    print("\n[1/6] 加载地震数据...")
    data_file = "data2/earthquake/usgs_m7_full.csv"
    
    if not os.path.exists(data_file):
        print(f"✗ 文件不存在: {data_file}")
        return
    
    data = read_earthquake_data(data_file)
    print(f"✓ 加载 {len(data)} 条M≥7.0地震记录")
    
    print("\n[2/6] 识别M≥7.0主震...")
    main_shocks = find_main_shocks(data, min_mag=7.0, min_days_between=30)
    print(f"✓ 找到 {len(main_shocks)} 次独立M≥7.0主震")
    
    if not main_shocks:
        print("✗ 未找到主震")
        return
    
    print("\n[3/6] 筛选有足够微震的主震...")
    valid_main_shocks = []
    for ms in main_shocks:
        pre_data = [eq for eq in data 
                   if ms['time'] - timedelta(days=10) <= eq['time'] < ms['time']]
        if len(pre_data) >= 20:
            valid_main_shocks.append(ms)
    
    print(f"✓ {len(valid_main_shocks)} 次主震有足够的前震数据")
    valid_main_shocks = valid_main_shocks[:30]
    print(f"  选取前 {len(valid_main_shocks)} 次进行分析")
    
    print("\n[4/6] 测试主震前TSE...")
    precursor_results = []
    for i, ms in enumerate(valid_main_shocks):
        results = test_precursor_detection(data, ms['time'], window_hours=6, hours_before=240, min_samples=5)
        
        if results:
            min_depth = min(r['depth_tse'] for r in results)
            min_mag = min(r['mag_tse'] for r in results)
            avg_depth = np.mean([r['depth_tse'] for r in results if r['depth_tse'] > 0])
            avg_mag = np.mean([r['mag_tse'] for r in results if r['mag_tse'] > 0])
            
            precursor_results.append({
                'time': ms['time'],
                'mag': ms['mag'],
                'min_depth_tse': min_depth,
                'min_mag_tse': min_mag,
                'avg_depth_tse': avg_depth,
                'avg_mag_tse': avg_mag,
                'window_count': len(results),
            })
        
        if (i + 1) % 10 == 0:
            print(f"  已测试 {i+1}/{len(valid_main_shocks)} 次主震")
    
    print(f"  有效主震样本: {len(precursor_results)}")
    
    print("\n[5/6] 生成并测试对照期间...")
    random.seed(42)
    control_periods = generate_random_control_periods(data, n_periods=30, days_before=10)
    print(f"✓ 生成 {len(control_periods)} 个对照期间")
    
    control_results = []
    for i, start in enumerate(control_periods):
        results = test_control_period(data, start, window_hours=6, hours_test=240, min_samples=5)
        
        if results:
            min_depth = min(r['depth_tse'] for r in results)
            min_mag = min(r['mag_tse'] for r in results)
            avg_depth = np.mean([r['depth_tse'] for r in results if r['depth_tse'] > 0])
            avg_mag = np.mean([r['mag_tse'] for r in results if r['mag_tse'] > 0])
            
            control_results.append({
                'start_time': start,
                'min_depth_tse': min_depth,
                'min_mag_tse': min_mag,
                'avg_depth_tse': avg_depth,
                'avg_mag_tse': avg_mag,
                'window_count': len(results),
            })
        
        if (i + 1) % 10 == 0:
            print(f"  已测试 {i+1}/{len(control_periods)} 个对照期间")
    
    print(f"  有效对照样本: {len(control_results)}")
    
    print("\n[6/6] 分析结果...")
    
    print("\n" + "=" * 70)
    print("统计结果")
    print("=" * 70)
    
    if precursor_results and control_results:
        print("\n主震前 (n={}):".format(len(precursor_results)))
        depths = [r['min_depth_tse'] for r in precursor_results]
        mags = [r['min_mag_tse'] for r in precursor_results]
        print(f"  深度TSE最小值: 最小={min(depths):.4f}, 中位数={np.median(depths):.4f}")
        print(f"  震级TSE最小值: 最小={min(mags):.4f}, 中位数={np.median(mags):.4f}")
        
        print("\n无震期间 (n={}):".format(len(control_results)))
        c_depths = [r['min_depth_tse'] for r in control_results]
        c_mags = [r['min_mag_tse'] for r in control_results]
        print(f"  深度TSE最小值: 最小={min(c_depths):.4f}, 中位数={np.median(c_depths):.4f}")
        print(f"  震级TSE最小值: 最小={min(c_mags):.4f}, 中位数={np.median(c_mags):.4f}")
        
        depth_threshold = 0.5
        prec_detected = sum(1 for r in precursor_results if r['min_depth_tse'] < depth_threshold)
        ctrl_detected = sum(1 for r in control_results if r['min_depth_tse'] < depth_threshold)
        
        print(f"\n使用深度TSE < {depth_threshold} 作为阈值:")
        print(f"  检测率: {prec_detected}/{len(precursor_results)} = {prec_detected/len(precursor_results):.1%}")
        print(f"  误报率: {ctrl_detected}/{len(control_results)} = {ctrl_detected/len(control_results):.1%}")
        
        print("\n" + "=" * 70)
        print("结论")
        print("=" * 70)
        
        if prec_detected/len(precursor_results) > 0.3 and ctrl_detected/len(control_results) < 0.2:
            print("✓ 检测到显著的前兆信号！")
        elif prec_detected/len(precursor_results) > 0.5:
            print("⚠ 检测到一定前兆信号，但需要更多分析")
        else:
            print("⚠ 未能检测到显著的前兆信号")
    
    output_file = "data2/results/backtest_detailed.csv"
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Type', 'Time', 'Mag', 'Min_Depth_TSE', 'Min_Mag_TSE', 'Avg_Depth_TSE', 'Avg_Mag_TSE', 'Window_Count'])
        
        for r in precursor_results:
            writer.writerow(['Precursor', r['time'], r['mag'], r['min_depth_tse'], r['min_mag_tse'], 
                          r['avg_depth_tse'], r['avg_mag_tse'], r['window_count']])
        
        for r in control_results:
            writer.writerow(['Control', r['start_time'], '', r['min_depth_tse'], r['min_mag_tse'],
                          r['avg_depth_tse'], r['avg_mag_tse'], r['window_count']])
    
    print(f"\n✓ 结果已保存到: {output_file}")
    print("\n回溯验证完成！")

if __name__ == "__main__":
    main()
