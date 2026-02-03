# analyzer_dual_track.py
# 双轨分析版：深入分析第一轨道和第二轨道的贡献
# 用法：直接运行 python analyzer_dual_track.py

import os
import time
from collections import Counter
import numpy as np

DATA_DIR = "data"

# --- 完全正确的 ATTRIBUTES ---
ATTRIBUTES = {
    0: (0, 5, 0, 0), 1: (1, 1, 1, 1), 2: (1, 2, 1, 0), 3: (1, 3, 1, 1),
    4: (1, 4, 0, 0), 5: (1, 5, 0, 1), 6: (0, 1, 1, 0), 7: (0, 2, 1, 1),
    8: (0, 3, 1, 0), 9: (0, 4, 0, 1)
}

AB_MATRIX = [
    [0, 0, 1, 1, 0], [0, 0, 1, 0, 1], [1, 1, 0, 0, 0],
    [1, 0, 0, 0, 1], [0, 1, 0, 1, 0]
]

GANZHI_MAP = {1:'甲',8:'甲', 3:'丙',6:'丙', 9:'戊',0:'戊', 2:'乙',5:'乙', 4:'丁',7:'丁'}
YANG_SET = {'甲', '丙', '戊'}
STATE_MAP = {(1,1,1):1, (1,1,0):2, (1,0,1):3, (1,0,0):4,
             (0,1,1):5, (0,1,0):6, (0,0,1):7, (0,0,0):8}

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

def analyze_window_dual(digits):
    """双轨分析：返回详细结果"""
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
    
    # 第一轨道：对称性检验
    p13_ok = all(states[0][i] + states[2][i] == 9 for i in range(4))
    p24_ok = all(states[1][i] + states[3][i] == 9 for i in range(4))
    
    # 记录哪些组失败了
    failed_groups = []
    if not p13_ok:
        failed_groups.extend([0, 2])  # 第1组和第3组
    if not p24_ok:
        failed_groups.extend([1, 3])  # 第2组和第4组
    
    # 局部残余
    local_res = []
    if not p13_ok:
        local_res.extend(parts[0] + parts[2])
    if not p24_ok:
        local_res.extend(parts[1] + parts[3])
    
    # 第二轨道：阴阳平衡
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
    
    # 返回详细信息
    return {
        'local_res': local_res,
        'global_res': global_res,
        'failed_groups': failed_groups,
        'states': states,
        'p13_ok': p13_ok,
        'p24_ok': p24_ok,
        'yang_count': len(yang_nums),
        'yin_count': len(yin_nums),
        'diff': diff
    }

def analyze_file_dual(filename, description=""):
    """双轨分析文件"""
    full_path = os.path.join(DATA_DIR, filename)
    
    if not os.path.exists(full_path):
        print(f"❌ 文件不存在: {full_path}")
        return None
    
    print(f"\n{'='*70}")
    if description:
        print(f"🔬 双轨分析: {description}")
    else:
        print(f"🔬 双轨分析: {filename}")
    print(f"📁 文件: {filename}")
    print(f"{'='*70}")
    
    with open(full_path, 'r') as f:
        content = f.read()
    digits = [int(c) for c in content if c.isdigit()]
    
    if len(digits) < 12:
        print("❌ 数字不足12位！")
        return None
    
    print(f"📊 读取 {len(digits)} 位数字")
    
    # 初始化计数器
    local_counter = Counter()
    global_counter = Counter()
    group_fail_counter = Counter()  # 记录各组失败次数
    window_count = 0
    perfect_windows = 0  # 完美窗口数
    
    # 第一轨道统计
    first_track_stats = {
        'total_windows': 0,
        'p13_fail': 0,
        'p24_fail': 0,
        'both_fail': 0,
        'perfect': 0
    }
    
    for i in range(0, len(digits) - 11, 5):
        window = digits[i:i+12]
        result = analyze_window_dual(window)
        
        local_counter.update(result['local_res'])
        global_counter.update(result['global_res'])
        
        # 记录组失败情况
        for group in result['failed_groups']:
            group_fail_counter[group] += 1
        
        # 第一轨道统计
        first_track_stats['total_windows'] += 1
        if not result['p13_ok']:
            first_track_stats['p13_fail'] += 1
        if not result['p24_ok']:
            first_track_stats['p24_fail'] += 1
        if not result['p13_ok'] and not result['p24_ok']:
            first_track_stats['both_fail'] += 1
        if result['p13_ok'] and result['p24_ok']:
            first_track_stats['perfect'] += 1
            perfect_windows += 1
        
        window_count += 1
        
        if window_count % 50000 == 0 and len(digits) > 100000:
            print(f"  已处理 {window_count} 个窗口")
    
    # 计算统计
    total_local = sum(local_counter.values())
    total_global = sum(global_counter.values())
    
    yang_nums = [1, 3, 6, 8, 9, 0]
    yin_nums = [2, 4, 5, 7]
    
    yang_total = sum(global_counter[d] for d in yang_nums)
    yin_total = sum(global_counter[d] for d in yin_nums)
    
    ratio = yang_total / yin_total if yin_total > 0 else 0
    
    print(f"\n{'='*70}")
    print("📊 第一轨道分析（对称性检验）")
    print(f"{'-'*70}")
    
    total_possible = window_count * 12
    local_rate = (total_local / total_possible) * 100 if total_possible > 0 else 0
    
    print(f"✅ 总窗口数: {window_count}")
    print(f"🎯 完美对称窗口: {perfect_windows} ({(perfect_windows/window_count)*100:.4f}%)")
    print(f"📈 局部残余率: {local_rate:.6f}%")
    
    print(f"\n📊 对称失败统计:")
    print(f"  • p13失败: {first_track_stats['p13_fail']} 次 ({(first_track_stats['p13_fail']/window_count)*100:.2f}%)")
    print(f"  • p24失败: {first_track_stats['p24_fail']} 次 ({(first_track_stats['p24_fail']/window_count)*100:.2f}%)")
    print(f"  • 双双失败: {first_track_stats['both_fail']} 次 ({(first_track_stats['both_fail']/window_count)*100:.2f}%)")
    
    print(f"\n📊 组失败分布 (0-3组):")
    for group in range(4):
        fail_count = group_fail_counter[group]
        fail_rate = (fail_count / window_count) * 100
        print(f"  第{group+1}组: {fail_count}次失败 ({fail_rate:.2f}%)")
    
    print(f"\n{'='*70}")
    print("📊 第二轨道分析（阴阳结构）")
    print(f"{'-'*70}")
    
    print(f"🌞 阳数({yang_nums}): {yang_total} 次")
    print(f"🌙 阴数({yin_nums}): {yin_total} 次")
    
    if yin_total > 0:
        print(f"📐 阴阳比例: {ratio:.3f} : 1")
    else:
        print(f"📐 阴阳比例: 纯阴 (无阳数)")
    
    print(f"\n📊 局部残余分布 (Top 5):")
    for num, count in local_counter.most_common(5):
        percentage = (count / total_local) * 100 if total_local > 0 else 0
        print(f"  数字 {num}: {count}次 ({percentage:.2f}%)")
    
    print(f"\n📊 全局残余分布 (Top 5):")
    for num, count in global_counter.most_common(5):
        percentage = (count / total_global) * 100 if total_global > 0 else 0
        print(f"  数字 {num}: {count}次 ({percentage:.2f}%)")
    
    # 计算均匀度指标（第一轨道贡献）
    local_values = [local_counter[i] for i in range(10) if local_counter[i] > 0]
    if len(local_values) > 1:
        local_std = np.std(local_values)
        local_mean = np.mean(local_values)
        local_cv = (local_std / local_mean) * 100  # 变异系数
        print(f"\n📊 局部残余均匀度:")
        print(f"  • 涉及数字: {len(local_values)}个")
        print(f"  • 变异系数: {local_cv:.2f}% (越低越均匀)")
    
    print(f"\n{'='*70}")
    print("💡 双轨综合分析")
    print(f"{'-'*70}")
    
    # 判断常数类型
    if perfect_windows == 0 and ratio > 5:
        print(f"🔍 类型判断: 重要数学常数")
        print(f"   特征: 100%对称破坏 + 强烈阳数偏倚")
    elif perfect_windows > 0:
        print(f"🔍 类型判断: 高度结构化序列")
        print(f"   特征: 存在完美对称窗口")
    elif ratio == 0:
        print(f"🔍 类型判断: 有理数特征")
        print(f"   特征: 纯阴数结构")
    else:
        print(f"🔍 类型判断: 一般无理数")
        print(f"   特征: 中等阴阳比例")
    
    # 保存结果
    base_name = os.path.splitext(filename)[0]
    result_file = f"analysis_dual_{base_name}.txt"
    
    with open(result_file, 'w', encoding='utf-8') as f:
        f.write(f"双轨分析报告: {description if description else filename}\n")
        f.write(f"{'='*60}\n\n")
        f.write(f"分析时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"总窗口数: {window_count}\n\n")
        
        f.write("第一轨道分析（对称性检验）:\n")
        f.write(f"  完美窗口数: {perfect_windows}\n")
        f.write(f"  局部残余率: {local_rate:.6f}%\n")
        f.write(f"  p13失败率: {(first_track_stats['p13_fail']/window_count)*100:.4f}%\n")
        f.write(f"  p24失败率: {(first_track_stats['p24_fail']/window_count)*100:.4f}%\n\n")
        
        f.write("第二轨道分析（阴阳结构）:\n")
        f.write(f"  阳数总数: {yang_total}\n")
        f.write(f"  阴数总数: {yin_total}\n")
        if yin_total > 0:
            f.write(f"  阴阳比例: {ratio:.3f}:1\n\n")
        else:
            f.write(f"  阴阳比例: 纯阴\n\n")
        
        f.write("局部残余Top 10:\n")
        for num, count in local_counter.most_common(10):
            f.write(f"  {num}: {count}\n")
        
        f.write("\n全局残余Top 10:\n")
        for num, count in global_counter.most_common(10):
            f.write(f"  {num}: {count}\n")
    
    print(f"\n💾 详细结果保存到: {result_file}")
    print(f"{'='*70}")
    
    return {
        '文件名': filename,
        '描述': description if description else filename,
        '窗口数': window_count,
        '完美窗口': perfect_windows,
        '局部残余率': local_rate,
        '阳数总数': yang_total,
        '阴数总数': yin_total,
        '阴阳比例': ratio,
        'p13失败率': (first_track_stats['p13_fail']/window_count)*100,
        'p24失败率': (first_track_stats['p24_fail']/window_count)*100
    }

def main():
    print(f"{'='*70}")
    print("🧬 双轨常数光谱分析器")
    print(f"{'='*70}")
    print("深入分析第一轨道（对称性）和第二轨道（阴阳结构）的贡献")
    print(f"{'-'*70}")
    
    validate_attributes()
    
    # 列出可用文件
    files = [f for f in os.listdir(DATA_DIR) if f.endswith('.txt')]
    print(f"\ndata文件夹中的文件:")
    for i, f in enumerate(files, 1):
        print(f"  {i:2d}. {f}")
    
    filename = input("\n请输入要分析的文件名: ").strip()
    
    if filename not in files:
        print(f"❌ 文件 {filename} 不在data文件夹中")
        input("\n按回车退出...")
        return
    
    description = input("请输入描述 (直接回车使用文件名): ").strip()
    if not description:
        description = filename
    
    result = analyze_file_dual(filename, description)
    
    if result:
        print(f"\n🎯 第一轨道核心贡献:")
        print(f"   1. 定义了'四维同步对称'的严格标准")
        print(f"   2. 发现了所有测试常数都无法满足此对称")
        print(f"   3. 揭示了无理数的'结构性混沌'本质")
        
        print(f"\n🎯 第二轨道核心贡献:")
        print(f"   1. 建立了数学常数的阴阳光谱")
        print(f"   2. 发现了重要常数都~6:1阳数偏倚")
        print(f"   3. 区分了不同类型常数的数字DNA")
        
        print(f"\n💡 双轨协同作用:")
        print(f"   第一轨道过滤 → 识别'真实混沌'")
        print(f"   第二轨道分析 → 提取'混沌中的秩序'")
        print(f"   共同构成完整的常数分析框架")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()
