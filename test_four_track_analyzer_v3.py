#!/usr/bin/env python3
# 测试四轨分析器 v3.0 - 双重配对分析

from core.analyzers.four_track_analyzer import FourTrackAnalyzer

print("=== 四轨分析器 v4.0 测试 ===")

# 创建分析器实例
print("1. 创建分析器实例...")
try:
    analyzer = FourTrackAnalyzer()
    print("   ✓ 分析器创建成功")
except Exception as e:
    print(f"   ✗ 分析器创建失败: {e}")
    exit(1)

# 测试配置验证
print("\n2. 测试配置验证...")
try:
    valid, errors = analyzer.validate_configuration()
    if valid:
        print("   ✓ 配置验证成功")
    else:
        print(f"   ✗ 配置验证失败: {errors}")
except Exception as e:
    print(f"   ✗ 配置验证出错: {e}")

# 测试数字配对分析
print("\n3. 测试数字配对分析...")
test_digits = [1, 8, 2, 7, 3, 6, 4, 5, 9, 0, 1, 8]  # 轨道2的有效配对
try:
    # 测试轨道2（和=9）
    result_track2 = analyzer._calculate_digit_pairs(test_digits, 'track2')
    print(f"   ✓ 轨道2数字配对分析成功")
    print(f"   有效配对: {result_track2['valid_pairs']}/{result_track2['total_pairs']}")
    print(f"   配对率: {result_track2['pair_ratio']:.4f}")
    
except Exception as e:
    print(f"   ✗ 轨道2数字配对分析出错: {e}")

try:
    # 测试轨道3（和=10）
    test_digits_track3 = [1, 9, 2, 8, 3, 7, 4, 6, 5, 0, 1, 9]  # 轨道3的有效配对
    result_track3 = analyzer._calculate_digit_pairs(test_digits_track3, 'track3')
    print(f"   ✓ 轨道3数字配对分析成功")
    print(f"   有效配对: {result_track3['valid_pairs']}/{result_track3['total_pairs']}")
    print(f"   配对率: {result_track3['pair_ratio']:.4f}")
    
except Exception as e:
    print(f"   ✗ 轨道3数字配对分析出错: {e}")

try:
    # 测试轨道4（特定组合）
    test_digits_track4 = [1, 8, 2, 5, 3, 6, 4, 7, 9, 0, 1, 8]  # 轨道4的有效配对
    result_track4 = analyzer._calculate_digit_pairs(test_digits_track4, 'track4')
    print(f"   ✓ 轨道4数字配对分析成功")
    print(f"   有效配对: {result_track4['valid_pairs']}/{result_track4['total_pairs']}")
    print(f"   配对率: {result_track4['pair_ratio']:.4f}")
    
except Exception as e:
    print(f"   ✗ 轨道4数字配对分析出错: {e}")

# 测试完整分析
print("\n4. 测试完整分析...")
test_sequence = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0] * 2  # 20位
try:
    result = analyzer.analyze(test_sequence)
    print(f"   ✓ 完整分析成功")
    
    # 检查轨道2的全局数字配对分析
    track2 = result.get('track2', {})
    if track2:
        forward = track2.get('forward', {})
        global_digit_pairs = forward.get('global_digit_pairs', {})
        print(f"   ✓ 轨道2全局数字配对率: {global_digit_pairs.get('pair_ratio', 0):.4f}")
        print(f"   ✓ 轨道2配对类型: {global_digit_pairs.get('pair_types', {})}")
        print(f"   ✓ 轨道2未配对数字: {global_digit_pairs.get('unpaired', {})}")
    
    # 检查轨道3的全局数字配对分析
    track3 = result.get('track3', {})
    if track3:
        forward = track3.get('forward', {})
        global_digit_pairs = forward.get('global_digit_pairs', {})
        print(f"   ✓ 轨道3全局数字配对率: {global_digit_pairs.get('pair_ratio', 0):.4f}")
    
    # 检查轨道4的全局数字配对分析
    track4 = result.get('track4', {})
    if track4:
        forward = track4.get('forward', {})
        global_digit_pairs = forward.get('global_digit_pairs', {})
        print(f"   ✓ 轨道4全局数字配对率: {global_digit_pairs.get('pair_ratio', 0):.4f}")

except Exception as e:
    print(f"   ✗ 完整分析出错: {e}")

# 测试全局数字配对分析
print("\n5. 测试全局数字配对分析...")
test_sequence_2 = [1, 8, 2, 7, 3, 6, 4, 5, 9, 0]  # 轨道2的有效配对
try:
    # 测试轨道2全局数字配对
    result_track2 = analyzer._analyze_global_digit_pairs(test_sequence_2, 'track2')
    print(f"   ✓ 轨道2全局数字配对分析成功")
    print(f"   有效配对: {result_track2['valid_pairs']}/{result_track2['total_pairs']}")
    print(f"   配对率: {result_track2['pair_ratio']:.4f}")
    print(f"   配对类型: {result_track2['pair_types']}")
    print(f"   未配对数字: {result_track2['unpaired']}")

except Exception as e:
    print(f"   ✗ 轨道2全局数字配对分析出错: {e}")

try:
    # 测试轨道3全局数字配对
    test_sequence_3 = [1, 9, 2, 8, 3, 7, 4, 6, 5, 0]  # 轨道3的有效配对
    result_track3 = analyzer._analyze_global_digit_pairs(test_sequence_3, 'track3')
    print(f"   ✓ 轨道3全局数字配对分析成功")
    print(f"   有效配对: {result_track3['valid_pairs']}/{result_track3['total_pairs']}")
    print(f"   配对率: {result_track3['pair_ratio']:.4f}")

except Exception as e:
    print(f"   ✗ 轨道3全局数字配对分析出错: {e}")

try:
    # 测试轨道4全局数字配对
    test_sequence_4 = [1, 8, 2, 5, 3, 6, 4, 7, 9, 0]  # 轨道4的有效配对
    result_track4 = analyzer._analyze_global_digit_pairs(test_sequence_4, 'track4')
    print(f"   ✓ 轨道4全局数字配对分析成功")
    print(f"   有效配对: {result_track4['valid_pairs']}/{result_track4['total_pairs']}")
    print(f"   配对率: {result_track4['pair_ratio']:.4f}")

except Exception as e:
    print(f"   ✗ 轨道4全局数字配对分析出错: {e}")

# 测试数字配对验证
print("\n5. 测试数字配对验证...")
test_cases = [
    # (d1, d2, track, expected)
    (1, 8, 'track2', True),
    (8, 1, 'track2', True),
    (2, 7, 'track2', True),
    (7, 2, 'track2', True),
    (3, 6, 'track2', True),
    (6, 3, 'track2', True),
    (4, 5, 'track2', True),
    (5, 4, 'track2', True),
    (9, 0, 'track2', True),
    (0, 9, 'track2', True),
    (1, 9, 'track2', False),  # 无效
    
    (1, 9, 'track3', True),
    (9, 1, 'track3', True),
    (2, 8, 'track3', True),
    (8, 2, 'track3', True),
    (3, 7, 'track3', True),
    (7, 3, 'track3', True),
    (4, 6, 'track3', True),
    (6, 4, 'track3', True),
    (5, 0, 'track3', True),
    (0, 5, 'track3', True),
    (1, 8, 'track3', False),  # 无效
    
    (1, 8, 'track4', True),
    (8, 1, 'track4', True),
    (2, 5, 'track4', True),
    (5, 2, 'track4', True),
    (3, 6, 'track4', True),
    (6, 3, 'track4', True),
    (4, 7, 'track4', True),
    (7, 4, 'track4', True),
    (9, 0, 'track4', True),
    (0, 9, 'track4', True),
    (1, 9, 'track4', False),  # 无效
]

passed = 0
total = len(test_cases)

for d1, d2, track, expected in test_cases:
    try:
        result = analyzer._is_valid_digit_pair(d1, d2, track)
        if result == expected:
            passed += 1
        else:
            print(f"   ✗ 测试失败: ({d1}, {d2}, {track}) 期望 {expected}, 实际 {result}")
    except Exception as e:
        print(f"   ✗ 测试出错: ({d1}, {d2}, {track}) - {e}")

print(f"   ✓ 数字配对验证: {passed}/{total} 测试通过")

print("\n=== 测试完成 ===")
if passed == total:
    print("✅ 所有测试通过，四轨分析器 v3.0 工作正常！")
else:
    print(f"❌ {total - passed} 个测试失败，需要修复！")
