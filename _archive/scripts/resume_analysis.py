
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
续处理分析脚本
能够从上次中断的地方继续处理文件
"""

import os
import sys
import json
import random
import numpy as np
import argparse
import logging
from pathlib import Path
from collections import Counter
from typing import List, Dict, Tuple, Optional
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tai_analysis_resume.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

RANDOM_SEED = 42
__version__ = "10.0.1"
random.seed(RANDOM_SEED)

# 核心功能类和函数
class DataProcessor:
    """数据处理类"""
    
    @staticmethod
    def file_to_bits(file_path: str) -> Optional[str]:
        """将文件转换为二进制字符串"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            bits = ''.join(format(byte, '08b') for byte in content)
            logger.info(f"文件 {os.path.basename(file_path)} 读取成功，大小: {len(content)} 字节，比特数: {len(bits)}")
            return bits
        except Exception as e:
            logger.error(f"读取文件时出错 {file_path}: {e}")
            return None
    
    @staticmethod
    def bits_to_patterns(bits: str) -> Optional[List[int]]:
        """将二进制字符串转换为6-bit模式列表"""
        if len(bits) < 6:
            logger.error("比特长度不足6位")
            return None
        patterns = []
        for i in range(len(bits) - 5):
            pattern = bits[i:i+6]
            pattern_int = int(pattern, 2)
            patterns.append(pattern_int)
        return patterns

def calculate_shannon_entropy(probabilities: List[float]) -> float:
    """计算香农熵"""
    entropy = 0.0
    for p in probabilities:
        if p > 0:
            entropy -= p * np.log2(p)
    return entropy

def calculate_tse(entropy: float) -> float:
    """计算TSE"""
    return 6.0 * entropy / 4.0

def run_both_operations(patterns: List[int], direction: str) -> Tuple[Optional[Dict], Optional[Dict]]:
    """运行两次运算"""
    try:
        # 第一次运算：无序随机验证
        pattern_counter = Counter(patterns)
        total_patterns = len(patterns)
        probabilities = [count / total_patterns for count in pattern_counter.values()]
        entropy = calculate_shannon_entropy(probabilities)
        tse = calculate_tse(entropy)
        
        # 计算各层概率
        layer_probs = [0.0] * 16
        for pattern in patterns:
            layer = (pattern // 4) + 1
            if 1 <= layer <= 16:
                layer_probs[layer-1] += 1
        layer_probs = [p / total_patterns for p in layer_probs]
        
        # 计算4/7/12层Z值
        layer4_z = (layer_probs[3] - 1/16) / (np.std(layer_probs) if np.std(layer_probs) > 0 else 1)
        layer7_z = (layer_probs[6] - 1/16) / (np.std(layer_probs) if np.std(layer_probs) > 0 else 1)
        layer12_z = (layer_probs[11] - 1/16) / (np.std(layer_probs) if np.std(layer_probs) > 0 else 1)
        
        stable = abs(layer4_z) < 2 and abs(layer7_z) < 2 and abs(layer12_z) < 2
        
        result1 = {
            'tse_base': tse,
            'entropy': entropy,
            'stable': stable,
            'layer4_z': layer4_z,
            'layer7_z': layer7_z,
            'layer12_z': layer12_z
        }
        
        # 第二次运算：有序色彩解读（VI值计算）
        weights = [0.12 * (0.75 ** (i)) for i in range(16)]
        weighted_sum = sum(w * p for w, p in zip(weights, layer_probs))
        w_min = min(weights)
        w_max = max(weights)
        vi = 6.0 * (weighted_sum - w_min) / (w_max - w_min) if (w_max - w_min) > 0 else 0
        
        result2 = {
            'visual_index': vi,
            'weighted_sum': weighted_sum
        }
        
        print(f"{direction} 扫描完成: TSE={tse:.4f}, VI={vi:.4f}, 稳定={stable}")
        return result1, result2
        
    except Exception as e:
        logger.error(f"运算失败: {e}")
        return None, None

def load_previous_results(output_dir):
    """加载之前的分析结果"""
    res_path = Path(output_dir)
    if not res_path.exists():
        return set()
    
    processed_files = set()
    
    # 查找所有JSON结果文件
    for json_file in res_path.glob("analysis_results_*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for result in data.get('results', []):
                    processed_files.add(result['filename'])
        except Exception as e:
            logger.error(f"读取结果文件失败 {json_file}: {e}")
    
    logger.info(f"已找到 {len(processed_files)} 个已处理的文件")
    return processed_files

def get_files_to_process(data_dir, processed_files):
    """获取需要处理的文件列表"""
    data_path = Path(data_dir)
    all_files = sorted([f.name for f in data_path.glob("*") if f.is_file()])
    
    # 过滤掉已处理的文件
    files_to_process = [f for f in all_files if f not in processed_files]
    
    logger.info(f"总文件数: {len(all_files)}")
    logger.info(f"已处理: {len(processed_files)}")
    logger.info(f"待处理: {len(files_to_process)}")
    
    if files_to_process:
        logger.info(f"开始处理从: {files_to_process[0]}")
    
    return files_to_process

def main(data_dir='data', output_dir='results'):
    """主函数"""
    start_time = datetime.now()
    
    print("="*60)
    print(f"TAI v{__version__} 续处理分析")
    print("能够从上次中断的地方继续处理")
    print("="*60)
    
    logger.info(f"程序启动，数据目录: {data_dir}，输出目录: {output_dir}")

    data_path = Path(data_dir)
    res_path = Path(output_dir)
    
    try:
        data_path.mkdir(exist_ok=True)
        res_path.mkdir(exist_ok=True)
    except Exception as e:
        logger.error(f"创建目录失败: {e}")
        return 1

    # 加载之前的处理结果
    processed_files = load_previous_results(output_dir)
    
    # 获取待处理的文件
    files_to_process = get_files_to_process(data_dir, processed_files)
    
    if not files_to_process:
        logger.info("所有文件都已处理完成")
        print("✅ 所有文件都已处理完成！")
        return 0

    all_results = []
    file_count = 0
    success_count = 0

    for filename in files_to_process:
        fpath = data_path / filename
        file_count += 1
        
        print(f"\n📄 处理文件：{filename} ({file_count}/{len(files_to_process)})")
        logger.info(f"开始处理文件: {filename}")

        bits = DataProcessor.file_to_bits(str(fpath))
        if bits is None:
            logger.error(f"跳过文件: {filename}")
            continue

        patterns_forward = DataProcessor.bits_to_patterns(bits)
        if patterns_forward is None:
            logger.error(f"跳过文件: {filename}")
            continue

        f1, f2 = run_both_operations(patterns_forward, "正向")
        if f1 is None or f2 is None:
            logger.error(f"跳过文件: {filename}")
            continue

        bits_reverse = bits[::-1]
        patterns_reverse = DataProcessor.bits_to_patterns(bits_reverse)
        if patterns_reverse is None:
            logger.error(f"跳过文件: {filename}")
            continue

        r1, r2 = run_both_operations(patterns_reverse, "反向")
        if r1 is None or r2 is None:
            logger.error(f"跳过文件: {filename}")
            continue

        print("\n" + "="*60)
        print("📊 双向扫描最终对比")
        print("="*60)
        print(f"正向 TSE：{f1['tse_base']:.4f}")
        print(f"反向 TSE：{r1['tse_base']:.4f}")
        print()
        print(f"正向 4/7/12 稳定：{f1['stable']}")
        print(f"反向 4/7/12 稳定：{r1['stable']}")
        print("="*60)
        print("✅ 双向扫描完成！")

        file_result = {
            'filename': filename,
            'version': __version__,
            'timestamp': datetime.now().isoformat(),
            'random_seed': RANDOM_SEED,
            'forward': {
                'tse': f1['tse_base'],
                'vi': f2['visual_index'],
                'stable': f1['stable'],
                'layer4_z': f1['layer4_z'],
                'layer7_z': f1['layer7_z'],
                'layer12_z': f1['layer12_z']
            },
            'reverse': {
                'tse': r1['tse_base'],
                'vi': r2['visual_index'],
                'stable': r1['stable'],
                'layer4_z': r1['layer4_z'],
                'layer7_z': r1['layer7_z'],
                'layer12_z': r1['layer12_z']
            },
            'tse_diff': abs(f1['tse_base'] - r1['tse_base']),
            'vi_diff': abs(f2['visual_index'] - r2['visual_index'])
        }
        
        all_results.append(file_result)
        success_count += 1
        logger.info(f"文件处理成功: {filename}")

    if all_results:
        json_file = res_path / f"analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'version': __version__,
                    'random_seed': RANDOM_SEED,
                    'start_time': start_time.isoformat(),
                    'end_time': datetime.now().isoformat(),
                    'total_files': file_count,
                    'success_files': success_count,
                    'results': all_results
                }, f, ensure_ascii=False, indent=2)
            print(f"\n✅ 结果已保存到: {json_file}")
            logger.info(f"JSON结果已保存: {json_file}")
        except Exception as e:
            logger.error(f"保存JSON失败: {e}")

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "="*60)
    print("📊 分析总结")
    print("="*60)
    print(f"总文件数: {file_count}")
    print(f"成功处理: {success_count}")
    print(f"总耗时: {duration:.2f} 秒")
    print("="*60)
    
    logger.info(f"分析完成，总文件: {file_count}，成功: {success_count}，耗时: {duration:.2f}秒")
    
    return 0 if success_count > 0 else 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f'TAI v{__version__} 续处理分析')
    parser.add_argument('--data-dir', type=str, default='data', 
                       help='数据目录路径 (默认: data)')
    parser.add_argument('--output-dir', type=str, default='results',
                       help='输出目录路径 (默认: results)')
    
    args = parser.parse_args()
    
    try:
        exit_code = main(
            data_dir=args.data_dir,
            output_dir=args.output_dir
        )
        exit(exit_code)
    except KeyboardInterrupt:
        logger.warning("程序被用户中断")
        print("\n程序被中断")
        exit(130)
    except Exception as e:
        logger.error(f"程序异常: {e}", exc_info=True)
        print(f"\n程序异常: {e}")
        exit(1)

