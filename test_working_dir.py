#!/usr/bin/env python3
# 测试工作目录

import os
print(f"当前工作目录: {os.getcwd()}")
print(f"./data 目录是否存在: {os.path.exists('./data')}")
print(f"./data 绝对路径: {os.path.abspath('./data')}")

# 检查数据目录中的文件
if os.path.exists('./data'):
    files = os.listdir('./data')
    print(f"数据目录中的文件数量: {len(files)}")
    print(f"前5个文件: {files[:5]}")
else:
    print("数据目录不存在！")
