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
        
        # 新的一步映射：直接将碱基对映射到0-9数字（用户提供的原始设计）
        self.basepair_to_num = {
            'AA': 0, 'AC': 1, 'AG': 2, 'AT': 3,
            'CA': 1, 'CC': 4, 'CG': 5, 'CT': 6,
            'GA': 2, 'GC': 5, 'GG': 7, 'GT': 8,
            'TA': 3, 'TC': 6, 'TG': 8, 'TT': 9
        }
        
        # 反向映射：数字到碱基对（用户提供的原始设计）
        self.num_to_basepair = {
            0: 'AA', 1: 'AC', 2: 'AG', 3: 'AT',
            4: 'CC', 5: 'CG', 6: 'CT', 7: 'GG',
            8: 'GT', 9: 'TT'
        }
        
        # 碱基到0-3的基础映射（仅用于简单编码）
        self.base_to_num = {'A': 0, 'C': 1, 'G': 2, 'T': 3}
        self.num_to_base = {0: 'A', 1: 'C', 2: 'G', 3: 'T'}
    
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
            # 处理碱基对（序列已确保为偶数长度）
            basepair = dna_seq[i:i+2]
            b1, b2 = basepair[0], basepair[1]
            
            # 使用新的一步映射：直接从碱基对获取编码
            code = self.basepair_to_num[basepair]
            
            # 确定方向（正序/逆序）
            # 根据碱基对与默认映射的关系确定方向
            default_basepair = self.num_to_basepair[code]
            is_forward = (basepair == default_basepair)
            direction = '' if is_forward else '←'  # 正序不标注，逆序用←标记
            
            digits.append(code)
            direction_flags.append(direction)
            encoding_details.append({
                'bases': basepair,
                'code': code,
                'direction': 'forward' if is_forward else 'reverse',
                'direction_mark': direction,
                'pair_type': self._get_pair_type_new(basepair)
            })
            
            i += 2
        
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
        
        dna_bases = []
        
        for idx, code in enumerate(digits):
            # 使用新的一步映射：直接从数字获取碱基对
            basepair = self.num_to_basepair[code]
            
            if idx < len(direction_flags):
                direction_mark = direction_flags[idx]
                
                if direction_mark == '':  # 正序（无标记）
                    dna_bases.extend(basepair)
                elif direction_mark == '←':  # 逆序（左箭头标记）
                    # 逆序碱基对
                    reversed_basepair = basepair[1] + basepair[0]
                    dna_bases.extend(reversed_basepair)
                else:
                    # 无方向信息，默认正序
                    dna_bases.extend(basepair)
            else:
                # 无方向信息，默认正序
                dna_bases.extend(basepair)
        
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
        
        # 确保序列为偶数长度（全是碱基对）
        if len(seq) % 2 != 0:
            # 截断最后一个碱基
            seq = seq[:-1]
            print("警告：序列长度为奇数，已截断最后一个碱基")
        
        return seq
    
    def _get_pair_type(self, x, y):
        """获取碱基对类型（旧方法，仅用于简单编码）"""
        if x == y:
            return 'homo'  # 相同碱基
        elif (x, y) in [(0, 3), (3, 0)]:  # A-T或T-A
            return 'watson_crick_at'
        elif (x, y) in [(1, 2), (2, 1)]:  # C-G或G-C
            return 'watson_crick_cg'
        else:
            return 'mismatch'
    
    def _get_pair_type_new(self, basepair):
        """获取碱基对类型（新方法，使用一步映射）"""
        b1, b2 = basepair[0], basepair[1]
        
        if b1 == b2:
            return 'homo'  # 相同碱基
        elif (b1, b2) in [('A', 'T'), ('T', 'A')]:  # A-T或T-A
            return 'watson_crick_at'
        elif (b1, b2) in [('C', 'G'), ('G', 'C')]:  # C-G或G-C
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