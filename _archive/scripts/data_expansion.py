#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据扩展行动 - 获取更多地震数据
保持核心算法不变，仅扩展数据来源
"""

import urllib.request
import csv
import os
from datetime import datetime, timedelta

class DataExpansion:
    def __init__(self):
        self.base_url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    
    def download_earthquake_data(self, start_time, end_time, min_mag=1.0, 
                               latitude=None, longitude=None, radius=None, 
                               output_file="earthquake_data.csv"):
        """从USGS下载地震数据"""
        
        params = {
            "format": "csv",
            "starttime": start_time,
            "endtime": end_time,
            "minmagnitude": min_mag
        }
        
        if latitude and longitude and radius:
            params["latitude"] = latitude
            params["longitude"] = longitude
            params["maxradiuskm"] = radius
        
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        url = f"{self.base_url}?{query}"
        
        print(f"下载: {url}")
        
        try:
            with urllib.request.urlopen(url, timeout=300) as response:
                content = response.read().decode('utf-8')
            
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            lines = content.strip().split('\n')
            count = len(lines) - 1
            print(f"✓ 保存到: {output_file}")
            print(f"  记录数: {count}")
            
            return True, count
        except Exception as e:
            print(f"✗ 失败: {e}")
            return False, 0
    
    def download_major_earthquakes(self):
        """下载多次重大地震的完整数据"""
        print("=" * 70)
        print("数据扩展行动 - 下载重大地震完整序列")
        print("=" * 70)
        
        # 定义重大地震列表
        earthquakes = [
            {
                'name': '智利2010',
                'time': '2010-02-27T06:34:11',
                'lat': -35.846,
                'lon': -72.719,
                'radius': 200,
                'start': '2010-01-27',
                'end': '2010-02-27T06:34:11',
                'output': 'data2/earthquake/chile_2010_full.csv'
            },
            {
                'name': '苏门答腊2004',
                'time': '2004-12-26T00:58:53',
                'lat': 3.295,
                'lon': 95.982,
                'radius': 300,
                'start': '2004-11-26',
                'end': '2004-12-26T00:58:53',
                'output': 'data2/earthquake/sumatra_2004_full.csv'
            },
            {
                'name': '尼泊尔2015',
                'time': '2015-04-25T06:11:26',
                'lat': 28.147,
                'lon': 84.708,
                'radius': 200,
                'start': '2015-03-25',
                'end': '2015-04-25T06:11:26',
                'output': 'data2/earthquake/nepal_2015_full.csv'
            },
            {
                'name': '墨西哥2017',
                'time': '2017-09-08T04:49:21',
                'lat': 15.022,
                'lon': -93.899,
                'radius': 200,
                'start': '2017-08-08',
                'end': '2017-09-08T04:49:21',
                'output': 'data2/earthquake/mexico_2017_full.csv'
            },
            {
                'name': '新西兰2016',
                'time': '2016-11-13T11:02:56',
                'lat': -42.693,
                'lon': 173.022,
                'radius': 200,
                'start': '2016-10-13',
                'end': '2016-11-13T11:02:56',
                'output': 'data2/earthquake/newzealand_2016_full.csv'
            }
        ]
        
        results = []
        
        for eq in earthquakes:
            print(f"\n下载 {eq['name']} 地震数据...")
            success, count = self.download_earthquake_data(
                start_time=eq['start'],
                end_time=eq['end'],
                min_mag=1.0,
                latitude=eq['lat'],
                longitude=eq['lon'],
                radius=eq['radius'],
                output_file=eq['output']
            )
            results.append((eq['name'], success, count))
        
        return results
    
    def run_expansion(self):
        """运行数据扩展行动"""
        results = self.download_major_earthquakes()
        
        print("\n" + "=" * 70)
        print("数据扩展行动结果")
        print("=" * 70)
        
        total = 0
        success_count = 0
        
        for name, success, count in results:
            status = "✓" if success else "✗"
            print(f"{status} {name}: {count} 条记录")
            if success:
                total += count
                success_count += 1
        
        print(f"\n总计: {success_count}/{len(results)} 个地震，{total} 条记录")
        print("\n数据扩展行动完成！")
        
        return results

if __name__ == "__main__":
    expansion = DataExpansion()
    expansion.run_expansion()
