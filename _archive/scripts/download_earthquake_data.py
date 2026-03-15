
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从USGS下载历史地震数据
用于太仪地震预警研究
"""

import urllib.request
import csv
import os
from datetime import datetime

def download_usgs_earthquakes(start_time, end_time, min_lat, max_lat, min_lon, max_lon, min_mag, output_file):
    """从USGS下载地震数据"""
    
    url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv&starttime={start_time}&endtime={end_time}&minlatitude={min_lat}&maxlatitude={max_lat}&minlongitude={min_lon}&maxlongitude={max_lon}&minmagnitude={min_mag}"
    
    print(f"下载数据: {url}")
    
    try:
        with urllib.request.urlopen(url, timeout=60) as response:
            content = response.read().decode('utf-8')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ 数据已保存到: {output_file}")
        
        lines = content.strip().split('\n')
        print(f"  共 {len(lines)-1} 条地震记录")
        
        return True
    except Exception as e:
        print(f"✗ 下载失败: {e}")
        return False

def convert_to_standard_format(input_file, output_file):
    """将USGS数据转换为标准格式"""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            with open(output_file, 'w', encoding='utf-8', newline='') as out:
                writer = csv.writer(out)
                writer.writerow(['type', 'time', 'latitude', 'longitude', 'depth', 'mag'])
                
                for row in reader:
                    writer.writerow([
                        'earthquake',
                        row['time'],
                        row['latitude'],
                        row['longitude'],
                        row['depth'],
                        row['mag']
                    ])
        
        print(f"✓ 格式转换完成: {output_file}")
        return True
    except Exception as e:
        print(f"✗ 格式转换失败: {e}")
        return False

def main():
    """主函数 - 下载历史特大地震数据"""
    
    os.makedirs('data2/earthquake', exist_ok=True)
    
    print("=" * 60)
    print("开始下载历史特大地震数据")
    print("=" * 60)
    
    earthquakes = [
        {
            'name': '日本311地震',
            'start_time': '2011-02-10',
            'end_time': '2011-03-12',
            'min_lat': 30, 'max_lat': 46,
            'min_lon': 125, 'max_lon': 150,
            'min_mag': 4,
            'output': 'data2/earthquake/japan_311_2011.csv'
        },
        {
            'name': '汶川地震',
            'start_time': '2008-04-12',
            'end_time': '2008-05-13',
            'min_lat': 25, 'max_lat': 35,
            'min_lon': 95, 'max_lon': 110,
            'min_mag': 4,
            'output': 'data2/earthquake/wenchuan_2008.csv'
        },
        {
            'name': '土耳其双震',
            'start_time': '2023-01-20',
            'end_time': '2023-02-20',
            'min_lat': 35, 'max_lat': 42,
            'min_lon': 25, 'max_lon': 45,
            'min_mag': 4,
            'output': 'data2/earthquake/turkey_2023.csv'
        }
    ]
    
    for eq in earthquakes:
        print(f"\n{'='*60}")
        print(f"下载 {eq['name']} 数据...")
        print(f"{'='*60}")
        
        if download_usgs_earthquakes(
            eq['start_time'], eq['end_time'],
            eq['min_lat'], eq['max_lat'],
            eq['min_lon'], eq['max_lon'],
            eq['min_mag'], eq['output']
        ):
            print(f"✓ {eq['name']} 数据下载完成")
        else:
            print(f"✗ {eq['name']} 数据下载失败")
    
    print(f"\n{'='*60}")
    print("所有数据下载任务完成")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
