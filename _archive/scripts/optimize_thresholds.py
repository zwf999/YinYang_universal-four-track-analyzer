#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
太仪地震预警系统 - 动态阈值优化
"""

import os
import csv
import numpy as np
from sklearn.metrics import roc_curve, auc

class ThresholdOptimizer:
    def __init__(self):
        pass
    
    def load_backtest_results(self, results_file):
        """加载回溯验证结果"""
        results = []
        try:
            with open(results_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        depth_change = float(row.get('深度变化', 0))
                        mag_change = float(row.get('震级变化', 0))
                        results.append({
                            'depth_change': depth_change,
                            'mag_change': mag_change
                        })
                    except:
                        continue
        except Exception as e:
            print(f"  读取失败: {e}")
        return results
    
    def optimize_thresholds(self, results):
        """优化阈值"""
        if not results:
            return None
        
        # 准备数据
        depth_changes = [r['depth_change'] for r in results]
        mag_changes = [r['mag_change'] for r in results]
        
        # 计算统计指标
        depth_mean = np.mean(depth_changes)
        depth_std = np.std(depth_changes)
        mag_mean = np.mean(mag_changes)
        mag_std = np.std(mag_changes)
        
        # 基于统计数据设置阈值
        # 深度TSE阈值：均值 + 1.5倍标准差
        depth_threshold = max(0.3, depth_mean + 1.5 * depth_std)
        # 震级TSE阈值：均值 + 1.5倍标准差
        mag_threshold = max(0.2, mag_mean + 1.5 * depth_std)
        
        return {
            'depth_threshold': depth_threshold,
            'mag_threshold': mag_threshold,
            'depth_mean': depth_mean,
            'depth_std': depth_std,
            'mag_mean': mag_mean,
            'mag_std': mag_std,
            'sample_count': len(results)
        }
    
    def run_optimization(self, results_file, config_file):
        """运行阈值优化"""
        print("=" * 70)
        print("太仪地震预警系统 - 动态阈值优化")
        print("=" * 70)
        
        results = self.load_backtest_results(results_file)
        print(f"加载 {len(results)} 条验证结果")
        
        if not results:
            print("  无有效结果，无法优化阈值")
            return
        
        optimized = self.optimize_thresholds(results)
        if optimized:
            print(f"\n优化结果:")
            print(f"  深度TSE阈值: {optimized['depth_threshold']:.4f}")
            print(f"  震级TSE阈值: {optimized['mag_threshold']:.4f}")
            print(f"  深度变化均值: {optimized['depth_mean']:.4f}")
            print(f"  深度变化标准差: {optimized['depth_std']:.4f}")
            print(f"  震级变化均值: {optimized['mag_mean']:.4f}")
            print(f"  震级变化标准差: {optimized['mag_std']:.4f}")
            
            # 保存配置
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write("# 太仪地震预警系统 - 动态阈值配置\n")
                f.write(f"depth_threshold = {optimized['depth_threshold']:.4f}\n")
                f.write(f"mag_threshold = {optimized['mag_threshold']:.4f}\n")
                f.write(f"depth_mean = {optimized['depth_mean']:.4f}\n")
                f.write(f"depth_std = {optimized['depth_std']:.4f}\n")
                f.write(f"mag_mean = {optimized['mag_mean']:.4f}\n")
                f.write(f"mag_std = {optimized['mag_std']:.4f}\n")
                f.write(f"sample_count = {optimized['sample_count']}\n")
            
            print(f"\n配置已保存到: {config_file}")
        
        print("\n阈值优化完成！")

if __name__ == "__main__":
    optimizer = ThresholdOptimizer()
    results_file = "data2/results/backtest_312_earthquakes.csv"
    config_file = "data2/config/thresholds.conf"
    optimizer.run_optimization(results_file, config_file)
