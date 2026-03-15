
# data2 - 真实数据文件夹

这个文件夹包含用于TSE（Total Structural Entropy）方法测试的真实数据源。

## 数据来源与获取方式

### 1. 地震数据 (earthquake/)
**官方数据源：**
- USGS Earthquake Catalog: https://earthquake.usgs.gov/earthquakes/feed/v1.0/csv.php
- 全球地震活动数据：https://earthquake.usgs.gov/earthquakes/search/

**获取方法：**
```python
# CSV格式直接下载
# 过去30天所有地震：
# https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.csv

# 过去7天大于4.5级地震：
# https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_week.csv
```

### 2. 气象数据 (weather/)
**官方数据源：**
- NOAA Climate Data Online: https://www.ncdc.noaa.gov/cdo-web/
- 全球气象数据：https://www.weather.gov/
- 中国气象数据：http://data.cma.cn/

### 3. 金融数据 (finance/)
**官方数据源：**
- Yahoo Finance (历史数据)
- Alpha Vantage API
- 上证所/深交所公开数据

### 4. 文本数据 (text/)
- 古腾堡计划 (公共领域书籍): https://www.gutenberg.org/
- Wikipedia 数据导出

### 5. 音频数据 (audio/)
- 公共领域音乐: https://musopen.org/
- Free Sound Archive: https://freesound.org/

## 关于地震预警与TSE方法

### 地震预警原理
地震预警系统（EEWS）是在地震发生后，利用P波（纵波，速度快但破坏力小）与S波（横波，速度慢但破坏力大）的时间差，在破坏性S波到达前发布警报。

**现有方法特点：**
1. 需要密集的地震台网
2. 震后数秒内快速估算
3. 依赖地震波物理特性

### TSE方法在地震数据上的潜在应用
虽然TSE方法目前主要用于DNA序列分析，但可以探索以下方向：

1. **地震波信号分析**
   - 将地震波形数据转换为二进制序列
   - 用TSE分析波形的结构复杂度变化
   - 寻找地震前的异常结构熵模式

2. **地震目录时间序列分析**
   - 分析地震发生时间序列的结构特征
   - 探索地震活动的有序性变化

3. **多变量综合分析**
   - 结合地质、气象、地球物理等多源数据
   - 用TSE寻找综合指标的异常变化

## 获取真实数据的Python脚本示例

```python
import urllib.request
import os

def download_usgs_earthquake_data():
    """下载USGS地震数据"""
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.csv"
    output_file = "data2/earthquake/usgs_all_month.csv"
    
    print(f"正在下载: {url}")
    urllib.request.urlretrieve(url, output_file)
    print(f"✓ 已保存到: {output_file}")

def download_gutenberg_book(book_id=1342):
    """从古腾堡计划下载书籍（傲慢与偏见）"""
    url = f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt"
    output_file = "data2/text/pride_and_prejudice.txt"
    
    print(f"正在下载: {url}")
    try:
        urllib.request.urlretrieve(url, output_file)
        print(f"✓ 已保存到: {output_file}")
    except:
        print("下载失败，请手动获取")
```

## 下一步

1. 从上述官方网站下载真实数据
2. 将数据放入对应子文件夹
3. 修改分析脚本以支持data2文件夹
4. 运行TSE分析，对比不同领域数据的特征

