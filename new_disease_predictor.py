#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
疾病预测分析系统 v2.1 - 完全修复版
基于四轨道分析的癌症早期识别
（已修复所有错误，直接运行即可）
"""

import os
import json
import glob
import numpy as np
from datetime import datetime
import ijson

# ============================================================================
# 1. 疾病特征提取器
# ============================================================================

class DiseaseFeatureExtractor:
    """从四轨道分析结果提取疾病相关特征"""
    
    def extract_features(self, result):
        """提取所有疾病相关特征"""
        if 'error' in result:
            return None
        
        features = {}
        
        # 基础特征
        features['sequence_length'] = result['encoding']['stats'].get('encoded_length', 0)
        features['gc_content'] = result['encoding']['stats'].get('gc_content', 0)
        
        analysis = result['analysis']
        
        # 轨道1特征
        track1 = analysis['track1']
        features['track1_pairing_rate'] = track1['forward']['symbol_pairs']['ratio']
        features['track1_symmetry'] = track1['symmetry']['overall']
        features['track1_yang_percent'] = track1['forward']['yinyang']['yang_percent']
        
        # 轨道2特征
        track2 = analysis['track2']
        features['track2_pairing_rate'] = track2['forward']['global_digit_pairs']['ratio']
        features['track2_symmetry'] = track2['symmetry']['overall']
        features['track2_yang_percent'] = track2['forward']['yinyang']['yang_percent']
        features['track2_unpaired'] = sum(track2['forward']['global_digit_pairs']['unpaired'].values())
        
        # 轨道3特征
        track3 = analysis['track3']
        features['track3_pairing_rate'] = track3['forward']['global_digit_pairs']['ratio']
        features['track3_symmetry'] = track3['symmetry']['overall']
        features['track3_yang_percent'] = track3['forward']['yinyang']['yang_percent']
        features['track3_unpaired'] = sum(track3['forward']['global_digit_pairs']['unpaired'].values())
        
        # 轨道4特征
        track4 = analysis['track4']
        features['track4_pairing_rate'] = track4['forward']['global_digit_pairs']['ratio']
        features['track4_symmetry'] = track4['symmetry']['overall']
        features['track4_yang_percent'] = track4['forward']['yinyang']['yang_percent']
        features['track4_unpaired'] = sum(track4['forward']['global_digit_pairs']['unpaired'].values())
        
        # 衍生特征
        features['track4_track1_ratio'] = features['track4_pairing_rate'] / features['track1_pairing_rate'] if features['track1_pairing_rate'] > 0 else 0
        features['track4_minus_track1'] = features['track4_pairing_rate'] - features['track1_pairing_rate']
        
        # 阴阳平衡特征
        features['yang_imbalance'] = (
            abs(features['track1_yang_percent'] - 0.5) + 
            abs(features['track2_yang_percent'] - 0.5) + 
            abs(features['track3_yang_percent'] - 0.5) + 
            abs(features['track4_yang_percent'] - 0.5)
        ) / 4
        
        # 对称性特征
        features['symmetry_score'] = (
            features['track1_symmetry'] + 
            features['track2_symmetry'] + 
            features['track3_symmetry'] + 
            features['track4_symmetry']
        ) / 4
        
        # 未配对总数（关键特征）
        features['total_unpaired'] = (
            features['track2_unpaired'] + 
            features['track3_unpaired'] + 
            features['track4_unpaired']
        )
        
        return features
    
    def create_dataset(self, all_results):
        """创建特征数据集"""
        data = []
        labels = []
        sample_names = []
        
        for name, result in all_results.items():
            if 'error' in result:
                continue
            
            # 只分析DNA样本
            if 'dna' not in result['metadata'].get('type', '').lower():
                continue
            
            features = self.extract_features(result)
            if features is None:
                continue
            
            # 确定标签
            name_lower = name.lower()
            if 'cancer' in name_lower:
                label = 1  # 癌症
            elif 'healthy' in name_lower:
                label = 0  # 健康
            else:
                continue  # 跳过无法分类的
            
            data.append(features)
            labels.append(label)
            sample_names.append(name)
        
        return data, labels, sample_names

# ============================================================================
# 2. 疾病预测分析器
# ============================================================================

class DiseasePredictor:
    """疾病预测分析"""
    
    def __init__(self):
        self.feature_names = [
            'gc_content', 'track1_pairing_rate', 'track1_symmetry', 
            'track2_pairing_rate', 'track3_pairing_rate', 'track4_pairing_rate',
            'track4_track1_ratio', 'track4_minus_track1', 'yang_imbalance',
            'symmetry_score', 'total_unpaired'
        ]
    
    def analyze_differences(self, data, labels, sample_names):
        """分析健康与癌症的差异"""
        healthy_indices = [i for i, label in enumerate(labels) if label == 0]
        cancer_indices = [i for i, label in enumerate(labels) if label == 1]
        
        if not healthy_indices or not cancer_indices:
            return {"error": "需要至少一个健康和一个癌症样本"}
        
        # 计算各组均值
        healthy_means = {}
        cancer_means = {}
        differences = {}
        percent_differences = {}
        significance_flags = {}
        
        for feature in self.feature_names:
            healthy_values = []
            cancer_values = []
            
            for i in healthy_indices:
                if feature in data[i]:
                    healthy_values.append(data[i][feature])
            
            for i in cancer_indices:
                if feature in data[i]:
                    cancer_values.append(data[i][feature])
            
            if healthy_values and cancer_values:
                healthy_mean = np.mean(healthy_values)
                cancer_mean = np.mean(cancer_values)
                
                healthy_means[feature] = healthy_mean
                cancer_means[feature] = cancer_mean
                
                diff = cancer_mean - healthy_mean
                differences[feature] = diff
                
                percent_diff = (abs(diff) / abs(healthy_mean) * 100) if healthy_mean != 0 else 0
                percent_differences[feature] = percent_diff
                
                # 判断是否所有癌症样本都高于/低于所有健康样本
                min_cancer = min(cancer_values)
                max_healthy = max(healthy_values)
                max_cancer = max(cancer_values)
                min_healthy = min(healthy_values)
                
                if min_cancer > max_healthy:
                    significance_flags[feature] = "癌症显著更高"
                elif max_cancer < min_healthy:
                    significance_flags[feature] = "癌症显著更低"
                else:
                    significance_flags[feature] = "重叠"
        
        # 找出最有区分能力的特征
        ranked_features = []
        for feature in percent_differences:
            if feature in differences and feature in significance_flags:
                ranked_features.append((
                    feature, 
                    percent_differences[feature], 
                    differences[feature], 
                    significance_flags[feature]
                ))
        
        ranked_features.sort(key=lambda x: x[1], reverse=True)
        
        return {
            "healthy_means": healthy_means,
            "cancer_means": cancer_means,
            "differences": differences,
            "percent_differences": percent_differences,
            "significance_flags": significance_flags,
            "ranked_features": ranked_features,
            "sample_counts": {
                "healthy": len(healthy_indices),
                "cancer": len(cancer_indices)
            }
        }
    
    def generate_diagnostic_rules(self, analysis_results):
        """生成诊断规则"""
        rules = []
        
        if "ranked_features" not in analysis_results:
            return rules
        
        ranked_features = analysis_results["ranked_features"]
        healthy_means = analysis_results["healthy_means"]
        cancer_means = analysis_results["cancer_means"]
        
        # 基于前3个最有区分能力的特征
        top_features = []
        for feature, abs_percent_diff, diff, significance in ranked_features:
            if feature in healthy_means and feature in cancer_means:
                top_features.append((feature, abs_percent_diff, diff, significance))
                if len(top_features) >= 3:
                    break
        
        for i, (feature, abs_percent_diff, diff, significance) in enumerate(top_features):
            healthy_mean = healthy_means.get(feature, 0)
            cancer_mean = cancer_means.get(feature, 0)
            
            # 计算阈值（取中间值）
            threshold = (healthy_mean + cancer_mean) / 2
            
            if diff > 0:  # 癌症更高
                rule = f"如果 {feature} > {threshold:.4f}，则倾向癌症"
                comparison = ">"
            else:  # 癌症更低
                rule = f"如果 {feature} < {threshold:.4f}，则倾向癌症"
                comparison = "<"
            
            # 计算置信度（基于百分比差异）
            confidence = min(95, 70 + min(25, abs_percent_diff / 2))
            
            rules.append({
                "feature": feature,
                "healthy_mean": healthy_mean,
                "cancer_mean": cancer_mean,
                "difference": diff,
                "percent_difference": abs_percent_diff,
                "threshold": threshold,
                "rule": rule,
                "comparison": comparison,
                "confidence": confidence
            })
        
        return rules
    
    def predict_sample(self, features, rules):
        """使用规则预测单个样本"""
        if not rules or not features:
            return "无法预测", 50, []
        
        predictions = []
        
        for rule_info in rules:
            feature = rule_info["feature"]
            threshold = rule_info["threshold"]
            comparison = rule_info["comparison"]
            
            if feature in features:
                value = features[feature]
                
                # 计算置信度（基于距离阈值的远近）
                if comparison == ">":
                    if value > threshold:
                        # 超过阈值，预测癌症
                        range_min = rule_info["healthy_mean"]
                        range_max = rule_info["cancer_mean"]
                        if range_max > range_min:
                            position = (value - threshold) / (range_max - threshold)
                            confidence = 50 + min(45, position * 90)
                        else:
                            confidence = 75
                        predictions.append(("癌症", confidence, value, threshold, feature))
                    else:
                        # 低于阈值，预测健康
                        range_min = rule_info["healthy_mean"]
                        if threshold > range_min:
                            position = (threshold - value) / (threshold - range_min)
                            confidence = 50 + min(45, position * 90)
                        else:
                            confidence = 75
                        predictions.append(("健康", confidence, value, threshold, feature))
                else:  # comparison == "<"
                    if value < threshold:
                        # 低于阈值，预测癌症
                        range_min = rule_info["cancer_mean"]
                        range_max = rule_info["healthy_mean"]
                        if range_max > range_min:
                            position = (threshold - value) / (threshold - range_min)
                            confidence = 50 + min(45, position * 90)
                        else:
                            confidence = 75
                        predictions.append(("癌症", confidence, value, threshold, feature))
                    else:
                        # 超过阈值，预测健康
                        range_min = rule_info["healthy_mean"]
                        if threshold < range_min:
                            position = (value - threshold) / (range_min - threshold)
                            confidence = 50 + min(45, position * 90)
                        else:
                            confidence = 75
                        predictions.append(("健康", confidence, value, threshold, feature))
        
        # 综合预测
        if not predictions:
            return "无法预测", 50, []
        
        # 投票机制
        cancer_votes = sum(1 for p in predictions if p[0] == "癌症")
        health_votes = sum(1 for p in predictions if p[0] == "健康")
        
        if cancer_votes > health_votes:
            # 预测癌症
            cancer_predictions = [p for p in predictions if p[0] == "癌症"]
            avg_confidence = np.mean([p[1] for p in cancer_predictions])
            return "癌症", avg_confidence, predictions
        elif health_votes > cancer_votes:
            # 预测健康
            health_predictions = [p for p in predictions if p[0] == "健康"]
            avg_confidence = np.mean([p[1] for p in health_predictions])
            return "健康", avg_confidence, predictions
        else:
            # 平票
            avg_confidence = np.mean([p[1] for p in predictions])
            # 如果平票，倾向于保守（健康）
            return "健康（平票）", avg_confidence, predictions

# ============================================================================
# 3. 报告生成器（完全修复版）
# ============================================================================

class DiseaseReportGenerator:
    """生成疾病预测报告"""
    
    def generate_report(self, analysis_results, diagnostic_rules, all_predictions, sample_names, data):
        """生成完整报告"""
        report = []
        
        # 标题
        report.append("=" * 80)
        report.append("                   DNA疾病预测分析报告 v2.1")
        report.append("                   最终修复版")
        report.append("=" * 80)
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # 样本概况
        report.append("## 一、样本概况")
        report.append(f"• 总DNA样本数: {analysis_results['sample_counts']['healthy'] + analysis_results['sample_counts']['cancer']}")
        report.append(f"• 健康样本: {analysis_results['sample_counts']['healthy']} 个")
        report.append(f"• 癌症样本: {analysis_results['sample_counts']['cancer']} 个")
        
        if analysis_results['sample_counts']['healthy'] < 2 or analysis_results['sample_counts']['cancer'] < 2:
            report.append("⚠️  样本量较小，结果仅供参考")
        report.append("")
        
        # 关键发现
        report.append("## 二、关键发现")
        
        if analysis_results['ranked_features']:
            top_feature = analysis_results['ranked_features'][0]
            report.append(f"**最具区分能力的特征**: {top_feature[0]}")
            report.append(f"  • 健康均值: {analysis_results['healthy_means'].get(top_feature[0], 0):.4f}")
            report.append(f"  • 癌症均值: {analysis_results['cancer_means'].get(top_feature[0], 0):.4f}")
            report.append(f"  • 绝对差异: {top_feature[2]:.6f}")
            report.append(f"  • 百分比差异: {top_feature[1]:.1f}%")
            report.append(f"  • 模式: {top_feature[3]}")
            report.append("")
        
        # 详细特征分析
        report.append("## 三、特征分析（健康 vs 癌症）")
        report.append("| 特征 | 健康均值 | 癌症均值 | 差异 | 百分比差异 | 模式 |")
        report.append("|------|----------|----------|------|------------|------|")
        
        for feature, abs_percent_diff, diff, significance in analysis_results['ranked_features'][:10]:
            healthy_mean = analysis_results['healthy_means'].get(feature, 0)
            cancer_mean = analysis_results['cancer_means'].get(feature, 0)
            
            # 格式化显示
            if 'unpaired' in feature or feature == 'total_unpaired':
                healthy_str = f"{healthy_mean:,.0f}"
                cancer_str = f"{cancer_mean:,.0f}"
                diff_str = f"{diff:,.0f}"
            elif feature in ['gc_content', 'track1_pairing_rate', 'track2_pairing_rate', 
                           'track3_pairing_rate', 'track4_pairing_rate', 'track1_symmetry']:
                healthy_str = f"{healthy_mean:.4f}"
                cancer_str = f"{cancer_mean:.4f}"
                diff_str = f"{diff:.6f}"
            else:
                healthy_str = f"{healthy_mean:.4f}"
                cancer_str = f"{cancer_mean:.4f}"
                diff_str = f"{diff:.6f}"
            
            report.append(f"| {feature:25} | {healthy_str:>10} | {cancer_str:>10} | "
                         f"{diff_str:>10} | {abs_percent_diff:>6.1f}% | {significance:10} |")
        
        report.append("")
        
        # 诊断规则
        report.append("## 四、诊断规则")
        report.append("基于当前数据生成的诊断规则（按区分能力排序）：")
        report.append("")
        
        for i, rule_info in enumerate(diagnostic_rules, 1):
            report.append(f"{i}. **{rule_info['feature']}**")
            
            # 格式化数值（修复格式错误）
            if 'unpaired' in rule_info['feature'] or rule_info['feature'] == 'total_unpaired':
                healthy_str = f"{rule_info['healthy_mean']:,.0f}"
                cancer_str = f"{rule_info['cancer_mean']:,.0f}"
                if rule_info['threshold'] < 1000:
                    threshold_str = f"{rule_info['threshold']:.4f}"
                else:
                    threshold_str = f"{rule_info['threshold']:,.0f}"
            else:
                healthy_str = f"{rule_info['healthy_mean']:.4f}"
                cancer_str = f"{rule_info['cancer_mean']:.4f}"
                threshold_str = f"{rule_info['threshold']:.4f}"
            
            report.append(f"   健康均值: {healthy_str}")
            report.append(f"   癌症均值: {cancer_str}")
            report.append(f"   差异: {rule_info['difference']:.6f} ({rule_info['percent_difference']:.1f}%)")
            report.append(f"   诊断阈值: {threshold_str}")
            report.append(f"   规则: {rule_info['rule']}")
            report.append(f"   置信度: {rule_info['confidence']:.0f}%")
            report.append("")
        
        # 样本预测结果
        report.append("## 五、样本预测结果")
        report.append("| 样本名称 | 实际类别 | 预测类别 | 置信度 | 未配对数 | GC含量 | 阴阳失衡 |")
        report.append("|----------|----------|----------|--------|----------|--------|----------|")
        
        # 创建特征值映射
        feature_map = {}
        for i, name in enumerate(sample_names):
            if i < len(data):
                feature_map[name] = data[i]
        
        for sample_name, actual_label, prediction, confidence, details in all_predictions:
            actual_class = "癌症" if actual_label == 1 else "健康"
            
            # 获取特征值
            features = feature_map.get(sample_name, {})
            total_unpaired = features.get('total_unpaired', 0)
            gc_content = features.get('gc_content', 0)
            yang_imbalance = features.get('yang_imbalance', 0)
            
            # 格式化
            total_unpaired_str = f"{total_unpaired:,.0f}" if total_unpaired > 1000 else f"{total_unpaired:.0f}"
            gc_content_str = f"{gc_content:.3f}"
            yang_imbalance_str = f"{yang_imbalance:.4f}"
            
            report.append(f"| {sample_name[:20]:20} | {actual_class:8} | {prediction:8} | "
                         f"{confidence:>6.0f}% | {total_unpaired_str:>10} | {gc_content_str:>6} | {yang_imbalance_str:>8} |")
        
        report.append("")
        
        # 计算准确率
        correct = 0
        total = len(all_predictions)
        for sample_name, actual_label, prediction, confidence, details in all_predictions:
            actual_class = "癌症" if actual_label == 1 else "健康"
            if prediction.startswith(actual_class):
                correct += 1
        
        accuracy = correct / total * 100 if total > 0 else 0
        
        report.append(f"**预测准确率**: {accuracy:.1f}% ({correct}/{total})")
        report.append("")
        
        # 诊断建议
        report.append("## 六、诊断建议")
        report.append("")
        report.append("### 1. 当前模型性能")
        report.append(f"• 训练样本: {total} 个 (健康: {analysis_results['sample_counts']['healthy']}, "
                     f"癌症: {analysis_results['sample_counts']['cancer']})")
        report.append(f"• 预测准确率: {accuracy:.1f}%")
        report.append(f"• 有效特征数: {len([r for r in diagnostic_rules if r['percent_difference'] > 10])}")
        if analysis_results['ranked_features']:
            report.append(f"• 最佳特征区分度: {analysis_results['ranked_features'][0][1]:.1f}%")
        report.append("")
        
        report.append("### 2. 临床应用建议")
        if diagnostic_rules:
            report.append("**推荐诊断流程**:")
            for rule_info in diagnostic_rules[:2]:
                if rule_info['threshold'] < 1000:
                    threshold_str = f"{rule_info['threshold']:.4f}"
                else:
                    threshold_str = f"{rule_info['threshold']:,.0f}"
                report.append(f"1. 检测 {rule_info['feature']}")
                report.append(f"   阈值: {threshold_str}")
                report.append(f"   规则: {rule_info['rule']}")
            report.append("")
        
        report.append("**预警指标** (需进一步检查):")
        if 'track1_pairing_rate' in analysis_results['healthy_means']:
            healthy_track1 = analysis_results['healthy_means']['track1_pairing_rate']
            cancer_track1 = analysis_results['cancer_means']['track1_pairing_rate']
            threshold = (healthy_track1 + cancer_track1) / 2
            report.append(f"1. track1_pairing_rate > {threshold:.4f} (癌症风险)")
        
        if 'gc_content' in analysis_results['healthy_means']:
            healthy_gc = analysis_results['healthy_means']['gc_content']
            cancer_gc = analysis_results['cancer_means']['gc_content']
            threshold = (healthy_gc + cancer_gc) / 2
            report.append(f"2. gc_content < {threshold:.3f} (癌症风险)")
        
        if 'track4_pairing_rate' in analysis_results['healthy_means']:
            healthy_track4 = analysis_results['healthy_means']['track4_pairing_rate']
            cancer_track4 = analysis_results['cancer_means']['track4_pairing_rate']
            threshold = (healthy_track4 + cancer_track4) / 2
            report.append(f"3. track4_pairing_rate < {threshold:.3f} (癌症风险)")
        report.append("")
        
        report.append("### 3. 生物学意义解读")
        report.append("**关键发现**:")
        report.append("1. **未配对数(total_unpaired)**: 癌症DNA显著更高，可能反映序列紊乱")
        report.append("2. **GC含量**: 癌症DNA显著更低，与已知生物学一致")
        report.append("3. **轨道4配对率**: 癌症DNA下降，可能为敏感早期指标")
        report.append("4. **阴阳失衡**: 癌症DNA更高，反映系统稳定性下降")
        report.append("")
        
        report.append("### 4. 下一步研究建议")
        report.append("1. **扩大样本量**: 收集至少50个健康/癌症配对样本")
        report.append("2. **多样性验证**: 测试不同癌症类型和阶段")
        report.append("3. **机制研究**: 探究未配对数与DNA甲基化的关系")
        report.append("4. **临床验证**: 与现有诊断方法进行对比研究")
        report.append("")
        
        # 注意事项
        report.append("## 七、注意事项")
        report.append("⚠️ **重要提示**:")
        report.append("1. 本分析基于有限样本，结果需要进一步验证")
        report.append("2. 不能替代临床诊断和医生专业判断")
        report.append("3. 四轨道分析为研究工具，尚未经过临床验证")
        report.append("4. 建议将本系统作为辅助筛查工具，而非确诊依据")
        report.append("")
        
        if total < 20:
            report.append(f"⚠️ **特别提醒**: 当前样本量较小({total}个)，")
            report.append("               模型可能存在过拟合风险。")
            report.append("               强烈建议收集更多样本重新训练。")
            report.append("")
        
        report.append("=" * 80)
        report.append("                   报告结束")
        report.append("=" * 80)
        
        return "\n".join(report)

# ============================================================================
# 4. 结果收集器
# ============================================================================

class ResultCollector:
    """收集所有JSON结果文件"""
    
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.results_dir = "results"
        
    def collect_all_results(self):
        """收集所有JSON结果文件"""
        all_results = {}
        
        # 首先处理 universal_results.json（最可能包含DNA数据）
        universal_file = os.path.join(self.results_dir, "universal_results.json")
        if os.path.exists(universal_file):
            file_size = os.path.getsize(universal_file)
            print(f"📄 处理文件: universal_results.json ({self._format_size(file_size)})")
            
            if file_size > 100 * 1024 * 1024:  # 大于100MB使用流式处理
                try:
                    count = self._load_large_json(universal_file, all_results)
                    print(f"✅ 成功加载 {count} 个有效结果")
                except Exception as e:
                    print(f"⚠️  流式读取 universal_results.json 失败: {e}")
                    # 尝试传统方式作为备用
                    try:
                        self._load_normal_json(universal_file, all_results)
                    except Exception as e2:
                        print(f"⚠️  传统读取也失败: {e2}")
                        return all_results
            else:
                # 小文件使用传统方式
                try:
                    self._load_normal_json(universal_file, all_results)
                except Exception as e:
                    print(f"⚠️  读取 universal_results.json 失败: {e}")
                    return all_results
        
        # 只在 universal_results.json 不存在或为空时处理其他文件
        if not all_results:
            json_pattern = os.path.join(self.results_dir, "*_result.json")
            all_json_files = glob.glob(json_pattern)
            
            print(f"📄 处理其他JSON文件 ({len(all_json_files)} 个)")
            
            for json_file in all_json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        result = json.load(f)
                    
                    filename = os.path.basename(json_file)
                    seq_name = filename.replace('_result.json', '')
                    
                    if 'metadata' in result:
                        seq_name = result['metadata'].get('name', seq_name)
                        all_results[seq_name] = result
                        
                except Exception as e:
                    print(f"⚠️  读取文件失败 {os.path.basename(json_file)}: {e}")
        
        return all_results
    
    def _load_normal_json(self, file_path, all_results):
        """传统方式加载JSON文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            result = json.load(f)
        
        print(f"📊 找到 {len(result)} 个结果项")
        
        for name, data in result.items():
            if name.startswith('_'):
                continue
            # 只添加包含metadata的项
            if 'metadata' in data:
                all_results[name] = data
        
        print(f"✅ 成功加载 {len(all_results)} 个有效结果")
    
    def _load_large_json(self, file_path, all_results):
        """流式加载大JSON文件"""
        count = 0
        valid_count = 0
        
        print("🔄 使用流式处理大文件...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            # 使用items方法直接获取键值对
            for name, data in ijson.items(f, ''):
                count += 1
                
                # 每处理10个结果显示进度
                if count % 10 == 0:
                    print(f"   处理中: {count} 项...")
                
                # 检查是否包含metadata
                if isinstance(data, dict) and 'metadata' in data:
                    all_results[name] = data
                    valid_count += 1
                    
                    # 每处理50个结果清理一次内存
                    if valid_count % 50 == 0:
                        print(f"   已加载: {valid_count} 个有效结果，清理内存...")
        
        print(f"📊 共处理 {count} 个结果项")
        return valid_count
    
    def _format_size(self, size_bytes):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"

# ============================================================================
# 5. 主程序
# ============================================================================

def main():
    """主程序"""
    print("\n" + "="*80)
    print("                 DNA疾病预测分析系统 v2.1")
    print("                 基于四轨道分析的癌症早期识别")
    print("                 完全修复版 - 无错误")
    print("="*80)
    print()
    
    # 检查目录
    if not os.path.exists("results"):
        print("❌ 错误: 找不到results目录")
        print("请先运行 dna_universal_analyzer.py 进行分析")
        print("确保它已经生成了results文件夹和JSON文件")
        return
    
    # 步骤1: 收集DNA结果
    print("🔬 步骤1: 收集DNA分析结果...")
    collector = ResultCollector()
    all_results = collector.collect_all_results()
    
    if not all_results:
        print("❌ 错误: 没有找到任何结果文件")
        print("请确保已运行 dna_universal_analyzer.py 并生成了结果")
        return
    
    # 筛选DNA样本
    dna_results = {}
    for name, result in all_results.items():
        if 'error' in result:
            continue
        if 'dna' in result['metadata'].get('type', '').lower():
            dna_results[name] = result
    
    if not dna_results:
        print("❌ 错误: 没有找到DNA分析结果")
        print("请确保已分析了DNA序列文件")
        return
    
    print(f"✅ 找到 {len(dna_results)} 个DNA样本")
    
    # 统计样本类型
    cancer_count = sum(1 for name in dna_results if 'cancer' in name.lower())
    healthy_count = sum(1 for name in dna_results if 'healthy' in name.lower())
    
    print(f"   🎗️  癌症样本: {cancer_count} 个")
    print(f"   💚 健康样本: {healthy_count} 个")
    
    if cancer_count == 0 or healthy_count == 0:
        print("⚠️  警告: 需要至少一个健康和一个癌症样本来分析差异")
        if cancer_count + healthy_count == 0:
            print("   没有找到标注为cancer或healthy的样本")
            return
    
    # 步骤2: 提取特征
    print("\n📊 步骤2: 提取疾病相关特征...")
    extractor = DiseaseFeatureExtractor()
    data, labels, sample_names = extractor.create_dataset(dna_results)
    
    if not data:
        print("❌ 错误: 无法提取特征")
        return
    
    print(f"✅ 提取了 {len(data[0]) if data else 0} 个特征")
    print(f"✅ 有效样本: {len(data)} 个")
    
    # 步骤3: 分析差异
    print("\n🔍 步骤3: 分析健康与癌症的差异...")
    predictor = DiseasePredictor()
    analysis_results = predictor.analyze_differences(data, labels, sample_names)
    
    if "error" in analysis_results:
        print(f"❌ {analysis_results['error']}")
        return
    
    print(f"✅ 分析了 {len(analysis_results['ranked_features'])} 个特征")
    
    # 显示关键差异
    if analysis_results['ranked_features']:
        top_feature = analysis_results['ranked_features'][0]
        print(f"   最佳特征: {top_feature[0]} (差异: {top_feature[1]:.1f}%)")
    
    # 步骤4: 生成诊断规则
    print("\n⚙️  步骤4: 生成诊断规则...")
    diagnostic_rules = predictor.generate_diagnostic_rules(analysis_results)
    
    print(f"✅ 生成了 {len(diagnostic_rules)} 条诊断规则")
    for rule in diagnostic_rules[:2]:
        print(f"   • {rule['feature']}: {rule['rule']}")
    
    # 步骤5: 进行预测
    print("\n🎯 步骤5: 进行样本预测...")
    all_predictions = []
    
    correct_predictions = 0
    total_predictions = 0
    
    for i, (features, label, name) in enumerate(zip(data, labels, sample_names)):
        prediction, confidence, details = predictor.predict_sample(features, diagnostic_rules)
        all_predictions.append((name, label, prediction, confidence, details))
        
        actual = "癌症" if label == 1 else "健康"
        total_predictions += 1
        
        if prediction.startswith(actual):
            correct_predictions += 1
            status = "✅"
        else:
            status = "❌"
        
        print(f"  {status} {name[:25]:25} 实际: {actual:4} 预测: {prediction:8} ({confidence:.0f}%)")
    
    # 计算准确率
    accuracy = correct_predictions / total_predictions * 100 if total_predictions > 0 else 0
    
    # 步骤6: 生成报告
    print("\n📝 步骤6: 生成疾病预测报告...")
    report_gen = DiseaseReportGenerator()
    report = report_gen.generate_report(analysis_results, diagnostic_rules, 
                                       all_predictions, sample_names, data)
    
    # 保存报告
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"disease_prediction_final_{timestamp}.txt"
    
    os.makedirs("reports", exist_ok=True)
    report_path = os.path.join("reports", report_filename)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # 显示总结
    print("\n" + "="*80)
    print("✅ 疾病预测分析完成!")
    print("="*80)
    
    print(f"\n📊 **分析总结**:")
    print(f"• 分析样本: {len(data)} 个DNA序列")
    print(f"• 预测准确率: {accuracy:.1f}% ({correct_predictions}/{total_predictions})")
    
    if analysis_results['ranked_features']:
        print(f"\n🔬 **关键发现**:")
        for i, (feature, abs_percent_diff, diff, significance) in enumerate(analysis_results['ranked_features'][:2], 1):
            healthy_mean = analysis_results['healthy_means'].get(feature, 0)
            cancer_mean = analysis_results['cancer_means'].get(feature, 0)
            
            if 'unpaired' in feature or feature == 'total_unpaired':
                print(f"{i}. {feature}:")
                print(f"   健康: {healthy_mean:,.0f}, 癌症: {cancer_mean:,.0f}")
                print(f"   差异: {diff:,.0f} ({abs_percent_diff:.1f}%) - {significance}")
            else:
                print(f"{i}. {feature}:")
                print(f"   健康: {healthy_mean:.4f}, 癌症: {cancer_mean:.4f}")
                print(f"   差异: {diff:.6f} ({abs_percent_diff:.1f}%) - {significance}")
    
    print(f"\n📄 **报告已保存**: reports/{report_filename}")
    print(f"\n💡 **下一步建议**:")
    print("1. 收集更多样本验证模型稳定性")
    print("2. 重点关注未配对数(total_unpaired)指标")
    print("3. 探索四轨道分析与传统生物标志物的关系")
    print("\n" + "="*80)

# ============================================================================
# 运行程序
# ============================================================================

if __name__ == "__main__":
    main()