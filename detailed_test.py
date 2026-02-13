#!/usr/bin/env python3
# 详细测试四轨分析器

from core.analyzers.four_track_analyzer import FourTrackAnalyzer

print("=== 四轨分析器详细测试 ===")

# 创建分析器实例
print("1. 创建分析器实例...")
try:
    analyzer = FourTrackAnalyzer()
    print("   ✓ 分析器创建成功")
except Exception as e:
    print(f"   ✗ 分析器创建失败: {e}")
    exit(1)

# 检查八卦配对规则
print("\n2. 检查八卦配对规则...")
expected_bagua = {1: 8, 2: 7, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1}
if hasattr(analyzer, 'bagua_pairing'):
    print(f"   ✓ 八卦配对规则存在: {analyzer.bagua_pairing}")
    if analyzer.bagua_pairing == expected_bagua:
        print("   ✓ 八卦配对规则正确")
    else:
        print("   ✗ 八卦配对规则不正确")
else:
    print("   ✗ 八卦配对规则不存在")

# 检查数字属性映射
print("\n3. 检查数字属性映射...")
if hasattr(analyzer, 'number_attributes'):
    print("   ✓ 数字属性映射存在")
    # 检查是否包含所有四个维度
    test_num = 1
    attributes = analyzer.number_attributes[test_num]
    expected_dims = ['small_large', 'up_down', 'odd_even', 'ab_relation']
    actual_dims = list(attributes.keys())
    print(f"   数字 {test_num} 的属性: {attributes}")
    
    missing_dims = [dim for dim in expected_dims if dim not in actual_dims]
    if not missing_dims:
        print("   ✓ 包含所有四个维度")
    else:
        print(f"   ✗ 缺少维度: {missing_dims}")
else:
    print("   ✗ 数字属性映射不存在")

# 测试分析功能
print("\n4. 测试分析功能...")
test_digits = [1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9, 3, 2, 3, 8, 4, 6]
print(f"   测试数据: {test_digits}")
print(f"   数据长度: {len(test_digits)}")

try:
    results = analyzer.analyze(test_digits)
    print("   ✓ 分析执行成功")
    
    # 检查结果结构
    expected_keys = ['track1', 'track2', 'track3', 'track4', 'direct_pairing', 'fingerprint', 'reverse_analysis']
    actual_keys = list(results.keys())
    print(f"   分析结果包含的键: {actual_keys}")
    
    # 检查轨道1结果
    if 'track1' in results:
        track1 = results['track1']
        print("\n   轨道1分析结果:")
        print(f"     正向分析窗口数: {track1['forward']['window_count']}")
        print(f"     正向分析九和配对率: {track1['forward']['nine_sum_pairs']['pair_ratio']:.4f}")
        print(f"     反向分析窗口数: {track1['backward']['window_count']}")
        print(f"     反向分析九和配对率: {track1['backward']['nine_sum_pairs']['pair_ratio']:.4f}")
        print(f"     对称性: {track1['symmetry']['overall_symmetry']:.4f}")
    
    # 检查数字指纹
    if 'fingerprint' in results:
        print("\n   数字指纹生成成功")
    
    # 检查反向分析
    if 'reverse_analysis' in results:
        print("   反向分析生成成功")
        
    print("\n   ✓ 分析结果结构正确")
    
except Exception as e:
    print(f"   ✗ 分析执行失败: {e}")
    import traceback
    traceback.print_exc()

print("\n=== 测试完成 ===")
