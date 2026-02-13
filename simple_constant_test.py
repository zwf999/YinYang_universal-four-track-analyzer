#!/usr/bin/env python3
# 简单测试常数列表功能

from core.data.data_manager import DataManager

print("=== 简单测试常数列表功能 ===")

# 创建数据管理器实例
data_manager = DataManager()

# 列出所有可用常数
constants = data_manager.list_constants()
print(f"找到 {len(constants)} 个可用常数")

# 打印常数名称
constant_names = [const['name'] for const in constants]
constant_names.sort()

print("\n常数名称:")
for name in constant_names:
    print(name)

# 检查精细常数
print("\n=== 检查精细常数 ===")
fine_structure_constants = [name for name in constant_names if 'fine_structure' in name]
print(f"找到 {len(fine_structure_constants)} 个精细结构常数:")
for name in fine_structure_constants:
    print(f"- {name}")

# 检查光速
print("\n=== 检查光速 ===")
speed_constants = [name for name in constant_names if 'speed' in name or 'light' in name]
print(f"找到 {len(speed_constants)} 个光速相关常数:")
for name in speed_constants:
    print(f"- {name}")
