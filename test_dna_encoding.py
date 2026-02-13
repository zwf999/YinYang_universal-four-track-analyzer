# test_dna_encoding.py
# 测试 DNA 编码功能

from dna_encoder import DNAEncoder
from core.data.data_manager import DataManager


def test_dna_encoder():
    """测试 DNA 编码器"""
    print("测试 DNA 编码器...")
    
    encoder = DNAEncoder()
    
    # 测试 DNA 编码
    test_sequences = [
        "ACGTACGT",
        "AAAA",
        "TTTT",
        "ACGT",
        "AGCT",
        "ACGTACGTACGT"
    ]
    
    for seq in test_sequences:
        print(f"\n测试序列: {seq}")
        result = encoder.encode(seq)
        print(f"编码结果: {result['encoded_digits']}")
        print(f"编码方案: {result['encoding_scheme']}")
        print(f"统计信息: {result['stats']}")
        
        # 测试解码
        decoded_seq = encoder.decode(result)
        print(f"解码结果: {decoded_seq}")
        print(f"解码是否正确: {decoded_seq == seq}")


def test_data_manager_dna():
    """测试数据管理器的 DNA 处理功能"""
    print("\n\n测试数据管理器的 DNA 处理功能...")
    
    data_manager = DataManager()
    
    # 测试 DNA 序列检测
    test_cases = [
        "ACGTACGT",  # 是 DNA 序列
        "pi",        # 不是 DNA 序列
        "e",         # 不是 DNA 序列
        "TTTT",      # 是 DNA 序列
        "AGCTAGCT",  # 是 DNA 序列
    ]
    
    for case in test_cases:
        is_dna = data_manager._is_dna_sequence(case)
        print(f"{case}: {'是 DNA 序列' if is_dna else '不是 DNA 序列'}")
    
    # 测试 DNA 编码
    dna_seq = "ACGTACGTACGT"
    print(f"\n测试 DNA 编码: {dna_seq}")
    encoded_digits = data_manager.encode_dna(dna_seq)
    print(f"编码结果: {encoded_digits}")
    
    # 测试通过 load_constant 加载 DNA 序列
    print(f"\n测试通过 load_constant 加载 DNA 序列")
    loaded_digits = data_manager.load_constant(dna_seq, max_digits=20)
    print(f"加载结果: {loaded_digits}")


if __name__ == "__main__":
    test_dna_encoder()
    test_data_manager_dna()
    print("\n所有测试完成！")
