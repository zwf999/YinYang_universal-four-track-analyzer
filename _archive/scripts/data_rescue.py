#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据救援行动 - 重新获取完整的前震-主震序列
"""

import urllib.request
import csv
import os
from datetime import datetime, timedelta

class DataRescue:
    def __init__(self):
        self.base_url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    
    def download_earthquake_data(self, start_time, end_time, min_mag=1.0, max_mag=None, 
                               latitude=None, longitude=None, radius=None, 
                               output_file="earthquake_data.csv"):
        """从USGS下载指定区域和时间的地震数据"""
        
        # 构建URL
        params = {
            "format": "csv",
            "starttime": start_time,
            "endtime": end_time,
            "minmagnitude": min_mag
        }
        
        if max_mag:
            params["maxmagnitude"] = max_mag
        
        if latitude and longitude and radius:
            params["latitude"] = latitude
            params["longitude"] = longitude
            params["maxradiuskm"] = radius
        
        # 构建查询字符串
        query = "&" .join([f"{k}={v}" for k, v in params.items()])
        url = f"{self.base_url}?{query}"
        
        print(f"下载数据: {url}")
        print(f"输出文件: {output_file}")
        
        try:
            with urllib.request.urlopen(url, timeout=300) as response:
                content = response.read().decode('utf-8')
            
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            lines = content.strip().split('\n')
            print(f"✓ 数据已保存到: {output_file}")
            print(f"  共 {len(lines)-1} 条地震记录")
            
            return True, len(lines)-1
        except Exception as e:
            print(f"✗ 下载失败: {e}")
            return False, 0
    
    def download_wenchuan_data(self):
        """下载汶川地震完整数据"""
        print("=" * 60)
        print("下载汶川地震完整前震序列")
        print("=" * 60)
        
        # 汶川地震主震：2008-05-12 14:28:01 (UTC+8) → 2008-05-12 06:28:01 UTC
        mainshock_time = "2008-05-12T06:28:01"
        mainshock_lat = 31.0
        mainshock_lon = 103.4
        radius = 100  # 100公里半径
        
        # 下载前震数据（震前10天）
        start_time = "2008-04-12"
        end_time = "2008-05-12T06:28:01"
        output_file = "data2/earthquake/wenchuan_2008_full.csv"
        
        return self.download_earthquake_data(
            start_time=start_time,
            end_time=end_time,
            min_mag=1.0,
            latitude=mainshock_lat,
            longitude=mainshock_lon,
            radius=radius,
            output_file=output_file
        )
    
    def download_japan311_data(self):
        """下载日本311地震完整数据"""
        print("=" * 60)
        print("下载日本311地震完整前震序列")
        print("=" * 60)
        
        # 日本311主震：2011-03-11 05:46:23 UTC
        mainshock_time = "2011-03-11T05:46:23"
        mainshock_lat = 38.322
        mainshock_lon = 142.369
        radius = 200  # 200公里半径
        
        # 下载前震数据（震前30天）
        start_time = "2011-02-11"
        end_time = "2011-03-11T05:46:23"
        output_file = "data2/earthquake/japan_311_2011_full.csv"
        
        return self.download_earthquake_data(
            start_time=start_time,
            end_time=end_time,
            min_mag=1.0,
            latitude=mainshock_lat,
            longitude=mainshock_lon,
            radius=radius,
            output_file=output_file
        )
    
    def download_turkey2023_data(self):
        """下载土耳其2023地震完整数据"""
        print("=" * 60)
        print("下载土耳其2023地震完整前震序列")
        print("=" * 60)
        
        # 土耳其主震：2023-02-06 01:17:34 UTC
        mainshock_time = "2023-02-06T01:17:34"
        mainshock_lat = 37.158
        mainshock_lon = 37.015
        radius = 150  # 150公里半径
        
        # 下载前震数据（震前30天）
        start_time = "2023-01-06"
        end_time = "2023-02-06T01:17:34"
        output_file = "data2/earthquake/turkey_2023_full.csv"
        
        return self.download_earthquake_data(
            start_time=start_time,
            end_time=end_time,
            min_mag=1.0,
            latitude=mainshock_lat,
            longitude=mainshock_lon,
            radius=radius,
            output_file=output_file
        )
    
    def run_data_rescue(self):
        """运行数据救援行动"""
        print("=" * 70)
        print("数据救援行动 - 重新获取完整前震序列")
        print("=" * 70)
        
        results = []
        
        # 下载汶川数据
        success, count = self.download_wenchuan_data()
        results.append(('汶川2008', success, count))
        
        # 下载日本311数据
        success, count = self.download_japan311_data()
        results.append(('日本311', success, count))
        
        # 下载土耳其2023数据
        success, count = self.download_turkey2023_data()
        results.append(('土耳其2023', success, count))
        
        print("\n" + "=" * 70)
        print("数据救援行动结果")
        print("=" * 70)
        
        for name, success, count in results:
            status = "✓ 成功" if success else "✗ 失败"
            print(f"{name}: {status}, 记录数: {count}")
        
        print("\n数据救援行动完成！")

if __name__ == "__main__":
    rescue = DataRescue()
    rescue.run_data_rescue()
