# core/data/data_reader.py
# 数据读取器

import os
import re
from typing import Dict, List, Any

class DataReader:
    """数据读取器"""
    
    def __init__(self, data_dir: str = './data'):
        """
        初始化数据读取器
        
        Args:
            data_dir: 数据目录
        """
        self.data_dir = data_dir
    
    def read_constant(self, name: str, max_digits: int = 10000) -> List[int]:
        """
        读取常数数据
        
        Args:
            name: 常数名称
            max_digits: 最大读取位数
            
        Returns:
            数字序列
        """
        # 尝试不同的文件格式
        file_patterns = [
            f"{name}.txt",
            f"{name}_100k.txt",
            f"{name}_digits.txt",
            f"{name}_digits_1m.txt",
            f"{name}_high_precision.txt"
        ]
        
        for pattern in file_patterns:
            file_path = os.path.join(self.data_dir, pattern)
            if os.path.exists(file_path):
                return self._read_file(file_path, max_digits)
        
        # 尝试在当前目录查找
        for pattern in file_patterns:
            file_path = pattern
            if os.path.exists(file_path):
                return self._read_file(file_path, max_digits)
        
        return []
    
    def _read_file(self, file_path: str, max_digits: int) -> List[int]:
        """
        读取文件内容
        
        Args:
            file_path: 文件路径
            max_digits: 最大读取位数
            
        Returns:
            数字序列
        """
        digits = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().strip()
                
                # 处理不同格式
                if '.' in content:
                    content = content.replace('.', '').replace(' ', '').replace(',', '')
                
                # 提取数字
                for char in content:
                    if char.isdigit():
                        digits.append(int(char))
                        if len(digits) >= max_digits:
                            break
        except Exception as e:
            print(f"读取文件失败 {file_path}: {e}")
        
        return digits
    
    def list_constants(self) -> List[Dict[str, Any]]:
        """
        列出所有可用的常数
        
        Returns:
            常数列表
        """
        constants = []
        
        # 遍历数据目录
        if os.path.exists(self.data_dir):
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.txt'):
                    # 提取常数名称
                    constant_name = self._extract_constant_name(filename)
                    if constant_name:
                        info = self.get_constant_info(constant_name)
                        constants.append(info)
        
        # 去重
        unique_constants = []
        seen_names = set()
        for const in constants:
            name = const.get('name')
            if name and name not in seen_names:
                seen_names.add(name)
                unique_constants.append(const)
        
        return unique_constants
    
    def get_constant_info(self, name: str) -> Dict[str, Any]:
        """
        获取常数信息
        
        Args:
            name: 常数名称
            
        Returns:
            常数信息
        """
        # 查找文件
        file_patterns = [
            f"{name}.txt",
            f"{name}_100k.txt",
            f"{name}_digits.txt",
            f"{name}_digits_1m.txt",
            f"{name}_high_precision.txt"
        ]
        
        file_path = None
        for pattern in file_patterns:
            candidate_path = os.path.join(self.data_dir, pattern)
            if os.path.exists(candidate_path):
                file_path = candidate_path
                break
        
        if not file_path:
            # 尝试在当前目录查找
            for pattern in file_patterns:
                if os.path.exists(pattern):
                    file_path = pattern
                    break
        
        info = {
            'name': name,
            'description': self._get_constant_description(name),
            'has_file': file_path is not None,
            'file_path': file_path,
            'estimated_length': 0
        }
        
        if file_path:
            info['estimated_length'] = self._estimate_file_length(file_path)
        
        return info
    
    def _extract_constant_name(self, filename: str) -> str:
        """
        从文件名提取常数名称
        
        Args:
            filename: 文件名
            
        Returns:
            常数名称
        """
        # 移除扩展名
        name = os.path.splitext(filename)[0]
        
        # 移除后缀
        name = re.sub(r'_\d+k$', '', name)  # 移除 _100k 等
        name = re.sub(r'_\d+digits.*$', '', name)  # 移除 _100000digits 等
        name = re.sub(r'_digits.*$', '', name)  # 移除 _digits 等
        name = re.sub(r'_high_precision$', '', name)  # 移除 _high_precision
        name = re.sub(r'_precise.*$', '', name)  # 移除 _precise_100k 等
        name = re.sub(r'_theory.*$', '', name)  # 移除 _theory_100k 等
        
        return name
    
    def _get_constant_description(self, name: str) -> str:
        """
        获取常数描述
        
        Args:
            name: 常数名称
            
        Returns:
            常数描述
        """
        descriptions = {
            'pi': '圆周率',
            'e': '自然常数',
            'phi': '黄金分割率',
            'sqrt2': '根号2',
            'sqrt3': '根号3',
            'zeta3': '阿佩里常数ζ(3)',
            'catalan': '卡塔兰常数G',
            'apery': '阿佩里常数',
            'euler_gamma': '欧拉常数γ',
            'champernowne': '钱珀瑙恩常数',
            'speed_of_light': '光速',
            'fine_structure_constant': '精细结构常数α',
            'planck_constant': '普朗克常数h',
            'elementary_charge': '基本电荷e',
            'electron_mass': '电子质量mₑ',
            'proton_mass': '质子质量mₚ',
            'neutron_mass': '中子质量mₙ',
            'gravitational_constant': '万有引力常数G',
            'boltzmann_constant': '玻尔兹曼常数k',
            'avogadro_constant': '阿伏伽德罗常数Nₐ',
            'rydberg_constant': '里德伯常数R∞',
            'bohr_radius': '玻尔半径a₀',
            'planck_length': '普朗克长度',
            'planck_mass': '普朗克质量',
            'planck_time': '普朗克时间',
            'standard_gravity': '标准重力加速度g',
            'astronomical_unit': '天文单位AU',
            'light_year': '光年ly',
            'hubble_constant': '哈勃常数H₀',
            'vacuum_permeability': '真空磁导率μ₀',
            'vacuum_permittivity': '真空介电常数ε₀',
            'impedance_free_space': '自由空间阻抗Z₀',
            'compton_wavelength': '电子康普顿波长λ_c',
            'classical_electron_radius': '经典电子半径rₑ'
        }
        
        return descriptions.get(name, '未知常数')
    
    def _estimate_file_length(self, file_path: str) -> int:
        """
        估计文件长度
        
        Args:
            file_path: 文件路径
            
        Returns:
            估计的数字长度
        """
        try:
            # 获取文件大小
            file_size = os.path.getsize(file_path)
            
            # 估计数字数量（假设文件主要是数字）
            estimated_digits = int(file_size * 0.9)  # 假设90%是数字
            
            return estimated_digits
        except Exception:
            return 0
    
    def set_data_dir(self, data_dir: str):
        """
        设置数据目录
        
        Args:
            data_dir: 数据目录路径
        """
        self.data_dir = data_dir
