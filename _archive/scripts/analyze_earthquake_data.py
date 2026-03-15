
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
地震数据TSE分析脚本
将地震数据转换为二进制序列并进行TSE分析
"""

import os
import csv
import numpy as np
from datetime import datetime

def read_earthquake_data(file_path):
    """读取地震数据"""
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['type'] == 'earthquake':
                    # 提取关键信息
                    mag = float(row['mag'])
                    depth = float(row['depth'])
                    lat = float(row['latitude'])
                    lon = float(row['longitude'])
                    time_str = row['time']
                    
                    # 解析时间
                    try:
                        time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                        timestamp = time.timestamp()
                    except:
                        continue
                    
                    data.append({
                        'mag': mag,
                        'depth': depth,
                        'lat': lat,
                        'lon': lon,
                        'time': time,
                        'timestamp': timestamp
                    })
        print(f"✓ 读取文件: {file_path}")
        print(f"  共 {len(data)} 条地震记录")
        return data
    except Exception as e:
        print(f"✗ 读取文件失败: {e}")
        return []

def data_to_binary(data, feature='mag'):
    """将地震数据转换为二进制序列"""
    if not data:
        return ""
    
    # 提取特征值
    values = [d[feature] for d in data]
    
    # 标准化到0-1范围
    min_val = min(values)
    max_val = max(values)
    if max_val == min_val:
        return ""
    
    normalized = [(v - min_val) / (max_val - min_val) for v in values]
    
    # 转换为二进制
    binary = []
    for val in normalized:
        # 8位精度
        byte = int(val * 255)
        # 转换为8位二进制
        binary_str = bin(byte)[2:].zfill(8)
        binary.append(binary_str)
    
    return ''.join(binary)

def calculate_entropy(binary_string):
    """计算香农熵"""
    if not binary_string:
        return 0.0
    
    # 计算频率
    total = len(binary_string)
    counts = {}
    for bit in binary_string:
        counts[bit] = counts.get(bit, 0) + 1
    
    # 计算熵
    entropy = 0.0
    for count in counts.values():
        p = count / total
        entropy -= p * np.log2(p)
    
    return entropy

def calculate_tse(binary_string):
    """计算TSE"""
    entropy = calculate_entropy(binary_string)
    # 确保熵不超过4.0（16层的最大熵）
    entropy = min(entropy, 4.0)
    # TSE = 6.0 * H / 4.0
    tse = 6.0 * entropy / 4.0
    return tse

def analyze_earthquake_files():
    """分析地震数据文件"""
    earthquake_dir = os.path.join('data2', 'earthquake')
    files = [f for f in os.listdir(earthquake_dir) if f.endswith('.csv')]
    
    results = []
    
    for file_name in files:
        file_path = os.path.join(earthquake_dir, file_name)
        data = read_earthquake_data(file_path)
        
        if data:
            # 按特征分析
            features = ['mag', 'depth', 'lat', 'lon']
            file_results = {
                'file': file_name,
                'records': len(data),
                'analysis': {}
            }
            
            for feature in features:
                binary = data_to_binary(data, feature)
                if binary:
                    tse = calculate_tse(binary)
                    entropy = calculate_entropy(binary)
                    
                    file_results['analysis'][feature] = {
                        'tse': round(tse, 4),
                        'entropy': round(entropy, 4),
                        'binary_length': len(binary)
                    }
            
            results.append(file_results)
    
    return results

def main():
    """主函数"""
    print("=" * 60)
    print("地震数据TSE分析")
    print("=" * 60)
    
    results = analyze_earthquake_files()
    
    if not results:
        print("✗ 没有找到地震数据文件")
        return
    
    print("\n分析结果:")
    print("-" * 60)
    
    for result in results:
        print(f"\n文件: {result['file']}")
        print(f"记录数: {result['records']}")
        print("特征分析:")
        
        for feature, analysis in result['analysis'].items():
            print(f"  {feature:6} - TSE: {analysis['tse']:8.4f}, 熵: {analysis['entropy']:8.4f}, 二进制长度: {analysis['binary_length']:,}")
    
    print("\n" + "=" * 60)
    print("分析完成！")
    print("=" * 60)
    
    # 保存结果
    output_file = os.path.join('data2', 'earthquake_analysis_results.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("地震数据TSE分析结果\n")
        f.write("=" * 60 + "\n")
        for result in results:
            f.write(f"\n文件: {result['file']}\n")
            f.write(f"记录数: {result['records']}\n")
            f.write("特征分析:\n")
            for feature, analysis in result['analysis'].items():
                f.write(f"  {feature:6} - TSE: {analysis['tse']:8.4f}, 熵: {analysis['entropy']:8.4f}, 二进制长度: {analysis['binary_length']:,}\n")
    
    print(f"\n✓ 结果已保存到: {output_file}")

if __name__ == "__main__":
    main()

