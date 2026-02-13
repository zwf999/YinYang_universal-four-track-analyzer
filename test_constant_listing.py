#!/usr/bin/env python3
# 测试常数列表功能

from core.data.data_manager import DataManager

print("=== 测试常数列表功能 ===")

# 创建数据管理器实例
data_manager = DataManager()

# 列出所有可用常数
print("\n1. 获取所有可用常数...")
constants = data_manager.list_constants()
print(f"找到 {len(constants)} 个可用常数")

# 打印常数名称列表
print("\n2. 常数名称列表:")
constant_names = [const['name'] for const in constants]
constant_names.sort()
for i, name in enumerate(constant_names, 1):
    print(f"{i:2d}. {name}")

# 检查特定常数
print("\n3. 检查特定常数:")
check_names = ['fine_structure_constant', 'speed_of_light', 'planck_constant', 'astronomical_unit', 'avogadro_constant']
for name in check_names:
    if name in constant_names:
        print(f"✅ {name} - 已识别")
    else:
        print(f"❌ {name} - 未识别")

# 检查精细常数
print("\n4. 检查精细常数:")
fine_structure_names = [name for name in constant_names if 'fine_structure' in name]
if fine_structure_names:
    print(f"找到 {len(fine_structure_names)} 个精细结构常数:")
    for name in fine_structure_names:
        print(f"   ✅ {name}")
else:
    print("❌ 未找到精细结构常数")

# 检查光速
print("\n5. 检查光速:")
speed_names = [name for name in constant_names if 'speed' in name or 'light' in name]
if speed_names:
    print(f"找到 {len(speed_names)} 个光速相关常数:")
    for name in speed_names:
        print(f"   ✅ {name}")
else:
    print("❌ 未找到光速相关常数")

# 检查文件路径
print("\n6. 检查文件路径:")
for const in constants[:5]:  # 只检查前5个
    name = const['name']
    file_path = const['file_path']
    has_file = const['has_file']
    print(f"{name}: {'有文件' if has_file else '无文件'} {file_path if file_path else ''}")

print("\n=== 测试完成 ===")
print(f"总计找到 {len(constants)} 个常数")
