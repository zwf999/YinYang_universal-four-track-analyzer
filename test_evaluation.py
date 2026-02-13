#!/usr/bin/env python3
# 测试预测评估功能

from core.data.data_manager import DataManager
from core.predictors.ensemble_predictor import EnsemblePredictor

print("测试预测评估功能")
print("=" * 50)

# 初始化组件
data_manager = DataManager()
predictor = EnsemblePredictor()

# 测试常数
constant_name = "pi"
train_length = 10000
predict_length = 100

print(f"测试常数: {constant_name}")
print(f"训练长度: {train_length}")
print(f"预测长度: {predict_length}")
print()

# 加载完整数据
print("加载数据...")
full_digits = data_manager.load_constant(constant_name, train_length + predict_length)
print(f"加载数据长度: {len(full_digits)}")

# 分割数据
train_data = full_digits[:train_length]
real_data = full_digits[train_length:train_length + predict_length]

# 预测
print("预测数据...")
prediction = predictor.predict(train_data, length=predict_length)

# 评估
correct_count = sum(1 for pred, real in zip(prediction, real_data) if pred == real)
accuracy = (correct_count / predict_length) * 100

print(f"\n预测结果: {prediction[:20]}...")
print(f"真实结果: {real_data[:20]}...")
print(f"\n准确性: {accuracy:.2f}% ({correct_count}/{predict_length})")
print()
print("测试完成！")
