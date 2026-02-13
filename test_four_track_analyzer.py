#!/usr/bin/env python3
# 测试四轨分析器

from core.analyzers.four_track_analyzer import FourTrackAnalyzer

# 创建分析器实例
analyzer = FourTrackAnalyzer()

# 测试数据：π的前30位小数
test_digits = [1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9, 3, 2, 3, 8, 4, 6, 2, 6, 4, 3, 3, 8, 3, 2, 7, 9]

print("测试四轨分析器")
print("测试数据:", test_digits)
print("数据长度:", len(test_digits))
print()

# 执行分析
results = analyzer.analyze(test_digits)

# 打印分析结果
print("=== 分析结果 ===")
for track, track_result in results.items():
    if track not in ['direct_pairing', 'fingerprint', 'reverse_analysis']:
        print(f"\n轨道 {track}:")
        forward = track_result['forward']
        backward = track_result['backward']
        symmetry = track_result['symmetry']
        
        print(f"  正向分析:")
        print(f"    窗口数量: {forward['window_count']}")
        print(f"    九和配对率: {forward['nine_sum_pairs']['pair_ratio']:.4f}")
        print(f"    有效配对: {forward['nine_sum_pairs']['valid_pairs']}/{forward['nine_sum_pairs']['total_pairs']}")
        print(f"    阴阳比例: 阳{forward['yinyang']['yang_count']}:阴{forward['yinyang']['yin_count']}")
        print(f"    阳占比: {forward['yinyang']['yang_percent']:.4f}")
        
        print(f"  反向分析:")
        print(f"    窗口数量: {backward['window_count']}")
        print(f"    九和配对率: {backward['nine_sum_pairs']['pair_ratio']:.4f}")
        print(f"    有效配对: {backward['nine_sum_pairs']['valid_pairs']}/{backward['nine_sum_pairs']['total_pairs']}")
        print(f"    阴阳比例: 阳{backward['yinyang']['yang_count']}:阴{backward['yinyang']['yin_count']}")
        print(f"    阳占比: {backward['yinyang']['yang_percent']:.4f}")
        
        print(f"  对称性:")
        print(f"    整体对称性: {symmetry['overall_symmetry']:.4f}")
        print(f"    配对率相似度: {symmetry['pair_ratio_similarity']:.4f}")
        print(f"    阳占比相似度: {symmetry['yang_percent_similarity']:.4f}")

print("\n=== 数字指纹 ===")
if 'fingerprint' in results:
    for track, fingerprint in results['fingerprint'].items():
        print(f"\n{track}:")
        print(f"  正向配对率: {fingerprint['forward']['pair_ratio']:.4f}")
        print(f"  反向配对率: {fingerprint['backward']['pair_ratio']:.4f}")
        print(f"  对称性: {fingerprint['symmetry']['overall_symmetry']:.4f}")

print("\n测试完成！")
