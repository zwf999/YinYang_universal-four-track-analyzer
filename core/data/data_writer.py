# core/data/data_writer.py
# 数据写入器

import os
import json
from typing import Dict, List, Any, Optional

class DataWriter:
    """数据写入器"""
    
    def __init__(self, data_dir: str = './data'):
        """
        初始化数据写入器
        
        Args:
            data_dir: 数据目录
        """
        self.data_dir = data_dir
        # 确保目录存在
        os.makedirs(self.data_dir, exist_ok=True)
    
    def write_constant(self, name: str, digits: List[int], metadata: Dict[str, Any] = None) -> bool:
        """
        写入常数数据
        
        Args:
            name: 常数名称
            digits: 数字序列
            metadata: 元数据
            
        Returns:
            是否成功
        """
        try:
            # 构建文件路径
            file_path = os.path.join(self.data_dir, f"{name}.txt")
            
            # 写入数据
            with open(file_path, 'w', encoding='utf-8') as f:
                # 格式化为字符串
                digits_str = ''.join(map(str, digits))
                # 添加小数点（如果需要）
                if len(digits_str) > 0:
                    f.write(digits_str[0] + '.' + digits_str[1:] if len(digits_str) > 1 else digits_str)
            
            # 写入元数据
            if metadata:
                meta_file_path = os.path.join(self.data_dir, f"{name}_metadata.json")
                with open(meta_file_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"写入常数失败: {e}")
            return False
    
    def write_constant_with_precision(self, name: str, digits: List[int], precision: int = 10000) -> bool:
        """
        写入指定精度的常数数据
        
        Args:
            name: 常数名称
            digits: 数字序列
            precision: 精度（位数）
            
        Returns:
            是否成功
        """
        # 截取指定精度
        truncated_digits = digits[:precision]
        
        # 构建文件路径
        file_path = os.path.join(self.data_dir, f"{name}_{precision}digits.txt")
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                digits_str = ''.join(map(str, truncated_digits))
                if len(digits_str) > 0:
                    f.write(digits_str[0] + '.' + digits_str[1:] if len(digits_str) > 1 else digits_str)
            
            return True
        except Exception as e:
            print(f"写入指定精度常数失败: {e}")
            return False
    
    def write_analysis_result(self, name: str, result: Dict[str, Any]) -> bool:
        """
        写入分析结果
        
        Args:
            name: 结果名称
            result: 分析结果
            
        Returns:
            是否成功
        """
        try:
            file_path = os.path.join(self.data_dir, f"analysis_{name}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"写入分析结果失败: {e}")
            return False
    
    def write_prediction_result(self, name: str, prediction: List[int], actual: List[int] = None, metadata: Dict[str, Any] = None) -> bool:
        """
        写入预测结果
        
        Args:
            name: 结果名称
            prediction: 预测序列
            actual: 实际序列
            metadata: 元数据
            
        Returns:
            是否成功
        """
        try:
            result = {
                'prediction': prediction,
                'actual': actual,
                'metadata': metadata,
                'length': len(prediction)
            }
            
            file_path = os.path.join(self.data_dir, f"prediction_{name}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"写入预测结果失败: {e}")
            return False
    
    def delete_constant(self, name: str) -> bool:
        """
        删除常数数据
        
        Args:
            name: 常数名称
            
        Returns:
            是否成功
        """
        try:
            # 删除主文件
            file_path = os.path.join(self.data_dir, f"{name}.txt")
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # 删除元数据文件
            meta_file_path = os.path.join(self.data_dir, f"{name}_metadata.json")
            if os.path.exists(meta_file_path):
                os.remove(meta_file_path)
            
            # 删除其他可能的文件
            for ext in ['_100k.txt', '_digits.txt', '_high_precision.txt', '_metadata.json']:
                candidate_path = os.path.join(self.data_dir, f"{name}{ext}")
                if os.path.exists(candidate_path):
                    os.remove(candidate_path)
            
            return True
        except Exception as e:
            print(f"删除常数失败: {e}")
            return False
    
    def write_batch_constants(self, constants: Dict[str, List[int]]) -> Dict[str, bool]:
        """
        批量写入常数
        
        Args:
            constants: 常数字典，键为名称，值为数字序列
            
        Returns:
            每个常数的写入结果
        """
        results = {}
        for name, digits in constants.items():
            results[name] = self.write_constant(name, digits)
        return results
    
    def set_data_dir(self, data_dir: str):
        """
        设置数据目录
        
        Args:
            data_dir: 数据目录路径
        """
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
