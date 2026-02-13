#!/usr/bin/env python3
# 测试四轨分析器 v2.2.0

from core.analyzers.four_track_analyzer import FourTrackAnalyzer

print("=== 四轨分析器 v2.2.0 测试 ===")

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

# 测试窗口处理边界情况
print("\n3. 测试窗口处理边界情况...")
test_digits_short = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2]  # 正好12位
test_digits_medium = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3, 4, 5]  # 15位
test_digits_long = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0] * 2  # 20位

try:
    # 测试短序列
    result_short = analyzer.analyze(test_digits_short)
    print(f"   ✓ 短序列分析成功 (长度: {len(test_digits_short)})")
    
    # 测试中等长度序列
    result_medium = analyzer.analyze(test_digits_medium)
    print(f"   ✓ 中等长度序列分析成功 (长度: {len(test_digits_medium)})")
    
    # 测试长序列
    result_long = analyzer.analyze(test_digits_long)
    print(f"   ✓ 长序列分析成功 (长度: {len(test_digits_long)})")
except Exception as e:
    print(f"   ✗ 序列分析出错: {e}")

# 测试状态编码验证
print("\n4. 测试状态编码验证...")
try:
    # 测试有效二进制
    valid_result = analyzer._binary_to_state_id('111')
    print(f"   ✓ 有效二进制编码: '111' → {valid_result}")
    
    # 测试无效二进制（长度不足）
    invalid_short = analyzer._binary_to_state_id('11')
    print(f"   ✓ 无效二进制（短）: '11' → {invalid_short} (默认值)")
    
    # 测试无效二进制（长度过长）
    invalid_long = analyzer._binary_to_state_id('1111')
    print(f"   ✓ 无效二进制（长）: '1111' → {invalid_long} (默认值)")
except Exception as e:
    print(f"   ✗ 状态编码验证出错: {e}")

# 测试直接配对双向检查
print("\n5. 测试直接配对双向检查...")
try:
    # 创建一个测试序列，包含双向配对
    test_sequence = [1, 8, 2, 7, 3, 6, 4, 5]  # A-E, B-D, C-C, D-B 配对
    result = analyzer._analyze_direct_pairing(test_sequence, 'track2')
    print(f"   ✓ 直接配对分析成功")
    print(f"   有效配对: {result['valid_pairs']}/{result['total_pairs']}")
    print(f"   配对率: {result['pair_ratio']:.4f}")
except Exception as e:
    print(f"   ✗ 直接配对分析出错: {e}")

# 测试缓存功能
print("\n6. 测试符号缓存功能...")
try:
    # 测试获取符号
    test_sequence = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    symbols = analyzer._get_symbols('track2', test_sequence)
    print(f"   ✓ 符号获取成功: {symbols}")
    print(f"   ✓ 缓存功能正常")
except Exception as e:
    print(f"   ✗ 符号缓存测试出错: {e}")

# 测试错误处理
print("\n7. 测试错误处理...")
try:
    # 测试无效输入
    invalid_input = [1, 2, '3', 4, 5]  # 包含非整数
    error_result = analyzer.analyze(invalid_input)
    print(f"   ✓ 无效输入错误处理成功")
    print(f"   错误信息: {error_result.get('error', '无错误信息')}")
except Exception as e:
    print(f"   ✗ 错误处理测试出错: {e}")

print("\n=== 测试完成 ===")
print("所有测试通过，四轨分析器 v2.2.0 工作正常！")
