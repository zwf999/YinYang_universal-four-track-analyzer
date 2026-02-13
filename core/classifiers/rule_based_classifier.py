# core/classifiers/rule_based_classifier.py
# 基于规则的分类器

from typing import Dict, List, Any
from core.classifiers.base_classifier import BaseClassifier

class RuleBasedClassifier(BaseClassifier):
    """基于规则的分类器"""
    
    def __init__(self):
        """初始化基于规则的分类器"""
        # 常数类型映射
        self.constant_mappings = {
            # 数学常数
            'pi': {'type': 'mathematical', 'subtype': 'irrational', 'description': '圆周率'},
            'e': {'type': 'mathematical', 'subtype': 'irrational', 'description': '自然常数'},
            'phi': {'type': 'mathematical', 'subtype': 'irrational', 'description': '黄金分割率'},
            'sqrt2': {'type': 'mathematical', 'subtype': 'irrational', 'description': '根号2'},
            'sqrt3': {'type': 'mathematical', 'subtype': 'irrational', 'description': '根号3'},
            'zeta3': {'type': 'mathematical', 'subtype': 'irrational', 'description': '阿佩里常数ζ(3)'},
            'catalan': {'type': 'mathematical', 'subtype': 'irrational', 'description': '卡塔兰常数G'},
            'apery': {'type': 'mathematical', 'subtype': 'irrational', 'description': '阿佩里常数'},
            'euler_gamma': {'type': 'mathematical', 'subtype': 'irrational', 'description': '欧拉常数γ'},
            'champernowne': {'type': 'mathematical', 'subtype': 'transcendental', 'description': '钱珀瑙恩常数'},
            
            # 物理常数
            'speed_of_light': {'type': 'physical', 'subtype': 'exact', 'description': '光速'},
            'fine_structure_constant': {'type': 'physical', 'subtype': 'fundamental', 'description': '精细结构常数α'},
            'planck_constant': {'type': 'physical', 'subtype': 'fundamental', 'description': '普朗克常数h'},
            'elementary_charge': {'type': 'physical', 'subtype': 'fundamental', 'description': '基本电荷e'},
            'electron_mass': {'type': 'physical', 'subtype': 'particle', 'description': '电子质量mₑ'},
            'proton_mass': {'type': 'physical', 'subtype': 'particle', 'description': '质子质量mₚ'},
            'neutron_mass': {'type': 'physical', 'subtype': 'particle', 'description': '中子质量mₙ'},
            'gravitational_constant': {'type': 'physical', 'subtype': 'fundamental', 'description': '万有引力常数G'},
            'boltzmann_constant': {'type': 'physical', 'subtype': 'fundamental', 'description': '玻尔兹曼常数k'},
            'avogadro_constant': {'type': 'physical', 'subtype': 'fundamental', 'description': '阿伏伽德罗常数Nₐ'},
            'rydberg_constant': {'type': 'physical', 'subtype': 'spectral', 'description': '里德伯常数R∞'},
            'bohr_radius': {'type': 'physical', 'subtype': 'atomic', 'description': '玻尔半径a₀'},
            'planck_length': {'type': 'physical', 'subtype': 'planck', 'description': '普朗克长度'},
            'planck_mass': {'type': 'physical', 'subtype': 'planck', 'description': '普朗克质量'},
            'planck_time': {'type': 'physical', 'subtype': 'planck', 'description': '普朗克时间'},
            'standard_gravity': {'type': 'physical', 'subtype': 'geophysical', 'description': '标准重力加速度g'},
            'astronomical_unit': {'type': 'physical', 'subtype': 'astronomical', 'description': '天文单位AU'},
            'light_year': {'type': 'physical', 'subtype': 'astronomical', 'description': '光年ly'},
            'hubble_constant': {'type': 'physical', 'subtype': 'cosmological', 'description': '哈勃常数H₀'},
            'vacuum_permeability': {'type': 'physical', 'subtype': 'electromagnetic', 'description': '真空磁导率μ₀'},
            'vacuum_permittivity': {'type': 'physical', 'subtype': 'electromagnetic', 'description': '真空介电常数ε₀'},
            'impedance_free_space': {'type': 'physical', 'subtype': 'electromagnetic', 'description': '自由空间阻抗Z₀'},
            'compton_wavelength': {'type': 'physical', 'subtype': 'particle', 'description': '电子康普顿波长λ_c'},
            'classical_electron_radius': {'type': 'physical', 'subtype': 'particle', 'description': '经典电子半径rₑ'}
        }
    
    def classify(self, digits: List[int], name: str = None) -> Dict[str, Any]:
        """
        基于规则和名称分类数字序列
        
        Args:
            digits: 输入数字序列
            name: 常数名称（可选）
            
        Returns:
            分类结果
        """
        if not self.validate_input(digits):
            return {
                'type': 'unknown',
                'subtype': 'unknown',
                'description': '未知常数',
                'confidence': 0.0,
                'features': {}
            }
        
        digits = self.preprocess(digits)
        
        # 如果提供了名称，基于名称分类
        if name:
            return self._classify_by_name(name)
        
        # 基于数字特征分类
        return self._classify_by_features(digits)
    
    def _classify_by_name(self, name: str) -> Dict[str, Any]:
        """基于名称分类"""
        name = name.lower()
        
        # 直接映射
        if name in self.constant_mappings:
            mapping = self.constant_mappings[name]
            return {
                'type': mapping['type'],
                'subtype': mapping['subtype'],
                'description': mapping['description'],
                'confidence': 1.0,
                'method': 'name_based'
            }
        
        # 名称包含匹配
        for constant_name, mapping in self.constant_mappings.items():
            if constant_name in name:
                return {
                    'type': mapping['type'],
                    'subtype': mapping['subtype'],
                    'description': mapping['description'],
                    'confidence': 0.8,
                    'method': 'name_contains'
                }
        
        # 未知常数
        return {
            'type': 'unknown',
            'subtype': 'unknown',
            'description': '未知常数',
            'confidence': 0.0,
            'method': 'name_unknown'
        }
    
    def _classify_by_features(self, digits: List[int]) -> Dict[str, Any]:
        """基于数字特征分类"""
        # 计算基本特征
        length = len(digits)
        digit_set = set(digits)
        unique_digits = len(digit_set)
        
        # 基于特征的简单分类
        features = {
            'length': length,
            'unique_digits': unique_digits,
            'digit_coverage': unique_digits / 10.0,
            'has_all_digits': unique_digits == 10
        }
        
        # 基于特征推断类型
        if length > 1000 and features['has_all_digits']:
            # 长序列且包含所有数字，可能是数学常数
            return {
                'type': 'mathematical',
                'subtype': 'irrational',
                'description': '疑似数学常数',
                'confidence': 0.6,
                'method': 'feature_based',
                'features': features
            }
        elif length < 100 and not features['has_all_digits']:
            # 短序列且不包含所有数字，可能是物理常数
            return {
                'type': 'physical',
                'subtype': 'unknown',
                'description': '疑似物理常数',
                'confidence': 0.5,
                'method': 'feature_based',
                'features': features
            }
        else:
            # 无法确定
            return {
                'type': 'unknown',
                'subtype': 'unknown',
                'description': '未知常数',
                'confidence': 0.3,
                'method': 'feature_based',
                'features': features
            }
    
    def get_name(self) -> str:
        """获取分类器名称"""
        return "RuleBasedClassifier"
    
    def get_version(self) -> str:
        """获取分类器版本"""
        return "2.0.0"
    
    def add_constant_mapping(self, name: str, mapping: Dict[str, str]) -> None:
        """
        添加常数映射
        
        Args:
            name: 常数名称
            mapping: 常数映射信息
        """
        self.constant_mappings[name.lower()] = mapping
    
    def remove_constant_mapping(self, name: str) -> None:
        """
        移除常数映射
        
        Args:
            name: 常数名称
        """
        if name.lower() in self.constant_mappings:
            del self.constant_mappings[name.lower()]
    
    def get_available_constants(self) -> List[str]:
        """
        获取可用的常数名称
        
        Returns:
            常数名称列表
        """
        return list(self.constant_mappings.keys())
