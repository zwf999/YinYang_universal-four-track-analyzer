# dna_encoder.py
class DNAEncoder:
    """DNA到数字的编码器"""
    
    def __init__(self, encoding_scheme='triangle'):
        """
        初始化编码器
        
        Args:
            encoding_scheme: 编码方案
                - 'triangle': 三角形编码（你的方案）
                - 'simple': 简单映射
        """
        self.encoding_scheme = encoding_scheme
        
        # 碱基到0-3的基础映射
        self.base_to_num = {'A': 0, 'C': 1, 'G': 2, 'T': 3}
        self.num_to_base = {0: 'A', 1: 'C', 2: 'G', 3: 'T'}
        
        # 你的三角形编码表
        self.triangle_encoding = {
            (0, 0): 0,                    # AA
            (0, 1): 1, (1, 1): 4,         # AC, CC
            (0, 2): 2, (1, 2): 5, (2, 2): 7,  # AG, CG, GG
            (0, 3): 3, (1, 3): 6, (2, 3): 8, (3, 3): 9  # AT, CT, GT, TT
        }
        
        # 反向映射
        self.code_to_pair = {v: k for k, v in self.triangle_encoding.items()}
    
    def encode(self, dna_sequence):
        """
        将DNA序列编码为0-9数字序列
        
        Args:
            dna_sequence: DNA字符串（只包含A,C,G,T）
            
        Returns:
            dict: 包含编码结果和元数据
        """
        # 验证输入
        validated_seq = self._validate_and_normalize(dna_sequence)
        
        if self.encoding_scheme == 'triangle':
            return self._encode_triangle(validated_seq)
        else:
            return self._encode_simple(validated_seq)
    
    def _encode_triangle(self, dna_seq):
        """使用三角形编码方案"""
        digits = []
        direction_flags = []  # 正序1，逆序-1
        encoding_details = []  # 记录每个数字的编码细节
        
        i = 0
        while i < len(dna_seq):
            if i + 1 < len(dna_seq):
                # 处理碱基对
                b1, b2 = dna_seq[i], dna_seq[i+1]
                n1, n2 = self.base_to_num[b1], self.base_to_num[b2]
                
                # 排序用于三角形编码
                small, large = (n1, n2) if n1 <= n2 else (n2, n1)
                code = self.triangle_encoding[(small, large)]
                
                # 记录方向
                is_forward = (n1 <= n2)
                # 使用左箭头标注反序，正序不标注
                direction = '' if is_forward else '←'
                
                digits.append(code)
                direction_flags.append(direction)
                encoding_details.append({
                    'bases': b1 + b2,
                    'numbers': (n1, n2),
                    'code': code,
                    'direction': 'forward' if is_forward else 'reverse',
                    'direction_mark': direction,
                    'pair_type': self._get_pair_type(small, large)
                })
                
                i += 2
            else:
                # 单个碱基（奇数长度序列）
                b = dna_seq[i]
                n = self.base_to_num[b]
                # 直接使用0-3表示单个碱基，不使用+5
                code = n
                
                digits.append(code)
                direction_flags.append(0)  # 无方向
                encoding_details.append({
                    'base': b,
                    'number': n,
                    'code': code,
                    'direction': 'single',
                    'pair_type': 'single'
                })
                
                i += 1
        
        return {
            'dna_sequence': dna_seq,
            'encoded_digits': digits,
            'direction_flags': direction_flags,
            'encoding_details': encoding_details,
            'encoding_scheme': self.encoding_scheme,
            'stats': self._calculate_stats(dna_seq, digits)
        }
    
    def _encode_simple(self, dna_seq):
        """简单编码方案（每个碱基直接映射）"""
        digits = []
        encoding_details = []
        
        for base in dna_seq:
            code = self.base_to_num[base]
            digits.append(code)
            encoding_details.append({
                'base': base,
                'code': code
            })
        
        return {
            'dna_sequence': dna_seq,
            'encoded_digits': digits,
            'encoding_details': encoding_details,
            'encoding_scheme': 'simple',
            'stats': self._calculate_stats(dna_seq, digits)
        }
    
    def decode(self, encoded_data):
        """从编码数据解码回DNA（三角形编码可逆）"""
        if encoded_data['encoding_scheme'] != 'triangle':
            raise ValueError("只有三角形编码方案支持解码")
        
        digits = encoded_data['encoded_digits']
        direction_flags = encoded_data.get('direction_flags', [])
        details = encoded_data.get('encoding_details', [])
        
        dna_bases = []
        
        for idx, code in enumerate(digits):
            if idx < len(details) and 'pair_type' in details[idx]:
                if details[idx]['pair_type'] == 'single':
                    # 单个碱基
                    n = code
                    dna_bases.append(self.num_to_base[n])
                else:
                    # 碱基对
                    if idx < len(direction_flags):
                        direction_mark = direction_flags[idx]
                        n1, n2 = self.code_to_pair[code]
                        
                        if direction_mark == '':  # 正序（无标记）
                            dna_bases.extend([self.num_to_base[n1], self.num_to_base[n2]])
                        elif direction_mark == '←':  # 逆序（左箭头标记）
                            dna_bases.extend([self.num_to_base[n2], self.num_to_base[n1]])
                        else:
                            # 无方向信息，默认正序
                            dna_bases.extend([self.num_to_base[n1], self.num_to_base[n2]])
        
        return ''.join(dna_bases)
    
    def _validate_and_normalize(self, dna_seq):
        """验证和规范化DNA序列"""
        # 转换为大写
        seq = dna_seq.upper()
        
        # 移除空白字符
        seq = ''.join(seq.split())
        
        # 验证字符
        valid_bases = set('ACGT')
        for char in seq:
            if char not in valid_bases:
                raise ValueError(f"DNA序列包含无效字符: {char}")
        
        return seq
    
    def _get_pair_type(self, x, y):
        """获取碱基对类型"""
        if x == y:
            return 'homo'  # 相同碱基
        elif (x, y) in [(0, 3), (3, 0)]:  # A-T或T-A
            return 'watson_crick_at'
        elif (x, y) in [(1, 2), (2, 1)]:  # C-G或G-C
            return 'watson_crick_cg'
        else:
            return 'mismatch'
    
    def _calculate_stats(self, dna_seq, digits):
        """计算统计信息"""
        total_bases = len(dna_seq)
        gc_count = dna_seq.count('G') + dna_seq.count('C')
        
        # 数字分布
        from collections import Counter
        digit_dist = Counter(digits)
        
        return {
            'total_bases': total_bases,
            'gc_content': gc_count / total_bases if total_bases > 0 else 0,
            'gc_count': gc_count,
            'at_count': total_bases - gc_count,
            'digit_distribution': dict(digit_dist),
            'unique_digits': len(set(digits))
        }