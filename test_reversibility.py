#!/usr/bin/env python3
"""
测试DNA编码和解码的可逆性
"""

from dna_encoder import DNAEncoder

# 创建编码器实例
encoder = DNAEncoder()

# 测试序列1
print("测试序列1: ACGTACGT")
result1 = encoder.encode('ACGTACGT')
print('编码结果:', result1['encoded_digits'])
print('编码详情:', result1['encoding_details'])
decoded1 = encoder.decode(result1)
print('解码结果:', decoded1)
print('解码是否正确:', decoded1 == 'ACGTACGT')
print()

# 测试序列2
print("测试序列2: AATTCCGG")
result2 = encoder.encode('AATTCCGG')
print('编码结果:', result2['encoded_digits'])
print('编码详情:', result2['encoding_details'])
decoded2 = encoder.decode(result2)
print('解码结果:', decoded2)
print('解码是否正确:', decoded2 == 'AATTCCGG')
print()

# 测试序列3
print("测试序列3: ATGCGCTA")
result3 = encoder.encode('ATGCGCTA')
print('编码结果:', result3['encoded_digits'])
print('编码详情:', result3['encoding_details'])
decoded3 = encoder.decode(result3)
print('解码结果:', decoded3)
print('解码是否正确:', decoded3 == 'ATGCGCTA')
print()

# 测试序列4（较长序列）
print("测试序列4: ACGTACGTACGTACGT")
result4 = encoder.encode('ACGTACGTACGTACGT')
print('编码结果:', result4['encoded_digits'])
decoded4 = encoder.decode(result4)
print('解码结果:', decoded4)
print('解码是否正确:', decoded4 == 'ACGTACGTACGTACGT')
print()

print("所有测试完成！")
