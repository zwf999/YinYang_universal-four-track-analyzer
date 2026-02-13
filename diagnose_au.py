#!/usr/bin/env python3
# 诊断天文单位的数字分布问题

from collections import Counter
from core.data.data_manager import DataManager

class AU_Diagnoser:
    def __init__(self):
        self.data_manager = DataManager()
        # 轨道2的映射规则
        self.track2_mapping = {0: 'E', 1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'D', 6: 'C', 7: 'B', 8: 'A', 9: 'E'}
        # 轨道3的映射规则
        self.track3_mapping = {0: '戊', 1: '甲', 2: '乙', 3: '丙', 4: '丁', 5: '戊', 6: '丁', 7: '丙', 8: '乙', 9: '甲'}
        # 轨道4的映射规则
        self.track4_mapping = {0: '癸', 1: '己', 2: '庚', 3: '辛', 4: '壬', 5: '庚', 6: '辛', 7: '壬', 8: '己', 9: '癸'}
        # 阴阳分类
        self.yinyang_classifications = {
            'track2': {'yang': {'A', 'C', 'E'}, 'yin': {'B', 'D'}},
            'track3': {'yang': {'甲', '丙', '戊'}, 'yin': {'乙', '丁'}},
            'track4': {'yang': {'己', '辛', '癸'}, 'yin': {'庚', '壬'}}
        }
        # 二进制到状态ID映射
        self.state_encoding = {
            '111': 1, '110': 2, '101': 3, '100': 4,
            '011': 5, '010': 6, '001': 7, '000': 8
        }
        # 八卦配对规则
        self.bagua_pairing = {
            1: 8, 2: 7, 3: 6, 4: 5,
            5: 4, 6: 3, 7: 2, 8: 1
        }
    
    def quick_diagnose(self, constant_name="astronomical_unit", sample_size=1000):
        """快速诊断常数"""
        print(f"=== 诊断 {constant_name} ===")
        
        # 加载常数
        digits = self.data_manager.load_constant(constant_name, sample_size)
        if not digits:
            print(f"无法加载常数: {constant_name}")
            return
        
        print(f"加载了 {len(digits)} 位数字")
        
        # 1. 检查数字分布
        print("\n1. 数字分布:")
        counts = Counter(digits)
        total = len(digits)
        for num in range(10):
            count = counts.get(num, 0)
            percentage = (count / total) * 100
            print(f"数字 {num}: {count} 次 ({percentage:.2f}%)")
        
        # 2. 检查是否有数字缺失
        missing_digits = [num for num in range(10) if num not in counts]
        if missing_digits:
            print(f"\n⚠️  缺失数字: {missing_digits}")
        else:
            print("\n✅ 所有数字都存在")
        
        # 3. 检查轨道2的符号分布
        print("\n2. 轨道2符号分布:")
        symbols = [self.track2_mapping[d] for d in digits]
        symbol_counts = Counter(symbols)
        for symbol, count in sorted(symbol_counts.items()):
            percentage = (count / total) * 100
            print(f"符号 {symbol}: {count} 次 ({percentage:.2f}%)")
        
        # 4. 检查轨道2的阴阳分布
        print("\n3. 轨道2阴阳分布:")
        yinyang = []
        for symbol in symbols:
            if symbol in self.yinyang_classifications['track2']['yang']:
                yinyang.append(1)
            else:
                yinyang.append(0)
        yang_count = sum(yinyang)
        yin_count = len(yinyang) - yang_count
        print(f"阳 (1): {yang_count} 次 ({(yang_count/total)*100:.2f}%)")
        print(f"阴 (0): {yin_count} 次 ({(yin_count/total)*100:.2f}%)")
        
        # 5. 检查二进制组合分布
        print("\n4. 二进制组合分布 (前100个):")
        binary_combinations = []
        for i in range(0, min(len(yinyang)-2, 100)):
            combo = ''.join(map(str, yinyang[i:i+3]))
            binary_combinations.append(combo)
        combo_counts = Counter(binary_combinations)
        for combo, count in sorted(combo_counts.items()):
            print(f"组合 {combo}: {count} 次")
        
        # 6. 检查状态ID分布
        print("\n5. 状态ID分布 (前100个):")
        state_ids = []
        for combo in binary_combinations:
            state_id = self.state_encoding.get(combo, 1)
            state_ids.append(state_id)
        state_counts = Counter(state_ids)
        for state, count in sorted(state_counts.items()):
            print(f"状态 {state}: {count} 次")
        
        # 7. 检查配对可能性
        print("\n6. 配对可能性分析:")
        available_states = set(state_ids)
        possible_pairs = []
        for state in available_states:
            paired_state = self.bagua_pairing.get(state)
            if paired_state in available_states:
                possible_pairs.append((state, paired_state))
        
        print(f"可用状态: {sorted(available_states)}")
        print(f"可能的配对: {possible_pairs}")
        
        if not possible_pairs:
            print("⚠️  没有可能的配对！这解释了为什么配对率为0")
        else:
            print("✅ 存在可能的配对")
        
        # 8. 检查前20位详细分析
        print("\n7. 前20位详细分析:")
        for i in range(0, min(len(digits), 20)):
            d = digits[i]
            s2 = self.track2_mapping[d]
            y2 = 1 if s2 in self.yinyang_classifications['track2']['yang'] else 0
            print(f"位置 {i}: 数字={d}, 轨道2符号={s2}, 阴阳={y2}")
        
        return {
            'digits': digits,
            'counts': counts,
            'missing_digits': missing_digits,
            'symbol_counts': symbol_counts,
            'yinyang_counts': {'yang': yang_count, 'yin': yin_count},
            'combo_counts': combo_counts,
            'state_counts': state_counts,
            'possible_pairs': possible_pairs
        }
    
    def compare_with_avogadro(self):
        """与阿伏伽德罗常数对比"""
        print("\n" + "="*80)
        print("=== 天文单位 vs 阿伏伽德罗常数 ===")
        print("="*80)
        
        au_result = self.quick_diagnose("astronomical_unit")
        print("\n" + "-"*80)
        avo_result = self.quick_diagnose("avogadro_constant")
        
        return au_result, avo_result

if __name__ == "__main__":
    diagnoser = AU_Diagnoser()
    # 诊断天文单位
    au_result = diagnoser.quick_diagnose()
    
    # 与阿伏伽德罗常数对比
    # diagnoser.compare_with_avogadro()
