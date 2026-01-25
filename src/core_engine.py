# === FD-JTMS v2.0: 四维九和拓扑模型 (100% 符合论文规范) ===
import math

# === 表1：数字属性映射 (硬编码) ===
DIGIT_MAP = {
    0: {"小大": 0, "层": 5, "上下": 0, "奇偶": 1},
    1: {"小大": 1, "层": 1, "上下": 1, "奇偶": 1},
    2: {"小大": 1, "层": 2, "上下": 1, "奇偶": 0},
    3: {"小大": 1, "层": 3, "上下": 1, "奇偶": 1},
    4: {"小大": 1, "层": 4, "上下": 0, "奇偶": 0},
    5: {"小大": 1, "层": 5, "上下": 0, "奇偶": 1},
    6: {"小大": 1, "层": 1, "上下": 1, "奇偶": 1},
    7: {"小大": 1, "层": 2, "上下": 1, "奇偶": 0},
    8: {"小大": 0, "层": 3, "上下": 1, "奇偶": 1},
    9: {"小大": 0, "层": 4, "上下": 0, "奇偶": 0}
}

# === 表2：AB关系矩阵 (1=生, 0=克) ===
AB_MATRIX = [
    [0, 0, 1, 1, 0],  # 层1
    [0, 0, 1, 0, 1],  # 层2
    [1, 1, 0, 0, 0],  # 层3
    [1, 0, 0, 0, 1],  # 层4
    [0, 1, 0, 1, 0]   # 层5
]

# === 表4：八态编码表 ===
STATE_ID_MAP = {
    (1,1,1): 1,
    (1,1,0): 2,
    (1,0,1): 3,
    (1,0,0): 4,
    (0,1,1): 5,
    (0,1,0): 6,
    (0,0,1): 7,
    (0,0,0): 8
}

def get_state_id(bits):
    """根据3位二进制序列返回状态ID (表4)"""
    return STATE_ID_MAP[tuple(bits)]

def get_AB_state(part):
    """计算3位序列的AB状态ID (表6)"""
    levels = [DIGIT_MAP[d]['层'] for d in part]
    e1 = AB_MATRIX[levels[0]-1][levels[1]-1]
    e2 = AB_MATRIX[levels[1]-1][levels[2]-1]
    e3 = AB_MATRIX[levels[2]-1][levels[0]-1]
    return get_state_id((e1, e2, e3))

def split_into_12blocks(digits):
    """分割为12位块 (表3)"""
    blocks = []
    for i in range(0, len(digits) - 11, 12):
        block = digits[i:i+12]
        if len(block) == 12:
            blocks.append(block)
    return blocks

def get_four_parts(block):
    """四部划分 (表3)"""
    return {
        '一部': block[0:3],
        '二部': block[3:6],
        '三部': block[6:9],
        '四部': block[9:12]
    }

def calculate_R_dimension(blocks, dim):
    """计算单维度R值 (论文公式)"""
    valid_pairs = 0
    total_pairs = 0
    
    for block in blocks:
        parts = get_four_parts(block)
        
        # 一部 ↔ 三部 配对
        if dim == 'AB':
            s1 = get_AB_state(parts['一部'])
            s2 = get_AB_state(parts['三部'])
        else:
            bits1 = [DIGIT_MAP[d][dim] for d in parts['一部']]
            bits2 = [DIGIT_MAP[d][dim] for d in parts['三部']]
            s1 = get_state_id(bits1)
            s2 = get_state_id(bits2)
        
        if s1 + s2 == 9:
            valid_pairs += 1
        total_pairs += 1
        
        # 二部 ↔ 四部 配对
        if dim == 'AB':
            s1 = get_AB_state(parts['二部'])
            s2 = get_AB_state(parts['四部'])
        else:
            bits1 = [DIGIT_MAP[d][dim] for d in parts['二部']]
            bits2 = [DIGIT_MAP[d][dim] for d in parts['四部']]
            s1 = get_state_id(bits1)
            s2 = get_state_id(bits2)
        
        if s1 + s2 == 9:
            valid_pairs += 1
        total_pairs += 1
    
    return valid_pairs / total_pairs if total_pairs > 0 else 0

def calculate_Omega(pi_digits):
    """计算四维Ω值 (论文公式3)"""
    # 正向序列: B_k^forward = [d_{12k+1}, ..., d_{12k+12}]
    forward_blocks = split_into_12blocks(pi_digits)
    
    # 反向序列: B_k^backward = [d_{N-12k}, ..., d_{N-12k-11}]
    reversed_digits = pi_digits[::-1]
    backward_blocks = split_into_12blocks(reversed_digits)
    
    if not forward_blocks or not backward_blocks:
        return 0.0, {"小大": 0.0, "上下": 0.0, "奇偶": 0.0, "AB": 0.0}
    
    dims = ['小大', '上下', '奇偶', 'AB']
    Delta_R = {}
    
    for dim in dims:
        R_fwd = calculate_R_dimension(forward_blocks, dim)
        R_bwd = calculate_R_dimension(backward_blocks, dim)
        Delta_R[dim] = abs(R_fwd - R_bwd)
    
    # Ω = sqrt(ΔR_小大² + ΔR_上下² + ΔR_奇偶² + ΔR_AB²)
    Omega = math.sqrt(
        Delta_R['小大']**2 + 
        Delta_R['上下']**2 + 
        Delta_R['奇偶']**2 + 
        Delta_R['AB']**2
    )
    
    return Omega, Delta_R
