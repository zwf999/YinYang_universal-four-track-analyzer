#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用四轨道分析系统
既能分析DNA序列，也能分析数字常数文件
"""

import os
import json
import re
from typing import List, Dict, Any, Tuple
from collections import Counter
from datetime import datetime

# ============================================================================
# 1. 通用数字分析器（用于数字常数文件）
# ============================================================================

class UniversalEncoder:
    """通用编码器：处理DNA和数字"""
    
    def __init__(self):
        # DNA编码部分：新的一步映射（用户提供的原始设计）
        self.basepair_to_num = {
            'AA': 0, 'AC': 1, 'AG': 2, 'AT': 3,
            'CA': 1, 'CC': 4, 'CG': 5, 'CT': 6,
            'GA': 2, 'GC': 5, 'GG': 7, 'GT': 8,
            'TA': 3, 'TC': 6, 'TG': 8, 'TT': 9
        }
        
        # 反向映射：数字到碱基对（用户提供的原始设计）
        self.num_to_basepair = {
            0: 'AA', 1: 'AC', 2: 'AG', 3: 'AT',
            4: 'CC', 5: 'CG', 6: 'CT', 7: 'GG',
            8: 'GT', 9: 'TT'
        }
        
        # 碱基到0-3的映射（仅用于兼容旧代码）
        self.base_to_num = {'A': 0, 'C': 1, 'G': 2, 'T': 3}
    
    def encode_dna(self, dna_sequence: str) -> Dict[str, Any]:
        """编码DNA序列"""
        dna_seq = self._clean_dna_sequence(dna_sequence)
        
        digits = []
        details = []
        
        i = 0
        while i < len(dna_seq):
            # 处理碱基对（序列已确保为偶数长度）
            basepair = dna_seq[i:i+2]
            
            # 使用新的一步映射：直接从碱基对获取编码
            code = self.basepair_to_num[basepair]
            
            # 确定方向（正序/逆序）
            # 根据碱基对与默认映射的关系确定方向
            default_basepair = self.num_to_basepair[code]
            is_forward = (basepair == default_basepair)
            direction = 'forward' if is_forward else 'reverse'
            direction_mark = '' if is_forward else '←'  # 正序不标注，逆序用←标记
            
            digits.append(code)
            details.append({
                'bases': basepair,
                'code': code,
                'direction': direction,
                'direction_mark': direction_mark
            })
            i += 2
        
        # 统计
        gc_count = dna_seq.count('G') + dna_seq.count('C')
        total = len(dna_seq)
        
        stats = {
            'length': total,
            'gc_content': gc_count / total if total > 0 else 0,
            'gc_count': gc_count,
            'at_count': total - gc_count,
            'type': 'dna',
            'digit_counts': dict(Counter(digits)),
            'unique_digits': len(set(digits)),
            'encoded_length': len(digits)
        }
        
        return {
            'original': dna_seq[:100] + ('...' if len(dna_seq) > 100 else ''),
            'digits': digits,
            'details': details,
            'stats': stats
        }
    
    def encode_numbers(self, number_str: str) -> Dict[str, Any]:
        """编码数字字符串（直接提取0-9数字）"""
        # 提取所有数字
        digits = []
        for char in number_str:
            if char.isdigit():
                digits.append(int(char))
        
        # 统计
        digit_counts = Counter(digits)
        
        stats = {
            'length': len(number_str),
            'digit_length': len(digits),
            'type': 'numbers',
            'digit_counts': dict(digit_counts),
            'unique_digits': len(set(digits)),
            'digit_ratio': len(digits) / len(number_str) if number_str else 0
        }
        
        return {
            'original': number_str[:100] + ('...' if len(number_str) > 100 else ''),
            'digits': digits,
            'stats': stats
        }
    
    def _clean_dna_sequence(self, seq: str) -> str:
        """清理DNA序列"""
        seq = seq.upper().strip()
        seq = ''.join(seq.split())
        
        # 检查是否是DNA（只包含ACGT）
        dna_chars = set('ACGT')
        non_dna_chars = [c for c in seq if c not in dna_chars]
        
        if non_dna_chars:
            # 如果有非DNA字符，尝试只提取DNA部分
            dna_only = ''.join([c for c in seq if c in dna_chars])
            if len(dna_only) > 0:
                seq = dna_only
            else:
                raise ValueError("没有找到有效的DNA字符")
        
        # 确保序列为偶数长度（全是碱基对）
        if len(seq) % 2 != 0:
            # 截断最后一个碱基
            seq = seq[:-1]
            print("警告：序列长度为奇数，已截断最后一个碱基")
        
        return seq

# ============================================================================
# 2. 四轨道分析器
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
            'track4': {0: '五', 1: '一', 2: '二', 3: '三', 4: '四', 5: '二', 6: '三', 7: '四', 8: '一', 9: '五'}
        }
        
        # 轨道2-4阴阳分类
        self.yinyang_class = {
            'track2': {'yang': {'A', 'C', 'E'}, 'yin': {'B', 'D'}},
            'track3': {'yang': {'甲', '丙', '戊'}, 'yin': {'乙', '丁'}},
            'track4': {'yang': {'一', '三', '五'}, 'yin': {'二', '四'}}
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
# 3. 文件处理器
# ============================================================================

class FileProcessor:
    """文件处理器"""
    
    def __init__(self):
        self.encoder = UniversalEncoder()
        self.analyzer = FourTrackAnalyzer()
        
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """处理单个文件"""
        try:
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 判断文件类型
            file_type = self._detect_file_type(content)
            
            if file_type == 'dna':
                # DNA序列
                encoding = self.encoder.encode_dna(content)
                analysis = self.analyzer.analyze(encoding['digits'])
            else:
                # 数字常数
                encoding = self.encoder.encode_numbers(content)
                analysis = self.analyzer.analyze(encoding['digits'])
            
            # 构建结果
            filename = os.path.basename(file_path)
            result = {
                'metadata': {
                    'file_path': file_path,
                    'filename': filename,
                    'display_name': filename,
                    'type': file_type,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                'encoding': encoding,
                'analysis': analysis
            }
            
            return result
            
        except Exception as e:
            filename = os.path.basename(file_path)
            return {
                'metadata': {
                    'file_path': file_path,
                    'filename': filename,
                    'display_name': filename
                },
                'error': str(e)
            }
    
    def _detect_file_type(self, content: str) -> str:
        """检测文件类型"""
        # 清理内容
        cleaned = content.strip().upper()
        cleaned = ''.join(cleaned.split())
        
        # 检查是否为DNA
        if len(cleaned) > 0:
            # 检查前100个字符
            sample = cleaned[:100]
            dna_chars = set('ACGT')
            non_dna_chars = [c for c in sample if c not in dna_chars]
            
            # 如果超过90%是DNA字符，认为是DNA文件
            if len(sample) > 0:
                dna_ratio = (len(sample) - len(non_dna_chars)) / len(sample)
                if dna_ratio > 0.9:
                    return 'dna'
        
        return 'numbers'
    
    def save_results(self, filename: str, results: Dict[str, Any]):
        """保存结果到文件"""
        # 确保results目录存在
        os.makedirs('results', exist_ok=True)
        
        filepath = os.path.join('results', filename)
        
        # 保存为JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def save_summary_csv(self, all_results: Dict[str, Any]) -> str:
        """保存摘要为CSV"""
        # 确保reports目录存在
        os.makedirs('reports', exist_ok=True)
        
        csv_path = os.path.join('reports', 'analysis_summary.csv')
        
        with open(csv_path, 'w', encoding='utf-8') as f:
            # 写入表头
            f.write('File,Type,Length,GC Content,Track1 Pairing,Track2 Pairing,Track3 Pairing,Track4 Pairing,Avg Symmetry,Best Track,Error\n')
            
            for name, result in all_results.items():
                if 'error' in result:
                    f.write(f"{name},,,0,0,0,0,0,0,,{result['error']}\n")
                    continue
                
                metadata = result['metadata']
                encoding = result['encoding']
                analysis = result['analysis']
                
                # 提取数据
                file_type = metadata.get('type', 'unknown')
                length = encoding['stats'].get('length', 0)
                gc_content = encoding['stats'].get('gc_content', 0)
                
                track1_pairing = analysis.get('track1', {}).get('forward', {}).get('symbol_pairs', {}).get('ratio', 0)
                track2_pairing = analysis.get('track2', {}).get('forward', {}).get('global_digit_pairs', {}).get('ratio', 0)
                track3_pairing = analysis.get('track3', {}).get('forward', {}).get('global_digit_pairs', {}).get('ratio', 0)
                track4_pairing = analysis.get('track4', {}).get('forward', {}).get('global_digit_pairs', {}).get('ratio', 0)
                
                avg_symmetry = analysis.get('summary', {}).get('average_symmetry', 0)
                best_track = analysis.get('summary', {}).get('best_track', '')
                
                # 写入数据
                f.write(f"{name},{file_type},{length},{gc_content},{track1_pairing},{track2_pairing},{track3_pairing},{track4_pairing},{avg_symmetry},{best_track},\n")
        
        return csv_path

# ============================================================================
# 4. 主程序
# ============================================================================

def main():
    """主程序"""
    print("\n" + "="*80)
    print("                 通用四轨道分析系统")
    print("                 既能分析DNA序列，也能分析数字常数文件")
    print("="*80)
    print()
    
    # 初始化
    file_processor = FileProcessor()
    analyzer = FourTrackAnalyzer()
    
    # 查找所有可能的文件
    print("🔍 搜索文件...")
    
    # 搜索data目录
    data_files = []
    if os.path.exists('data'):
        for root, dirs, files in os.walk('data'):
            for file in files:
                if file.endswith(('.txt', '.dat')):
                    data_files.append(os.path.join(root, file))
    
    if not data_files:
        print("❌ 错误: 没有找到任何数据文件")
        print("请在data目录中放置.txt或.dat文件")
        return
    
    print(f"✅ 找到 {len(data_files)} 个文件")
    print()
    
    # 处理文件
    print("📊 分析文件...")
    print("=" * 80)
    
    all_results = {}
    successful = 0
    failed = 0
    skipped = 0
    total_files = len(data_files)
    
    for i, file_path in enumerate(data_files, 1):
        filename = os.path.basename(file_path)
        print(f"\n{i}/{total_files}. 处理: {filename}")
        
        try:
            # 处理文件
            result = file_processor.process_file(file_path)
            
            if 'error' in result:
                print(f"  ❌ 失败: {result['error']}")
                failed += 1
                continue
            
            # 保存到总结果
            all_results[result['metadata']['display_name']] = result
            successful += 1
            
            # 显示简要结果
            analysis = result['analysis']
            track1_score = analysis['track1']['forward']['symbol_pairs']['ratio']
            file_type = result['metadata']['type']
            
            if file_type in ['dna', 'dna_mixed']:
                gc = result['encoding']['stats']['gc_content']
                print(f"  ✅ 完成: GC={gc:.2%}, 轨道1配对={track1_score:.2%}")
            else:
                digits = len(result['encoding']['digits'])
                print(f"  ✅ 完成: {digits}个数字, 轨道1配对={track1_score:.2%}")
        
        except Exception as e:
            error_msg = str(e)
            if len(error_msg) > 80:
                error_msg = error_msg[:80] + "..."
            print(f"  ❌ 异常: {error_msg}")
            failed += 1
            print()
    
    print("=" * 80)
    print(f"📊 分析完成统计:")
    print(f"  ✅ 成功: {successful} 个")
    print(f"  ❌ 失败: {failed} 个")
    print(f"  ⚠️  跳过: {skipped} 个")
    print(f"  📁 总计: {total_files} 个文件")
    print()
    
    # 保存结果
    if all_results:
        # 保存所有结果
        all_results_file = "universal_results.json"
        file_processor.save_results(all_results_file, all_results)
        print(f"📁 详细结果保存在: results/{all_results_file}")
        
        # 生成并保存CSV摘要
        csv_path = file_processor.save_summary_csv(all_results)
        print(f"📊 CSV摘要保存在: {csv_path}")
        
        # 生成比较报告
        comparison = analyzer.generate_comparison_report(all_results)
        comparison_file = "universal_comparison.txt"
        with open(os.path.join('reports', comparison_file), 'w', encoding='utf-8') as f:
            f.write(comparison)
        print(f"📈 比较报告保存在: reports/{comparison_file}")
        
        # 显示关键统计
        print("\n" + "="*80)
        print(comparison)
    
    print("\n" + "="*80)
    print("分析完成！所有结果已保存到 results/ 和 reports/ 文件夹")
    print("="*80)

# ============================================================================
# 运行程序
# ============================================================================

if __name__ == "__main__":
    main()
