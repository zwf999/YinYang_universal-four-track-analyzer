#!/usr/bin/env python3
# 测试天文单位文件识别

from core.data.data_manager import DataManager

print("=== 测试天文单位文件识别 ===")

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

# 检查天文单位
print("\n=== 检查天文单位 ===")
if 'astronomical_unit' in constant_names:
    print("✅ 天文单位已识别")
    # 获取天文单位信息
    info = data_manager.get_constant_info('astronomical_unit')
    print(f"  文件路径: {info['file_path']}")
    print(f"  文件存在: {info['has_file']}")
    print(f"  估计长度: {info['estimated_length']}")
else:
    print("❌ 天文单位未识别")

# 尝试直接加载天文单位
print("\n=== 尝试加载天文单位 ===")
try:
    digits = data_manager.load_constant('astronomical_unit', 100)
    if digits:
        print(f"✅ 成功加载天文单位，长度: {len(digits)}")
        print(f"  前20位: {digits[:20]}")
    else:
        print("❌ 无法加载天文单位")
except Exception as e:
    print(f"❌ 加载时出错: {e}")
