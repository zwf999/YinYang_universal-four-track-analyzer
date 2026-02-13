# analyze_dna_simple.py
# 简化版DNA分析脚本（快速分析）

import os
import sys
from core.data.data_manager import DataManager
from core.analyzers.composite_analyzer import CompositeAnalyzer


def analyze_dna_file_simple(file_path):
    """
    简化版分析DNA文件
    
    Args:
        file_path: DNA文件路径
        
    Returns:
        分析结果
    """
    print(f"\n=== 分析文件: {os.path.basename(file_path)} ===")
    
    # 读取DNA序列
    try:
        with open(file_path, 'r') as f:
            dna_sequence = f.read().strip()
        
        # 只使用前10万位DNA序列
        dna_sequence = dna_sequence[:100000]
        print(f"DNA序列长度: {len(dna_sequence)}")
        print(f"前50个碱基: {dna_sequence[:50]}...")
        
        # 创建数据管理器
        data_manager = DataManager()
        
        # 编码DNA序列
        print("\n正在编码DNA序列...")
        encoded_digits = data_manager.encode_dna(dna_sequence)
        print(f"编码后长度: {len(encoded_digits)}")
        print(f"前20个编码数字: {encoded_digits[:20]}...")
        
        # 只分析前1万位编码结果
        encoded_digits = encoded_digits[:10000]
        print(f"分析前 {len(encoded_digits)} 位编码结果...")
        
        # 创建分析器
        analyzer = CompositeAnalyzer()
        
        # 分析编码后的数字序列
        print("\n正在分析编码后的序列...")
        result = analyzer.analyze(encoded_digits)
        
        # 显示分析结果
        display_analysis_result(result)
        
        return result
        
    except Exception as e:
        print(f"分析失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def display_analysis_result(result):
    """
    显示分析结果
    
    Args:
        result: 分析结果字典
    """
    print("\n=== 分析结果 ===")
    
    # 统计分析
    if 'statistical' in result:
        stats = result['statistical']
        print("\n统计分析:")
        print(f"  长度: {stats.get('total_digits', 0)}")
        print(f"  平均值: {stats.get('mean', 0):.4f}")
        print(f"  标准差: {stats.get('std', 0):.4f}")
        print(f"  熵值: {stats.get('entropy', 0):.4f}")
    
    # 综合评分
    if 'scores' in result:
        scores = result['scores']
        print("\n综合评分:")
        print(f"  随机性: {scores.get('randomness', 0):.4f}")
        print(f"  模式复杂度: {scores.get('pattern_complexity', 0):.4f}")
        print(f"  对称性: {scores.get('symmetry', 0):.4f}")
        print(f"  可预测性: {scores.get('predictability', 0):.4f}")
        print(f"  总体评分: {scores.get('overall', 0):.4f}")


def analyze_all_dna_files_simple(directory):
    """
    分析目录中的所有DNA文件（简化版）
    
    Args:
        directory: DNA文件目录
    """
    print(f"\n=== 分析目录中的所有DNA文件: {directory} ===")
    
    # 获取目录中的所有文件
    files = []
    for filename in os.listdir(directory):
        if filename.endswith('.txt') and (filename.startswith('healthy_') or filename.startswith('cancer_')):
            files.append(os.path.join(directory, filename))
    
    # 按类型排序
    healthy_files = [f for f in files if f.startswith(os.path.join(directory, 'healthy_'))]
    cancer_files = [f for f in files if f.startswith(os.path.join(directory, 'cancer_'))]
    
    print(f"\n找到 {len(healthy_files)} 个健康基因文件")
    print(f"找到 {len(cancer_files)} 个癌症基因文件")
    
    # 分析健康基因文件
    print("\n" + "="*60)
    print("分析健康基因文件")
    print("="*60)
    healthy_results = []
    for file in healthy_files[:1]:  # 只分析1个健康基因文件
        result = analyze_dna_file_simple(file)
        if result:
            healthy_results.append(result)
    
    # 分析癌症基因文件
    print("\n" + "="*60)
    print("分析癌症基因文件")
    print("="*60)
    cancer_results = []
    for file in cancer_files[:1]:  # 只分析1个癌症基因文件
        result = analyze_dna_file_simple(file)
        if result:
            cancer_results.append(result)
    
    # 比较分析结果
    compare_results(healthy_results, cancer_results)


def compare_results(healthy_results, cancer_results):
    """
    比较健康和癌症基因的分析结果
    
    Args:
        healthy_results: 健康基因分析结果列表
        cancer_results: 癌症基因分析结果列表
    """
    print("\n" + "="*60)
    print("健康 vs 癌症基因分析结果比较")
    print("="*60)
    
    if not healthy_results or not cancer_results:
        print("没有足够的分析结果进行比较")
        return
    
    # 计算健康基因的平均评分
    healthy_scores = []
    for result in healthy_results:
        if 'scores' in result:
            healthy_scores.append(result['scores'])
    
    # 计算癌症基因的平均评分
    cancer_scores = []
    for result in cancer_results:
        if 'scores' in result:
            cancer_scores.append(result['scores'])
    
    # 计算平均值
    def calculate_average(scores_list):
        if not scores_list:
            return {}
        
        avg_scores = {}
        score_keys = scores_list[0].keys()
        
        for key in score_keys:
            values = [s.get(key, 0) for s in scores_list]
            avg_scores[key] = sum(values) / len(values)
        
        return avg_scores
    
    healthy_avg = calculate_average(healthy_scores)
    cancer_avg = calculate_average(cancer_scores)
    
    # 显示比较结果
    print("\n平均评分比较:")
    print("{:<15} {:<10} {:<10} {:<10}".format('评分类型', '健康基因', '癌症基因', '差异'))
    print("-" * 45)
    
    score_types = ['randomness', 'pattern_complexity', 'symmetry', 'predictability', 'overall']
    score_names = ['随机性', '模式复杂度', '对称性', '可预测性', '总体评分']
    
    for i, score_type in enumerate(score_types):
        healthy_val = healthy_avg.get(score_type, 0)
        cancer_val = cancer_avg.get(score_type, 0)
        diff = cancer_val - healthy_val
        
        print("{:<15} {:<10.4f} {:<10.4f} {:<10.4f}".format(
            score_names[i], healthy_val, cancer_val, diff
        ))
    
    # 分析差异
    print("\n差异分析:")
    if cancer_avg.get('randomness', 0) > healthy_avg.get('randomness', 0):
        print("✓ 癌症基因序列随机性更高")
    else:
        print("✓ 健康基因序列随机性更高")
    
    if cancer_avg.get('pattern_complexity', 0) > healthy_avg.get('pattern_complexity', 0):
        print("✓ 癌症基因序列模式复杂度更高")
    else:
        print("✓ 健康基因序列模式复杂度更高")
    
    if cancer_avg.get('symmetry', 0) > healthy_avg.get('symmetry', 0):
        print("✓ 癌症基因序列对称性更高")
    else:
        print("✓ 健康基因序列对称性更高")
    
    if cancer_avg.get('predictability', 0) > healthy_avg.get('predictability', 0):
        print("✓ 癌症基因序列可预测性更高")
    else:
        print("✓ 健康基因序列可预测性更高")


if __name__ == "__main__":
    # 分析所有DNA数据文件
    dna_dir = 'data/dna'
    if os.path.exists(dna_dir):
        analyze_all_dna_files_simple(dna_dir)
    else:
        print(f"错误: 目录 {dna_dir} 不存在")
        print("请先运行 get_real_dna_data.py 获取DNA数据")
