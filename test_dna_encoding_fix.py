#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修改后的DNA编码程序
"""

from dna_encoder import DNAEncoder
from dna_four_track_enhanced import DNAEncoder as FourTrackDNAEncoder

def test_encoding_fix():
    print("=" * 60)
    print("测试修改后的DNA编码程序")
    print("=" * 60)
    
    # 测试序列
    test_sequences = [
        "ATCG",          # 偶数长度
        "ATCGA",         # 奇数长度（测试单个碱基）
        "GGGG",          # 相同碱基
        "ATATAT",        # 重复模式
        "GCATGCAT",      # 混合序列
    ]
    
    print("\n1. 测试 dna_encoder.py")
    print("-" * 40)
    
    encoder = DNAEncoder(encoding_scheme='triangle')
    
    for seq in test_sequences:
        print(f"\n测试序列: {seq}")
        print(f"长度: {len(seq)}")
        
        # 编码
        encoded = encoder.encode(seq)
        digits = encoded['encoded_digits']
        print(f"编码结果: {digits}")
        
        # 检查数字范围
        min_digit = min(digits) if digits else 0
        max_digit = max(digits) if digits else 0
        print(f"数字范围: {min_digit}-{max_digit}")
        
        if min_digit < 0 or max_digit > 9:
            print("❌ 错误: 数字超出0-9范围")
        else:
            print("✅ 数字在0-9范围内")
        
        # 检查方向标记
        direction_flags = encoded.get('direction_flags', [])
        print(f"方向标记: {direction_flags}")
        has_negative = any(flag == -1 for flag in direction_flags)
        print(f"包含负号标记: {has_negative}")
        
        # 解码
        decoded = encoder.decode(encoded)
        print(f"解码结果: {decoded}")
        print(f"解码正确: {decoded == seq}")
    
    print("\n2. 测试 dna_four_track_enhanced.py")
    print("-" * 40)
    
    four_track_encoder = FourTrackDNAEncoder()
    
    for seq in test_sequences:
        print(f"\n测试序列: {seq}")
        print(f"长度: {len(seq)}")
        
        # 编码
        encoded = four_track_encoder.encode(seq)
        digits = encoded['digits']
        print(f"编码结果: {digits}")
        
        # 检查数字范围
        min_digit = min(digits) if digits else 0
        max_digit = max(digits) if digits else 0
        print(f"数字范围: {min_digit}-{max_digit}")
        
        if min_digit < 0 or max_digit > 9:
            print("❌ 错误: 数字超出0-9范围")
        else:
            print("✅ 数字在0-9范围内")
        
        # 检查方向信息
        details = encoded.get('details', [])
        directions = [d.get('direction') for d in details]
        print(f"方向信息: {directions}")
        has_reverse = any(d == 'reverse' for d in directions)
        print(f"包含反向标记: {has_reverse}")
        
        # 解码
        decoded = four_track_encoder.decode(encoded)
        print(f"解码结果: {decoded}")
        print(f"解码正确: {decoded == seq}")
    
    print("\n3. 批量测试DNA文件")
    print("-" * 40)
    
    # 测试一个实际的DNA文件
    test_file = "data/dna/healthy_NM_000014_1000000.txt"
    try:
        with open(test_file, 'r') as f:
            long_seq = f.read().strip()[:100]  # 只取前100个碱基测试
        
        print(f"测试长序列（前100个碱基）: {long_seq}")
        
        # 编码
        encoded = encoder.encode(long_seq)
        digits = encoded['encoded_digits']
        print(f"编码结果长度: {len(digits)}")
        print(f"前20个数字: {digits[:20]}")
        
        # 检查数字范围
        min_digit = min(digits) if digits else 0
        max_digit = max(digits) if digits else 0
        print(f"数字范围: {min_digit}-{max_digit}")
        
        if min_digit < 0 or max_digit > 9:
            print("❌ 错误: 数字超出0-9范围")
        else:
            print("✅ 数字在0-9范围内")
        
        # 解码
        decoded = encoder.decode(encoded)
        print(f"解码结果长度: {len(decoded)}")
        print(f"解码正确: {decoded == long_seq}")
        
    except Exception as e:
        print(f"文件测试失败: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)

if __name__ == "__main__":
    test_encoding_fix()
