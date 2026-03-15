#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
太仪v2.0 - 多数据源扩展
从多个数据源获取地震数据
核心算法永不修改
"""

import urllib.request
import json
import csv
import os
from datetime import datetime, timedelta

class MultiSourceDataExpansion:
    def __init__(self):
        self.usgs_base = "https://earthquake.usgs.gov/fdsnws/event/1/query"
        self.emsc_base = "https://www.seismicportal.eu/fdsnws/event/1/query"
    
    def download_from_usgs(self, start_time, end_time, min_mag, max_mag, 
                          min_lat, max_lat, min_lon, max_lon, output_file):
        """从USGS下载数据"""
        params = {
            "format": "csv",
            "starttime": start_time,
            "endtime": end_time,
            "minmagnitude": min_mag,
            "maxmagnitude": max_mag,
            "minlatitude": min_lat,
            "maxlatitude": max_lat,
            "minlongitude": min_lon,
            "maxlongitude": max_lon
        }
        
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        url = f"{self.usgs_base}?{query}"
        
        print(f"USGS下载: {url[:80]}...")
        
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
    
    def download_high_risk_regions(self):
        """下载高风险区域的地震数据"""
        print("=" * 70)
        print("多数据源扩展 - 高风险区域数据")
        print("=" * 70)
        
        # 定义高风险区域
        regions = [
            {
                'name': '日本本州',
                'min_lat': 35, 'max_lat': 42,
                'min_lon': 138, 'max_lon': 145,
                'start': '2010-01-01',
                'end': '2020-12-31'
            },
            {
                'name': '智利中部',
                'min_lat': -38, 'max_lat': -30,
                'min_lon': -75, 'max_lon': -68,
                'start': '2009-01-01',
                'end': '2019-12-31'
            },
            {
                'name': '印尼苏门答腊',
                'min_lat': -8, 'max_lat': 6,
                'min_lon': 93, 'max_lon': 106,
                'start': '2003-01-01',
                'end': '2013-12-31'
            },
            {
                'name': '中国西南',
                'min_lat': 25, 'max_lat': 35,
                'min_lon': 98, 'max_lon': 108,
                'start': '2007-01-01',
                'end': '2017-12-31'
            },
            {
                'name': '新西兰',
                'min_lat': -48, 'max_lat': -35,
                'min_lon': 165, 'max_lon': 180,
                'start': '2015-01-01',
                'end': '2020-12-31'
            }
        ]
        
        results = []
        
        for region in regions:
            print(f"\n下载 {region['name']} 区域数据...")
            
            output_file = f"data2/earthquake/region_{region['name'].replace(' ', '_')}.csv"
            
            success, count = self.download_from_usgs(
                start_time=region['start'],
                end_time=region['end'],
                min_mag=3.0,
                max_mag=10.0,
                min_lat=region['min_lat'],
                max_lat=region['max_lat'],
                min_lon=region['min_lon'],
                max_lon=region['max_lon'],
                output_file=output_file
            )
            
            results.append({
                'name': region['name'],
                'success': success,
                'count': count
            })
        
        return results
    
    def download_recent_earthquakes(self):
        """下载最近1年的地震数据"""
        print("\n" + "=" * 70)
        print("下载最近1年的地震数据")
        print("=" * 70)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        output_file = "data2/earthquake/recent_1year.csv"
        
        success, count = self.download_from_usgs(
            start_time=start_date.strftime('%Y-%m-%d'),
            end_time=end_date.strftime('%Y-%m-%d'),
            min_mag=4.0,
            max_mag=10.0,
            min_lat=-90,
            max_lat=90,
            min_lon=-180,
            max_lon=180,
            output_file=output_file
        )
        
        return success, count
    
    def run_expansion(self):
        """运行多数据源扩展"""
        print("=" * 70)
        print("太仪v2.0 - 多数据源扩展")
        print("=" * 70)
        
        # 下载高风险区域数据
        region_results = self.download_high_risk_regions()
        
        # 下载最近数据
        recent_success, recent_count = self.download_recent_earthquakes()
        
        # 统计结果
        print("\n" + "=" * 70)
        print("数据扩展结果")
        print("=" * 70)
        
        total = 0
        success_count = 0
        
        for r in region_results:
            status = "✓" if r['success'] else "✗"
            print(f"{status} {r['name']}: {r['count']} 条记录")
            if r['success']:
                total += r['count']
                success_count += 1
        
        if recent_success:
            print(f"✓ 最近1年: {recent_count} 条记录")
            total += recent_count
            success_count += 1
        
        print(f"\n总计: {success_count} 个数据源，{total} 条记录")
        print("\n多数据源扩展完成！")
        
        return region_results

if __name__ == "__main__":
    expansion = MultiSourceDataExpansion()
    expansion.run_expansion()
