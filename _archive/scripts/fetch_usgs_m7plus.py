
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量下载USGS M≥7.0地震目录
用于太仪地震预警系统验证
"""

import urllib.request
import csv
import os
from datetime import datetime

def download_usgs_earthquakes(start_time, end_time, min_mag=7.0, output_file="usgs_m7_plus.csv"):
    """从USGS下载指定震级范围的地震数据"""
    
    url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv&starttime={start_time}&endtime={end_time}&minmagnitude={min_mag}"
    
    print(f"下载数据: {url}")
    print(f"输出文件: {output_file}")
    
    try:
        with urllib.request.urlopen(url, timeout=120) as response:
            content = response.read().decode('utf-8')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        lines = content.strip().split('\n')
        print(f"✓ 数据已保存到: {output_file}")
        print(f"  共 {len(lines)-1} 条M≥{min_mag}地震记录")
        
        return True, len(lines)-1
    except Exception as e:
        print(f"✗ 下载失败: {e}")
        return False, 0

def main():
    """主函数"""
    print("=" * 60)
    print("批量下载USGS M≥7.0地震目录")
    print("=" * 60)
    
    os.makedirs('data2/earthquake', exist_ok=True)
    
    download_periods = [
        ('2000-01-01', '2010-12-31', 'data2/earthquake/usgs_m7_2000_2010.csv'),
        ('2011-01-01', '2020-12-31', 'data2/earthquake/usgs_m7_2011_2020.csv'),
        ('2000-01-01', '2020-12-31', 'data2/earthquake/usgs_m7_2000_2020.csv'),
    ]
    
    total_count = 0
    for start, end, output in download_periods:
        print(f"\n下载 {start} 至 {end} 的M≥7.0地震...")
        success, count = download_usgs_earthquakes(start, end, 7.0, output)
        if success:
            total_count += count
    
    print(f"\n{'='*60}")
    print(f"下载完成！总计 {total_count} 条M≥7.0地震记录")
    print(f"{'='*60}")
    
    print("\n生成测试地震清单...")
    
    earthquake_list = []
    
    with open('data2/earthquake/usgs_m7_2000_2020.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                time = datetime.fromisoformat(row['time'].replace('Z', '+00:00'))
                mag = float(row['mag'])
                lat = float(row['latitude'])
                lon = float(row['longitude'])
                depth = float(row['depth'])
                
                earthquake_list.append({
                    'time': time.strftime('%Y-%m-%d %H:%M'),
                    'mag': mag,
                    'lat': lat,
                    'lon': lon,
                    'depth': depth,
                    'place': row.get('place', 'Unknown')
                })
            except:
                continue
    
    earthquake_list.sort(key=lambda x: x['time'], reverse=True)
    
    with open('data2/earthquake/m7_earthquake_list.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['time', 'mag', 'lat', 'lon', 'depth', 'place'])
        writer.writeheader()
        writer.writerows(earthquake_list)
    
    print(f"✓ 测试地震清单已保存到: data2/earthquake/m7_earthquake_list.csv")
    print(f"  共 {len(earthquake_list)} 次M≥7.0地震")
    
    print("\n前20次最强的M≥7.0地震：")
    top20 = sorted(earthquake_list, key=lambda x: x['mag'], reverse=True)[:20]
    for i, eq in enumerate(top20, 1):
        print(f"  {i}. {eq['time']} M{eq['mag']:.1f} - {eq['place']}")

if __name__ == "__main__":
    main()
