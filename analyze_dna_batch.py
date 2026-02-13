#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量分析DNA数据的非交互式脚本
"""

import json
import os
from dna_four_track_enhanced import DNAFourTrackSystem

def main():
    print("=" * 60)
    print("批量分析DNA数据")
    print("=" * 60)
    
    # 创建分析系统
    system = DNAFourTrackSystem()
    
    # 加载默认目录中的DNA文件
    directory = "data/dna"
    print(f"从目录加载DNA文件: {directory}")
    
    if not os.path.exists(directory):
        print(f"❌ 目录不存在: {directory}")
        return
    
    try:
        sequences = system.load_from_directory(directory)
        if sequences:
            print(f"找到 {len(sequences)} 个DNA文件:")
            for i, filename in enumerate(sequences.keys(), 1):
                print(f"  {i}. {filename}")
            
            print("\n开始批量分析...")
            results = system.batch_analyze(sequences)
            
            # 保存结果
            output_file = "batch_directory_results.json"
            if system.save_results(results, output_file):
                print(f"✅ 结果已保存到 {output_file}")
                
                # 打印分析摘要
                print("\n📊 分析摘要:")
                if '_comparison' in results:
                    comp = results['_comparison']
                    print(f"  GC含量范围: {comp['gc_stats']['min']:.3f}-{comp['gc_stats']['max']:.3f}")
                    print(f"  平均GC含量: {comp['gc_stats']['avg']:.3f}")
                    
                    if comp['similar_groups']:
                        print("  相似组:")
                        for group in comp['similar_groups']:
                            print(f"    {group['group']}: {', '.join(group['sequences'])}")
            
        else:
            print(f"❌ 目录中没有找到有效的DNA文件")
    except Exception as e:
        print(f"❌ 分析失败: {e}")

if __name__ == "__main__":
    main()
