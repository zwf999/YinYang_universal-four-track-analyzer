# analyzer_philosophy.py
# 哲学正确版：完全分离双轨，凸显第一轨道的独立价值
# 用法：直接运行 python analyzer_philosophy.py

import os
import time
from collections import Counter

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

def first_track_analysis(digits):
    """
    第一轨道：对称性检验
    输入：12位数字
    输出：(p13_ok, p24_ok, states, failed_dimensions)
    哲学：检验是否存在四维同步对称秩序
    """
    # 分成4组，每组3位
    parts = [digits[i:i+3] for i in range(0, 12, 3)]
    states = []
    
    # 计算每组的状态
    for part in parts:
        # 小大状态
        s1 = get_state(tuple(ATTRIBUTES[d][0] for d in part))
        # 上下状态
        s2 = get_state(tuple(ATTRIBUTES[d][2] for d in part))
        # 奇偶状态
        s3 = get_state(tuple(ATTRIBUTES[d][3] for d in part))
        
        # 层级相互作用状态
        layers = [ATTRIBUTES[d][1]-1 for d in part]
        ab_bits = (
            AB_MATRIX[layers[0]][layers[1]],
            AB_MATRIX[layers[1]][layers[2]],
            AB_MATRIX[layers[2]][layers[0]]
        )
        s4 = get_state(ab_bits)
        states.append((s1, s2, s3, s4))
    
    # 检查对称性条件（核心）
    p13_ok = all(states[0][i] + states[2][i] == 9 for i in range(4))
    p24_ok = all(states[1][i] + states[3][i] == 9 for i in range(4))
    
    # 记录哪些维度失败了
    failed_dimensions = []
    if not p13_ok:
        for i in range(4):
            if states[0][i] + states[2][i] != 9:
                failed_dimensions.append(('p13', i, states[0][i], states[2][i]))
    
    if not p24_ok:
        for i in range(4):
            if states[1][i] + states[3][i] != 9:
                failed_dimensions.append(('p24', i, states[1][i], states[3][i]))
    
    return {
        'p13_ok': p13_ok,
        'p24_ok': p24_ok,
        'states': states,
        'failed_dimensions': failed_dimensions,
        'perfect': p13_ok and p24_ok
    }

def second_track_analysis(digits):
    """
    第二轨道：阴阳结构分析
    输入：12位数字
    输出：阴阳统计和残余数字
    哲学：量化结构性偏倚，提取数字DNA
    """
    # 天干映射
    tags = [GANZHI_MAP[d] for d in digits]
    
    # 统计阴阳数字
    yang_nums = [d for d, t in zip(digits, tags) if t in YANG_SET]
    yin_nums = [d for d, t in zip(digits, tags) if t not in YANG_SET]
    
    # 计算差异
    diff = len(yang_nums) - len(yin_nums)
    
    # 产生残余（基于阴阳失衡）
    if diff > 0:
        # 阳多阴少，保留多余的阳数
        residues = yang_nums[-diff:] if diff <= len(yang_nums) else yang_nums
        residue_type = 'yang'
    elif diff < 0:
        # 阴多阳少，保留多余的阴数
        residues = yin_nums[:abs(diff)] if abs(diff) <= len(yin_nums) else yin_nums
        residue_type = 'yin'
    else:
        # 阴阳平衡，无残余
        residues = []
        residue_type = 'balanced'
    
    return {
        'yang_count': len(yang_nums),
        'yin_count': len(yin_nums),
        'diff': diff,
        'residues': residues,
        'residue_type': residue_type,
        'yang_nums': yang_nums,
        'yin_nums': yin_nums
    }

def analyze_constant(filename, description=""):
    """分析一个常数文件"""
    full_path = os.path.join(DATA_DIR, filename)
    
    if not os.path.exists(full_path):
        print(f"❌ 文件不存在: {full_path}")
        return None
    
    print(f"\n{'='*70}")
    if description:
        print(f"🧮 哲学分析: {description}")
    else:
        print(f"🧮 哲学分析: {filename}")
    print(f"📁 文件: {filename}")
    print(f"{'='*70}")
    
    # 读取数字
    with open(full_path, 'r') as f:
        content = f.read()
    digits = [int(c) for c in content if c.isdigit()]
    
    if len(digits) < 12:
        print("❌ 数字不足12位！")
        return None
    
    print(f"📊 读取 {len(digits)} 位数字")
    
    # 初始化统计
    window_count = 0
    perfect_windows = 0
    first_track_stats = {
        'p13_ok_count': 0,
        'p24_ok_count': 0,
        'both_ok_count': 0,
        'dimension_fails': [0, 0, 0, 0],  # 四个维度的失败次数
        'p13_fail_details': Counter(),
        'p24_fail_details': Counter()
    }
    
    second_track_stats = {
        'yang_total': 0,
        'yin_total': 0,
        'residue_counter': Counter(),
        'window_types': {'yang': 0, 'yin': 0, 'balanced': 0}
    }
    
    # 分析每个窗口
    for i in range(0, len(digits) - 11, 5):
        window = digits[i:i+12]
        
        # 第一轨道分析
        first_result = first_track_analysis(window)
        
        # 第一轨道统计
        if first_result['p13_ok']:
            first_track_stats['p13_ok_count'] += 1
        if first_result['p24_ok']:
            first_track_stats['p24_ok_count'] += 1
        if first_result['perfect']:
            first_track_stats['both_ok_count'] += 1
            perfect_windows += 1
        
        # 记录失败维度
        for fail in first_result['failed_dimensions']:
            pair, dim, val1, val2 = fail
            first_track_stats['dimension_fails'][dim] += 1
            if pair == 'p13':
                key = f"dim{dim}:{val1}+{val2}"
                first_track_stats['p13_fail_details'][key] += 1
            else:
                key = f"dim{dim}:{val1}+{val2}"
                first_track_stats['p24_fail_details'][key] += 1
        
        # 第二轨道分析
        second_result = second_track_analysis(window)
        
        # 第二轨道统计
        second_track_stats['yang_total'] += second_result['yang_count']
        second_track_stats['yin_total'] += second_result['yin_count']
        second_track_stats['residue_counter'].update(second_result['residues'])
        second_track_stats['window_types'][second_result['residue_type']] += 1
        
        window_count += 1
        
        if window_count % 50000 == 0 and len(digits) > 100000:
            print(f"  已处理 {window_count} 个窗口")
    
    print(f"\n✅ 分析完成，共 {window_count} 个窗口")
    
    # 输出第一轨道结果
    print(f"\n{'='*70}")
    print("🎯 第一轨道：对称性检验（回答：是否存在秩序？）")
    print(f"{'-'*70}")
    
    perfect_rate = (perfect_windows / window_count) * 100
    p13_ok_rate = (first_track_stats['p13_ok_count'] / window_count) * 100
    p24_ok_rate = (first_track_stats['p24_ok_count'] / window_count) * 100
    
    print(f"📊 对称性统计:")
    print(f"  • 完美窗口（p13且p24通过）: {perfect_windows} ({perfect_rate:.6f}%)")
    print(f"  • p13单独通过: {first_track_stats['p13_ok_count']} ({p13_ok_rate:.2f}%)")
    print(f"  • p24单独通过: {first_track_stats['p24_ok_count']} ({p24_ok_rate:.2f}%)")
    
    print(f"\n📊 维度失败分布（哪个维度最难满足）:")
    for dim in range(4):
        fail_rate = (first_track_stats['dimension_fails'][dim] / (window_count * 2)) * 100
        print(f"  维度{dim+1}: {first_track_stats['dimension_fails'][dim]}次失败 ({fail_rate:.1f}%)")
    
    # 输出第二轨道结果
    print(f"\n{'='*70}")
    print("🎯 第二轨道：阴阳结构分析（回答：偏向哪边？）")
    print(f"{'-'*70}")
    
    total_residues = sum(second_track_stats['residue_counter'].values())
    yang_total = second_track_stats['yang_total']
    yin_total = second_track_stats['yin_total']
    
    print(f"📊 阴阳统计:")
    print(f"  • 阳数总数: {yang_total}")
    print(f"  • 阴数总数: {yin_total}")
    
    if yin_total > 0:
        ratio = yang_total / yin_total
        print(f"  • 阴阳比例: {ratio:.3f} : 1")
    else:
        print(f"  • 阴阳比例: 无穷大 (纯阳)")
    
    print(f"\n📊 窗口类型分布:")
    total_windows = window_count
    for wtype, count in second_track_stats['window_types'].items():
        percentage = (count / total_windows) * 100
        if wtype == 'yang':
            desc = "阳多阴少"
        elif wtype == 'yin':
            desc = "阴多阳少"
        else:
            desc = "阴阳平衡"
        print(f"  • {desc}: {count}窗口 ({percentage:.1f}%)")
    
    if total_residues > 0:
        print(f"\n📊 残余数字分布 (Top 5):")
        for num, count in second_track_stats['residue_counter'].most_common(5):
            percentage = (count / total_residues) * 100
            print(f"  数字 {num}: {count}次 ({percentage:.2f}%)")
    
    # 哲学总结
    print(f"\n{'='*70}")
    print("💡 哲学总结")
    print(f"{'-'*70}")
    
    print(f"第一轨道的独立贡献:")
    print(f"  1. 定义了'四维同步对称'的数学标准")
    print(f"  2. 检验结果: {perfect_windows}/{window_count} 完美窗口 ({perfect_rate:.6f}%)")
    
    if perfect_windows == 0:
        print(f"  3. 重要发现: 该常数完全不具备四维同步对称性")
        print(f"  4. 哲学意义: 揭示了该常数的'结构性混沌'本质")
    else:
        print(f"  3. 重要发现: 该常数存在 {perfect_windows} 个对称结构点")
        print(f"  4. 哲学意义: 揭示了该常数的'有序-无序'混合特征")
    
    print(f"\n第二轨道的独立贡献:")
    if yin_total > 0:
        print(f"  1. 阴阳比例: {yang_total/yin_total:.3f}:1")
    else:
        print(f"  1. 阴阳比例: 无穷大 (纯阳)")
    
    if yang_total > yin_total:
        print(f"  2. 结构偏倚: 强烈阳数主导")
    elif yin_total > yang_total:
        print(f"  2. 结构偏倚: 强烈阴数主导")
    else:
        print(f"  2. 结构偏倚: 完美平衡")
    
    print(f"  3. 哲学意义: 量化了该常数的'结构性偏倚'特征")
    
    print(f"\n双轨协同的完整图景:")
    print(f"  第一轨道 → 检验'是否存在秩序' → 回答对称性问题")
    print(f"  第二轨道 → 分析'秩序偏向何方' → 回答结构性问题")
    print(f"  共同构成对数学常数的完整认知")
    
    # 保存结果
    base_name = os.path.splitext(filename)[0]
    result_file = f"analysis_philosophy_{base_name}.txt"
    
    with open(result_file, 'w', encoding='utf-8') as f:
        f.write(f"哲学分析报告: {description if description else filename}\n")
        f.write(f"{'='*60}\n\n")
        f.write(f"分析时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"总窗口数: {window_count}\n\n")
        
        f.write("第一轨道 - 对称性检验:\n")
        f.write(f"  完美窗口数: {perfect_windows} ({perfect_rate:.6f}%)\n")
        f.write(f"  p13通过率: {p13_ok_rate:.2f}%\n")
        f.write(f"  p24通过率: {p24_ok_rate:.2f}%\n\n")
        
        f.write("第二轨道 - 阴阳结构分析:\n")
        f.write(f"  阳数总数: {yang_total}\n")
        f.write(f"  阴数总数: {yin_total}\n")
        if yin_total > 0:
            f.write(f"  阴阳比例: {yang_total/yin_total:.3f}:1\n\n")
        else:
            f.write(f"  阴阳比例: 无穷大\n\n")
        
        f.write("窗口类型分布:\n")
        for wtype, count in second_track_stats['window_types'].items():
            if wtype == 'yang':
                desc = "阳多阴少"
            elif wtype == 'yin':
                desc = "阴多阳少"
            else:
                desc = "阴阳平衡"
            percentage = (count / window_count) * 100
            f.write(f"  {desc}: {count} ({percentage:.1f}%)\n")
        
        if total_residues > 0:
            f.write(f"\n残余数字Top 10:\n")
            for num, count in second_track_stats['residue_counter'].most_common(10):
                f.write(f"  {num}: {count}\n")
    
    print(f"\n💾 详细报告保存到: {result_file}")
    print(f"{'='*70}")
    
    return {
        'filename': filename,
        'description': description if description else filename,
        'windows': window_count,
        'first_track': {
            'perfect_windows': perfect_windows,
            'perfect_rate': perfect_rate,
            'p13_ok_rate': p13_ok_rate,
            'p24_ok_rate': p24_ok_rate
        },
        'second_track': {
            'yang_total': yang_total,
            'yin_total': yin_total,
            'ratio': yang_total / yin_total if yin_total > 0 else float('inf'),
            'window_types': second_track_stats['window_types']
        }
    }

def main():
    print(f"{'='*70}")
    print("🧬 哲学正确双轨分析器")
    print(f"{'='*70}")
    print("完全分离双轨，凸显各自独立价值")
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
    
    result = analyze_constant(filename, description)
    
    if result:
        print(f"\n🎯 第一轨道核心发现:")
        print(f"  完美窗口率: {result['first_track']['perfect_rate']:.6f}%")
        if result['first_track']['perfect_rate'] == 0:
            print(f"  → 该常数完全不具有四维同步对称性")
        else:
            print(f"  → 该常数具有微弱对称性")
        
        print(f"\n🎯 第二轨道核心发现:")
        ratio = result['second_track']['ratio']
        if ratio == float('inf'):
            print(f"  阴阳比例: 无穷大 (纯阳)")
        else:
            print(f"  阴阳比例: {ratio:.3f}:1")
            if ratio > 5:
                print(f"  → 强烈阳数偏倚 (重要常数特征)")
            elif ratio < 0.2:
                print(f"  → 强烈阴数偏倚 (有理数特征)")
            else:
                print(f"  → 中等比例")
        
        print(f"\n💡 双轨哲学定位:")
        print(f"  第一轨道是'对称性检测器'，独立回答秩序存在问题")
        print(f"  第二轨道是'结构性分析器'，独立回答偏倚方向问题")
        print(f"  两者平等协作，共同揭示常数本质")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()
