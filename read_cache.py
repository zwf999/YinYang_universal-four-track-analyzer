# read_cache.py
# 读取缓存文件内容

import pickle


try:
    with open('cache/cache.pkl', 'rb') as f:
        data = pickle.load(f)
    
    print('缓存内容:')
    print(f'缓存项数量: {len(data)}')
    
    # 遍历缓存项
    for key, value in data.items():
        print(f'\n键: {key}')
        print(f'值: {value}')
        print(f'类型: {type(value)}')
        
        # 检查是否是DNA相关的缓存
        if 'dna_' in key:
            print('✓ 这是DNA相关的缓存项')
            
            # 尝试从键中提取DNA序列信息
            import re
            match = re.search(r'dna_(.+)_\d+', key)
            if match:
                print(f'提取的DNA信息: {match.group(1)}')
                
except Exception as e:
    print(f'读取缓存失败: {e}')
    import traceback
    traceback.print_exc()
