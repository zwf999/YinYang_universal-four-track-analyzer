#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据扩展行动 v2 - 扩大搜索范围
"""

import urllib.request
import csv
import os
from datetime import datetime, timedelta

class DataExpansionV2:
    def __init__(self):
        self.base_url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    
    def download_earthquake_data(self, start_time, end_time, min_mag=0.0, 
                               min_lat=None, max_lat=None, min_lon=None, max_lon=None, 
                               output_file="earthquake_data.csv"):
        """从USGS下载地震数据（矩形区域）"""
        
        params = {
            "format": "csv",
            "starttime": start_time,
            "endtime": end_time,
            "minmagnitude": min_mag
        }
        
        if min_lat and max_lat and min_lon and max_lon:
            params["minlatitude"] = min_lat
            params["maxlatitude"] = max_lat
            params["minlongitude"] = min_lon
            params["maxlongitude"] = max_lon
        
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        url = f"{self.base_url}?{query}"
        
        print(f"下载: {url[:100]}...")
        
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
    
    def download_all_m7_earthquakes(self):
        """下载所有M≥7.0地震的完整序列"""
        print("=" * 70)
        print("下载所有M≥7.0地震的完整前震序列")
        print("=" * 70)
        
        # 读取312次地震列表
        m7_file = "data2/earthquake/usgs_m7_2000_2020.csv"
        if not os.path.exists(m7_file):
            print(f"文件不存在: {m7_file}")
            return []
        
        earthquakes = []
        with open(m7_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    time_str = row.get('time', '').replace('Z', '+00:00')
                    time = datetime.fromisoformat(time_str).replace(tzinfo=None)
                    mag = float(row.get('mag', 0))
                    lat = float(row.get('latitude', 0))
                    lon = float(row.get('longitude', 0))
                    place = row.get('place', '')
                    earthquakes.append({
                        'time': time,
                        'mag': mag,
                        'lat': lat,
                        'lon': lon,
                        'place': place
                    })
                except:
                    continue
        
        print(f"加载 {len(earthquakes)} 次M≥7.0地震")
        
        results = []
        
        # 只处理前20个最强的地震
        earthquakes = sorted(earthquakes, key=lambda x: x['mag'], reverse=True)[:20]
        
        for i, eq in enumerate(earthquakes):
            print(f"\n[{i+1}/20] {eq['place']} M{eq['mag']:.1f}")
            
            # 计算矩形区域（±3度）
            min_lat = eq['lat'] - 3
            max_lat = eq['lat'] + 3
            min_lon = eq['lon'] - 3
            max_lon = eq['lon'] + 3
            
            # 时间范围：主震前30天
            start_time = (eq['time'] - timedelta(days=30)).strftime('%Y-%m-%d')
            end_time = eq['time'].strftime('%Y-%m-%dT%H:%M:%S')
            
            output_file = f"data2/earthquake/m7_{eq['time'].strftime('%Y%m%d')}_full.csv"
            
            success, count = self.download_earthquake_data(
                start_time=start_time,
                end_time=end_time,
                min_mag=2.5,  # 降低到M2.5
                min_lat=min_lat,
                max_lat=max_lat,
                min_lon=min_lon,
                max_lon=max_lon,
                output_file=output_file
            )
            
            results.append({
                'name': eq['place'],
                'mag': eq['mag'],
                'time': eq['time'],
                'success': success,
                'count': count,
                'file': output_file
            })
        
        return results
    
    def run_expansion(self):
        """运行数据扩展行动"""
        results = self.download_all_m7_earthquakes()
        
        print("\n" + "=" * 70)
        print("数据扩展行动结果")
        print("=" * 70)
        
        total = 0
        success_count = 0
        
        for r in results:
            status = "✓" if r['success'] else "✗"
            print(f"{status} M{r['mag']:.1f} {r['name']}: {r['count']} 条记录")
            if r['success']:
                total += r['count']
                success_count += 1
        
        print(f"\n总计: {success_count}/{len(results)} 个地震，{total} 条记录")
        print("\n数据扩展行动完成！")
        
        return results

if __name__ == "__main__":
    expansion = DataExpansionV2()
    expansion.run_expansion()
