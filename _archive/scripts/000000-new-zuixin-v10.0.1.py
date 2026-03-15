#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAI v10.0 + 双向扫描升级版（技术改进版）
==============================================
✅ 完全保留原版两次运算：无序随机验证 → 有序色彩解读
✅ 只新增：正向扫描 + 反向扫描（比特流反转）
✅ 无花哨功能、无新增卦象、无共振、无镜像

【技术改进】（不触碰核心理念）
- ✅ 添加随机种子（可复现性）
- ✅ 添加版本标识
- ✅ 添加异常捕获
- ✅ 添加边界条件检查
- ✅ 移除全局警告屏蔽
- ✅ 添加JSON结果输出
- ✅ 添加日志记录
- ✅ 添加命令行参数支持
- ✅ 完善类型提示
"""

__version__ = "10.0.1"
__author__ = "TAI Research Team"

import os
import sys
import random
import numpy as np
import json
import logging
import argparse
from pathlib import Path
from collections import Counter
from typing import List, Dict, Tuple, Optional
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tai_analysis.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 固定随机种子（确保可复现性）
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

logger.info(f"TAI v{__version__} 启动，随机种子设置为: {RANDOM_SEED}")

# ==============================================================================
# 固定映射表（完全不动）
# ==============================================================================
class TruthTable:
    PATTERN_TO_LAYER: Dict[str, int] = {
        '111111':1,'000000':1,'101010':1,'010101':1,
        '010010':2,'101101':2,'111000':2,'000111':2,
        '101111':3,'111101':3,'111010':3,'010111':3,
        '000101':4,'101000':4,'010000':4,'000010':4,
        '100100':5,'001001':5,'011011':5,'110110':5,
        '100001':6,'011110':6,'110011':6,'001100':6,
        '100110':7,'011001':7,'001011':7,'110100':7,
        '110001':8,'100011':8,'001110':8,'011100':8,
        '111011':9,'110111':9,'111110':9,'011111':9,
        '001000':10,'000100':10,'000001':10,'100000':10,
        '100111':11,'111001':11,'001111':11,'111100':11,
        '110000':12,'000011':12,'000110':12,'011000':12,
        '101110':13,'011101':13,'101011':13,'110101':13,
        '101100':14,'001101':14,'100101':14,'101001':14,
        '010110':15,'011010':15,'010011':15,'110010':15,
        '001010':16,'010100':16,'100010':16,'010001':16
    }

    @classmethod
    def get_layer(cls, pattern: str) -> int:
        return cls.PATTERN_TO_LAYER[pattern]

# ==============================================================================
# 易经字典（完全不动）
# ==============================================================================
class YijingDictionary:
    LAYER4: Dict = {'卦象': ['晋', '明夷', '师', '比'],    '语义': '底层秩序初现、内外边界形成、状态跃迁受阻'}
    LAYER7: Dict = {'卦象': ['随', '蛊', '渐', '归妹'],  '语义': '新旧交替、渐进演化与突变共生、信息交互核心'}
    LAYER12: Dict = {'卦象': ['临', '观', '萃', '升'],    '语义': '整体秩序显现、聚合升发、宏观形态稳定'}

    @classmethod
    def interpret(cls, layer: int) -> Dict:
        if layer == 4:  return cls.LAYER4
        if layer == 7:  return cls.LAYER7
        if layer == 12: return cls.LAYER12
        return {'卦象': [], '语义': '非关键节点'}

# ==============================================================================
# 权重：0.12 * 0.75^(l-1) 严格原版（完全不动）
# ==============================================================================
class OriginalWeights:
    VALUES: np.ndarray = np.array([
        0.1200, 0.0900, 0.0675, 0.0506, 0.0380, 0.0285, 0.0214, 0.0160,
        0.0120, 0.0090, 0.0068, 0.0051, 0.0038, 0.0029, 0.0021, 0.0016
    ])
    MIN_VAL: float = 0.0016
    MAX_VAL: float = 0.1200

    @classmethod
    def get(cls, layer: int) -> float:
        return cls.VALUES[layer-1]

    @classmethod
    def get_all(cls) -> np.ndarray:
        return cls.VALUES.copy()

# ==============================================================================
# 数据处理器（添加异常捕获和边界检查）
# ==============================================================================
class DataProcessor:
    @staticmethod
    def file_to_bits(filepath: str) -> Optional[List[int]]:
        """读取文件并转换为比特列表"""
        try:
            if not os.path.exists(filepath):
                logger.error(f"文件不存在: {filepath}")
                return None
            
            if not os.path.isfile(filepath):
                logger.error(f"不是文件: {filepath}")
                return None
            
            filesize = os.path.getsize(filepath)
            if filesize == 0:
                logger.error(f"文件为空: {filepath}")
                return None
            
            with open(filepath, 'rb') as f:
                data = f.read()
            
            bits = []
            for byte in data:
                for i in range(7, -1, -1):
                    bits.append((byte >> i) & 1)
            
            logger.info(f"文件 {os.path.basename(filepath)} 读取成功，"
                       f"大小: {filesize} 字节，比特数: {len(bits)}")
            return bits
            
        except PermissionError:
            logger.error(f"无权限读取文件: {filepath}")
            return None
        except Exception as e:
            logger.error(f"读取文件时出错 {filepath}: {str(e)}")
            return None

    @staticmethod
    def bits_to_patterns(bits: List[int]) -> Optional[List[str]]:
        """将比特列表转换为6-bit模式列表"""
        if len(bits) < 6:
            logger.error(f"比特数不足6个，无法生成模式: {len(bits)}")
            return None
        
        patterns = []
        for i in range(len(bits) - 5):
            window = bits[i:i+6]
            patterns.append(''.join(str(b) for b in window))
        
        return patterns

# ==============================================================================
# 第一次运算：无序随机验证（已修复随机种子）
# ==============================================================================
class FirstOperation:
    def __init__(self, n_trials: int = 100):
        self.n_trials = n_trials
        logger.info(f"第一次运算初始化，试验次数: {n_trials}")

    def run(self, patterns: List[str]) -> Optional[Dict]:
        print("\n" + "="*50)
        print("【第一次运算】无序随机验证（真随机 + Z-score）")
        print("="*50)

        all_patterns = list(TruthTable.PATTERN_TO_LAYER.keys())
        total = len(patterns)

        orig_layers = [TruthTable.PATTERN_TO_LAYER[p] for p in patterns]
        orig_cnt = Counter(orig_layers)
        orig_probs = np.array([orig_cnt.get(l, 0) / total for l in range(1, 17)])

        H = -np.sum(orig_probs[orig_probs > 0] * np.log2(orig_probs[orig_probs > 0]))
        # 确保H不超过4.0（16层的最大熵）
        H = min(H, 4.0)
        tse_base = 6.0 * H / 4.0

        dev4, dev7, dev12 = [], [], []
        uniform = 1/16

        for trial in range(self.n_trials):
            shuffled = all_patterns.copy()
            random.shuffle(shuffled)
            r_map = {p: (i//4)+1 for i, p in enumerate(shuffled)}
            r_layers = [r_map[p] for p in patterns]
            r_cnt = Counter(r_layers)
            r_probs = np.array([r_cnt.get(l, 0)/total for l in range(1,17)])
            dev4.append(abs(r_probs[3]-uniform))
            dev7.append(abs(r_probs[6]-uniform))
            dev12.append(abs(r_probs[11]-uniform))

        def z(val: float, lst: List[float]) -> float:
            std = np.std(lst)
            if std == 0:
                logger.warning("标准差为0，Z-score计算可能异常")
                return 0.0
            return (val - np.mean(lst)) / std

        z4 = z(abs(orig_probs[3]-uniform), dev4)
        z7 = z(abs(orig_probs[6]-uniform), dev7)
        z12 = z(abs(orig_probs[11]-uniform), dev12)

        stable = all(abs(x) >= 1.0 - 1e-10 for x in [z4, z7, z12])

        result = {
            'tse_base': float(tse_base),
            'layer4_z': float(z4),
            'layer7_z': float(z7),
            'layer12_z': float(z12),
            'stable': stable
        }

        logger.info(f"第一次运算完成: TSE={tse_base:.4f}, stable={stable}")
        return result

# ==============================================================================
# 第二次运算：有序色彩解读（完全不动）
# ==============================================================================
class SecondOperation:
    def __init__(self):
        self.weights = OriginalWeights.get_all()
        logger.info("第二次运算初始化")

    def run(self, patterns: List[str]) -> Optional[Dict]:
        layers_seq = [TruthTable.get_layer(p) for p in patterns]
        cnt = Counter(layers_seq)
        total = len(layers_seq)
        probs = np.array([cnt.get(l,0)/total for l in range(1,17)])

        w = self.weights
        weighted_sum = np.sum(w * probs)
        vis_index = 6.0 * (weighted_sum - w.min()) / (w.max() - w.min())

        p4,p7,p12 = probs[3], probs[6], probs[11]
        w4,w7,w12 = w[3]*p4, w[6]*p7, w[11]*p12

        d4 = YijingDictionary.interpret(4)
        d7 = YijingDictionary.interpret(7)
        d12 = YijingDictionary.interpret(12)

        result = {
            'visual_index': float(vis_index),
            'probs': probs.tolist(),
            'layer4': {'p': float(p4),'w': float(w4),**d4},
            'layer7': {'p': float(p7),'w': float(w7),**d7},
            'layer12': {'p': float(p12),'w': float(w12),**d12},
            'weights_seq': [float(self.weights[l-1]) for l in layers_seq]
        }

        logger.info(f"第二次运算完成: VI={vis_index:.4f}")
        return result

# ==============================================================================
# 统一执行函数：正向 / 反向 共用
# ==============================================================================
def run_both_operations(patterns: List[str], direction_name: str) -> Tuple[Optional[Dict], Optional[Dict]]:
    print(f"\n" + "="*60)
    print(f"🔍 方向：{direction_name}")
    print(f"="*60)

    first = FirstOperation(n_trials=100)
    res1 = first.run(patterns)
    if res1 is None:
        logger.error("第一次运算失败")
        return None, None

    second = SecondOperation()
    res2 = second.run(patterns)
    if res2 is None:
        logger.error("第二次运算失败")
        return None, None

    return res1, res2

# ==============================================================================
# 主程序：双向扫描
# ==============================================================================
def main(data_dir: str = "data", output_dir: str = "results", 
         output_json: bool = True) -> int:
    start_time = datetime.now()
    
    print("="*60)
    print(f"🚀 TAI v{__version__} 双向扫描版（技术改进版）")
    print("   正向：原始顺序   |   反向：比特流反转")
    print("   两次运算完全保留，无额外花哨功能")
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

    if not any(data_path.iterdir()):
        logger.warning("数据目录为空，创建示例文件")
        with open(data_path/"example.txt", 'w', encoding='utf-8') as f:
            f.write("TAI 10.0 bidirectional test " * 100)

    all_results = []
    file_count = 0
    success_count = 0

    for fpath in sorted(data_path.glob("*")):
        if not fpath.is_file():
            continue
        
        file_count += 1
        filename = fpath.name
        
        print(f"\n📄 处理文件：{filename}")
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

    if output_json and all_results:
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

# ==============================================================================
# 命令行参数解析
# ==============================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f'TAI v{__version__} 双向扫描分析')
    parser.add_argument('--data-dir', type=str, default='data', 
                       help='数据目录路径 (默认: data)')
    parser.add_argument('--output-dir', type=str, default='results',
                       help='输出目录路径 (默认: results)')
    parser.add_argument('--no-json', action='store_false', dest='output_json',
                       help='不输出JSON结果文件')
    parser.add_argument('--version', action='version', 
                       version=f'TAI v{__version__}')
    
    args = parser.parse_args()
    
    try:
        exit_code = main(
            data_dir=args.data_dir,
            output_dir=args.output_dir,
            output_json=args.output_json
        )
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.warning("程序被用户中断")
        print("\n程序被中断")
        sys.exit(130)
    except Exception as e:
        logger.error(f"程序异常: {e}", exc_info=True)
        print(f"\n程序异常: {e}")
        sys.exit(1)
