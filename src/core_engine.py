import numpy as np

# === 表1：数字属性映射 (严格按论文定义) ===
DIGIT_MAP = {
    0: {"规模": 0, "水平": 5, "生克": 0, "奇偶": 1},
    1: {"规模": 1, "水平": 1, "生克": 1, "奇偶": 1},
    2: {"规模": 1, "水平": 2, "生克": 1, "奇偶": 0},
    3: {"规模": 1, "水平": 3, "生克": 1, "奇偶": 1},
    4: {"规模": 1, "水平": 4, "生克": 1, "奇偶": 0},
    5: {"规模": 1, "水平": 5, "生克": 0, "奇偶": 1},
    6: {"规模": 1, "水平": 1, "生克": 1, "奇偶": 1},
    7: {"规模": 1, "水平": 2, "生克": 1, "奇偶": 0},
    8: {"规模": 0, "水平": 3, "生克": 1, "奇偶": 1},
    9: {"规模": 0, "水平": 4, "生克": 0, "奇偶": 0}
}

# === 表2：AB关系矩阵 (生=1, 克=0) ===
AB_MATRIX = np.array([
    [0, 0, 1, 1, 0],
    [0, 0, 1, 0, 1],
    [1, 1, 0, 0, 0],
    [1, 0, 0, 0, 1],
    [0, 1, 0, 1, 0]
])

def get_state_id(bits):
    mapping = {(1,1,1):1,(1,1,0):2,(1,0,1):3,(1,0,0):4,
               (0,1,1):5,(0,1,0):6,(0,0,1):7,(0,0,0):8}
    return mapping[tuple(bits)]

def calculate_Omega(digit_seq):
    N = len(digit_seq)
    K = N // 12
    if K == 0: return 0.0, {}
    
    dims = ['规模', '水平', '奇偶']
    Delta_R = {d: 0.0 for d in dims}
    Delta_R['生克'] = 0.0
    
    R_forward = {d: 0.0 for d in dims + ['生克']}
    R_backward = {d: 0.0 for d in dims + ['生克']}
    
    for dir_name in ['forward', 'backward']:
        R_vals = {d: 0.0 for d in dims + ['生克']}
        for k in range(K):
            if dir_name == 'forward':
                block = digit_seq[12*k : 12*(k+1)]
            else:
                start_idx = N - 12*(k+1)
                block = digit_seq[start_idx : start_idx+12]
            
            part1, part2, part3, part4 = block[0:3], block[3:6], block[6:9], block[9:12]
            pairs = [(part1, part3), (part2, part4)]
            
            for dim in dims:
                valid_count = sum(
                    1 for pA, pB in pairs
                    if get_state_id([DIGIT_MAP[d][dim] for d in pA]) +
                       get_state_id([DIGIT_MAP[d][dim] for d in pB]) == 9
                )
                R_vals[dim] += valid_count / 2.0
            
            # 生克维度
            def get_AB_state(part):
                levels = [DIGIT_MAP[d]['水平'] for d in part]
                e1 = AB_MATRIX[levels[0]-1, levels[1]-1]
                e2 = AB_MATRIX[levels[1]-1, levels[2]-1]
                e3 = AB_MATRIX[levels[2]-1, levels[0]-1]
                return get_state_id((e1, e2, e3))
            
            valid_count_AB = sum(
                1 for pA, pB in pairs
                if get_AB_state(pA) + get_AB_state(pB) == 9
            )
            R_vals['生克'] += valid_count_AB / 2.0
        
        for d in R_vals: R_vals[d] /= K
        if dir_name == 'forward': R_forward = R_vals
        else: R_backward = R_vals
    
    for d in Delta_R: Delta_R[d] = abs(R_forward[d] - R_backward[d])
    Omega = np.sqrt(sum(dr**2 for dr in Delta_R.values()))
    return Omega, Delta_R
