# tests/test_data_manager.py
# 测试数据管理器

import unittest
import os
import tempfile
from core.data.data_manager import DataManager

class TestDataManager(unittest.TestCase):
    """测试数据管理器"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = os.path.join(self.temp_dir, 'cache')
        
        # 初始化数据管理器
        self.data_manager = DataManager(
            data_dir=self.temp_dir,
            cache_dir=self.cache_dir
        )
    
    def tearDown(self):
        """清理测试环境"""
        # 删除临时文件
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_save_and_load_constant(self):
        """测试保存和加载常数"""
        # 测试数据
        test_name = 'test_constant'
        test_digits = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
        test_metadata = {'source': 'test', 'created_at': '2024-01-01'}
        
        # 保存常数
        save_result = self.data_manager.save_constant(test_name, test_digits, test_metadata)
        self.assertTrue(save_result)
        
        # 加载常数
        loaded_digits = self.data_manager.load_constant(test_name, 100)
        self.assertEqual(loaded_digits, test_digits)
    
    def test_cache_functionality(self):
        """测试缓存功能"""
        # 测试数据
        test_name = 'cache_test'
        test_digits = [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
        
        # 保存常数
        self.data_manager.save_constant(test_name, test_digits)
        
        # 第一次加载（应该缓存）
        first_load = self.data_manager.load_constant(test_name, 10)
        self.assertEqual(first_load, test_digits)
        
        # 检查缓存统计
        cache_stats = self.data_manager.get_cache_stats()
        self.assertGreater(cache_stats.get('total_items', 0), 0)
        
        # 清理缓存
        clean_count = self.data_manager.clean_cache()
        self.assertGreater(clean_count, 0)
        
        # 检查缓存是否为空
        cache_stats_after = self.data_manager.get_cache_stats()
        self.assertEqual(cache_stats_after.get('total_items', 0), 0)
    
    def test_list_constants(self):
        """测试列出常数"""
        # 保存几个测试常数
        test_constants = {
            'test1': [1, 2, 3],
            'test2': [4, 5, 6],
            'test3': [7, 8, 9]
        }
        
        for name, digits in test_constants.items():
            self.data_manager.save_constant(name, digits)
        
        # 列出常数
        constants = self.data_manager.list_constants()
        constant_names = [const['name'] for const in constants]
        
        # 验证所有测试常数都在列表中
        for name in test_constants.keys():
            self.assertIn(name, constant_names)
    
    def test_delete_constant(self):
        """测试删除常数"""
        # 测试数据
        test_name = 'delete_test'
        test_digits = [1, 1, 2, 2, 3, 3]
        
        # 保存常数
        self.data_manager.save_constant(test_name, test_digits)
        
        # 验证常数存在
        loaded_digits = self.data_manager.load_constant(test_name, 10)
        self.assertEqual(loaded_digits, test_digits)
        
        # 删除常数
        delete_result = self.data_manager.delete_constant(test_name)
        self.assertTrue(delete_result)
        
        # 验证常数已删除
        deleted_digits = self.data_manager.load_constant(test_name, 10)
        self.assertEqual(deleted_digits, [])
    
    def test_save_and_load_analysis_result(self):
        """测试保存和加载分析结果"""
        # 测试数据
        test_name = 'analysis_test'
        test_result = {
            'basic_stats': {
                'length': 100,
                'mean': 4.5,
                'std': 2.87
            },
            'entropy': 2.97
        }
        
        # 保存分析结果
        save_result = self.data_manager.save_analysis_result(test_name, test_result)
        self.assertTrue(save_result)
        
        # 加载分析结果
        loaded_result = self.data_manager.load_analysis_result(test_name)
        self.assertEqual(loaded_result, test_result)

if __name__ == '__main__':
    unittest.main()