#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试方向标记功能 - 左箭头标注反序
"""

from dna_encoder import DNAEncoder
from dna_four_track_enhanced import DNAEncoder as FourTrackDNAEncoder
from dna_universal_analyzer import UniversalEncoder

def test_direction_marks():
    print("=" * 60)
    print("测试方向标记功能 - 左箭头标注反序")
    print("=" * 60)
    
    # 测试序列
    test_sequences = [
        "ATCG",          # 正序
        "GTCA",          # 反序
        "ATCGAT",        # 混合顺序
        "GCATGCAT",      # 混合模式
        "GGGG",          # 相同碱基（正序）
        "TTTT",          # 相同碱基（正序）
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
        direction_flags = encoded.get('direction_flags', [])
        details = encoded.get('encoding_details', [])
        
        print(f"编码结果: {digits}")
        print(f"方向标记: {direction_flags}")
        
        # 检查方向标记
        has_arrow = any(flag == '←' for flag in direction_flags)
        print(f"包含左箭头标记: {has_arrow}")
        
        # 显示详细信息
        print("编码详情:")
        for i, detail in enumerate(details):
            bases = detail.get('bases', detail.get('base', ''))
            code = detail.get('code')
            direction = detail.get('direction')
            direction_mark = detail.get('direction_mark', '')
            print(f"  {i}: {bases} → {code}{direction_mark} ({direction})")
        
        # 解码
        decoded = encoder.decode(encoded)
        print(f"解码结果: {decoded}")
        print(f"解码正确: {decoded == seq}")
    
    print("\n2. 测试 dna_four_track_enhanced.py")
    print("-" * 40)
    
    four_track_encoder = FourTrackDNAEncoder()
    
    for seq in test_sequences:
        print(f"\n测试序列: {seq}")
        
        # 编码
        encoded = four_track_encoder.encode(seq)
        digits = encoded['digits']
        details = encoded.get('details', [])
        
        print(f"编码结果: {digits}")
        
        # 检查方向标记
        has_arrow = any(detail.get('direction_mark') == '←' for detail in details)
        print(f"包含左箭头标记: {has_arrow}")
        
        # 显示详细信息
        print("编码详情:")
        for i, detail in enumerate(details):
            bases = detail.get('bases', detail.get('base', ''))
            code = detail.get('code')
            direction = detail.get('direction')
            direction_mark = detail.get('direction_mark', '')
            print(f"  {i}: {bases} → {code}{direction_mark} ({direction})")
        
        # 解码
        decoded = four_track_encoder.decode(encoded)
        print(f"解码结果: {decoded}")
        print(f"解码正确: {decoded == seq}")
    
    print("\n3. 测试 dna_universal_analyzer.py")
    print("-" * 40)
    
    universal_encoder = UniversalEncoder()
    
    for seq in test_sequences:
        print(f"\n测试序列: {seq}")
        
        # 编码
        encoded = universal_encoder.encode_dna(seq)
        digits = encoded['digits']
        details = encoded.get('details', [])
        
        print(f"编码结果: {digits}")
        
        # 检查方向标记
        has_arrow = any(detail.get('direction_mark') == '←' for detail in details)
        print(f"包含左箭头标记: {has_arrow}")
        
        # 显示详细信息
        print("编码详情:")
        for i, detail in enumerate(details):
            bases = detail.get('bases', detail.get('base', ''))
            code = detail.get('code')
            direction = detail.get('direction')
            direction_mark = detail.get('direction_mark', '')
            print(f"  {i}: {bases} → {code}{direction_mark} ({direction})")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)

if __name__ == "__main__":
    test_direction_marks()
