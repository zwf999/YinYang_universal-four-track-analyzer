# core/predictors/pattern_predictor.py
# 模式预测器

from typing import Dict, List, Any
from collections import Counter, defaultdict
from core.predictors.base_predictor import BasePredictor
from core.analyzers.pattern_analyzer import PatternAnalyzer

class PatternPredictor(BasePredictor):
    """模式预测器"""
    
    def __init__(self, pattern_analyzer: PatternAnalyzer = None):
        """初始化模式预测器
        
        Args:
            pattern_analyzer: 模式分析器实例
        """
        self.pattern_analyzer = pattern_analyzer if pattern_analyzer else PatternAnalyzer()
        self.detected_patterns = []
    
    def predict(self, digits: List[int], length: int = 100) -> List[int]:
        """
        基于模式识别预测数字序列
        
        Args:
            digits: 输入数字序列
            length: 预测长度
            
        Returns:
            预测的数字序列
        """
        if not self.validate_input(digits):
            return [0] * length
        
        digits = self.preprocess(digits)
        
        # 尝试基于多轨道协同预测
        prediction = self._predict_multi_track(digits, length)
        
        # 如果多轨道预测失败或结果多样性不足，使用基于模式识别的预测
        if not prediction or len(set(prediction)) < 5:
            prediction = self._predict_pattern_based(digits, length)
        
        # 如果模式预测失败或结果多样性不足，使用基于规则的预测
        if not prediction or len(set(prediction)) < 5:
            prediction = self._predict_rule_based(digits, length)
        
        # 如果规则预测失败或结果多样性不足，使用回退策略
        if not prediction or len(set(prediction)) < 5:
            prediction = self._predict_fallback(digits, length)
        
        return prediction
    
    def _predict_pattern_based(self, digits: List[int], length: int) -> List[int]:
        """基于模式识别的预测策略"""
        import random
        
        # 分析数字序列中的模式
        patterns = self._detect_patterns(digits)
        self.detected_patterns = patterns
        
        if not patterns:
            return []
        
        # 基于检测到的模式生成预测
        prediction = []
        current_position = 0
        
        while len(prediction) < length:
            # 尝试匹配当前位置的模式
            matched_pattern = None
            max_pattern_length = 0
            
            # 寻找最长匹配的模式
            for pattern in patterns:
                pattern_seq = pattern['sequence']
                pattern_length = len(pattern_seq)
                
                # 检查模式是否匹配当前位置的前几个数字
                if len(prediction) >= pattern_length:
                    current_seq = prediction[-pattern_length:]
                    if current_seq == pattern_seq[:len(current_seq)]:
                        if pattern_length > max_pattern_length:
                            matched_pattern = pattern
                            max_pattern_length = pattern_length
                elif len(prediction) == 0:
                    # 对于第一个预测，使用最常见的模式
                    if pattern_length > max_pattern_length:
                        matched_pattern = pattern
                        max_pattern_length = pattern_length
            
            if matched_pattern:
                # 使用匹配的模式预测下一个数字
                pattern_seq = matched_pattern['sequence']
                if len(prediction) < len(pattern_seq):
                    # 从模式开始处预测
                    next_digit = pattern_seq[len(prediction)]
                else:
                    # 基于模式的周期性质预测
                    next_digit = pattern_seq[len(prediction) % len(pattern_seq)]
            else:
                # 没有匹配的模式，使用统计回退
                next_digit = self._predict_next_digit_statistical(digits, prediction)
            
            prediction.append(next_digit)
            current_position += 1
        
        return prediction
    
    def _detect_patterns(self, digits: List[int]) -> list:
        """检测数字序列中的模式"""
        patterns = []
        
        # 检测重复模式
        self._detect_repeating_patterns(digits, patterns)
        
        # 检测序列模式
        self._detect_sequential_patterns(digits, patterns)
        
        # 检测交替模式
        self._detect_alternating_patterns(digits, patterns)
        
        # 按模式长度排序，优先使用长模式
        patterns.sort(key=lambda x: len(x['sequence']), reverse=True)
        
        return patterns[:10]  # 只保留前10个最相关的模式
    
    def _detect_repeating_patterns(self, digits: List[int], patterns: list):
        """检测重复模式"""
        # 尝试不同长度的重复模式
        max_pattern_length = min(10, len(digits) // 2)
        
        for pattern_length in range(2, max_pattern_length + 1):
            # 检查模式是否在序列中重复
            pattern_counts = defaultdict(int)
            
            for i in range(len(digits) - pattern_length + 1):
                pattern = tuple(digits[i:i+pattern_length])
                pattern_counts[pattern] += 1
            
            # 找出出现次数最多的模式
            for pattern, count in pattern_counts.items():
                if count >= 3:  # 至少出现3次
                    patterns.append({
                        'type': 'repeating',
                        'sequence': list(pattern),
                        'count': count,
                        'confidence': min(count / (len(digits) / len(pattern)), 1.0)
                    })
    
    def _detect_sequential_patterns(self, digits: List[int], patterns: list):
        """检测序列模式"""
        # 检测递增/递减序列
        for i in range(len(digits) - 2):
            if digits[i+1] == digits[i] + 1 and digits[i+2] == digits[i+1] + 1:
                # 找到长度为3的递增序列
                pattern = [digits[i], digits[i+1], digits[i+2]]
                patterns.append({
                    'type': 'sequential',
                    'sequence': pattern,
                    'count': 1,
                    'confidence': 0.5
                })
            elif digits[i+1] == digits[i] - 1 and digits[i+2] == digits[i+1] - 1:
                # 找到长度为3的递减序列
                pattern = [digits[i], digits[i+1], digits[i+2]]
                patterns.append({
                    'type': 'sequential',
                    'sequence': pattern,
                    'count': 1,
                    'confidence': 0.5
                })
    
    def _detect_alternating_patterns(self, digits: List[int], patterns: list):
        """检测交替模式"""
        # 检测两数交替模式
        if len(digits) >= 4:
            # 检查前4个数字是否形成交替模式
            if digits[0] == digits[2] and digits[1] == digits[3]:
                pattern = [digits[0], digits[1]]
                patterns.append({
                    'type': 'alternating',
                    'sequence': pattern,
                    'count': 1,
                    'confidence': 0.6
                })
    
    def _predict_next_digit_statistical(self, digits: List[int], prediction: List[int]) -> int:
        """基于统计信息预测下一个数字"""
        import random
        
        # 结合原始数据和已预测数据的统计信息
        combined_data = digits + prediction
        
        if not combined_data:
            return random.randint(0, 9)
        
        # 计算数字分布
        digit_counts = Counter(combined_data)
        total = len(combined_data)
        
        # 构建概率分布
        digits_list = list(digit_counts.keys())
        probs_list = [count / total for count in digit_counts.values()]
        
        # 随机选择一个数字，基于概率分布
        return random.choices(digits_list, weights=probs_list)[0]
    
    def _predict_fallback(self, digits: List[int], length: int) -> List[int]:
        """回退预测策略"""
        # 使用数字分布的统计信息，而不是简单的最后一位重复
        if digits:
            from collections import Counter
            import random
            
            digit_counts = Counter(digits)
            total = len(digits)
            
            if total > 0:
                # 基于数字分布随机生成预测
                digits_list = list(digit_counts.keys())
                probs_list = [count / total for count in digit_counts.values()]
                
                # 确保生成的预测具有足够的多样性
                prediction = []
                for _ in range(length):
                    # 随机选择一个数字，基于概率分布
                    digit = random.choices(digits_list, weights=probs_list)[0]
                    # 确保不会连续重复相同的数字
                    if prediction and prediction[-1] == digit:
                        # 选择另一个数字
                        other_digits = [d for d in digits_list if d != digit]
                        if other_digits:
                            other_probs = [p for d, p in zip(digits_list, probs_list) if d != digit]
                            digit = random.choices(other_digits, weights=other_probs)[0]
                    prediction.append(digit)
                return prediction
            else:
                return [random.randint(0, 9) for _ in range(length)]
        else:
            import random
            return [random.randint(0, 9) for _ in range(length)]
    
    def _predict_rule_based(self, digits: List[int], length: int) -> List[int]:
        """基于九和配对规则的预测策略"""
        import random
        
        # 九和配对规则
        nine_sum_pairs = {
            0: 9,
            1: 8,
            2: 7,
            3: 6,
            4: 5,
            5: 4,
            6: 3,
            7: 2,
            8: 1,
            9: 0
        }
        
        # 分析基础数据的统计信息和模式
        def analyze_base_data(base_digits):
            """分析基础数据的统计信息和模式"""
            from collections import Counter, defaultdict
            
            analysis = {
                'digit_counts': Counter(base_digits),
                'total': len(base_digits),
                '2grams': defaultdict(int),
                '3grams': defaultdict(int),
                'transitions': defaultdict(int)
            }
            
            # 分析2-gram模式
            for i in range(len(base_digits) - 1):
                analysis['2grams'][(base_digits[i], base_digits[i+1])] += 1
            
            # 分析3-gram模式
            for i in range(len(base_digits) - 2):
                analysis['3grams'][(base_digits[i], base_digits[i+1], base_digits[i+2])] += 1
            
            # 分析数字转移概率
            for i in range(len(base_digits) - 1):
                analysis['transitions'][(base_digits[i], base_digits[i+1])] += 1
            
            return analysis
        
        # 生成候选预测序列
        def generate_candidates(base_analysis, num_candidates=5000, candidate_length=20):
            """生成候选预测序列"""
            candidates = []
            
            # 基于基础数据分析生成数字
            if base_analysis['total'] > 0:
                digits_list = list(base_analysis['digit_counts'].keys())
                probs_list = [count / base_analysis['total'] for count in base_analysis['digit_counts'].values()]
            else:
                digits_list = list(range(10))
                probs_list = [0.1] * 10
            
            # 生成候选序列
            for _ in range(num_candidates):
                candidate = []
                for i in range(candidate_length):
                    if i == 0 or not base_analysis['transitions']:
                        # 第一个数字或没有转移数据，基于统计信息生成
                        digit = random.choices(digits_list, weights=probs_list)[0]
                    else:
                        # 基于转移概率生成下一个数字
                        previous_digit = candidate[-1]
                        # 收集所有可能的转移
                        possible_transitions = []
                        transition_probs = []
                        
                        for (prev, next_d), count in base_analysis['transitions'].items():
                            if prev == previous_digit:
                                possible_transitions.append(next_d)
                                transition_probs.append(count)
                        
                        if possible_transitions:
                            # 使用转移概率生成下一个数字
                            digit = random.choices(possible_transitions, weights=transition_probs)[0]
                        else:
                            # 如果没有转移数据，基于统计信息生成
                            digit = random.choices(digits_list, weights=probs_list)[0]
                    
                    # 确保不会连续重复相同的数字
                    if candidate and candidate[-1] == digit:
                        other_digits = [d for d in digits_list if d != digit]
                        if other_digits:
                            other_probs = [p for d, p in zip(digits_list, probs_list) if d != digit]
                            digit = random.choices(other_digits, weights=other_probs)[0]
                    
                    candidate.append(digit)
                candidates.append(candidate)
            
            return candidates
        
        # 评估候选序列
        def evaluate_candidate(candidate, base_analysis):
            """评估候选序列的质量"""
            score = 0
            
            # 规则1：轨道1和轨道2的九和配对
            for i in range(len(candidate) - 1):
                if candidate[i+1] == nine_sum_pairs.get(candidate[i], -1):
                    score += 1.5  # 九和配对的权重
            
            # 规则2：数字分布的均匀性（数学常数的特性）
            from collections import Counter
            candidate_counts = Counter(candidate)
            uniformity = 0
            for digit in range(10):
                # 理想情况下，每个数字出现的概率应该是0.1
                ideal_prob = 0.1
                actual_prob = candidate_counts.get(digit, 0) / len(candidate)
                uniformity += 1 - abs(actual_prob - ideal_prob)
            score += uniformity * 1.5  # 增加均匀性的权重
            
            # 规则3：避免连续重复
            for i in range(len(candidate) - 1):
                if candidate[i] != candidate[i+1]:
                    score += 0.1
                else:
                    score -= 0.5  # 对连续重复进行惩罚
            
            # 规则4：与基础数据的转移概率相似性
            if base_analysis['total'] >= 2:
                from collections import defaultdict
                candidate_transitions = defaultdict(int)
                for i in range(len(candidate) - 1):
                    candidate_transitions[(candidate[i], candidate[i+1])] += 1
                
                # 计算转移概率相似度
                transition_similarity = 0
                total_transitions = sum(base_analysis['transitions'].values())
                if total_transitions > 0:
                    for transition in candidate_transitions:
                        if transition in base_analysis['transitions']:
                            base_prob = base_analysis['transitions'][transition] / total_transitions
                            candidate_prob = candidate_transitions[transition] / (len(candidate) - 1)
                            transition_similarity += 1 - abs(base_prob - candidate_prob)
                score += transition_similarity * 2  # 增加转移概率相似性的权重
            
            # 规则5：与基础数据的2-gram模式相似性
            if base_analysis['total'] >= 2:
                from collections import defaultdict
                candidate_2grams = defaultdict(int)
                for i in range(len(candidate) - 1):
                    candidate_2grams[(candidate[i], candidate[i+1])] += 1
                
                # 计算匹配的2-gram数量
                matching_2grams = 0
                for gram in candidate_2grams:
                    if gram in base_analysis['2grams']:
                        matching_2grams += candidate_2grams[gram]
                
                # 计算2-gram匹配率
                if len(candidate) > 1:
                    gram_match_ratio = matching_2grams / (len(candidate) - 1)
                    score += gram_match_ratio * 2  # 增加2-gram模式相似性的权重
            
            return score
        
        # 迭代优化
        def optimize_candidates(base_analysis, num_iterations=20, num_candidates=5000, candidate_length=20):
            """迭代优化候选序列"""
            best_candidate = None
            best_score = -1
            
            for _ in range(num_iterations):
                # 生成候选序列
                candidates = generate_candidates(base_analysis, num_candidates, candidate_length)
                
                # 评估候选序列
                for candidate in candidates:
                    score = evaluate_candidate(candidate, base_analysis)
                    if score > best_score:
                        best_score = score
                        best_candidate = candidate
                
                # 如果找到足够好的候选，提前停止
                if best_score > candidate_length * 0.5:  # 50%的配对率
                    break
            
            return best_candidate
        
        # 分析基础数据
        base_analysis = analyze_base_data(digits)
        
        # 生成最终预测
        final_prediction = []
        current_digits = digits.copy()
        
        while len(final_prediction) < length:
            # 每次预测10个数字，减少误差累积
            prediction_length = min(10, length - len(final_prediction))
            
            # 重新分析当前数据
            current_analysis = analyze_base_data(current_digits)
            
            # 优化候选序列
            best_candidate = optimize_candidates(current_analysis, num_iterations=20, 
                                               num_candidates=5000, candidate_length=prediction_length)
            
            if best_candidate:
                # 添加到最终预测
                final_prediction.extend(best_candidate)
                # 更新当前数字序列
                current_digits.extend(best_candidate)
            else:
                # 如果优化失败，使用统计预测
                if current_analysis['total'] > 0:
                    digits_list = list(current_analysis['digit_counts'].keys())
                    probs_list = [count / current_analysis['total'] for count in current_analysis['digit_counts'].values()]
                    digit = random.choices(digits_list, weights=probs_list)[0]
                else:
                    digit = random.randint(0, 9)
                
                final_prediction.append(digit)
                current_digits.append(digit)
        
        return final_prediction
    
    def _predict_final_combined(self, digits: List[int], length: int) -> List[int]:
        """最终的组合预测方法"""
        import random
        from collections import Counter, defaultdict
        
        # 轨道2配对规则（和=9）
        track2_pairs = {
            1: 8, 8: 1,
            2: 7, 7: 2,
            3: 6, 6: 3,
            4: 5, 5: 4,
            9: 0, 0: 9
        }
        
        # 轨道3配对规则（和=10）
        track3_pairs = {
            1: 9, 9: 1,
            2: 8, 8: 2,
            3: 7, 7: 3,
            4: 6, 6: 4,
            5: 0, 0: 5
        }
        
        # 轨道4配对规则（特定组合）
        track4_pairs = {
            1: 8, 8: 1,
            2: 5, 5: 2,
            3: 6, 6: 3,
            4: 7, 7: 4,
            9: 0, 0: 9
        }
        
        # 分析输入数据
        def analyze_data(base_digits):
            """分析输入数据的详细特征"""
            analysis = {
                'digit_counts': Counter(base_digits),
                'total': len(base_digits),
                'digit_frequencies': {},
                'transitions': defaultdict(int),
                'last_digits': base_digits[-5:] if base_digits else [],
                'patterns': [],
                'n_gram_counts': defaultdict(int),
                'sequence_patterns': []
            }
            
            # 计算数字频率
            total = len(base_digits)
            for digit in range(10):
                analysis['digit_frequencies'][digit] = base_digits.count(digit) / total if total > 0 else 0.1
            
            # 分析转移概率
            for i in range(len(base_digits) - 1):
                d1, d2 = base_digits[i], base_digits[i+1]
                analysis['transitions'][(d1, d2)] += 1
            
            # 分析n-gram模式
            max_n = min(4, len(base_digits))
            for n in range(2, max_n + 1):
                for i in range(len(base_digits) - n + 1):
                    ngram = tuple(base_digits[i:i+n])
                    analysis['n_gram_counts'][ngram] += 1
            
            # 检测简单模式
            if len(base_digits) >= 6:
                for pattern_length in [2, 3]:
                    for i in range(len(base_digits) - pattern_length * 2 + 1):
                        pattern1 = base_digits[i:i+pattern_length]
                        pattern2 = base_digits[i+pattern_length:i+pattern_length*2]
                        if pattern1 == pattern2:
                            analysis['patterns'].append(pattern1)
            
            # 检测序列模式
            if len(base_digits) >= 4:
                for i in range(len(base_digits) - 3):
                    # 检测递增序列
                    if base_digits[i+1] == base_digits[i] + 1 and base_digits[i+2] == base_digits[i+1] + 1:
                        analysis['sequence_patterns'].append('increasing')
                    # 检测递减序列
                    elif base_digits[i+1] == base_digits[i] - 1 and base_digits[i+2] == base_digits[i+1] - 1:
                        analysis['sequence_patterns'].append('decreasing')
                    # 检测交替模式
                    elif base_digits[i] == base_digits[i+2] and base_digits[i+1] == base_digits[i+3]:
                        analysis['sequence_patterns'].append('alternating')
            
            return analysis
        
        # 生成候选数字并分配权重
        def generate_candidates_with_weights(previous_digit, analysis):
            """基于多种规则生成候选数字并分配权重"""
            weights = defaultdict(float)
            
            # 规则1：轨道配对规则（高权重）
            if previous_digit in track2_pairs:
                weights[track2_pairs[previous_digit]] += 3.0
            if previous_digit in track3_pairs:
                weights[track3_pairs[previous_digit]] += 2.5
            if previous_digit in track4_pairs:
                weights[track4_pairs[previous_digit]] += 2.0
            
            # 规则2：基于转移概率（中高权重）
            transition_total = sum(count for (prev, next_d), count in analysis['transitions'].items() if prev == previous_digit)
            if transition_total > 0:
                for (prev, next_d), count in analysis['transitions'].items():
                    if prev == previous_digit:
                        weight = (count / transition_total) * 2.5
                        weights[next_d] += weight
            
            # 规则3：高频数字（中等权重）
            sorted_digits = sorted(range(10), key=lambda d: analysis['digit_frequencies'][d], reverse=True)
            for i, digit in enumerate(sorted_digits[:5]):
                weights[digit] += (5 - i) * 0.5
            
            # 规则4：基于模式（中等权重）
            if analysis['patterns']:
                # 选择出现频率最高的模式
                pattern_counts = Counter(tuple(p) for p in analysis['patterns'])
                if pattern_counts:
                    most_common_pattern = list(pattern_counts.most_common(1)[0][0])
                    for j, digit in enumerate(most_common_pattern):
                        weights[digit] += (len(most_common_pattern) - j) * 0.8
            
            # 规则5：基于n-gram模式（中低权重）
            if analysis['n_gram_counts']:
                # 查找以previous_digit开头的n-gram
                relevant_ngrams = []
                for ngram, count in analysis['n_gram_counts'].items():
                    if len(ngram) > 1 and ngram[0] == previous_digit:
                        relevant_ngrams.append((ngram, count))
                
                # 按出现次数排序
                relevant_ngrams.sort(key=lambda x: x[1], reverse=True)
                
                # 为后续数字分配权重
                for ngram, count in relevant_ngrams[:3]:
                    for j in range(1, len(ngram)):
                        weights[ngram[j]] += count * 0.3
            
            # 规则6：序列模式（低权重）
            if analysis['sequence_patterns']:
                pattern_counts = Counter(analysis['sequence_patterns'])
                most_common = pattern_counts.most_common(1)
                if most_common:
                    pattern_type = most_common[0][0]
                    if pattern_type == 'increasing' and previous_digit < 9:
                        weights[previous_digit + 1] += 1.0
                    elif pattern_type == 'decreasing' and previous_digit > 0:
                        weights[previous_digit - 1] += 1.0
                    elif pattern_type == 'alternating' and len(analysis['last_digits']) >= 2:
                        # 预测与倒数第二个数字相同
                        weights[analysis['last_digits'][-2]] += 1.2
            
            # 规则7：避免连续重复（惩罚）
            if previous_digit in weights:
                weights[previous_digit] = 0.0
            
            # 规则8：确保多样性（为低频数字添加小权重）
            for digit in range(10):
                if digit not in weights:
                    weights[digit] += 0.1
            
            # 归一化权重
            total_weight = sum(weights.values())
            if total_weight > 0:
                normalized_weights = {digit: weight / total_weight for digit, weight in weights.items()}
            else:
                # 如果没有权重信息，均匀分配
                normalized_weights = {digit: 0.1 for digit in range(10)}
                if previous_digit in normalized_weights:
                    normalized_weights[previous_digit] = 0.0
            
            return normalized_weights
        
        # 分析输入数据
        analysis = analyze_data(digits)
        
        # 生成预测
        prediction = []
        current_digits = digits.copy()
        
        for i in range(length):
            if not current_digits:
                # 没有输入数据，随机生成
                digit = random.randint(0, 9)
            else:
                # 获取最后一个数字
                last_digit = current_digits[-1]
                
                # 生成候选数字和权重
                candidate_weights = generate_candidates_with_weights(last_digit, analysis)
                
                # 基于权重选择数字
                digits_list = list(candidate_weights.keys())
                weights_list = list(candidate_weights.values())
                digit = random.choices(digits_list, weights=weights_list)[0]
                
                # 每6步重新分析数据，以适应新的模式
                if (i + 1) % 6 == 0:
                    analysis = analyze_data(current_digits)
            
            # 添加到预测结果
            prediction.append(digit)
            current_digits.append(digit)
        
        return prediction
    
    def _predict_multi_track(self, digits: List[int], length: int) -> List[int]:
        """多轨道协同预测方法"""
        # 调用最终的组合预测方法
        return self._predict_final_combined(digits, length)
    
    def get_detected_patterns(self) -> List[Dict[str, Any]]:
        """
        获取检测到的模式
        
        Returns:
            检测到的模式列表
        """
        return self.detected_patterns
    
    def get_name(self) -> str:
        """获取预测器名称"""
        return "PatternPredictor"
    
    def get_version(self) -> str:
        """获取预测器版本"""
        return "2.0.0"

