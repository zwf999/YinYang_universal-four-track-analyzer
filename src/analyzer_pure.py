# analyzer_pure.py
# 纯净版：坚持"不对称即信息"哲学，无任何多余逻辑
# 用法：修改 FILENAME 变量，然后运行 python analyzer_pure.py

import os
import time
from collections import Counter

DATA_DIR = "data"
FILENAME = "b001620_full.txt"  # ← 修改这里指定要分析的文件
FULL_PATH = os.path.join(DATA_DIR, FILENAME)

# --- 完全正确的 ATTRIBUTES ---
ATTRIBUTES = {
    0: (0, 5, 0, 0),
    1: (1, 1, 1, 1),
    2: (1, 2, 1, 0),
    3: (1, 3, 1, 1),
    4: (1, 4, 0, 0),
    5: (1, 5, 0, 1),  # 5 是"小"！
    6: (0, 1, 1, 0),
    7: (0, 2, 1, 1),
    8: (0, 3, 1, 0),
    9: (0, 4, 0, 1)
}

AB_MATRIX = [
    [0, 0, 1, 1, 0],
    [0, 0, 1, 0, 1],
    [1, 1, 0, 0, 0],
    [1, 0, 0, 0, 1],
    [0, 1, 0, 1, 0]
]

GANZHI_MAP = {1:'甲',8:'甲', 3:'丙',6:'丙', 9:'戊',0:'戊', 2:'乙',5:'乙', 4:'丁',7:'丁'}
YANG_SET = {'甲', '丙', '戊'}
STATE_MAP = {(1,1,1):1, (1,1,0):2, (1,0,1):3, (1,0,0):4, (0,1,1):5, (0,1,0):6, (0,0,1):7, (0,0,0):8}

def validate_attributes():
    for num in range(10):
        small_big, layer, up_down, odd_even = ATTRIBUTES[num]
        expected_small = 1 if num in {1,2,3,4,5} else 0
        expected_up = 1 if num in {1,2,3,6,7,8} else 0
        expected_odd = num % 2
        assert small_big == expected_small, f"❌ 数字 {num} 小大属性错误"
        assert up_down == expected_up, f"❌ 数字 {num} 上下属性错误"
        assert odd_even == expected_odd, f"❌ 数字 {num} 奇偶属性错误"

def get_state(bits):
    return STATE_MAP.get(bits, 0)

def analyze_window(digits):
    parts = [digits[i:i+3] for i in range(0, 12, 3)]
    states = []
    for part in parts:
        s1 = get_state(tuple(ATTRIBUTES[d][0] for d in part))
        s2 = get_state(tuple(ATTRIBUTES[d][2] for d in part))
        s3 = get_state(tuple(ATTRIBUTES[d][3] for d in part))
        layers = [ATTRIBUTES[d][1]-1 for d in part]
        ab_bits = (
            AB_MATRIX[layers[0]][layers[1]],
            AB_MATRIX[layers[1]][layers[2]],
            AB_MATRIX[layers[2]][layers[0]]
        )
        s4 = get_state(ab_bits)
        states.append((s1, s2, s3, s4))
    
    p13_ok = all(states[0][i] + states[2][i] == 9 for i in range(4))
    p24_ok = all(states[1][i] + states[3][i] == 9 for i in range(4))
    
    local_res = []
    if not p13_ok: local_res.extend(parts[0] + parts[2])
    if not p24_ok: local_res.extend(parts[1] + parts[3])
    
    tags = [GANZHI_MAP[d] for d in digits]
    yang_nums = [d for d, t in zip(digits, tags) if t in YANG_SET]
    yin_nums = [d for d, t in zip(digits, tags) if t not in YANG_SET]
    diff = len(yang_nums) - len(yin_nums)
    
    if diff > 0:
        global_res = yang_nums[-diff:] if diff <= len(yang_nums) else yang_nums
    elif diff < 0:
        global_res = yin_nums[:abs(diff)] if abs(diff) <= len(yin_nums) else yin_nums
    else:
        global_res = []
    
    return local_res, global_res

def main():
    validate_attributes()
    print("=" * 50)
    print("🧬 常数光谱分析器（纯净版）")
    print("=" * 50)
    print(f"📁 分析文件: {FULL_PATH}")
    
    if not os.path.exists(FULL_PATH):
        print(f"❌ 文件不存在: {FULL_PATH}")
        input("按回车退出...")
        return
    
    with open(FULL_PATH, 'r') as f:
        content = f.read()
    digits = [int(c) for c in content if c.isdigit()]
    
    if len(digits) < 12:
        print("❌ 数字不足12位！")
        input("按回车退出...")
        return
    
    print(f"📊 读取 {len(digits)} 位数字")
    print("📈 分析开始...")
    print("-" * 50)
    
    local_counter = Counter()
    global_counter = Counter()
    window_count = 0
    
    for i in range(0, len(digits) - 11, 5):
        window = digits[i:i+12]
        local_res, global_res = analyze_window(window)
        local_counter.update(local_res)
        global_counter.update(global_res)
        window_count += 1
        
        if window_count % 50000 == 0:
            print(f"  已处理 {window_count} 个窗口")
    
    print("-" * 50)
    print("✅ 分析完成")
    
    total_local = sum(local_counter.values())
    total_global = sum(global_counter.values())
    
    yang_nums = [1, 3, 6, 8, 9, 0]
    yin_nums = [2, 4, 5, 7]
    yang_total = sum(global_counter[d] for d in yang_nums)
    yin_total = sum(global_counter[d] for d in yin_nums)
    
    print(f"\n📊 核心结果:")
    print(f"   总窗口数: {window_count}")
    print(f"   局部残余总数: {total_local}")
    print(f"   全局残余总数: {total_global}")
    print(f"\n🌞 阳数({yang_nums}): {yang_total} 次")
    print(f"🌙 阴数({yin_nums}): {yin_total} 次")
    
    if yin_total > 0:
        ratio = yang_total / yin_total
        print(f"📐 阴阳比例: {ratio:.3f} : 1")
    else:
        print(f"📐 阴阳比例: 仅阴数存在")
    
    print(f"\n🔝【局部残余 Top 10】:")
    for rank, (num, count) in enumerate(local_counter.most_common(10), 1):
        print(f"   #{rank} 数字 {num}: {count} 次")
    
    print(f"\n🔝【全局残余 Top 10】:")
    for rank, (num, count) in enumerate(global_counter.most_common(10), 1):
        print(f"   #{rank} 数字 {num}: {count} 次")
    
    base_name = os.path.splitext(FILENAME)[0]
    result_file = f"analysis_{base_name}_pure.txt"
    
    with open(result_file, 'w', encoding='utf-8') as f:
        f.write("常数光谱分析报告（纯净版）\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"分析文件: {FULL_PATH}\n")
        f.write(f"分析时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"总窗口数: {window_count}\n\n")
        f.write("核心统计:\n")
        f.write(f"  局部残余总数: {total_local}\n")
        f.write(f"  全局残余总数: {total_global}\n")
        f.write(f"  阳数总数: {yang_total} (数字: {yang_nums})\n")
        f.write(f"  阴数总数: {yin_total} (数字: {yin_nums})\n")
        if yin_total > 0:
            f.write(f"  阴阳比例: {yang_total/yin_total:.3f} : 1\n\n")
        else:
            f.write(f"  阴阳比例: 仅阴数存在\n\n")
        f.write("局部残余 Top 10:\n")
        for num, count in local_counter.most_common(10):
            f.write(f"  {num}: {count}\n")
        f.write("\n全局残余 Top 10:\n")
        for num, count in global_counter.most_common(10):
            f.write(f"  {num}: {count}\n")
        f.write("\n阴阳数字详细统计:\n")
        f.write("  阳数统计:\n")
        for num in yang_nums:
            f.write(f"    数字 {num}: {global_counter[num]} 次\n")
        f.write("  阴数统计:\n")
        for num in yin_nums:
            f.write(f"    数字 {num}: {global_counter[num]} 次\n")
    
    print(f"\n💾 结果已保存到: {result_file}")
    print("=" * 50)
    
    # 动态理论洞见
    if yang_total == 0 and yin_total > 0:
        print("\n💡 理论洞见:")
        print("  全局残余纯阴 → 有理数的周期对称性")
        print("  局部残余均匀 → 循环节的完美重复")
        print("  阳数完全抵消 → 阴性能量守恒")
    elif yin_total == 0 and yang_total > 0:
        print("\n💡 理论洞见:")
        print("  全局残余纯阳 → 强烈结构性偏倚")
        print("  局部残余接近100% → 拒绝简单对称")
        print("  此为超越数的典型特征")
    elif yang_total > yin_total * 3:
        print("\n💡 理论洞见:")
        print("  阴阳比例显著偏离 → 隐藏结构性偏倚")
        print("  局部残余高 → 非周期性序列")
        print("  符合超越数或复杂无理数特征")
    else:
        print("\n💡 理论洞见:")
        print("  阴阳比例接近平衡 → 可能为简单无理数或特殊结构")
        print("  需结合其他常数对比分析")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()
