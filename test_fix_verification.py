#!/usr/bin/env python3
# 验证预测结果修复

from core.data.data_manager import DataManager
from core.predictors.ensemble_predictor import EnsemblePredictor
from core.predictors.pattern_predictor import PatternPredictor

print("验证预测结果修复")
print("=" * 50)

# 初始化组件
data_manager = DataManager()
ensemble_predictor = EnsemblePredictor()
pattern_predictor = PatternPredictor()

# 测试常数
constant_name = "pi"
train_length = 1000
predict_length = 100

print(f"测试常数: {constant_name}")
print(f"训练长度: {train_length}")
print(f"预测长度: {predict_length}")
print()

# 加载数据
print("加载数据...")
train_data = data_manager.load_constant(constant_name, train_length)
print(f"训练数据长度: {len(train_data)}")

# 测试集成预测器
print("\n测试集成预测器...")
ensemble_prediction = ensemble_predictor.predict(train_data, length=predict_length)
ensemble_unique = len(set(ensemble_prediction))
print(f"集成预测结果: {ensemble_prediction[:30]}...")
print(f"唯一数字数量: {ensemble_unique}")
print(f"是否有重复: {'是' if ensemble_unique == 1 else '否'}")

# 测试模式预测器
print("\n测试模式预测器...")
pattern_prediction = pattern_predictor.predict(train_data, length=predict_length)
pattern_unique = len(set(pattern_prediction))
print(f"模式预测结果: {pattern_prediction[:30]}...")
print(f"唯一数字数量: {pattern_unique}")
print(f"是否有重复: {'是' if pattern_unique == 1 else '否'}")

# 验证修复效果
print("\n修复验证结果:")
print("=" * 50)
if ensemble_unique > 1 and pattern_unique > 1:
    print("✅ 修复成功！预测结果不再生成重复的数字")
else:
    print("❌ 修复失败！预测结果仍然有重复的数字")
    if ensemble_unique == 1:
        print("   - 集成预测器仍然生成重复数字")
    if pattern_unique == 1:
        print("   - 模式预测器仍然生成重复数字")

print("\n测试完成！")
