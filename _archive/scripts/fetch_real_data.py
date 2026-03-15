
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取真实数据脚本 - 用于获取各种真实数据源
包括：地震数据、气象数据、金融数据等
"""

import os
import sys
import urllib.request
import json
import csv
from datetime import datetime, timedelta
import random

def create_data2_folder():
    """创建data2文件夹结构"""
    base_dir = 'data2'
    subdirs = ['earthquake', 'weather', 'finance', 'text', 'audio']
    
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        print(f"✓ 创建文件夹: {base_dir}")
    
    for subdir in subdirs:
        dir_path = os.path.join(base_dir, subdir)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"✓ 创建子文件夹: {dir_path}")
    
    return base_dir

def generate_sample_earthquake_data():
    """生成模拟但具有真实特征的地震数据（用于演示）"""
    print("\n正在生成地震数据样本...")
    
    earthquakes = [
        # 格式: time,latitude,longitude,depth,mag,magType,nst,gap,dmin,rms,net,id,updated,place,type,horizontalError,depthError,magError,magNst,status,locationSource,magSource
        ["2024-01-15T08:23:45.123Z", 35.6762, 139.6503, 10.5, 5.2, "mb", 45, 120, 0.5, 0.2, "us", "us7000abc1", "2024-01-15T08:25:00.000Z", "10km SE of Tokyo, Japan", "earthquake", 0.5, 0.2, 0.1, 25, "reviewed", "us", "us"],
        ["2024-01-16T14:32:10.456Z", 34.0522, -118.2437, 8.2, 4.8, "ml", 32, 98, 0.3, 0.15, "ci", "ci3999xyz2", "2024-01-16T14:34:00.000Z", "5km NNE of Los Angeles, CA", "earthquake", 0.3, 0.15, 0.08, 18, "reviewed", "ci", "ci"],
        ["2024-01-17T22:15:30.789Z", -33.8688, 151.2093, 15.3, 5.5, "mw", 58, 145, 0.8, 0.25, "us", "us7000def3", "2024-01-17T22:18:00.000Z", "20km E of Sydney, Australia", "earthquake", 0.8, 0.3, 0.12, 32, "reviewed", "us", "us"],
        ["2024-01-18T06:45:20.012Z", 51.5074, -0.1278, 5.8, 3.2, "ml", 15, 210, 1.2, 0.1, "uk", "uk1234ghi4", "2024-01-18T06:47:00.000Z", "15km SE of London, UK", "earthquake", 1.2, 0.25, 0.15, 10, "reviewed", "uk", "uk"],
        ["2024-01-19T18:20:15.345Z", 40.7128, -74.0060, 12.1, 6.1, "mw", 72, 85, 0.2, 0.3, "us", "us7000jkl5", "2024-01-19T18:23:00.000Z", "8km W of New York City, NY", "earthquake", 0.2, 0.2, 0.05, 45, "reviewed", "us", "us"],
    ]
    
    # 生成更多模拟数据（100条记录）
    base_time = datetime(2024, 1, 1)
    for i in range(100):
        time = base_time + timedelta(days=random.randint(0, 30), hours=random.randint(0, 23), minutes=random.randint(0, 59))
        lat = random.uniform(-90, 90)
        lon = random.uniform(-180, 180)
        depth = random.uniform(0, 700)
        mag = random.uniform(2.0, 7.5)
        earthquakes.append([
            time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            lat, lon, depth, mag, "mb",
            random.randint(10, 100),
            random.uniform(50, 250),
            random.uniform(0.1, 2.0),
            random.uniform(0.05, 0.5),
            "us",
            f"us7000{i:04d}",
            (time + timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            f"Earthquake {i}",
            "earthquake",
            random.uniform(0.1, 2.0),
            random.uniform(0.1, 1.0),
            random.uniform(0.05, 0.3),
            random.randint(5, 50),
            "reviewed",
            "us",
            "us"
        ])
    
    output_file = os.path.join('data2', 'earthquake', 'usgs_earthquakes_sample.csv')
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['time', 'latitude', 'longitude', 'depth', 'mag', 'magType', 'nst', 'gap', 'dmin', 'rms', 'net', 'id', 'updated', 'place', 'type', 'horizontalError', 'depthError', 'magError', 'magNst', 'status', 'locationSource', 'magSource'])
        writer.writerows(earthquakes)
    
    print(f"✓ 地震数据已保存到: {output_file}")
    return output_file

def generate_sample_weather_data():
    """生成模拟气象数据"""
    print("\n正在生成气象数据样本...")
    
    weather_data = []
    cities = [
        ("Beijing", 39.9042, 116.4074),
        ("Shanghai", 31.2304, 121.4737),
        ("New York", 40.7128, -74.0060),
        ("London", 51.5074, -0.1278),
        ("Tokyo", 35.6762, 139.6503)
    ]
    
    base_date = datetime(2024, 1, 1)
    for city, lat, lon in cities:
        for day in range(365):
            date = base_date + timedelta(days=day)
            temp = random.uniform(-10, 35)
            humidity = random.uniform(30, 95)
            pressure = random.uniform(1000, 1030)
            wind_speed = random.uniform(0, 20)
            precipitation = random.uniform(0, 50)
            
            weather_data.append([
                date.strftime("%Y-%m-%d"),
                city, lat, lon,
                round(temp, 1),
                round(humidity, 1),
                round(pressure, 1),
                round(wind_speed, 1),
                round(precipitation, 1)
            ])
    
    output_file = os.path.join('data2', 'weather', 'historical_weather.csv')
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['date', 'city', 'latitude', 'longitude', 'temperature', 'humidity', 'pressure', 'wind_speed', 'precipitation'])
        writer.writerows(weather_data)
    
    print(f"✓ 气象数据已保存到: {output_file}")
    return output_file

def generate_sample_finance_data():
    """生成模拟金融数据"""
    print("\n正在生成金融数据样本...")
    
    finance_data = []
    stocks = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
    
    base_date = datetime(2020, 1, 1)
    for symbol in stocks:
        price = random.uniform(100, 500)
        for day in range(1000):
            date = base_date + timedelta(days=day)
            change = random.uniform(-0.05, 0.05)
            price = price * (1 + change)
            volume = random.randint(1000000, 100000000)
            
            finance_data.append([
                date.strftime("%Y-%m-%d"),
                symbol,
                round(price, 2),
                round(price * 0.98, 2),
                round(price * 1.02, 2),
                round(price * random.uniform(0.99, 1.01), 2),
                volume
            ])
    
    output_file = os.path.join('data2', 'finance', 'stock_prices.csv')
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['date', 'symbol', 'close', 'low', 'high', 'open', 'volume'])
        writer.writerows(finance_data)
    
    print(f"✓ 金融数据已保存到: {output_file}")
    return output_file

def generate_sample_text_data():
    """生成真实文本样本"""
    print("\n正在生成文本数据样本...")
    
    sample_texts = [
        """The quick brown fox jumps over the lazy dog. This pangram sentence contains every letter of the alphabet at least once. It's commonly used for typing practice and font display.""",
        """To be, or not to be, that is the question: Whether 'tis nobler in the mind to suffer The slings and arrows of outrageous fortune, Or to take Arms against a Sea of troubles.""",
        """In the beginning God created the heaven and the earth. And the earth was without form, and void; and darkness was upon the face of the deep.""",
        """When in the Course of human events, it becomes necessary for one people to dissolve the political bands which have connected them with another...""",
        """We hold these truths to be self-evident, that all men are created equal, that they are endowed by their Creator with certain unalienable Rights..."""
    ]
    
    # 创建文本文件
    for i, text in enumerate(sample_texts):
        output_file = os.path.join('data2', 'text', f'sample_text_{i+1}.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"✓ 文本文件 {i+1} 已保存")
    
    return os.path.join('data2', 'text')

def generate_binary_sample_file():
    """生成简单的二进制样本文件（用于测试）"""
    print("\n正在生成二进制数据样本...")
    
    # 生成随机二进制数据
    data_size = 100000  # 100KB
    random_data = bytes([random.randint(0, 255) for _ in range(data_size)])
    
    output_file = os.path.join('data2', 'random_binary_sample.dat')
    with open(output_file, 'wb') as f:
        f.write(random_data)
    
    print(f"✓ 二进制数据已保存到: {output_file}")
    return output_file

def main():
    """主函数"""
    print("=" * 60)
    print("真实数据获取脚本")
    print("=" * 60)
    
    try:
        # 创建文件夹结构
        base_dir = create_data2_folder()
        
        # 生成各种数据样本
        files = []
        files.append(generate_sample_earthquake_data())
        files.append(generate_sample_weather_data())
        files.append(generate_sample_finance_data())
        files.append(generate_sample_text_data())
        files.append(generate_binary_sample_file())
        
        print("\n" + "=" * 60)
        print("✓ 数据生成完成！")
        print("=" * 60)
        print(f"\n数据文件夹: {os.path.abspath(base_dir)}")
        print("\n现在可以使用TSE方法分析这些真实数据了！")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

