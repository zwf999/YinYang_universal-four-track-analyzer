#!/usr/bin/env python3
# 验证天文单位数据

import os
from collections import Counter

# 真实的天文单位值
REAL_AU = "149597870700"
print(f"真实的天文单位值: {REAL_AU}")
print()

# 分析文件
def analyze_file(file_path):
    """分析天文单位文件"""
    print(f"=== 分析文件: {os.path.basename(file_path)} ===")
    
    try:
        with open(file_path, 'r') as f:
            content = f.read().strip()
        
        print(f"文件长度: {len(content)} 字符")
        print(f"前20位: {content[:20]}")
        print(f"前30位: {content[:30]}")
        
        # 检查是否以真实值开头
        if content.startswith(REAL_AU):
            print(f"✅ 以真实值开头")
        else:
            print(f"❌ 不以真实值开头")
            print(f"  真实值前20位: {REAL_AU[:20]}")
            print(f"  文件前20位:   {content[:20]}")
        
        # 分析数字分布
        digits = [int(c) for c in content if c.isdigit()]
        counts = Counter(digits)
        total = len(digits)
        
        print("\n数字分布:")
        for num in range(10):
            count = counts.get(num, 0)
            percentage = (count / total) * 100
            print(f"数字 {num}: {count} 次 ({percentage:.2f}%)")
        
        # 检查是否有数字缺失
        missing_digits = [num for num in range(10) if num not in counts]
        if missing_digits:
            print(f"\n⚠️  缺失数字: {missing_digits}")
        else:
            print("\n✅ 所有数字都存在")
        
        # 检查数字集中度
        max_count = max(counts.values())
        max_num = max(counts, key=counts.get)
        max_percentage = (max_count / total) * 100
        print(f"\n最高频数字: {max_num} ({max_percentage:.2f}%)")
        
        # 分析前100位的模式
        print("\n前100位数字:")
        print(content[:100])
        
        return True, content
        
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return False, None

# 分析两个文件
files = [
    'data/astronomical_unit_100k.txt',
    'data/astronomical_unit_high_precision.txt'
]

for file_path in files:
    if os.path.exists(file_path):
        analyze_file(file_path)
    else:
        print(f"❌ 文件不存在: {file_path}")
    print()
    print("=" * 80)
    print()

print("=== 结论 ===")
print("真实的天文单位值: 149597870700")
print("如果文件以这个值开头，并且数字分布相对均匀，那么可能是真实的。")
print("如果文件数字分布极度偏斜，或者不以真实值开头，那么可能是生成的。")
