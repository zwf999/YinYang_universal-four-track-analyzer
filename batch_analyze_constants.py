#!/usr/bin/env python3
# 批量分析所有常数

import os
import json
import time
from typing import Dict, List, Any
from core.data.data_manager import DataManager
from core.analyzers.composite_analyzer import CompositeAnalyzer

class BatchAnalyzer:
    def __init__(self):
        """初始化批量分析器"""
        self.data_manager = DataManager()
        self.analyzer = CompositeAnalyzer()
        self.results_dir = 'analysis_results'
        
        # 创建结果目录
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)
            print(f"创建结果目录: {self.results_dir}")
    
    def get_available_constants(self) -> List[str]:
        """获取所有可用常数"""
        print("获取可用常数...")
        constants_info = self.data_manager.list_constants()
        constant_names = [const['name'] for const in constants_info]
        print(f"找到 {len(constant_names)} 个可用常数")
        return constant_names
    
    def analyze_constant(self, constant_name: str, max_digits: int = 10000) -> Dict[str, Any]:
        """分析单个常数"""
        try:
            # 加载常数
            digits = self.data_manager.load_constant(constant_name, max_digits)
            if not digits:
                print(f"❌ 无法加载常数: {constant_name}")
                return None
            
            # 分析常数
            start_time = time.time()
            result = self.analyzer.analyze(digits)
            analysis_time = time.time() - start_time
            
            # 添加分析时间
            result['analysis_time'] = analysis_time
            
            print(f"✅ 分析完成: {constant_name} (耗时: {analysis_time:.2f}秒)")
            return result
        except Exception as e:
            print(f"❌ 分析失败: {constant_name} - {str(e)}")
            return None
    
    def save_result(self, constant_name: str, result: Dict[str, Any]):
        """保存分析结果"""
        if result:
            filename = os.path.join(self.results_dir, f"{constant_name}_analysis.json")
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"📄 保存结果: {filename}")
    
    def generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成汇总报告"""
        summary = {
            'total_constants': len(results),
            'successful_analyses': sum(1 for r in results.values() if r is not None),
            'failed_analyses': sum(1 for r in results.values() if r is None),
            'constants': {},
            'statistics': {
                'average_analysis_time': 0,
                'average_randomness': 0,
                'average_symmetry': 0,
                'average_predictability': 0,
                'average_score': 0
            }
        }
        
        total_time = 0
        total_randomness = 0
        total_symmetry = 0
        total_predictability = 0
        total_score = 0
        valid_results = 0
        
        for constant_name, result in results.items():
            if result:
                # 提取关键指标
                stats = {
                    'analysis_time': result.get('analysis_time', 0),
                    'length': result.get('statistical', {}).get('total_digits', 0),
                    'entropy': result.get('statistical', {}).get('entropy', 0),
                    'randomness': result.get('scores', {}).get('randomness', 0),
                    'symmetry': result.get('scores', {}).get('symmetry', 0),
                    'predictability': result.get('scores', {}).get('predictability', 0),
                    'total_score': result.get('scores', {}).get('total_score', 0)
                }
                
                # 提取四轨分析结果
                four_track = {}
                if 'four_track' in result:
                    for i in range(1, 5):
                        track = result['four_track'].get(f'track{i}', {})
                        if 'forward' in track and 'backward' in track and 'symmetry' in track:
                            # 对于轨道1，使用符号配对率
                            if i == 1:
                                forward_ratio = track['forward'].get('symbol_pairs', {}).get('pair_ratio', 0)
                                backward_ratio = track['backward'].get('symbol_pairs', {}).get('pair_ratio', 0)
                            else:
                                # 对于轨道2-4，使用全局数字配对率
                                forward_ratio = track['forward'].get('global_digit_pairs', {}).get('pair_ratio', 0)
                                backward_ratio = track['backward'].get('global_digit_pairs', {}).get('pair_ratio', 0)
                            symmetry = track['symmetry'].get('overall_symmetry', 0)
                            four_track[f'track{i}'] = {
                                'forward_ratio': forward_ratio,
                                'backward_ratio': backward_ratio,
                                'symmetry': symmetry
                            }
                
                summary['constants'][constant_name] = {
                    'statistics': stats,
                    'four_track': four_track
                }
                
                # 累积统计数据
                total_time += stats['analysis_time']
                total_randomness += stats['randomness']
                total_symmetry += stats['symmetry']
                total_predictability += stats['predictability']
                total_score += stats['total_score']
                valid_results += 1
        
        # 计算平均值
        if valid_results > 0:
            summary['statistics']['average_analysis_time'] = total_time / valid_results
            summary['statistics']['average_randomness'] = total_randomness / valid_results
            summary['statistics']['average_symmetry'] = total_symmetry / valid_results
            summary['statistics']['average_predictability'] = total_predictability / valid_results
            summary['statistics']['average_score'] = total_score / valid_results
        
        return summary
    
    def save_summary(self, summary: Dict[str, Any]):
        """保存汇总报告"""
        filename = os.path.join(self.results_dir, 'summary_report.json')
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        print(f"📄 保存汇总报告: {filename}")
        
        # 生成文本报告
        text_filename = os.path.join(self.results_dir, 'summary_report.txt')
        with open(text_filename, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("常数分析汇总报告\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"总常数数量: {summary['total_constants']}\n")
            f.write(f"成功分析: {summary['successful_analyses']}\n")
            f.write(f"分析失败: {summary['failed_analyses']}\n\n")
            
            f.write("平均统计指标:\n")
            f.write(f"  分析时间: {summary['statistics']['average_analysis_time']:.2f}秒\n")
            f.write(f"  随机性: {summary['statistics']['average_randomness']:.4f}\n")
            f.write(f"  对称性: {summary['statistics']['average_symmetry']:.4f}\n")
            f.write(f"  可预测性: {summary['statistics']['average_predictability']:.4f}\n")
            f.write(f"  总体评分: {summary['statistics']['average_score']:.4f}\n\n")
            
            f.write("各常数分析结果:\n")
            f.write("-" * 80 + "\n")
            
            for constant_name, data in summary['constants'].items():
                stats = data['statistics']
                f.write(f"\n{constant_name}:\n")
                f.write(f"  长度: {stats['length']}\n")
                f.write(f"  熵值: {stats['entropy']:.4f}\n")
                f.write(f"  随机性: {stats['randomness']:.4f}\n")
                f.write(f"  对称性: {stats['symmetry']:.4f}\n")
                f.write(f"  可预测性: {stats['predictability']:.4f}\n")
                f.write(f"  总体评分: {stats['total_score']:.4f}\n")
                f.write(f"  分析时间: {stats['analysis_time']:.2f}秒\n")
                
                # 四轨分析结果
                four_track = data['four_track']
                if four_track:
                    f.write("  四轨配对率: ")
                    ratios = []
                    for track_num, track_data in four_track.items():
                        ratio = track_data['forward_ratio']
                        ratios.append(f"{track_num}:{ratio:.4f}")
                    f.write(", ".join(ratios) + "\n")
        
        print(f"📄 保存文本报告: {text_filename}")
    
    def run_batch_analysis(self, max_digits: int = 10000):
        """运行批量分析"""
        print("=" * 80)
        print("批量分析所有常数")
        print("=" * 80)
        
        start_time = time.time()
        
        # 获取可用常数
        constant_names = self.get_available_constants()
        
        # 分析每个常数
        results = {}
        for i, constant_name in enumerate(constant_names, 1):
            print(f"\n[{i}/{len(constant_names)}] 分析: {constant_name}")
            result = self.analyze_constant(constant_name, max_digits)
            results[constant_name] = result
            
            # 保存结果
            if result:
                self.save_result(constant_name, result)
        
        # 生成汇总报告
        print("\n生成汇总报告...")
        summary = self.generate_summary(results)
        self.save_summary(summary)
        
        total_time = time.time() - start_time
        print("\n" + "=" * 80)
        print(f"批量分析完成！")
        print(f"总耗时: {total_time:.2f}秒")
        print(f"分析常数数量: {len(constant_names)}")
        print(f"成功分析: {summary['successful_analyses']}")
        print(f"分析失败: {summary['failed_analyses']}")
        print(f"结果保存目录: {self.results_dir}")
        print("=" * 80)

if __name__ == "__main__":
    batch_analyzer = BatchAnalyzer()
    batch_analyzer.run_batch_analysis()
