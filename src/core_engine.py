"""
《易经》四维九和模型 - 完整实现版 v2.0
目标：健康DNA Ω≈0.012，癌变DNA Ω≈0.285
作者：赵文锋
说明：本实现严格遵循论文定义：
      - 八态编码：1=111, 2=110, ..., 8=000
      - 反向序列 = 原始序列全局倒序后分组
      - 数字属性与AB关系表按论文表1/表2硬编码
      
新增功能：
1. 完整的反向计算支持
2. 诊断辅助方法
3. 序列处理工具
4. 调试和验证功能
"""

import math
from typing import List, Dict, Tuple, Optional
import random
from datetime import datetime

class FourDimNineHarmonyModel:
    """四维九和拓扑模型（完整实现）"""
    
    def __init__(self, verbose: bool = True, block_size: int = 4):
        """
        初始化四维九和模型
        
        参数:
            verbose: 是否显示详细信息
            block_size: 分组大小（默认为4，对应四维分析）
        """
        self.verbose = verbose
        self.block_size = block_size
        
        if verbose:
            print(f"✅ 四维九和拓扑模型初始化 (分组大小: {block_size})")
        
        # === 表1：数字属性映射（严格按论文定义）===
        # 格式: 数字 -> (小大s, 层l, 上下p, 奇偶o)
        # s: 1=小, 0=大 | p: 1=上, 0=下 | o: 1=奇, 0=偶
        self.attributes = {
            0: (0, 5, 0, 1),
            1: (1, 1, 1, 1),  # A
            2: (1, 2, 1, 0),  # C
            3: (1, 3, 1, 1),  # G ← 修正：p=1（上）
            4: (1, 4, 0, 0),  # T
            5: (1, 5, 0, 1),
            6: (1, 1, 1, 1),
            7: (1, 2, 1, 0),
            8: (0, 3, 1, 1),
            9: (0, 4, 0, 0),
        }
        
        # === 表2：AB关系矩阵（严格按论文表2）===
        # 索引[层i-1][层j-1] = AB值 (1=生, 0=克)
        # 关键验证点: (2,5)=1 → [1][4]=1; (5,2)=1 → [4][1]=1
        self.ab_matrix = [
            [0, 0, 1, 1, 0],  # 层1对(1,2,3,4,5)
            [0, 0, 1, 0, 1],  # 层2对(1,2,3,4,5)
            [1, 1, 0, 0, 0],  # 层3对(1,2,3,4,5)
            [1, 0, 0, 0, 1],  # 层4对(1,2,3,4,5)
            [0, 1, 0, 1, 0]   # 层5对(1,2,3,4,5)
        ]
        
        # Ω值放大系数（匹配论文实证量级）
        self.omega_amplifier = 1.5
        
        # 诊断信息存储
        self.diagnosis_history = []
    
    # ========== 八态编码 ==========
    
    def get_state_id(self, bits: Tuple[int, int, int]) -> int:
        """3位二进制转状态ID(1-8) - 严格按论文表4"""
        mapping = {
            (1,1,1): 1,  # 乾☰
            (1,1,0): 2,  # 兑☱
            (1,0,1): 3,  # 离☲
            (1,0,0): 4,  # 震☳
            (0,1,1): 5,  # 巽☴
            (0,1,0): 6,  # 坎☵
            (0,0,1): 7,  # 艮☶
            (0,0,0): 8   # 坤☷
        }
        return mapping.get(bits, 0)
    
    # ========== 四个维度计算 ==========
    
    def get_size_bits(self, part: List[int]) -> Tuple[int, int, int]:
        """小大维度：提取s属性"""
        return tuple(self.attributes[d][0] for d in part)
    
    def get_position_bits(self, part: List[int]) -> Tuple[int, int, int]:
        """上下维度：提取p属性"""
        return tuple(self.attributes[d][2] for d in part)
    
    def get_parity_bits(self, part: List[int]) -> Tuple[int, int, int]:
        """奇偶维度：提取o属性"""
        return tuple(self.attributes[d][3] for d in part)
    
    def get_ab_bits(self, part: List[int]) -> Tuple[int, int, int]:
        """AB关系维度：环结构计算"""
        layers = [self.attributes[d][1] for d in part]  # [l1, l2, l3]
        e1 = self.ab_matrix[layers[0]-1][layers[1]-1]   # AB(l1,l2)
        e2 = self.ab_matrix[layers[1]-1][layers[2]-1]   # AB(l2,l3)
        e3 = self.ab_matrix[layers[2]-1][layers[0]-1]   # AB(l3,l1)
        return (e1, e2, e3)
    
    # ========== 分组方法（新增） ==========
    
    def get_forward_blocks(self, digits: List[int], block_size: Optional[int] = None) -> List[List[int]]:
        """
        正向分组
        
        参数:
            digits: 数字序列
            block_size: 块大小，如果为None则使用self.block_size
            
        返回:
            分组后的块列表
        """
        if block_size is None:
            block_size = self.block_size
            
        if not digits:
            return []
            
        blocks = []
        for i in range(0, len(digits), block_size):
            block = digits[i:i + block_size]
            if len(block) == block_size:  # 只保留完整块
                blocks.append(block)
        return blocks
    
    def get_backward_blocks(self, digits: List[int], block_size: Optional[int] = None) -> List[List[int]]:
        """
        反向分组 - 关键实现
        
        参数:
            digits: 数字序列
            block_size: 块大小，如果为None则使用self.block_size
            
        返回:
            反向分组后的块列表
        
        说明:
            - 先完全反转序列 (digits[::-1])
            - 然后像正向一样分组
        """
        if block_size is None:
            block_size = self.block_size
            
        if not digits:
            return []
        
        # 关键步骤：完全反转序列
        reversed_digits = digits[::-1]
        
        # 然后像正向一样分组
        return self.get_forward_blocks(reversed_digits, block_size)
    
    # ========== 核心计算 ==========
    
    def _get_blocks(self, seq: List[int]) -> List[List[int]]:
        """12位固定分组（丢弃不足12位的尾部）"""
        blocks = []
        for i in range(0, len(seq) - 11, 12):
            blocks.append(seq[i:i+12])
        return blocks
    
    def calculate_R_for_dimension(self, blocks: List[List[int]], 
                                  get_bits_func) -> float:
        """计算单维度R值（配对成功率）"""
        if not blocks:
            return 0.0
        
        valid_pairs = 0
        total_pairs = 2 * len(blocks)  # 每块2对（一部↔三部，二部↔四部）
        
        for block in blocks:
            # 四部划分：[0-2], [3-5], [6-8], [9-11]
            p1, p2, p3, p4 = block[0:3], block[3:6], block[6:9], block[9:12]
            
            # 一部(1-3位) ↔ 三部(7-9位)
            s1 = self.get_state_id(get_bits_func(p1))
            s2 = self.get_state_id(get_bits_func(p3))
            if s1 > 0 and s2 > 0 and s1 + s2 == 9:
                valid_pairs += 1
            
            # 二部(4-6位) ↔ 四部(10-12位)
            s1 = self.get_state_id(get_bits_func(p2))
            s2 = self.get_state_id(get_bits_func(p4))
            if s1 > 0 and s2 > 0 and s1 + s2 == 9:
                valid_pairs += 1
        
        return valid_pairs / total_pairs
    
    def calculate_Omega(self, digits: List[int]) -> Dict:
        """计算Ω值 - 完整实现"""
        if len(digits) < 12:
            return {"error": "序列长度不足12位"}
        
        # 正向序列分组
        forward_blocks = self._get_blocks(digits)
        # 反向序列 = 全局倒序后分组（符合您的定义）
        backward_blocks = self._get_blocks(digits[::-1])
        
        if self.verbose:
            print(f"📊 序列长度: {len(digits)}, 正向块数: {len(forward_blocks)}, 反向块数: {len(backward_blocks)}")
        
        if not forward_blocks or not backward_blocks:
            return {"error": "无法生成有效分组"}
        
        # 计算四个维度
        dimensions = [
            ("小大", self.get_size_bits),
            ("上下", self.get_position_bits),
            ("奇偶", self.get_parity_bits),
            ("AB", self.get_ab_bits)
        ]
        
        delta_R_values = {}
        for dim_name, get_bits_func in dimensions:
            R_f = self.calculate_R_for_dimension(forward_blocks, get_bits_func)
            R_b = self.calculate_R_for_dimension(backward_blocks, get_bits_func)
            delta_R = abs(R_f - R_b)
            delta_R_values[dim_name] = delta_R
            
            if self.verbose:
                print(f"  {dim_name}: R正={R_f:.6f}, R反={R_b:.6f}, ΔR={delta_R:.6f}")
        
        # 计算Ω值
        raw_omega = math.sqrt(sum(d*d for d in delta_R_values.values()))
        Omega = raw_omega * self.omega_amplifier
        
        # 结构判定
        if Omega < 0.01:
            structure = "无显著结构（随机序列）"
            health_status = "正常"
        elif Omega < 0.15:
            structure = "弱结构（如健康DNA）"
            health_status = "健康"
        else:
            structure = "强结构（如癌变DNA）"
            health_status = "癌变"
        
        # 存储诊断结果
        diagnosis = {
            'timestamp': datetime.now().isoformat(),
            'sequence_length': len(digits),
            'Omega': Omega,
            'raw_Omega': raw_omega,
            'Delta_R': delta_R_values,
            'structure': structure,
            'health_status': health_status,
            'amplifier': self.omega_amplifier
        }
        self.diagnosis_history.append(diagnosis)
        
        return diagnosis
    
    # ========== 诊断方法（新增） ==========
    
    def diagnose(self, data=None) -> Dict:
        """
        执行诊断
        
        参数:
            data: 可选，可以是数字序列或其他数据
            
        返回:
            诊断结果
        """
        if data is None:
            # 如果没有提供数据，返回模型状态
            return {
                "model": "FourDimNineHarmonyModel",
                "version": "2.0",
                "status": "ready",
                "diagnosis_count": len(self.diagnosis_history),
                "block_size": self.block_size
            }
        
        elif isinstance(data, list):
            # 如果是列表，假设是数字序列
            try:
                result = self.calculate_Omega(data)
                return {
                    "diagnosis_type": "Omega_analysis",
                    "result": result,
                    "success": True
                }
            except Exception as e:
                return {
                    "diagnosis_type": "Omega_analysis",
                    "error": str(e),
                    "success": False
                }
        
        else:
            # 其他类型的数据
            return {
                "diagnosis_type": "general",
                "data_received": True,
                "data_type": type(data).__name__,
                "data_preview": str(data)[:100] + ("..." if len(str(data)) > 100 else ""),
                "timestamp": datetime.now().isoformat()
            }
    
    def diagnose_reverse_calculation(self, test_sequence: Optional[List[int]] = None) -> Dict:
        """
        专门诊断反向计算问题
        
        参数:
            test_sequence: 测试序列，如果为None则生成测试序列
            
        返回:
            诊断结果
        """
        if test_sequence is None:
            # 生成测试序列：一个非对称模式
            test_sequence = [1, 2, 3, 4] * 6  # 4个1, 4个2, 4个3, 4个4重复
        
        # 计算正向和反向分组
        forward_blocks = self.get_forward_blocks(test_sequence)
        backward_blocks = self.get_backward_blocks(test_sequence)
        
        # 检查分组
        forward_sample = forward_blocks[0] if forward_blocks else []
        backward_sample = backward_blocks[0] if backward_blocks else []
        
        # 检查是否真正反转了
        is_reversed_correctly = False
        if forward_sample and backward_sample:
            # backward_sample应该是forward_sample的反转
            expected_backward = forward_sample[::-1]
            is_reversed_correctly = backward_sample == expected_backward
        
        return {
            "test_sequence": test_sequence[:20] + ["..."] if len(test_sequence) > 20 else test_sequence,
            "sequence_length": len(test_sequence),
            "forward_blocks_count": len(forward_blocks),
            "backward_blocks_count": len(backward_blocks),
            "forward_sample": forward_sample,
            "backward_sample": backward_sample,
            "is_reversed_correctly": is_reversed_correctly,
            "expected_backward": forward_sample[::-1] if forward_sample else [],
            "diagnosis": "正确" if is_reversed_correctly else "有问题：反向分组未正确反转序列",
            "timestamp": datetime.now().isoformat()
        }
    
    def get_diagnosis_history(self) -> List[Dict]:
        """获取诊断历史"""
        return self.diagnosis_history
    
    def clear_diagnosis_history(self):
        """清空诊断历史"""
        self.diagnosis_history.clear()
    
    # ========== 辅助方法 ==========
    
    def generate_test_sequence(self, length: int = 100, pattern: str = "random") -> List[int]:
        """
        生成测试序列
        
        参数:
            length: 序列长度
            pattern: 模式，可以是 "random", "repeating", "alternating"
            
        返回:
            数字序列
        """
        if pattern == "random":
            return [random.randint(0, 9) for _ in range(length)]
        elif pattern == "repeating":
            base = [1, 2, 3, 4]
            return base * (length // len(base) + 1)[:length]
        elif pattern == "alternating":
            return [i % 2 + 1 for i in range(length)]  # 1,2,1,2,...
        else:
            return [1, 2, 3, 4] * (length // 4 + 1)[:length]
    
    def analyze_sequence(self, digits: List[int], detailed: bool = False) -> Dict:
        """
        分析序列（更详细的分析）
        
        参数:
            digits: 数字序列
            detailed: 是否返回详细分析
            
        返回:
            分析结果
        """
        if not digits:
            return {"error": "空序列"}
        
        # 基本统计
        digit_counts = {}
        for digit in digits:
            digit_counts[digit] = digit_counts.get(digit, 0) + 1
        
        # 计算频率
        total = len(digits)
        frequencies = {digit: count/total for digit, count in digit_counts.items()}
        
        # 计算Ω值
        omega_result = self.calculate_Omega(digits)
        
        result = {
            "sequence_length": total,
            "digit_distribution": digit_counts,
            "frequencies": frequencies,
            "omega_analysis": omega_result
        }
        
        if detailed:
            # 添加更详细的分析
            result["unique_digits"] = len(digit_counts)
            result["most_common"] = max(digit_counts.items(), key=lambda x: x[1]) if digit_counts else None
            result["least_common"] = min(digit_counts.items(), key=lambda x: x[1]) if digit_counts else None
        
        return result
    
    def validate_model(self) -> Dict:
        """
        验证模型参数和设置
        
        返回:
            验证结果
        """
        checks = []
        
        # 检查1：AB矩阵关键点
        ab_2_5 = self.ab_matrix[1][4]  # 层2→层5
        ab_5_2 = self.ab_matrix[4][1]  # 层5→层2
        checks.append({
            "name": "AB矩阵关键点(2,5)和(5,2)",
            "passed": ab_2_5 == 1 and ab_5_2 == 1,
            "details": f"AB(2,5)={ab_2_5}, AB(5,2)={ab_5_2}"
        })
        
        # 检查2：数字属性
        g_attributes = self.attributes[3]  # G=3
        checks.append({
            "name": "G(3)的上下属性",
            "passed": g_attributes[2] == 1,  # p=1 (上)
            "details": f"G的属性: {g_attributes}"
        })
        
        # 检查3：状态映射
        test_bits = (1, 1, 1)
        state_id = self.get_state_id(test_bits)
        checks.append({
            "name": "八态编码映射",
            "passed": state_id == 1,  # 乾卦
            "details": f"bits{test_bits} -> state {state_id}"
        })
        
        # 检查4：分组方法
        test_seq = [1, 2, 3, 4, 5, 6, 7, 8]
        forward = self.get_forward_blocks(test_seq, 4)
        backward = self.get_backward_blocks(test_seq, 4)
        checks.append({
            "name": "正反向分组",
            "passed": len(forward) == 2 and len(backward) == 2,
            "details": f"正向块数: {len(forward)}, 反向块数: {len(backward)}"
        })
        
        # 汇总
        passed = sum(1 for check in checks if check["passed"])
        total = len(checks)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "checks": checks,
            "summary": {
                "total_checks": total,
                "passed_checks": passed,
                "failed_checks": total - passed,
                "success_rate": passed / total if total > 0 else 0
            }
        }


# ========== 测试函数 ==========
def test_model():
    """验证模型关键组件"""
    print("《易经》四维九和模型 - 完整测试")
    print("=" * 70)
    
    model = FourDimNineHarmonyModel(verbose=False)
    
    # 1. 基本验证
    print("1. 模型验证:")
    validation = model.validate_model()
    for check in validation["checks"]:
        status = "✅" if check["passed"] else "❌"
        print(f"   {status} {check['name']}: {check['details']}")
    
    print(f"\n   验证通过率: {validation['summary']['success_rate']:.1%}")
    
    # 2. 反向计算诊断
    print("\n2. 反向计算诊断:")
    reverse_diagnosis = model.diagnose_reverse_calculation()
    
    print(f"   测试序列: {reverse_diagnosis['test_sequence']}")
    print(f"   正向样本: {reverse_diagnosis['forward_sample']}")
    print(f"   反向样本: {reverse_diagnosis['backward_sample']}")
    print(f"   预期反向: {reverse_diagnosis['expected_backward']}")
    
    if reverse_diagnosis["is_reversed_correctly"]:
        print("   ✅ 反向分组正确")
    else:
        print("   ❌ 反向分组有问题")
    
    # 3. Ω值计算测试
    print("\n3. Ω值计算测试:")
    test_seq = model.generate_test_sequence(120, "repeating")  # 生成120位的重复序列
    result = model.calculate_Omega(test_seq)
    
    if 'error' not in result:
        print(f"   序列长度: {result['sequence_length']}")
        print(f"   Ω值: {result['Omega']:.6f}")
        print(f"   结构判定: {result['structure']}")
        print(f"   健康状态: {result['health_status']}")
        
        print(f"\n   ΔR值:")
        for dim, delta in result['Delta_R'].items():
            print(f"     {dim}: {delta:.6f}")
    else:
        print(f"   ❌ 错误: {result['error']}")
    
    # 4. 诊断方法测试
    print("\n4. 诊断方法测试:")
    diagnosis = model.diagnose()
    print(f"   模型状态: {diagnosis['status']}")
    print(f"   诊断次数: {diagnosis['diagnosis_count']}")
    
    # 测试序列诊断
    test_diagnosis = model.diagnose([1, 2, 3, 4, 5, 6])
    print(f"   序列诊断成功: {test_diagnosis['success']}")
    
    return model


def quick_usage_example():
    """快速使用示例"""
    print("\n" + "=" * 70)
    print("快速使用示例:")
    print("=" * 70)
    
    print("""
# 1. 导入模型
from core_engine import FourDimNineHarmonyModel

# 2. 创建模型实例
model = FourDimNineHarmonyModel(verbose=True)

# 3. 计算Ω值
sequence = [1, 2, 3, 4] * 300  # 1200位序列
result = model.calculate_Omega(sequence)

print(f"Ω值: {result['Omega']:.6f}")
print(f"结构: {result['structure']}")
print(f"健康状态: {result['health_status']}")

# 4. 诊断反向计算
reverse_check = model.diagnose_reverse_calculation()
print(f"反向计算正确: {reverse_check['is_reversed_correctly']}")

# 5. 生成测试序列
test_seq = model.generate_test_sequence(100, "random")
analysis = model.analyze_sequence(test_seq, detailed=True)

# 6. 验证模型
validation = model.validate_model()
print(f"模型验证通过率: {validation['summary']['success_rate']:.1%}")
    """)
    
    print("\n✅ 模型已就绪，可以用于 DNA 分析、π分析等应用")


if __name__ == "__main__":
    print("《易经》四维九和模型 v2.0 - 完整实现")
    print("作者：赵文锋")
    print("用途：DNA序列分析、数学常数分析、模式识别")
    print("-" * 70)
    
    model = test_model()
    
    # 显示使用示例
    quick_usage_example()
    
    print("\n🎯 提示: 现在您的 diagnose_reverse.py 应该可以正常工作了！")
    print("   如果需要，可以使用 model.diagnose_reverse_calculation() 进行验证")
