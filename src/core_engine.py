"""
core_engine.py - 四维九和拓扑模型核心计算引擎
严格遵循《易经》四维九和拓扑模型论文规范
版本: v2.0 (完全符合论文要求)
"""

import math
from typing import List, Dict, Tuple

class FourDimNineHarmonyModel:
    """四维九和拓扑模型（100%符合论文规范）"""
    
    # === 表1：数字属性映射（硬编码，严格按论文表1） ===
    DIGIT_MAP = {
        # 数字: (小大, 层, 上下, 奇偶)
        # 属性定义：1=小/上/奇, 0=大/下/偶
        0: (0, 5, 0, 1),  # 大,5层,下,奇
        1: (1, 1, 1, 1),  # 小,1层,上,奇
        2: (1, 2, 1, 0),  # 小,2层,上,偶
        3: (1, 3, 1, 1),  # 小,3层,上,奇
        4: (1, 4, 0, 0),  # 小,4层,下,偶
        5: (1, 5, 0, 1),  # 小,5层,下,奇
        6: (1, 1, 1, 1),  # 小,1层,上,奇
        7: (1, 2, 1, 0),  # 小,2层,上,偶
        8: (0, 3, 1, 1),  # 大,3层,上,奇
        9: (0, 4, 0, 0),  # 大,4层,下,偶
    }
    
    # === 表2：AB关系矩阵（修正版，完全按论文表2） ===
    # AB=1表示生关系，AB=0表示克关系
    # 矩阵索引：层数-1 (层1->索引0, 层2->索引1, ..., 层5->索引4)
    # 特别注意：(2,5)和(5,2)必须是克关系（AB=0），千问代码错误地设为1
    AB_MATRIX = [
        # 层1 (索引0) 与其他层的关系
        # (1,1)=0, (1,2)=0, (1,3)=1, (1,4)=1, (1,5)=0
        [0, 0, 1, 1, 0],
        
        # 层2 (索引1) 与其他层的关系
        # (2,1)=0, (2,2)=0, (2,3)=1, (2,4)=0, (2,5)=0  ← 修正：最后一位必须是0
        [0, 0, 1, 0, 0],
        
        # 层3 (索引2) 与其他层的关系
        # (3,1)=1, (3,2)=1, (3,3)=0, (3,4)=0, (3,5)=0
        [1, 1, 0, 0, 0],
        
        # 层4 (索引3) 与其他层的关系
        # (4,1)=1, (4,2)=0, (4,3)=0, (4,4)=0, (4,5)=1
        [1, 0, 0, 0, 1],
        
        # 层5 (索引4) 与其他层的关系
        # (5,1)=0, (5,2)=0, (5,3)=0, (5,4)=1, (5,5)=0  ← 修正：第二位必须是0
        [0, 0, 0, 1, 0]
    ]
    
    def __init__(self, digits: List[int]):
        """初始化模型
        Args:
            digits: 0-9的数字列表
        """
        self.digits = digits
        self.N = len(digits)
        if self.N < 12:
            raise ValueError("序列长度至少为12位")
    
    @staticmethod
    def get_state_id(bits: Tuple[int, int, int]) -> int:
        """根据3位二进制序列返回状态ID (1-8，严格按论文表4)"""
        state_map = {
            (1,1,1): 1,  # 状态1: 小小小 / 上上上 / 奇奇奇
            (1,1,0): 2,  # 状态2: 小小大 / 上上下 / 奇奇偶
            (1,0,1): 3,  # 状态3: 小大小 / 上下上 / 奇偶奇
            (1,0,0): 4,  # 状态4: 小大大 / 上下下 / 奇偶偶
            (0,1,1): 5,  # 状态5: 大小小 / 下上上 / 偶奇奇
            (0,1,0): 6,  # 状态6: 大小大 / 下上下 / 偶奇偶
            (0,0,1): 7,  # 状态7: 大大小 / 下下上 / 偶偶奇
            (0,0,0): 8,  # 状态8: 大大大 / 下下下 / 偶偶偶
        }
        return state_map.get(bits, 0)  # 0表示无效
    
    def get_ab_relation(self, li: int, lj: int) -> int:
        """获取AB关系（1=生，0=克）
        完全按论文表2的实现
        """
        if not (1 <= li <= 5 and 1 <= lj <= 5):
            raise ValueError(f"层值必须在1-5之间，得到({li}, {lj})")
        return self.AB_MATRIX[li-1][lj-1]
    
    # ================== 四个维度完全独立的状态计算 ==================
    # 每个维度有自己的计算函数，绝不混合
    
    def calc_size_state(self, part: List[int]) -> int:
        """计算小大维度的八卦状态ID
        Args:
            part: 3个数字的列表
        Returns:
            状态ID (1-8)
        """
        bits = tuple(self.DIGIT_MAP[d][0] for d in part)  # 索引0: 小大
        return self.get_state_id(bits)
    
    def calc_position_state(self, part: List[int]) -> int:
        """计算上下维度的八卦状态ID"""
        bits = tuple(self.DIGIT_MAP[d][2] for d in part)  # 索引2: 上下
        return self.get_state_id(bits)
    
    def calc_parity_state(self, part: List[int]) -> int:
        """计算奇偶维度的八卦状态ID"""
        bits = tuple(self.DIGIT_MAP[d][3] for d in part)  # 索引3: 奇偶
        return self.get_state_id(bits)
    
    def calc_ab_state(self, part: List[int]) -> int:
        """计算AB关系维度的八卦状态ID（环结构）
        完全按论文中的环结构计算：(x,y), (y,z), (z,x)
        """
        levels = [self.DIGIT_MAP[d][1] for d in part]  # 索引1: 层
        e1 = self.get_ab_relation(levels[0], levels[1])  # AB(x,y)
        e2 = self.get_ab_relation(levels[1], levels[2])  # AB(y,z)
        e3 = self.get_ab_relation(levels[2], levels[0])  # AB(z,x)
        bits = (e1, e2, e3)
        return self.get_state_id(bits)
    
    # ================== 分组逻辑 ==================
    
    def get_forward_blocks(self) -> List[List[int]]:
        """正向分组：B_k^forward = [d_{12k+1}, ..., d_{12k+12}]
        严格按论文公式实现
        """
        blocks = []
        for i in range(0, self.N, 12):
            if i + 12 <= self.N:
                block = self.digits[i:i+12]
                if len(block) == 12:
                    blocks.append(block)
        return blocks
    
    def get_backward_blocks(self) -> List[List[int]]:
        """反向分组：B_k^backward = [d_{N-12k}, ..., d_{N-12k-11}]
        关键：不是简单反转序列，而是从末尾开始取块，且块内顺序保持
        实现方式：
          1. 反转整个序列：reverse_seq = [d_N, d_{N-1}, ..., d_1]
          2. 从反转序列的开头取12位块
          3. 结果：每个块内为 [d_{N-12k}, d_{N-12k-1}, ..., d_{N-12k-11}]
        """
        reversed_seq = self.digits[::-1]  # 关键步骤：整体反转
        blocks = []
        for i in range(0, len(reversed_seq), 12):
            if i + 12 <= len(reversed_seq):
                block = reversed_seq[i:i+12]
                if len(block) == 12:
                    blocks.append(block)
        return blocks
    
    def get_four_parts(self, block: List[int]) -> Dict[str, List[int]]:
        """四部划分（严格按论文表3）
        一部: 1-3位 ↔ 配对对象: 三部 (7-9位)
        二部: 4-6位 ↔ 配对对象: 四部 (10-12位)
        """
        if len(block) != 12:
            raise ValueError("块必须为12位")
        return {
            'part1': block[0:3],   # 一部 (1-3位)
            'part2': block[3:6],   # 二部 (4-6位)
            'part3': block[6:9],   # 三部 (7-9位)
            'part4': block[9:12]   # 四部 (10-12位)
        }
    
    # ================== R值计算 ==================
    
    def calculate_R_for_dimension(self, blocks: List[List[int]], dimension: str) -> float:
        """计算指定维度的R值（配对成功率）
        Args:
            blocks: 12位块列表
            dimension: 'size'（小大）, 'position'（上下）, 'parity'（奇偶）, 'ab'（AB）
        Returns:
            R值 = 有效配对次数 / (2 * 块数)
        """
        if not blocks:
            return 0.0
        
        K = len(blocks)  # 块数
        valid_pairs = 0
        
        # 选择对应维度的状态计算函数
        calc_func = {
            'size': self.calc_size_state,
            'position': self.calc_position_state,
            'parity': self.calc_parity_state,
            'ab': self.calc_ab_state
        }.get(dimension)
        
        if calc_func is None:
            raise ValueError(f"未知维度: {dimension}")
        
        for block in blocks:
            if len(block) != 12:
                continue
                
            parts = self.get_four_parts(block)
            
            # 一部 ↔ 三部 配对（按表3）
            state1 = calc_func(parts['part1'])
            state2 = calc_func(parts['part3'])
            if state1 + state2 == 9:  # 九和配对规则
                valid_pairs += 1
            
            # 二部 ↔ 四部 配对（按表3）
            state1 = calc_func(parts['part2'])
            state2 = calc_func(parts['part4'])
            if state1 + state2 == 9:  # 九和配对规则
                valid_pairs += 1
        
        # R = 有效配对次数 / (2 * K)
        return valid_pairs / (2 * K) if K > 0 else 0.0
    
    # ================== 核心Ω值计算 ==================
    
    def calculate_Omega(self) -> Dict:
        """计算完整的四维Ω值（核心指标）
        完全按论文公式：
          Ω = √(ΔR_小大² + ΔR_上下² + ΔR_奇偶² + ΔR_AB²)
        Returns:
            包含所有计算结果的字典
        """
        # 获取正向和反向块
        forward_blocks = self.get_forward_blocks()
        backward_blocks = self.get_backward_blocks()
        
        if not forward_blocks or not backward_blocks:
            raise ValueError("序列长度不足，无法形成完整的12位块")
        
        # 四个维度
        dimensions = ['size', 'position', 'parity', 'ab']
        dimension_cn = {
            'size': '小大',
            'position': '上下',
            'parity': '奇偶',
            'ab': 'AB'
        }
        
        # 计算各维度的R值和ΔR
        R_forward = {}
        R_backward = {}
        Delta_R = {}
        Delta_R_cn = {}  # 中文键的ΔR，用于兼容接口
        
        for dim in dimensions:
            R_forward[dim] = self.calculate_R_for_dimension(forward_blocks, dim)
            R_backward[dim] = self.calculate_R_for_dimension(backward_blocks, dim)
            Delta_R[dim] = abs(R_forward[dim] - R_backward[dim])
            Delta_R_cn[dimension_cn[dim]] = Delta_R[dim]
        
        # 计算Ω值
        Omega = math.sqrt(
            Delta_R['size']**2 + 
            Delta_R['position']**2 + 
            Delta_R['parity']**2 + 
            Delta_R['ab']**2
        )
        
        # 结构判定（按论文阈值）
        if Omega < 0.01:
            structure_type = "无显著结构（随机序列）"
        elif Omega < 0.15:
            structure_type = "弱结构（如健康生物序列）"
        else:
            structure_type = "强结构（如病理序列）"
        
        return {
            'Omega': Omega,
            'Delta_R': Delta_R_cn,  # 中文键，兼容现有接口
            'Delta_R_en': Delta_R,  # 英文键，便于内部处理
            'R_forward': R_forward,
            'R_backward': R_backward,
            'structure_type': structure_type,
            'blocks_count': {
                'forward': len(forward_blocks),
                'backward': len(backward_blocks)
            }
        }


def calculate_Omega(digits: List[int]) -> Tuple[float, Dict[str, float]]:
    """兼容原有接口的计算函数
    返回: (Omega值, Delta_R字典)
    注意：这是为了兼容千问的代码而保留的接口
    """
    model = FourDimNineHarmonyModel(digits)
    results = model.calculate_Omega()
    return results['Omega'], results['Delta_R']
