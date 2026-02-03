"""
《易经》四维九和拓扑模型 - 最终版 v5.0
使用优化后的阈值参数 (弱: 0.040158, 强: 0.060237)
基于50个随机序列和9个数学常数的数据分析
"""

import math
import os
from typing import List, Dict, Tuple
import random

class FDJTMS:
    """四维九和拓扑模型（优化阈值版）"""
    
    def __init__(self):
        """初始化模型 - 使用优化后的阈值"""
        # 数字属性映射
        self.attributes = {
            0: (0, 5, 0, 1), 1: (1, 1, 1, 1), 2: (1, 2, 1, 0),
            3: (1, 3, 1, 1), 4: (1, 4, 0, 0), 5: (1, 5, 0, 1),
            6: (1, 1, 1, 1), 7: (1, 2, 1, 0), 8: (0, 3, 1, 1),
            9: (0, 4, 0, 0),
        }
        
        # AB关系矩阵
        self.ab_matrix = [
            [0, 0, 1, 1, 0],
            [0, 0, 1, 0, 1],
            [1, 1, 0, 0, 0],
            [1, 0, 0, 0, 1],
            [0, 1, 0, 1, 0]
        ]
        
        # 优化后的校准参数（基于50个随机序列和9个数学常数）
        self.benchmark = {
            'random_mean': 0.021778,      # 随机序列Ω均值
            'random_95_percentile': 0.036507,  # 随机序列95%分位数
            'weak_threshold': 0.040158,   # 弱结构阈值（优化后）
            'strong_threshold': 0.060237  # 强结构阈值（优化后）
        }
    
    # ========== 核心方法 ==========
    
    def windows(self, digits: List[int], size: int = 12, step: int = 5) -> List[List[int]]:
        """生成滑动窗口"""
        if len(digits) < size:
            return []
        return [digits[i:i+size] for i in range(0, len(digits)-size+1, step)]
    
    def state_id(self, bits: Tuple[int, int, int]) -> int:
        """3位转状态ID(1-8)"""
        mapping = {
            (1,1,1):1, (1,1,0):2, (1,0,1):3, (1,0,0):4,
            (0,1,1):5, (0,1,0):6, (0,0,1):7, (0,0,0):8
        }
        return mapping.get(bits, 0)
    
    # ========== 四个维度 ==========
    
    def size_bits(self, part: List[int]) -> Tuple[int, int, int]:
        """小大维度"""
        return tuple(self.attributes[d][0] for d in part)
    
    def position_bits(self, part: List[int]) -> Tuple[int, int, int]:
        """上下维度"""
        return tuple(self.attributes[d][2] for d in part)
    
    def parity_bits(self, part: List[int]) -> Tuple[int, int, int]:
        """奇偶维度"""
        return tuple(self.attributes[d][3] for d in part)
    
    def ab_bits(self, part: List[int]) -> Tuple[int, int, int]:
        """生克维度"""
        if len(part) != 3:
            return (0, 0, 0)
        layers = [self.attributes[d][1] for d in part]
        e1 = self.ab_matrix[layers[0]-1][layers[1]-1]
        e2 = self.ab_matrix[layers[1]-1][layers[2]-1]
        e3 = self.ab_matrix[layers[2]-1][layers[0]-1]
        return (e1, e2, e3)
    
    # ========== Ω值计算 ==========
    
    def R_value(self, windows: List[List[int]], bit_func) -> float:
        """计算单维度R值"""
        if not windows:
            return 0.0
        
        valid = total = 0
        for w in windows:
            if len(w) != 12:
                continue
            
            p1, p2, p3, p4 = w[0:3], w[3:6], w[6:9], w[9:12]
            s1, s2, s3, s4 = map(self.state_id, 
                                [bit_func(p1), bit_func(p2), bit_func(p3), bit_func(p4)])
            
            if s1 and s3:
                total += 1
                if s1 + s3 == 9:
                    valid += 1
            
            if s2 and s4:
                total += 1
                if s2 + s4 == 9:
                    valid += 1
        
        return valid / total if total > 0 else 0.0
    
    def analyze(self, digits: List[int]) -> Dict:
        """分析序列，返回Ω值和结构判定"""
        if len(digits) < 12:
            return {"error": "序列太短"}
        
        # 正向和反向窗口
        fw = self.windows(digits, 12, 5)
        bw = self.windows(digits[::-1], 12, 5)
        
        if not fw or not bw:
            return {"error": "无法生成窗口"}
        
        # 四个维度
        dimensions = [
            ("小大", self.size_bits),
            ("上下", self.position_bits),
            ("奇偶", self.parity_bits),
            ("生克", self.ab_bits)
        ]
        
        results = {}
        delta_squares = 0
        
        for name, func in dimensions:
            Rf = self.R_value(fw, func)
            Rb = self.R_value(bw, func)
            delta = abs(Rf - Rb)
            
            results[name] = {"R_forward": Rf, "R_backward": Rb, "delta": delta}
            delta_squares += delta * delta
        
        # 计算Ω
        Omega = math.sqrt(delta_squares)
        
        # 结构判定（使用优化后的阈值）
        if Omega < self.benchmark['weak_threshold']:
            structure = "随机"
        elif Omega < self.benchmark['strong_threshold']:
            structure = "有序"
        else:
            structure = "高度有序"
        
        return {
            "length": len(digits),
            "windows": len(fw),
            "Omega": Omega,
            "structure": structure,
            "dimensions": results,
            "thresholds": {
                "weak": self.benchmark['weak_threshold'],
                "strong": self.benchmark['strong_threshold']
            }
        }
    
    # ========== 辅助方法 ==========
    
    def random_seq(self, length: int = 1000) -> List[int]:
        """生成随机序列"""
        return [random.randint(0, 9) for _ in range(length)]
    
    def print_result(self, result: Dict):
        """打印结果"""
        if 'error' in result:
            print(f"错误: {result['error']}")
            return
        
        print(f"序列长度: {result['length']}")
        print(f"窗口数量: {result['windows']}")
        print(f"Ω值: {result['Omega']:.6f}")
        print(f"结构: {result['structure']}")
        print(f"阈值参考: 弱={result['thresholds']['weak']:.6f}, 强={result['thresholds']['strong']:.6f}")
        
        print("\n各维度:")
        for name, data in result['dimensions'].items():
            print(f"  {name}: ΔR={data['delta']:.6f} (正={data['R_forward']:.6f}, 反={data['R_backward']:.6f})")

def load_math_constant(filename, count=500):
    """
    从data目录加载数学常数数字
    """
    # 创建data目录（如果不存在）
    if not os.path.exists('data'):
        os.makedirs('data')
        print("📁 已创建 data 目录")
        print("📝 请将数学常数文件复制到 data/ 目录下")
        return None
    
    filepath = os.path.join('data', filename)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 清理内容：移除小数点、空格、换行符等
        cleaned = content.replace('.', '').replace('\n', '').replace(' ', '').replace(',', '')
        
        # 提取数字（确保是0-9）
        digits = []
        for char in cleaned[:count]:
            if char.isdigit():
                digits.append(int(char))
        
        if len(digits) < count:
            print(f"⚠️  注意: {filename} 只找到 {len(digits)} 位数字，少于要求的 {count} 位")
        
        return digits[:count]
        
    except FileNotFoundError:
        print(f"❌ 错误: 未找到文件 {filepath}")
        return None
    except Exception as e:
        print(f"❌ 读取文件时出错: {e}")
        return None

def demo():
    """演示函数 - 使用优化后的阈值"""
    print("《易经》四维九和模型演示 v5.0")
    print("=" * 60)
    print("📊 使用优化阈值: 弱=0.040158, 强=0.060237")
    print("=" * 60)
    
    model = FDJTMS()
    
    # 显示当前阈值
    print(f"\n📈 当前阈值参数:")
    print(f"  随机序列Ω均值: {model.benchmark['random_mean']:.6f}")
    print(f"  随机序列95%分位数: {model.benchmark['random_95_percentile']:.6f}")
    print(f"  弱结构阈值: {model.benchmark['weak_threshold']:.6f}")
    print(f"  强结构阈值: {model.benchmark['strong_threshold']:.6f}")
    
    # 测试随机序列
    print(f"\n🎲 随机序列测试 (1000位):")
    random_digits = model.random_seq(1000)
    result = model.analyze(random_digits)
    model.print_result(result)
    
    # 测试欧拉常数γ
    print(f"\n🔥 欧拉常数γ测试 (1000位):")
    gamma_digits = load_math_constant('b001620_full.txt', 1000)
    if gamma_digits:
        result = model.analyze(gamma_digits)
        model.print_result(result)
    
    # 测试圆周率π
    print(f"\nπ 圆周率测试 (1000位):")
    pi_digits = load_math_constant('pi_digits_1m.txt', 1000)
    if pi_digits:
        result = model.analyze(pi_digits)
        model.print_result(result)
    
    # 使用说明
    print("\n" + "=" * 60)
    print("📚 使用说明:")
    print("=" * 60)
    print("""
# 导入模型
from fd_jtms import FDJTMS, load_math_constant

# 创建实例（已使用优化阈值）
model = FDJTMS()

# 分析序列
digits = load_math_constant('pi_digits_1m.txt', 1000)
result = model.analyze(digits)

# 查看结果
print(f"Ω值: {result['Omega']:.6f}")
print(f"结构: {result['structure']}")
print(f"阈值: 弱={result['thresholds']['weak']:.6f}, 强={result['thresholds']['strong']:.6f}")
    """)

if __name__ == "__main__":
    demo()
