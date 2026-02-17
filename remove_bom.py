#!/usr/bin/env python3
"""
移除文件中的BOM字符
"""

import os

# 要处理的文件列表
files_to_process = [
    'core/predictors/ensemble_predictor.py',
    'core/predictors/pattern_predictor.py',
    'core/predictors/statistical_predictor.py',
    'core/predictors/hybrid_predictor.py',
    'core/predictors/base_predictor.py'
]

# 处理每个文件
for file_path in files_to_process:
    try:
        # 读取文件并移除BOM字符
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()

        # 写回文件（无BOM）
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"已移除文件 {file_path} 中的BOM字符")
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {e}")

print("\nBOM字符移除完成！")
