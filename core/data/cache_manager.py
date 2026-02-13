# core/data/cache_manager.py
# 缓存管理器

import os
import pickle
import time
from typing import Dict, List, Any, Optional
import glob

class CacheManager:
    """缓存管理器"""
    
    def __init__(self, cache_dir: str = './cache'):
        """
        初始化缓存管理器
        
        Args:
            cache_dir: 缓存目录
        """
        self.cache_dir = cache_dir
        self.cache = {}
        self.expire_times = {}
        
        # 确保缓存目录存在
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 加载缓存
        self._load_cache()
    
    def _load_cache(self):
        """加载缓存"""
        try:
            cache_file = os.path.join(self.cache_dir, 'cache.pkl')
            if os.path.exists(cache_file):
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)
                    self.cache = data.get('cache', {})
                    self.expire_times = data.get('expire_times', {})
                    # 清理过期缓存
                    self._clean_expired()
        except Exception as e:
            print(f"加载缓存失败: {e}")
    
    def _save_cache(self):
        """保存缓存"""
        try:
            cache_file = os.path.join(self.cache_dir, 'cache.pkl')
            data = {
                'cache': self.cache,
                'expire_times': self.expire_times
            }
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            print(f"保存缓存失败: {e}")
    
    def _clean_expired(self):
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = []
        
        for key, expire_time in self.expire_times.items():
            if expire_time > 0 and current_time > expire_time:
                expired_keys.append(key)
        
        for key in expired_keys:
            if key in self.cache:
                del self.cache[key]
            if key in self.expire_times:
                del self.expire_times[key]
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，不存在或过期返回None
        """
        # 清理过期缓存
        self._clean_expired()
        
        # 检查缓存
        if key in self.cache:
            return self.cache[key]
        
        return None
    
    def set(self, key: str, value: Any, expire_time: int = 0) -> bool:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            expire_time: 过期时间（秒），0表示永不过期
            
        Returns:
            是否成功
        """
        try:
            self.cache[key] = value
            if expire_time > 0:
                self.expire_times[key] = time.time() + expire_time
            else:
                self.expire_times[key] = 0
            
            # 保存缓存
            self._save_cache()
            return True
        except Exception as e:
            print(f"设置缓存失败: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        删除缓存
        
        Args:
            key: 缓存键
            
        Returns:
            是否成功
        """
        try:
            if key in self.cache:
                del self.cache[key]
            if key in self.expire_times:
                del self.expire_times[key]
            
            # 保存缓存
            self._save_cache()
            return True
        except Exception as e:
            print(f"删除缓存失败: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """
        删除匹配模式的缓存
        
        Args:
            pattern: 键模式，支持通配符
            
        Returns:
            删除的缓存项数量
        """
        import fnmatch
        keys_to_delete = []
        
        for key in self.cache.keys():
            if fnmatch.fnmatch(key, pattern):
                keys_to_delete.append(key)
        
        count = 0
        for key in keys_to_delete:
            if self.delete(key):
                count += 1
        
        return count
    
    def clean(self) -> int:
        """
        清理所有缓存
        
        Returns:
            删除的缓存项数量
        """
        count = len(self.cache)
        self.cache.clear()
        self.expire_times.clear()
        
        # 保存缓存
        self._save_cache()
        
        return count
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            缓存统计
        """
        # 清理过期缓存
        self._clean_expired()
        
        # 计算缓存大小
        cache_size = 0
        for key, value in self.cache.items():
            try:
                cache_size += len(pickle.dumps(value))
            except:
                pass
        
        # 计算过期时间分布
        current_time = time.time()
        expire_distribution = {
            'expired': 0,
            'expiring_soon': 0,  # 10分钟内过期
            'valid': 0
        }
        
        for key, expire_time in self.expire_times.items():
            if expire_time == 0:
                expire_distribution['valid'] += 1
            elif current_time > expire_time:
                expire_distribution['expired'] += 1
            elif expire_time - current_time < 600:  # 10分钟
                expire_distribution['expiring_soon'] += 1
            else:
                expire_distribution['valid'] += 1
        
        return {
            'total_items': len(self.cache),
            'cache_size_bytes': cache_size,
            'cache_size_mb': cache_size / (1024 * 1024),
            'expire_distribution': expire_distribution,
            'cache_dir': self.cache_dir
        }
    
    def exists(self, key: str) -> bool:
        """
        检查缓存是否存在
        
        Args:
            key: 缓存键
            
        Returns:
            是否存在
        """
        return key in self.cache
    
    def clear_expired(self) -> int:
        """
        清理过期缓存
        
        Returns:
            删除的缓存项数量
        """
        before_count = len(self.cache)
        self._clean_expired()
        after_count = len(self.cache)
        
        # 保存缓存
        self._save_cache()
        
        return before_count - after_count
