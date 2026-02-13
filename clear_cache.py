#!/usr/bin/env python3
# 清除缓存

import os
import shutil

print("=== 清除缓存 ===")

# 清除缓存目录
cache_dir = './cache'
if os.path.exists(cache_dir):
    shutil.rmtree(cache_dir)
    print(f"已删除缓存目录: {cache_dir}")
else:
    print(f"缓存目录不存在: {cache_dir}")

# 确保数据目录存在
data_dir = './data'
if os.path.exists(data_dir):
    print(f"数据目录存在: {data_dir}")
    files = os.listdir(data_dir)
    print(f"数据文件数量: {len(files)}")
else:
    print(f"数据目录不存在: {data_dir}")

print("\n=== 缓存清除完成 ===")
print("现在重新运行UI程序，应该能看到所有41个常数了！")
