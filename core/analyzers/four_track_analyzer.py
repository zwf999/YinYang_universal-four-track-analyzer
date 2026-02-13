# core/analyzers/four_track_analyzer.py
# 四轨道分析器

from typing import Dict, List, Any
from core.analyzers.base_analyzer import BaseAnalyzer

class FourTrackAnalyzer(BaseAnalyzer):
    """四轨道分析器"""
    
    def __init__(self):
        """初始化四轨道分析器"""
        # 数字属性映射表（用于轨道1）
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
        
        # 八卦系统九和配对规则
        self.bagua_pairing = {
            1: 8,
            2: 7,
            3: 6,
            4: 5,
            5: 4,
            6: 3,
            7: 2,
            8: 1
        }
        
        # 八态编码表（二进制到状态ID映射）
        self.state_encoding = {
            '111': 1, '110': 2, '101': 3, '100': 4,
            '011': 5, '010': 6, '001': 7, '000': 8
        }
        
        # 轨道2-4的映射规则
        self.track_mappings = {
            'track2': {0: 'E', 1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'D', 6: 'C', 7: 'B', 8: 'A', 9: 'E'},
            'track3': {0: '戊', 1: '甲', 2: '乙', 3: '丙', 4: '丁', 5: '戊', 6: '丁', 7: '丙', 8: '乙', 9: '甲'},
            'track4': {0: '癸', 1: '己', 2: '庚', 3: '辛', 4: '壬', 5: '庚', 6: '辛', 7: '壬', 8: '己', 9: '癸'}
        }
        
        # 轨道2-4的阴阳分类
        self.yinyang_classifications = {
            'track2': {'yang': {'A', 'C', 'E'}, 'yin': {'B', 'D'}},
            'track3': {'yang': {'甲', '丙', '戊'}, 'yin': {'乙', '丁'}},
            'track4': {'yang': {'己', '辛', '癸'}, 'yin': {'庚', '壬'}}
        }
        
        # 预计算符号缓存
        self._cached_symbols = {}
        for track_name in ['track2', 'track3', 'track4']:
            self._cached_symbols[track_name] = [
                self.track_mappings[track_name][i] for i in range(10)
            ]
        
        # 验证配置
        self._validate_initialization()
    
    def analyze(self, digits: List[int]) -> Dict[str, Any]:
        """
        分析数字序列
        
        Args:
            digits: 数字序列
            
        Returns:
            分析结果
        """
        try:
            # 验证输入
            if not self.validate_input(digits):
                return self._create_error_response("输入验证失败")
            
            # 验证配置
            config_valid, config_errors = self.validate_configuration()
            if not config_valid:
                return self._create_error_response(f"配置错误: {config_errors}")
            
            digits = self.preprocess(digits)
            
            # 生成反向序列
            reversed_digits = digits[::-1]
            
            # 分析所有轨道（正向和反向）
            results = {}
            for track in ['track1', 'track2', 'track3', 'track4']:
                # 正向分析
                forward_result = self._analyze_track(digits, track)
                # 反向分析
                backward_result = self._analyze_track(reversed_digits, track)
                # 计算对称性指标
                symmetry = self._calculate_symmetry(forward_result, backward_result)
                
                # 整合结果
                results[track] = {
                    'forward': forward_result,
                    'backward': backward_result,
                    'symmetry': symmetry
                }
            
            # 分析数字本身的直接配对（正向和反向）
            direct_results = {}
            for track in ['track2', 'track3', 'track4']:
                # 正向分析
                forward_pairing = self._analyze_direct_pairing(digits, track)
                # 反向分析
                backward_pairing = self._analyze_direct_pairing(reversed_digits, track)
                # 计算对称性指标
                pairing_symmetry = self._calculate_pairing_symmetry(forward_pairing, backward_pairing)
                
                # 整合结果
                direct_results[track] = {
                    'forward': forward_pairing,
                    'backward': backward_pairing,
                    'symmetry': pairing_symmetry
                }
            
            results['direct_pairing'] = direct_results
            results['fingerprint'] = self._generate_digital_fingerprint(results)
            results['reverse_analysis'] = self._generate_reverse_analysis_summary(results)
            
            return results
        except Exception as e:
            return self._create_error_response(f"分析过程中发生错误: {str(e)}")
    
    def _analyze_track(self, sequence: List[int], track_name: str) -> Dict[str, Any]:
        """分析单个轨道"""
        if len(sequence) < 2:
            return {
                'window_count': 0,
                'symbol_pairs': {'valid_pairs': 0, 'total_pairs': 0, 'pair_ratio': 0},
                'digit_pairs': {'valid_pairs': 0, 'total_pairs': 0, 'pair_ratio': 0},
                'global_digit_pairs': {'valid_pairs': 0, 'total_pairs': 0, 'pair_ratio': 0, 'pair_types': {}, 'unpaired': {}},
                'yinyang': {'yang_count': 0, 'yin_count': 0, 'ratio': 0, 'yang_percent': 0}
            }
        
        # 对于轨道1，继续使用原来的窗口分析方法
        if track_name == 'track1':
            # 处理所有窗口
            windows = []
            for i in range(0, len(sequence) - 11 + 1):
                window = sequence[i:i+12]
                if len(window) == 12:
                    states = self._process_window(window, track_name)
                    windows.append(states)
            
            # 计算符号映射的配对（原九和配对）
            symbol_valid = 0
            symbol_total = 0
            for states in windows:
                pair_result = self._calculate_nine_sum_pairs(states, track_name)
                symbol_valid += pair_result['valid_pairs']
                symbol_total += pair_result['total_pairs']
            
            symbol_result = {
                'valid_pairs': symbol_valid,
                'total_pairs': symbol_total,
                'pair_ratio': symbol_valid / symbol_total if symbol_total > 0 else 0
            }
            
            # 计算数字本身的直接配对
            digit_result = self._calculate_digit_pairs(sequence, track_name)
            
            # 计算阴阳状态
            yinyang_result = self._calculate_yinyang(sequence, track_name)
            
            return {
                'window_count': len(windows),
                'symbol_pairs': symbol_result,
                'digit_pairs': digit_result,
                'global_digit_pairs': {'valid_pairs': 0, 'total_pairs': 0, 'pair_ratio': 0, 'pair_types': {}, 'unpaired': {}},
                'yinyang': yinyang_result
            }
        else:
            # 对于轨道2-4，只使用全局直接配对分析
            global_pairs_result = self._analyze_global_digit_pairs(sequence, track_name)
            
            # 计算阴阳状态
            yinyang_result = self._calculate_yinyang(sequence, track_name)
            
            return {
                'window_count': 0,
                'symbol_pairs': {'valid_pairs': 0, 'total_pairs': 0, 'pair_ratio': 0},
                'digit_pairs': {'valid_pairs': 0, 'total_pairs': 0, 'pair_ratio': 0},
                'global_digit_pairs': global_pairs_result,
                'yinyang': yinyang_result
            }
    
    def _process_window(self, window: List[int], track_name: str) -> Dict[str, Any]:
        """处理单个窗口，生成状态"""
        # 分割为四个3位子序列
        p1 = window[0:3]
        p2 = window[3:6]
        p3 = window[6:9]
        p4 = window[9:12]
        
        states = {}
        
        if track_name == 'track1':
            # 轨道1：四个维度
            dimensions = ['small_large', 'up_down', 'odd_even', 'ab_relation']
            for dim in dimensions:
                states[dim] = {
                    'p1': self._generate_track1_states(p1, dim),
                    'p2': self._generate_track1_states(p2, dim),
                    'p3': self._generate_track1_states(p3, dim),
                    'p4': self._generate_track1_states(p4, dim)
                }
        else:
            # 轨道2-4：单一状态
            states['main'] = {
                'p1': self._generate_track_state(p1, track_name),
                'p2': self._generate_track_state(p2, track_name),
                'p3': self._generate_track_state(p3, track_name),
                'p4': self._generate_track_state(p4, track_name)
            }
        
        return states
    
    def _generate_track1_states(self, subseq: List[int], dimension: str) -> int:
        """生成轨道1的状态"""
        attributes = [self.number_attributes[num][dimension] for num in subseq]
        binary_str = ''.join(map(str, attributes))
        return self._binary_to_state_id(binary_str)
    
    def _generate_track_state(self, subseq: List[int], track_name: str) -> int:
        """生成轨道2-4的状态"""
        mapping = self.track_mappings[track_name]
        symbols = [mapping[num] for num in subseq]
        
        # 为每个符号生成二进制表示
        yinyang_class = self.yinyang_classifications[track_name]
        binary_values = [1 if s in yinyang_class['yang'] else 0 for s in symbols]
        binary_str = ''.join(map(str, binary_values))
        
        return self._binary_to_state_id(binary_str)
    
    def _binary_to_state_id(self, binary_str: str) -> int:
        """将3位二进制映射到状态ID"""
        if len(binary_str) != 3:
            return 1
        return self.state_encoding.get(binary_str, 1)
    
    def _calculate_nine_sum_pairs(self, states: Dict[str, Any], track_name: str) -> Dict[str, Any]:
        """计算九和配对"""
        valid_pairs = 0
        total_pairs = 0
        
        if track_name == 'track1':
            # 轨道1：四个维度
            for dim, parts in states.items():
                # P1与P3配对（使用八卦系统规则）
                if self.bagua_pairing.get(parts['p1']) == parts['p3']:
                    valid_pairs += 1
                total_pairs += 1
                # P2与P4配对（使用八卦系统规则）
                if self.bagua_pairing.get(parts['p2']) == parts['p4']:
                    valid_pairs += 1
                total_pairs += 1
        else:
            # 轨道2-4：单一状态
            parts = states['main']
            # P1与P3配对（使用状态ID直接比较，状态1-8）
            if parts['p1'] == parts['p3']:
                valid_pairs += 1
            total_pairs += 1
            # P2与P4配对（使用状态ID直接比较，状态1-8）
            if parts['p2'] == parts['p4']:
                valid_pairs += 1
            total_pairs += 1
        
        pair_ratio = valid_pairs / total_pairs if total_pairs > 0 else 0
        return {
            'valid_pairs': valid_pairs,
            'total_pairs': total_pairs,
            'pair_ratio': pair_ratio
        }
    
    def _calculate_digit_pairs(self, digits: List[int], track_name: str) -> Dict[str, Any]:
        """计算数字本身的直接配对"""
        valid_pairs = 0
        total_pairs = 0
        
        # 每两个数字一对
        for i in range(0, len(digits) - 1, 2):
            if i + 1 < len(digits):
                d1 = digits[i]
                d2 = digits[i+1]
                
                # 根据轨道选择配对规则
                if self._is_valid_digit_pair(d1, d2, track_name):
                    valid_pairs += 1
                total_pairs += 1
        
        return {
            'valid_pairs': valid_pairs,
            'total_pairs': total_pairs,
            'pair_ratio': valid_pairs / total_pairs if total_pairs > 0 else 0
        }
    
    def _is_valid_digit_pair(self, d1: int, d2: int, track_name: str) -> bool:
        """检查数字对是否有效"""
        if track_name == 'track2':
            # 轨道2：和=9
            valid_pairs = {
                (1, 8): True, (8, 1): True,
                (2, 7): True, (7, 2): True,
                (3, 6): True, (6, 3): True,
                (4, 5): True, (5, 4): True,
                (9, 0): True, (0, 9): True
            }
            return valid_pairs.get((d1, d2), False)
        
        elif track_name == 'track3':
            # 轨道3：和=10
            valid_pairs = {
                (1, 9): True, (9, 1): True,
                (2, 8): True, (8, 2): True,
                (3, 7): True, (7, 3): True,
                (4, 6): True, (6, 4): True,
                (5, 0): True, (0, 5): True
            }
            return valid_pairs.get((d1, d2), False)
        
        elif track_name == 'track4':
            # 轨道4：特定组合
            valid_pairs = {
                (1, 8): True, (8, 1): True,
                (2, 5): True, (5, 2): True,
                (3, 6): True, (6, 3): True,
                (4, 7): True, (7, 4): True,
                (9, 0): True, (0, 9): True
            }
            return valid_pairs.get((d1, d2), False)
        
        else:
            # 轨道1：不使用数字配对
            return False
    
    def _calculate_yinyang(self, sequence: List[int], track_name: str) -> Dict[str, Any]:
        """计算阴阳状态和比例"""
        if track_name == 'track1':
            # 轨道1的阴阳计算：小数字(1-7)为阳，大数字(0,8,9)为阴
            yang_count = sum(1 for num in sequence if 1 <= num <= 7)
            yin_count = len(sequence) - yang_count
        else:
            # 轨道2-4的阴阳计算
            yinyang_class = self.yinyang_classifications[track_name]
            
            symbols = self._get_symbols(track_name, sequence)
            yang_count = sum(1 for s in symbols if s in yinyang_class['yang'])
            yin_count = sum(1 for s in symbols if s in yinyang_class['yin'])
        
        ratio = yang_count / yin_count if yin_count > 0 else float('inf')
        
        return {
            'yang_count': yang_count,
            'yin_count': yin_count,
            'ratio': ratio,
            'yang_percent': yang_count / len(sequence) if sequence else 0
        }
    
    def _analyze_direct_pairing(self, sequence: List[int], track_name: str) -> Dict[str, Any]:
        """分析数字本身的直接配对"""
        if len(sequence) < 2:
            return {
                'valid_pairs': 0,
                'total_pairs': 0,
                'pair_ratio': 0,
                'unpaired_count': 0
            }
        
        # 全局配对分析
        total_pairs = len(sequence) // 2
        valid_pairs = 0
        
        for i in range(0, len(sequence) - 1, 2):
            d1 = sequence[i]
            d2 = sequence[i+1]
            
            # 根据轨道选择配对规则
            if self._is_valid_digit_pair(d1, d2, track_name):
                valid_pairs += 1
        
        unpaired_count = len(sequence) % 2
        
        return {
            'valid_pairs': valid_pairs,
            'total_pairs': total_pairs,
            'pair_ratio': valid_pairs / total_pairs if total_pairs > 0 else 0,
            'unpaired_count': unpaired_count
        }
    
    def _analyze_global_digit_pairs(self, digits: List[int], track_name: str) -> Dict[str, Any]:
        """分析数字本身的全局直接配对"""
        from collections import Counter
        
        # 统计数字出现次数
        digit_count = Counter(digits)
        
        # 复制计数器用于配对分析
        remaining_digits = Counter(digits)
        
        # 配对结果
        valid_pairs = 0
        pair_types = {}
        unpaired = {}
        
        # 根据轨道选择配对规则
        if track_name == 'track2':
            # 轨道2：和=9的配对
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
            # 轨道3：和=10的配对
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
            # 轨道4：特定组合的配对
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
        else:
            return {
                'valid_pairs': 0,
                'total_pairs': 0,
                'pair_ratio': 0,
                'pair_types': {},
                'unpaired': {}
            }
        
        # 执行配对分析
        for pair, pair_type, yinyang in pair_rules:
            d1, d2 = pair
            
            # 计算可以形成的配对数量
            if d1 == d2:
                # 相同数字配对（如5和5）
                pair_count = remaining_digits[d1] // 2
            else:
                # 不同数字配对
                pair_count = min(remaining_digits[d1], remaining_digits[d2])
            
            if pair_count > 0:
                valid_pairs += pair_count
                
                # 更新配对类型统计
                if pair_type not in pair_types:
                    pair_types[pair_type] = {'count': 0, 'yinyang': yinyang}
                pair_types[pair_type]['count'] += pair_count
                
                # 更新剩余数字
                if d1 == d2:
                    remaining_digits[d1] -= pair_count * 2
                else:
                    remaining_digits[d1] -= pair_count
                    remaining_digits[d2] -= pair_count
        
        # 统计未配对的数字
        for digit, count in remaining_digits.items():
            if count > 0:
                unpaired[digit] = count
        
        # 计算总可能的配对数
        total_pairs = len(digits) // 2
        
        return {
            'valid_pairs': valid_pairs,
            'total_pairs': total_pairs,
            'pair_ratio': valid_pairs / total_pairs if total_pairs > 0 else 0,
            'pair_types': pair_types,
            'unpaired': unpaired
        }
    
    def _generate_digital_fingerprint(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成数字指纹"""
        fingerprint = {}
        
        for track_name, track_result in results.items():
            if track_name != 'direct_pairing' and track_name != 'fingerprint' and track_name != 'reverse_analysis':
                # 提取正向分析结果
                forward_result = track_result['forward']
                # 提取反向分析结果
                backward_result = track_result['backward']
                # 提取对称性结果
                symmetry_result = track_result['symmetry']
                
                fingerprint[track_name] = {
                    'forward': {
                        'pair_ratio': forward_result['symbol_pairs']['pair_ratio'],
                        'yinyang_ratio': forward_result['yinyang']['ratio'],
                        'yang_percent': forward_result['yinyang']['yang_percent'],
                        'window_count': forward_result['window_count'],
                        'global_digit_pair_ratio': forward_result.get('global_digit_pairs', {}).get('pair_ratio', 0),
                        'global_digit_pair_types': forward_result.get('global_digit_pairs', {}).get('pair_types', {}),
                        'global_digit_unpaired': forward_result.get('global_digit_pairs', {}).get('unpaired', {})
                    },
                    'backward': {
                        'pair_ratio': backward_result['symbol_pairs']['pair_ratio'],
                        'yinyang_ratio': backward_result['yinyang']['ratio'],
                        'yang_percent': backward_result['yinyang']['yang_percent'],
                        'window_count': backward_result['window_count'],
                        'global_digit_pair_ratio': backward_result.get('global_digit_pairs', {}).get('pair_ratio', 0),
                        'global_digit_pair_types': backward_result.get('global_digit_pairs', {}).get('pair_types', {}),
                        'global_digit_unpaired': backward_result.get('global_digit_pairs', {}).get('unpaired', {})
                    },
                    'symmetry': {
                        'overall_symmetry': symmetry_result['overall_symmetry'],
                        'pair_ratio_similarity': symmetry_result['pair_ratio_similarity'],
                        'yang_percent_similarity': symmetry_result['yang_percent_similarity']
                    }
                }
        
        # 添加数字直接配对的结果
        if 'direct_pairing' in results:
            fingerprint['direct_pairing'] = {}
            for track_name, direct_result in results['direct_pairing'].items():
                forward_pairing = direct_result['forward']
                backward_pairing = direct_result['backward']
                symmetry = direct_result['symmetry']
                
                fingerprint['direct_pairing'][track_name] = {
                    'forward': {
                        'pair_ratio': forward_pairing['pair_ratio'],
                        'valid_pairs': forward_pairing['valid_pairs'],
                        'total_pairs': forward_pairing['total_pairs'],
                        'unpaired_count': forward_pairing['unpaired_count']
                    },
                    'backward': {
                        'pair_ratio': backward_pairing['pair_ratio'],
                        'valid_pairs': backward_pairing['valid_pairs'],
                        'total_pairs': backward_pairing['total_pairs'],
                        'unpaired_count': backward_pairing['unpaired_count']
                    },
                    'symmetry': {
                        'pair_ratio_similarity': symmetry['pair_ratio_similarity'],
                        'valid_pairs_diff': symmetry['valid_pairs_diff']
                    }
                }
        
        return fingerprint
    
    def get_name(self) -> str:
        """获取分析器名称"""
        return "FourTrackAnalyzer"
    
    def get_version(self) -> str:
        """获取分析器版本"""
        return "4.0.0"
    
    def _validate_initialization(self):
        """验证初始化配置"""
        # 验证八卦配对规则
        for i in range(1, 9):
            if i not in self.bagua_pairing:
                raise ValueError(f"八卦配对规则缺少状态 {i}")
        
        # 验证数字属性
        for i in range(10):
            if i not in self.number_attributes:
                raise ValueError(f"数字 {i} 缺少属性定义")
            required_dims = ['small_large', 'up_down', 'odd_even', 'ab_relation']
            for dim in required_dims:
                if dim not in self.number_attributes[i]:
                    raise ValueError(f"数字 {i} 缺少维度 {dim}")
    
    def validate_configuration(self):
        """验证所有配置的完整性"""
        errors = []
        
        # 验证 number_attributes
        for i in range(10):
            if i not in self.number_attributes:
                errors.append(f"数字 {i} 缺少属性定义")
            else:
                required_dims = ['small_large', 'up_down', 'odd_even', 'ab_relation']
                for dim in required_dims:
                    if dim not in self.number_attributes[i]:
                        errors.append(f"数字 {i} 缺少维度 {dim}")
        
        # 验证八卦配对规则
        for i in range(1, 9):
            if i not in self.bagua_pairing:
                errors.append(f"八卦配对规则缺少状态 {i}")
        
        if errors:
            return False, errors
        return True, []
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """创建错误响应"""
        return {
            'error': error_message,
            'track1': {},
            'track2': {},
            'track3': {},
            'track4': {},
            'direct_pairing': {}
        }
    
    def _get_symbols(self, track_name: str, sequence: List[int]) -> List[str]:
        """获取符号序列（使用缓存）"""
        if track_name == 'track1':
            return sequence  # track1 不使用符号
        cached = self._cached_symbols.get(track_name)
        if cached:
            return [cached[num] for num in sequence]
        # 回退到原始方法
        mapping = self.track_mappings[track_name]
        return [mapping[num] for num in sequence]
    
    def _calculate_symmetry(self, forward_result: Dict[str, Any], backward_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算正向和反向分析结果的对称性指标
        
        Args:
            forward_result: 正向分析结果
            backward_result: 反向分析结果
            
        Returns:
            对称性指标
        """
        # 计算符号配对对称性
        forward_pair_ratio = forward_result['symbol_pairs']['pair_ratio']
        backward_pair_ratio = backward_result['symbol_pairs']['pair_ratio']
        pair_ratio_diff = abs(forward_pair_ratio - backward_pair_ratio)
        pair_ratio_similarity = 1 - pair_ratio_diff if pair_ratio_diff <= 1 else 0
        
        # 计算全局数字配对对称性
        forward_global_ratio = forward_result.get('global_digit_pairs', {}).get('pair_ratio', 0)
        backward_global_ratio = backward_result.get('global_digit_pairs', {}).get('pair_ratio', 0)
        global_ratio_diff = abs(forward_global_ratio - backward_global_ratio)
        global_ratio_similarity = 1 - global_ratio_diff if global_ratio_diff <= 1 else 0
        
        # 计算阴阳对称性
        forward_yang_percent = forward_result['yinyang']['yang_percent']
        backward_yang_percent = backward_result['yinyang']['yang_percent']
        yang_percent_diff = abs(forward_yang_percent - backward_yang_percent)
        yang_percent_similarity = 1 - yang_percent_diff if yang_percent_diff <= 1 else 0
        
        # 计算窗口数量差异
        window_diff = abs(forward_result['window_count'] - backward_result['window_count'])
        
        # 综合对称性得分
        if 'global_digit_pairs' in forward_result and 'global_digit_pairs' in backward_result:
            # 对于轨道2-4，使用全局数字配对对称性
            overall_symmetry = (pair_ratio_similarity + global_ratio_similarity + yang_percent_similarity) / 3
        else:
            # 对于轨道1，使用原来的对称性计算
            overall_symmetry = (pair_ratio_similarity + yang_percent_similarity) / 2
        
        return {
            'pair_ratio_diff': pair_ratio_diff,
            'pair_ratio_similarity': pair_ratio_similarity,
            'global_ratio_diff': global_ratio_diff,
            'global_ratio_similarity': global_ratio_similarity,
            'yang_percent_diff': yang_percent_diff,
            'yang_percent_similarity': yang_percent_similarity,
            'window_diff': window_diff,
            'overall_symmetry': overall_symmetry
        }
    
    def _calculate_pairing_symmetry(self, forward_result: Dict[str, Any], backward_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算正向和反向直接配对的对称性指标
        
        Args:
            forward_result: 正向配对结果
            backward_result: 反向配对结果
            
        Returns:
            配对对称性指标
        """
        # 计算配对率差异
        forward_pair_ratio = forward_result['pair_ratio']
        backward_pair_ratio = backward_result['pair_ratio']
        pair_ratio_diff = abs(forward_pair_ratio - backward_pair_ratio)
        pair_ratio_similarity = 1 - pair_ratio_diff if pair_ratio_diff <= 1 else 0
        
        # 计算有效配对差异
        valid_pairs_diff = abs(forward_result['valid_pairs'] - backward_result['valid_pairs'])
        
        # 计算总配对差异
        total_pairs_diff = abs(forward_result['total_pairs'] - backward_result['total_pairs'])
        
        return {
            'pair_ratio_diff': pair_ratio_diff,
            'pair_ratio_similarity': pair_ratio_similarity,
            'valid_pairs_diff': valid_pairs_diff,
            'total_pairs_diff': total_pairs_diff
        }
    
    def _generate_reverse_analysis_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成反向分析的综合摘要
        
        Args:
            results: 完整的分析结果
            
        Returns:
            反向分析摘要
        """
        summary = {
            'track_symmetry': {},
            'overall_symmetry': 0,
            'symmetry_distribution': {
                'high': 0,  # > 0.8
                'medium': 0,  # 0.4-0.8
                'low': 0  # < 0.4
            }
        }
        
        # 计算每个轨道的对称性
        symmetry_scores = []
        for track in ['track1', 'track2', 'track3', 'track4']:
            if track in results and 'symmetry' in results[track]:
                symmetry = results[track]['symmetry']['overall_symmetry']
                summary['track_symmetry'][track] = symmetry
                symmetry_scores.append(symmetry)
                
                # 分类对称性水平
                if symmetry > 0.8:
                    summary['symmetry_distribution']['high'] += 1
                elif symmetry > 0.4:
                    summary['symmetry_distribution']['medium'] += 1
                else:
                    summary['symmetry_distribution']['low'] += 1
        
        # 计算整体对称性
        if symmetry_scores:
            summary['overall_symmetry'] = sum(symmetry_scores) / len(symmetry_scores)
        
        # 分析对称性模式
        symmetry_pattern = self._analyze_symmetry_pattern(summary['track_symmetry'])
        summary['symmetry_pattern'] = symmetry_pattern
        
        return summary
    
    def _analyze_symmetry_pattern(self, track_symmetry: Dict[str, float]) -> Dict[str, Any]:
        """
        分析对称性模式
        
        Args:
            track_symmetry: 各轨道的对称性得分
            
        Returns:
            对称性模式分析
        """
        # 计算对称性得分的统计信息
        scores = list(track_symmetry.values())
        avg_symmetry = sum(scores) / len(scores) if scores else 0
        max_symmetry = max(scores) if scores else 0
        min_symmetry = min(scores) if scores else 0
        symmetry_range = max_symmetry - min_symmetry if scores else 0
        
        # 识别最对称和最不对称的轨道
        most_symmetric = max(track_symmetry, key=track_symmetry.get) if track_symmetry else None
        least_symmetric = min(track_symmetry, key=track_symmetry.get) if track_symmetry else None
        
        # 分析对称性分布
        high_symmetry = [track for track, score in track_symmetry.items() if score > 0.8]
        medium_symmetry = [track for track, score in track_symmetry.items() if 0.4 < score <= 0.8]
        low_symmetry = [track for track, score in track_symmetry.items() if score <= 0.4]
        
        return {
            'average_symmetry': avg_symmetry,
            'max_symmetry': max_symmetry,
            'min_symmetry': min_symmetry,
            'symmetry_range': symmetry_range,
            'most_symmetric_track': most_symmetric,
            'least_symmetric_track': least_symmetric,
            'high_symmetry_tracks': high_symmetry,
            'medium_symmetry_tracks': medium_symmetry,
            'low_symmetry_tracks': low_symmetry
        }
