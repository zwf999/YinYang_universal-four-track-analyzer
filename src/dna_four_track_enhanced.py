#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DNA四轨道分析系统 - 增强版
作者：AI助手
版本：1.1.0

这是一个增强版的DNA分析程序，包含：
1. DNA编码器（将DNA转为0-9数字）
2. 四轨道分析器（你的算法）
3. 结果解释器
4. 从文件/目录加载功能
"""

import json
import os
from typing import List, Dict, Any, Tuple, Optional
from collections import Counter
from datetime import datetime
import math

# ============================================================================
# 第一部分：DNA编码器
# ============================================================================

class DNAEncoder:
    """DNA到数字的编码器"""
    
    def __init__(self):
        # 碱基到0-3的映射
        self.base_to_num = {'A': 0, 'C': 1, 'G': 2, 'T': 3}
        self.num_to_base = {0: 'A', 1: 'C', 2: 'G', 3: 'T'}
        
        # 三角形编码表
        self.triangle_table = {
            (0, 0): 0,                    # AA
            (0, 1): 1, (1, 1): 4,         # AC, CC
            (0, 2): 2, (1, 2): 5, (2, 2): 7,  # AG, CG, GG
            (0, 3): 3, (1, 3): 6, (2, 3): 8, (3, 3): 9  # AT, CT, GT, TT
        }
        
        # 反向映射
        self.code_to_pair = {v: k for k, v in self.triangle_table.items()}
    
    def encode(self, dna_sequence: str) -> Dict[str, Any]:
        """将DNA编码为数字"""
        # 清理序列
        dna_seq = self._clean_sequence(dna_sequence)
        
        digits = []      # 数字序列
        details = []     # 编码详情
        
        i = 0
        while i < len(dna_seq):
            if i + 1 < len(dna_seq):
                # 两个碱基的情况
                b1, b2 = dna_seq[i], dna_seq[i+1]
                n1, n2 = self.base_to_num[b1], self.base_to_num[b2]
                
                # 排序（小到大）
                small, large = (n1, n2) if n1 <= n2 else (n2, n1)
                code = self.triangle_table[(small, large)]
                
                # 方向
                is_forward = (n1 <= n2)
                direction = 'forward' if is_forward else 'reverse'
                direction_mark = '' if is_forward else '←'
                
                digits.append(code)
                details.append({
                    'position': i,
                    'bases': b1 + b2,
                    'code': code,
                    'direction': direction,
                    'direction_mark': direction_mark
                })
                
                i += 2
            else:
                # 单个碱基
                b = dna_seq[i]
                n = self.base_to_num[b]
                # 直接使用0-3表示单个碱基，不使用+5
                code = n
                
                digits.append(code)
                details.append({
                    'position': i,
                    'base': b,
                    'code': code,
                    'direction': 'single'
                })
                
                i += 1
        
        # 计算统计
        stats = self._calculate_stats(dna_seq, digits)
        
        return {
            'original': dna_seq,
            'digits': digits,
            'details': details,
            'stats': stats
        }
    
    def _clean_sequence(self, seq: str) -> str:
        """清理DNA序列"""
        seq = seq.upper().strip().replace(' ', '').replace('\n', '').replace('\t', '')
        
        # 检查有效字符
        valid_chars = set('ACGT')
        for char in seq:
            if char not in valid_chars:
                raise ValueError(f"无效DNA字符: '{char}'，只允许A,C,G,T")
        
        return seq
    
    def _calculate_stats(self, dna_seq: str, digits: List[int]) -> Dict[str, Any]:
        """计算统计信息"""
        gc_count = dna_seq.count('G') + dna_seq.count('C')
        total = len(dna_seq)
        
        digit_counts = Counter(digits)
        
        return {
            'length': total,
            'gc_content': gc_count / total if total > 0 else 0,
            'gc_count': gc_count,
            'at_count': total - gc_count,
            'digit_counts': dict(digit_counts),
            'unique_digits': len(set(digits)),
            'encoded_length': len(digits)
        }
    
    def decode(self, encoded_data: Dict[str, Any]) -> str:
        """从编码数据解码回DNA"""
        digits = encoded_data['digits']
        details = encoded_data['details']
        
        bases = []
        for idx, detail in enumerate(details):
            if 'direction' in detail:
                if detail['direction'] == 'single':
                    # 单个碱基
                    code = digits[idx]
                    n = code
                    bases.append(self.num_to_base[n])
                else:
                    # 碱基对
                    code = digits[idx]
                    n1, n2 = self.code_to_pair[code]
                    
                    if detail['direction'] == 'forward':
                        bases.extend([self.num_to_base[n1], self.num_to_base[n2]])
                    else:  # reverse
                        bases.extend([self.num_to_base[n2], self.num_to_base[n1]])
        
        return ''.join(bases)

# ============================================================================
# 第二部分：四轨道分析器
# ============================================================================

class FourTrackAnalyzer:
    """四轨道分析器"""
    
    def __init__(self):
        # 数字属性表（轨道1）
        self.number_attributes = {
            0: {'small_large': 0, 'up_down': 0, 'odd_even': 0, 'ab_relation': 0},
            1: {'small_large': 1, 'up_down': 1, 'odd_even': 1, 'ab_relation': 1},
            2: {'small_large': 1, 'up_down': 1, 'odd_even': 0, 'ab_relation': 1},
            3: {'small_large': 1, 'up_down': 1, 'odd_even': 1, 'ab_relation': 1},
            4: {'small_large': 1, 'up_down': 0, 'odd_even': 0, 'ab_relation': 1},
            5: {'small_large': 1, 'up_down': 0, 'odd_even': 1, 'ab_relation': 0},
            6: {'small_large': 1, 'up_down': 1, 'odd_even': 0, 'ab_relation': 0},
            7: {'small_large': 1, 'up_down': 1, 'odd_even': 1, 'ab_relation': 0},
            8: {'small_large': 0, 'up_down': 1, 'odd_even': 0, 'ab_relation': 0},
            9: {'small_large': 0, 'up_down': 0, 'odd_even': 1, 'ab_relation': 1}
        }
        
        # 八卦配对规则
        self.bagua_pairing = {1: 8, 2: 7, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1}
        
        # 八态编码
        self.state_encoding = {
            '111': 1, '110': 2, '101': 3, '100': 4,
            '011': 5, '010': 6, '001': 7, '000': 8
        }
        
        # 轨道2-4映射
        self.track_mappings = {
            'track2': {0: 'E', 1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'D', 6: 'C', 7: 'B', 8: 'A', 9: 'E'},
            'track3': {0: '戊', 1: '甲', 2: '乙', 3: '丙', 4: '丁', 5: '戊', 6: '丁', 7: '丙', 8: '乙', 9: '甲'},
            'track4': {0: '癸', 1: '己', 2: '庚', 3: '辛', 4: '壬', 5: '庚', 6: '辛', 7: '壬', 8: '己', 9: '癸'}
        }
        
        # 轨道2-4阴阳分类
        self.yinyang_class = {
            'track2': {'yang': {'A', 'C', 'E'}, 'yin': {'B', 'D'}},
            'track3': {'yang': {'甲', '丙', '戊'}, 'yin': {'乙', '丁'}},
            'track4': {'yang': {'己', '辛', '癸'}, 'yin': {'庚', '壬'}}
        }
    
    def analyze(self, digits: List[int]) -> Dict[str, Any]:
        """分析数字序列"""
        try:
            # 验证输入
            for d in digits:
                if not 0 <= d <= 9:
                    return {'error': f'无效数字: {d}，必须在0-9范围内'}
            
            # 正向分析
            results = {}
            for track in ['track1', 'track2', 'track3', 'track4']:
                forward_result = self._analyze_track(digits, track)
                
                # 反向分析
                reversed_digits = digits[::-1]
                backward_result = self._analyze_track(reversed_digits, track)
                
                # 对称性
                symmetry = self._calculate_symmetry(forward_result, backward_result)
                
                results[track] = {
                    'forward': forward_result,
                    'backward': backward_result,
                    'symmetry': symmetry
                }
            
            # 全局结果
            results['summary'] = self._generate_summary(results)
            
            return results
            
        except Exception as e:
            return {'error': f'分析错误: {str(e)}'}
    
    def _analyze_track(self, digits: List[int], track_name: str) -> Dict[str, Any]:
        """分析单个轨道"""
        if track_name == 'track1':
            return self._analyze_track1(digits)
        else:
            return self._analyze_other_track(digits, track_name)
    
    def _analyze_track1(self, digits: List[int]) -> Dict[str, Any]:
        """分析轨道1"""
        result = {
            'window_count': 0,
            'symbol_pairs': {'valid': 0, 'total': 0, 'ratio': 0},
            'digit_pairs': {'valid': 0, 'total': 0, 'ratio': 0},
            'global_digit_pairs': {'valid': 0, 'total': 0, 'ratio': 0, 'pair_types': {}, 'unpaired': {}},
            'yinyang': {'yang': 0, 'yin': 0, 'ratio': 0, 'yang_percent': 0}
        }
        
        if len(digits) < 12:
            return result
        
        # 窗口滑动分析（12位窗口，步长5）
        windows = []
        for i in range(0, len(digits) - 11, 5):
            window = digits[i:i+12]
            if len(window) == 12:
                windows.append(window)
        
        result['window_count'] = len(windows)
        
        # 分析每个窗口
        symbol_valid = 0
        symbol_total = 0
        
        for window in windows:
            # 分割为4个子序列
            p1 = window[0:3]
            p2 = window[3:6]
            p3 = window[6:9]
            p4 = window[9:12]
            
            # 四个维度分别分析
            for dim in ['small_large', 'up_down', 'odd_even', 'ab_relation']:
                # 生成状态
                state_p1 = self._get_track1_state(p1, dim)
                state_p2 = self._get_track1_state(p2, dim)
                state_p3 = self._get_track1_state(p3, dim)
                state_p4 = self._get_track1_state(p4, dim)
                
                # 检查配对
                if self.bagua_pairing.get(state_p1) == state_p3:
                    symbol_valid += 1
                symbol_total += 1
                
                if self.bagua_pairing.get(state_p2) == state_p4:
                    symbol_valid += 1
                symbol_total += 1
        
        # 符号配对结果
        if symbol_total > 0:
            result['symbol_pairs'] = {
                'valid': symbol_valid,
                'total': symbol_total,
                'ratio': symbol_valid / symbol_total
            }
        
        # 数字直接配对
        digit_valid = 0
        digit_total = 0
        for i in range(0, len(digits) - 1, 2):
            if i + 1 < len(digits):
                if self._is_valid_track1_pair(digits[i], digits[i+1]):
                    digit_valid += 1
                digit_total += 1
        
        if digit_total > 0:
            result['digit_pairs'] = {
                'valid': digit_valid,
                'total': digit_total,
                'ratio': digit_valid / digit_total
            }
        
        # 全局数字配对
        global_pairs = self._analyze_global_pairs(digits, 'track1')
        result['global_digit_pairs'] = global_pairs
        
        # 阴阳计算（轨道1特殊规则）
        yang_count = sum(1 for d in digits if 1 <= d <= 7)
        yin_count = len(digits) - yang_count
        
        result['yinyang'] = {
            'yang': yang_count,
            'yin': yin_count,
            'ratio': yang_count / yin_count if yin_count > 0 else 0,
            'yang_percent': yang_count / len(digits) if digits else 0
        }
        
        return result
    
    def _analyze_other_track(self, digits: List[int], track_name: str) -> Dict[str, Any]:
        """分析轨道2-4"""
        result = {
            'window_count': 0,
            'symbol_pairs': {'valid': 0, 'total': 0, 'ratio': 0},
            'digit_pairs': {'valid': 0, 'total': 0, 'ratio': 0},
            'global_digit_pairs': {'valid': 0, 'total': 0, 'ratio': 0, 'pair_types': {}, 'unpaired': {}},
            'yinyang': {'yang': 0, 'yin': 0, 'ratio': 0, 'yang_percent': 0}
        }
        
        # 全局数字配对分析
        global_pairs = self._analyze_global_pairs(digits, track_name)
        result['global_digit_pairs'] = global_pairs
        
        # 阴阳计算
        symbols = [self.track_mappings[track_name][d] for d in digits]
        yinyang_set = self.yinyang_class[track_name]
        
        yang_count = sum(1 for s in symbols if s in yinyang_set['yang'])
        yin_count = sum(1 for s in symbols if s in yinyang_set['yin'])
        
        result['yinyang'] = {
            'yang': yang_count,
            'yin': yin_count,
            'ratio': yang_count / yin_count if yin_count > 0 else 0,
            'yang_percent': yang_count / (yang_count + yin_count) if (yang_count + yin_count) > 0 else 0
        }
        
        return result
    
    def _get_track1_state(self, subseq: List[int], dimension: str) -> int:
        """获取轨道1状态"""
        bits = []
        for num in subseq:
            bits.append(str(self.number_attributes[num][dimension]))
        
        binary = ''.join(bits)
        return self.state_encoding.get(binary, 1)
    
    def _is_valid_track1_pair(self, d1: int, d2: int) -> bool:
        """检查轨道1数字对是否有效"""
        # 轨道1没有特定的数字配对规则
        return False
    
    def _analyze_global_pairs(self, digits: List[int], track_name: str) -> Dict[str, Any]:
        """分析全局数字配对"""
        digit_counts = Counter(digits)
        remaining = Counter(digits)
        
        valid_pairs = 0
        pair_types = {}
        total_pairs = len(digits) // 2
        
        # 配对规则
        pair_rules = []
        if track_name == 'track1':
            # 轨道1没有全局配对规则
            pass
        elif track_name == 'track2':
            # 轨道2：和=9
            pair_rules = [
                ((1, 8), 'A', '阳'),
                ((8, 1), 'A', '阳'),
                ((2, 7), 'B', '阴'),
                ((7, 2), 'B', '阴'),
                ((3, 6), 'C', '阳'),
                ((6, 3), 'C', '阳'),
                ((4, 5), 'D', '阴'),
                ((5, 4), 'D', '阴'),
                ((9, 0), 'E', '阳'),
                ((0, 9), 'E', '阳')
            ]
        elif track_name == 'track3':
            # 轨道3：和=10
            pair_rules = [
                ((1, 9), '甲', '阳'),
                ((9, 1), '甲', '阳'),
                ((2, 8), '乙', '阴'),
                ((8, 2), '乙', '阴'),
                ((3, 7), '丙', '阳'),
                ((7, 3), '丙', '阳'),
                ((4, 6), '丁', '阴'),
                ((6, 4), '丁', '阴'),
                ((5, 0), '戊', '阳'),
                ((0, 5), '戊', '阳')
            ]
        elif track_name == 'track4':
            # 轨道4：特定组合
            pair_rules = [
                ((1, 8), '一', '阳'),
                ((8, 1), '一', '阳'),
                ((2, 5), '二', '阴'),
                ((5, 2), '二', '阴'),
                ((3, 6), '三', '阳'),
                ((6, 3), '三', '阳'),
                ((4, 7), '四', '阴'),
                ((7, 4), '四', '阴'),
                ((9, 0), '五', '阳'),
                ((0, 9), '五', '阳')
            ]
        
        # 应用配对规则
        for pair, pair_type, yinyang in pair_rules:
            d1, d2 = pair
            
            if d1 == d2:
                pair_count = remaining[d1] // 2
            else:
                pair_count = min(remaining.get(d1, 0), remaining.get(d2, 0))
            
            if pair_count > 0:
                valid_pairs += pair_count
                
                # 记录配对类型
                if pair_type not in pair_types:
                    pair_types[pair_type] = {'count': 0, 'yinyang': yinyang}
                pair_types[pair_type]['count'] += pair_count
                
                # 更新剩余数字
                if d1 == d2:
                    remaining[d1] -= pair_count * 2
                else:
                    remaining[d1] -= pair_count
                    remaining[d2] -= pair_count
        
        # 统计未配对的数字
        unpaired = {d: count for d, count in remaining.items() if count > 0}
        
        return {
            'valid': valid_pairs,
            'total': total_pairs,
            'ratio': valid_pairs / total_pairs if total_pairs > 0 else 0,
            'pair_types': pair_types,
            'unpaired': unpaired
        }
    
    def _calculate_symmetry(self, forward: Dict[str, Any], backward: Dict[str, Any]) -> Dict[str, Any]:
        """计算对称性"""
        # 配对率相似度
        forward_pair = forward.get('symbol_pairs', {}).get('ratio', 0)
        backward_pair = backward.get('symbol_pairs', {}).get('ratio', 0)
        pair_diff = abs(forward_pair - backward_pair)
        pair_sim = 1 - pair_diff
        
        # 全局配对相似度
        forward_global = forward.get('global_digit_pairs', {}).get('ratio', 0)
        backward_global = backward.get('global_digit_pairs', {}).get('ratio', 0)
        global_diff = abs(forward_global - backward_global)
        global_sim = 1 - global_diff
        
        # 阴阳相似度
        forward_yang = forward.get('yinyang', {}).get('yang_percent', 0)
        backward_yang = backward.get('yinyang', {}).get('yang_percent', 0)
        yang_diff = abs(forward_yang - backward_yang)
        yang_sim = 1 - yang_diff
        
        # 整体对称性
        overall = (pair_sim + global_sim + yang_sim) / 3
        
        return {
            'pair_similarity': pair_sim,
            'global_similarity': global_sim,
            'yang_similarity': yang_sim,
            'overall': overall
        }
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成摘要"""
        summary = {
            'best_track': None,
            'worst_track': None,
            'average_symmetry': 0,
            'track_scores': {}
        }
        
        track_scores = []
        for track_name, track_data in results.items():
            if track_name == 'summary':
                continue
            
            symmetry = track_data['symmetry']['overall']
            
            # 计算轨道分数
            forward = track_data['forward']
            
            if track_name == 'track1':
                pair_score = forward['symbol_pairs']['ratio']
            else:
                pair_score = forward['global_digit_pairs']['ratio']
            
            yang_score = 1 - abs(forward['yinyang']['yang_percent'] - 0.5) * 2
            
            track_score = (pair_score * 0.4 + symmetry * 0.4 + yang_score * 0.2)
            
            summary['track_scores'][track_name] = {
                'score': track_score,
                'symmetry': symmetry,
                'pairing': pair_score
            }
            
            track_scores.append((track_name, track_score))
        
        # 找出最佳和最差轨道
        if track_scores:
            track_scores.sort(key=lambda x: x[1], reverse=True)
            summary['best_track'] = track_scores[0][0]
            summary['worst_track'] = track_scores[-1][0]
            
            # 平均对称性
            symmetries = [results[track]['symmetry']['overall'] 
                         for track in results if track != 'summary']
            if symmetries:
                summary['average_symmetry'] = sum(symmetries) / len(symmetries)
        
        return summary

# ============================================================================
# 第三部分：DNA分析系统
# ============================================================================

class DNAFourTrackSystem:
    """DNA四轨道分析系统"""
    
    def __init__(self):
        self.encoder = DNAEncoder()
        self.analyzer = FourTrackAnalyzer()
    
    def analyze(self, dna_sequence: str, name: str = "") -> Dict[str, Any]:
        """分析DNA序列"""
        try:
            print(f"🔬 分析序列: {name if name else '未命名序列'}")
            print(f"   长度: {len(dna_sequence)} bp")
            
            # 1. 编码DNA
            print("   步骤1: 编码DNA...")
            encoded = self.encoder.encode(dna_sequence)
            digits = encoded['digits']
            print(f"   编码为 {len(digits)} 个数字: {digits[:20]}{'...' if len(digits) > 20 else ''}")
            
            # 2. 四轨道分析
            print("   步骤2: 四轨道分析...")
            analysis = self.analyzer.analyze(digits)
            
            if 'error' in analysis:
                return {'error': analysis['error']}
            
            # 3. 解释结果
            print("   步骤3: 解释结果...")
            interpretation = self._interpret_results(dna_sequence, encoded, analysis)
            
            # 4. 构建最终结果
            result = {
                'metadata': {
                    'name': name,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'length': len(dna_sequence)
                },
                'encoding': encoded,
                'analysis': analysis,
                'interpretation': interpretation,
                'summary': self._create_summary(encoded, analysis, interpretation)
            }
            
            print("   ✅ 分析完成!")
            print()
            
            return result
            
        except Exception as e:
            error_msg = f"分析失败: {str(e)}"
            print(f"   ❌ {error_msg}")
            return {'error': error_msg}
    
    def _interpret_results(self, dna_seq: str, encoded: Dict[str, Any], 
                          analysis: Dict[str, Any]) -> Dict[str, Any]:
        """解释分析结果"""
        interpretations = {
            'gc_analysis': [],
            'track_insights': {},
            'biological_hypotheses': []
        }
        
        # GC含量分析
        gc_content = encoded['stats']['gc_content']
        if gc_content > 0.6:
            interpretations['gc_analysis'].append(f"高GC含量({gc_content:.1%})，热稳定性可能较高")
        elif gc_content < 0.4:
            interpretations['gc_analysis'].append(f"低GC含量({gc_content:.1%})，易于解链")
        else:
            interpretations['gc_analysis'].append(f"中等GC含量({gc_content:.1%})")
        
        # 轨道分析
        for track in ['track1', 'track2', 'track3', 'track4']:
            if track in analysis:
                track_data = analysis[track]
                forward = track_data['forward']
                symmetry = track_data['symmetry']['overall']
                
                insights = []
                
                if track == 'track1':
                    pair_ratio = forward['symbol_pairs']['ratio']
                    if pair_ratio > 0.8:
                        insights.append("高配对率，可能具有周期性结构")
                    elif pair_ratio < 0.2:
                        insights.append("低配对率，可能为随机区域")
                    
                    if forward['window_count'] >= 3:
                        insights.append(f"检测到{forward['window_count']}个分析窗口")
                else:
                    pair_ratio = forward['global_digit_pairs']['ratio']
                    if pair_ratio > 0.7:
                        insights.append("高全局配对率")
                    
                    unpaired = sum(forward['global_digit_pairs']['unpaired'].values())
                    if unpaired > 0:
                        insights.append(f"{unpaired}个未配对数字")
                
                if symmetry > 0.8:
                    insights.append("高对称性")
                elif symmetry < 0.3:
                    insights.append("低对称性")
                
                if insights:
                    interpretations['track_insights'][track] = insights
        
        # 生物学假设
        summary = analysis.get('summary', {})
        if 'best_track' in summary:
            best = summary['best_track']
            interpretations['biological_hypotheses'].append(
                f"最佳表现轨道: {best}，可能反映主要序列特征"
            )
        
        if 'average_symmetry' in summary:
            avg_sym = summary['average_symmetry']
            if avg_sym > 0.75:
                interpretations['biological_hypotheses'].append(
                    "高对称性序列，可能为回文结构或对称功能元件"
                )
        
        return interpretations
    
    def _create_summary(self, encoded: Dict[str, Any], 
                       analysis: Dict[str, Any], 
                       interpretation: Dict[str, Any]) -> Dict[str, Any]:
        """创建摘要"""
        summary = {
            'basic_info': {
                'length': encoded['stats']['length'],
                'gc_content': encoded['stats']['gc_content'],
                'encoded_length': len(encoded['digits'])
            },
            'performance': {},
            'key_findings': []
        }
        
        # 轨道性能
        if 'summary' in analysis and 'track_scores' in analysis['summary']:
            track_scores = analysis['summary']['track_scores']
            for track, scores in track_scores.items():
                summary['performance'][track] = {
                    'score': round(scores['score'], 3),
                    'rank': '优' if scores['score'] > 0.7 else '良' if scores['score'] > 0.5 else '中'
                }
        
        # 关键发现
        if interpretation['gc_analysis']:
            summary['key_findings'].append(interpretation['gc_analysis'][0])
        
        if interpretation['biological_hypotheses']:
            summary['key_findings'].extend(interpretation['biological_hypotheses'][:2])
        
        return summary
    
    def batch_analyze(self, sequences: Dict[str, str]) -> Dict[str, Any]:
        """批量分析"""
        results = {}
        print("=" * 60)
        print("开始批量分析...")
        print("=" * 60)
        
        for name, seq in sequences.items():
            results[name] = self.analyze(seq, name)
        
        # 比较分析
        if len(results) > 1:
            results['_comparison'] = self._compare_sequences(results)
        
        return results
    
    def _compare_sequences(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """比较多个序列"""
        comparison = {
            'gc_stats': {'min': 1.0, 'max': 0.0, 'avg': 0.0},
            'performance_stats': {'min': 1.0, 'max': 0.0, 'avg': 0.0},
            'similar_groups': []
        }
        
        gc_values = []
        perf_values = []
        valid_seqs = []
        
        for name, result in results.items():
            if name.startswith('_') or 'error' in result:
                continue
            
            valid_seqs.append(name)
            
            # GC含量
            gc = result['encoding']['stats']['gc_content']
            gc_values.append(gc)
            
            # 平均性能
            if 'summary' in result and 'performance' in result['summary']:
                scores = [v['score'] for v in result['summary']['performance'].values()]
                if scores:
                    perf_values.append(sum(scores) / len(scores))
        
        # 统计
        if gc_values:
            comparison['gc_stats'] = {
                'min': min(gc_values),
                'max': max(gc_values),
                'avg': sum(gc_values) / len(gc_values)
            }
        
        if perf_values:
            comparison['performance_stats'] = {
                'min': min(perf_values),
                'max': max(perf_values),
                'avg': sum(perf_values) / len(perf_values)
            }
        
        # 分组
        if len(gc_values) >= 2:
            high_gc = [name for name, gc in zip(valid_seqs, gc_values) if gc > 0.6]
            low_gc = [name for name, gc in zip(valid_seqs, gc_values) if gc < 0.4]
            
            if high_gc:
                comparison['similar_groups'].append({
                    'group': 'high_gc',
                    'sequences': high_gc
                })
            if low_gc:
                comparison['similar_groups'].append({
                    'group': 'low_gc',
                    'sequences': low_gc
                })
        
        return comparison
    
    def save_results(self, results: Dict[str, Any], filename: str = "results.json"):
        """保存结果到文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"结果已保存到: {filename}")
            return True
        except Exception as e:
            print(f"保存失败: {e}")
            return False
    
    def print_report(self, result: Dict[str, Any]):
        """打印报告"""
        if 'error' in result:
            print(f"错误: {result['error']}")
            return
        
        print("=" * 60)
        print("             分析报告")
        print("=" * 60)
        
        # 基本信息
        meta = result['metadata']
        print(f"序列: {meta.get('name', '未命名')}")
        print(f"时间: {meta.get('timestamp', '未知')}")
        print(f"长度: {meta.get('length', 0)} bp")
        print()
        
        # 编码信息
        enc = result['encoding']
        stats = enc['stats']
        print("📊 编码信息:")
        print(f"  数字序列长度: {stats['encoded_length']}")
        print(f"  GC含量: {stats['gc_content']:.1%}")
        print(f"  唯一数字: {stats['unique_digits']}种")
        print()
        
        # 轨道分析
        print("🎯 轨道分析:")
        analysis = result['analysis']
        
        for track in ['track1', 'track2', 'track3', 'track4']:
            if track in analysis:
                track_data = analysis[track]
                forward = track_data['forward']
                symmetry = track_data['symmetry']['overall']
                
                if track == 'track1':
                    pair_ratio = forward['symbol_pairs']['ratio']
                    print(f"  {track}: 配对率={pair_ratio:.1%}, 对称性={symmetry:.1%}, "
                          f"窗口数={forward['window_count']}")
                else:
                    pair_ratio = forward['global_digit_pairs']['ratio']
                    print(f"  {track}: 全局配对率={pair_ratio:.1%}, 对称性={symmetry:.1%}")
        print()
        
        # 解释
        interp = result['interpretation']
        print("💡 解释:")
        
        if interp['gc_analysis']:
            print(f"  GC分析: {interp['gc_analysis'][0]}")
        
        if interp['biological_hypotheses']:
            print(f"  假设: {interp['biological_hypotheses'][0]}")
        
        # 摘要
        if 'summary' in result:
            summ = result['summary']
            if 'performance' in summ:
                print()
                print("⭐ 性能评分:")
                for track, perf in summ['performance'].items():
                    print(f"  {track}: {perf['score']:.3f} ({perf['rank']})")
        
        print("=" * 60)
    
    def load_from_file(self, file_path: str) -> str:
        """从文件加载DNA序列"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            return content
        except Exception as e:
            raise Exception(f"读取文件失败: {e}")
    
    def load_from_directory(self, directory: str) -> Dict[str, str]:
        """从目录加载DNA序列"""
        sequences = {}
        try:
            for filename in os.listdir(directory):
                if filename.endswith('.txt'):
                    file_path = os.path.join(directory, filename)
                    try:
                        content = self.load_from_file(file_path)
                        sequences[filename] = content
                    except Exception as e:
                        print(f"跳过文件 {filename}: {e}")
            return sequences
        except Exception as e:
            raise Exception(f"读取目录失败: {e}")

# ============================================================================
# 第四部分：主程序
# ============================================================================

def main():
    """主函数"""
    print("\n" + "="*60)
    print("      DNA四轨道分析系统 v1.1")
    print("="*60)
    print("说明: 将DNA序列(A,C,G,T)转换为数字并分析")
    print("增强功能: 支持从文件和目录加载DNA序列")
    print()
    
    # 创建分析系统
    system = DNAFourTrackSystem()
    
    # 示例DNA序列
    example_sequences = {
        "启动子序列": "ATCGATCGATCGATCGATCG",
        "高GC区域": "GGGCCCGGGCCCGGGCCCGG",
        "重复序列": "AGCTAGCTAGCTAGCTAGCT",
        "回文序列": "GAATTCCTTAAGGAATTCCTTAAG"
    }
    
    print("📋 示例序列:")
    for i, (name, seq) in enumerate(example_sequences.items(), 1):
        print(f"  {i}. {name}: {seq}")
    print()
    
    while True:
        print("\n请选择操作:")
        print("  1. 分析示例序列")
        print("  2. 输入自定义DNA序列")
        print("  3. 批量分析所有示例")
        print("  4. 从文件加载DNA序列")
        print("  5. 批量分析目录中的DNA文件")
        print("  6. 退出")
        
        choice = input("请输入选择 (1-6): ").strip()
        
        if choice == '1':
            print("\n选择要分析的示例序列:")
            for i, name in enumerate(example_sequences.keys(), 1):
                print(f"  {i}. {name}")
            
            try:
                seq_choice = int(input("请输入编号 (1-4): ").strip()) - 1
                seq_names = list(example_sequences.keys())
                if 0 <= seq_choice < len(seq_names):
                    name = seq_names[seq_choice]
                    seq = example_sequences[name]
                    
                    result = system.analyze(seq, name)
                    system.print_report(result)
                    
                    # 保存选项
                    save = input("是否保存结果到文件? (y/n): ").strip().lower()
                    if save == 'y':
                        filename = f"result_{name}.json"
                        system.save_results({name: result}, filename)
                else:
                    print("❌ 无效的选择")
            except ValueError:
                print("❌ 请输入有效数字")
        
        elif choice == '2':
            print("\n请输入DNA序列 (只包含A,C,G,T):")
            dna_input = input("DNA序列: ").strip()
            name = input("序列名称 (可选): ").strip()
            
            if not name:
                name = "自定义序列"
            
            if not dna_input:
                print("❌ 序列不能为空")
                continue
            
            result = system.analyze(dna_input, name)
            system.print_report(result)
            
            save = input("是否保存结果到文件? (y/n): ").strip().lower()
            if save == 'y':
                filename = f"result_{name}.json"
                system.save_results({name: result}, filename)
        
        elif choice == '3':
            print("\n开始批量分析所有示例序列...")
            results = system.batch_analyze(example_sequences)
            
            # 打印比较结果
            if '_comparison' in results:
                comp = results['_comparison']
                print("\n📈 比较分析:")
                print(f"  GC含量范围: {comp['gc_stats']['min']:.3f}-{comp['gc_stats']['max']:.3f}")
                print(f"  平均GC含量: {comp['gc_stats']['avg']:.3f}")
                
                if comp['similar_groups']:
                    print("  相似组:")
                    for group in comp['similar_groups']:
                        print(f"    {group['group']}: {', '.join(group['sequences'])}")
            
            save = input("\n是否保存所有结果到文件? (y/n): ").strip().lower()
            if save == 'y':
                filename = "batch_results.json"
                if system.save_results(results, filename):
                    print(f"✅ 结果已保存到 {filename}")
        
        elif choice == '4':
            print("\n从文件加载DNA序列")
            print("请输入文件路径，或按Enter使用默认目录 (data/dna):")
            file_path = input("文件路径: ").strip()
            
            if not file_path:
                # 使用默认目录
                default_dir = "data/dna"
                if os.path.exists(default_dir):
                    files = [f for f in os.listdir(default_dir) if f.endswith('.txt')]
                    if files:
                        print(f"\n默认目录 ({default_dir}) 中的文件:")
                        for i, f in enumerate(files, 1):
                            print(f"  {i}. {f}")
                        
                        try:
                            file_choice = int(input("请选择文件编号: ").strip()) - 1
                            if 0 <= file_choice < len(files):
                                selected_file = files[file_choice]
                                file_path = os.path.join(default_dir, selected_file)
                                print(f"\n选择的文件: {file_path}")
                            else:
                                print("❌ 无效的选择")
                                continue
                        except ValueError:
                            print("❌ 请输入有效数字")
                            continue
                    else:
                        print(f"❌ 默认目录中没有找到.txt文件")
                        continue
                else:
                    print(f"❌ 默认目录 {default_dir} 不存在")
                    continue
            
            if os.path.exists(file_path):
                try:
                    dna_seq = system.load_from_file(file_path)
                    filename = os.path.basename(file_path)
                    result = system.analyze(dna_seq, filename)
                    system.print_report(result)
                    
                    save = input("是否保存结果到文件? (y/n): ").strip().lower()
                    if save == 'y':
                        output_file = f"result_{filename.replace('.txt', '')}.json"
                        system.save_results({filename: result}, output_file)
                except Exception as e:
                    print(f"❌ 加载文件失败: {e}")
            else:
                print(f"❌ 文件不存在: {file_path}")
        
        elif choice == '5':
            print("\n批量分析目录中的DNA文件")
            print("请输入目录路径，或按Enter使用默认目录 (data/dna):")
            directory = input("目录路径: ").strip()
            
            if not directory:
                directory = "data/dna"
            
            if os.path.exists(directory):
                try:
                    sequences = system.load_from_directory(directory)
                    if sequences:
                        print(f"\n找到 {len(sequences)} 个DNA文件:")
                        for i, filename in enumerate(sequences.keys(), 1):
                            print(f"  {i}. {filename}")
                        
                        confirm = input("\n是否分析所有文件? (y/n): ").strip().lower()
                        if confirm == 'y':
                            results = system.batch_analyze(sequences)
                            
                            # 打印比较结果
                            if '_comparison' in results:
                                comp = results['_comparison']
                                print("\n📈 比较分析:")
                                print(f"  GC含量范围: {comp['gc_stats']['min']:.3f}-{comp['gc_stats']['max']:.3f}")
                                print(f"  平均GC含量: {comp['gc_stats']['avg']:.3f}")
                                
                                if comp['similar_groups']:
                                    print("  相似组:")
                                    for group in comp['similar_groups']:
                                        print(f"    {group['group']}: {', '.join(group['sequences'])}")
                            
                            save = input("\n是否保存所有结果到文件? (y/n): ").strip().lower()
                            if save == 'y':
                                output_file = "batch_directory_results.json"
                                if system.save_results(results, output_file):
                                    print(f"✅ 结果已保存到 {output_file}")
                    else:
                        print(f"❌ 目录中没有找到有效的DNA文件")
                except Exception as e:
                    print(f"❌ 加载目录失败: {e}")
            else:
                print(f"❌ 目录不存在: {directory}")
        
        elif choice == '6':
            print("\n谢谢使用，再见！")
            break
        
        else:
            print("❌ 无效的选择，请重新输入")

if __name__ == "__main__":
    main()

