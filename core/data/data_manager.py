# core/data/data_manager.py
# 数据管理器

import os
import json
import pickle
from typing import Dict, List, Any, Optional
from core.data.data_reader import DataReader
from core.data.data_writer import DataWriter
from core.data.cache_manager import CacheManager
from dna_encoder import DNAEncoder

class DataManager:
    """数据管理器"""
    
    def __init__(self, data_dir: str = './data', cache_dir: str = './cache'):
        """
        初始化数据管理器
        
        Args:
            data_dir: 数据目录
            cache_dir: 缓存目录
        """
        self.data_dir = data_dir
        self.cache_dir = cache_dir
        self.reader = DataReader(data_dir)
        self.writer = DataWriter(data_dir)
        self.cache = CacheManager(cache_dir)
        self.dna_encoder = DNAEncoder()  # 添加DNA编码器
        
        # 确保目录存在
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保目录存在"""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _is_dna_sequence(self, data: str) -> bool:
        """
        检测输入是否为DNA序列
        
        Args:
            data: 输入字符串
            
        Returns:
            是否为DNA序列
        """
        # 只包含A,C,G,T的字符串视为DNA序列
        valid_bases = set('ACGT')
        return all(char in valid_bases for char in data.upper())
    
    def encode_dna(self, dna_sequence: str) -> List[int]:
        """
        将DNA序列编码为数字序列
        
        Args:
            dna_sequence: DNA字符串
            
        Returns:
            数字序列
        """
        # 检查缓存
        cache_key = f"dna_{dna_sequence[:50]}_{len(dna_sequence)}"
        cached_data = self.cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # 编码DNA序列
        result = self.dna_encoder.encode(dna_sequence)
        digits = result['encoded_digits']
        
        # 缓存数据
        if digits:
            self.cache.set(cache_key, digits, expire_time=3600)  # 缓存1小时
        
        return digits
    
    def load_constant(self, name: str, max_digits: int = 10000) -> List[int]:
        """
        加载常数数据
        
        Args:
            name: 常数名称
            max_digits: 最大读取位数
            
        Returns:
            数字序列
        """
        # 检查是否为DNA序列
        if self._is_dna_sequence(name):
            # 直接处理DNA序列
            return self.encode_dna(name)[:max_digits]
        
        # 检查缓存
        cache_key = f"{name}_{max_digits}"
        cached_data = self.cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # 加载数据
        digits = self.reader.read_constant(name, max_digits)
        
        # 缓存数据
        if digits:
            self.cache.set(cache_key, digits, expire_time=3600)  # 缓存1小时
        
        return digits
    
    def save_constant(self, name: str, digits: List[int], metadata: Dict[str, Any] = None) -> bool:
        """
        保存常数数据
        
        Args:
            name: 常数名称
            digits: 数字序列
            metadata: 元数据
            
        Returns:
            是否成功
        """
        # 保存数据
        success = self.writer.write_constant(name, digits, metadata)
        
        if success:
            # 清除相关缓存
            self.cache.delete_pattern(f"{name}_*")
        
        return success
    
    def list_constants(self) -> List[Dict[str, Any]]:
        """
        列出所有可用的常数
        
        Returns:
            常数列表
        """
        return self.reader.list_constants()
    
    def get_constant_info(self, name: str) -> Dict[str, Any]:
        """
        获取常数信息
        
        Args:
            name: 常数名称
            
        Returns:
            常数信息
        """
        return self.reader.get_constant_info(name)
    
    def delete_constant(self, name: str) -> bool:
        """
        删除常数
        
        Args:
            name: 常数名称
            
        Returns:
            是否成功
        """
        # 删除数据文件
        success = self.writer.delete_constant(name)
        
        if success:
            # 清除相关缓存
            self.cache.delete_pattern(f"{name}_*")
        
        return success
    
    def clean_cache(self) -> int:
        """
        清理缓存
        
        Returns:
            删除的缓存项数量
        """
        return self.cache.clean()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            缓存统计
        """
        return self.cache.get_stats()
    
    def load_analysis_result(self, name: str) -> Dict[str, Any]:
        """
        加载分析结果
        
        Args:
            name: 分析结果名称
            
        Returns:
            分析结果
        """
        # 检查缓存
        cache_key = f"analysis_{name}"
        cached_data = self.cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # 加载文件
        file_path = os.path.join(self.data_dir, f"analysis_{name}.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 缓存结果
                self.cache.set(cache_key, data, expire_time=7200)  # 缓存2小时
                return data
            except Exception as e:
                print(f"加载分析结果失败: {e}")
        
        return {}
    
    def save_analysis_result(self, name: str, result: Dict[str, Any]) -> bool:
        """
        保存分析结果
        
        Args:
            name: 分析结果名称
            result: 分析结果
            
        Returns:
            是否成功
        """
        try:
            file_path = os.path.join(self.data_dir, f"analysis_{name}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            # 缓存结果
            cache_key = f"analysis_{name}"
            self.cache.set(cache_key, result, expire_time=7200)  # 缓存2小时
            
            return True
        except Exception as e:
            print(f"保存分析结果失败: {e}")
            return False
    
    def get_data_dir(self) -> str:
        """
        获取数据目录
        
        Returns:
            数据目录路径
        """
        return self.data_dir
    
    def set_data_dir(self, data_dir: str):
        """
        设置数据目录
        
        Args:
            data_dir: 数据目录路径
        """
        self.data_dir = data_dir
        self.reader.set_data_dir(data_dir)
        self.writer.set_data_dir(data_dir)
        self._ensure_directories()
