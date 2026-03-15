# TAI (TaiYi) - 通用数据分析工具

## 简介

TAI（太仪）是一个基于信息熵和八卦映射的数据结构分析工具。

## 版本说明

**本版本为公开版**，专为学术研究设计，不包含核心机密算法。

## 核心方法

1. **第一次运算**：随机16层映射 - 测量数据复杂度(TSE)和时间方向性(ΔTSE)
2. **第二次运算**：64模式直接映射64卦 - 提供八卦视角的文化解读

## 安装

```bash
pip install -r requirements.txt
```

## 使用方法

```bash
python tai_lite.py <数据文件> [--n-random 100]
```

### 示例

```bash
# 分析圆周率数据
python tai_lite.py data/pi_digits_1m.txt

# 分析DNA数据
python tai_lite.py _archive/dna/dna/healthy_NM_000014_1000000.txt --n-random 20
```

## 数据编码规则

- **数据文件**（.dat, .bin等）：原始8-bit字节流
- **文本文件**（.txt, .csv等）：字符ASCII码
- 程序会自动识别文件类型

## 输出说明

- **TSE**：信息复杂度指标，范围0-6
- **ΔTSE**：时间方向性指标，表示数据流的方向性
- **卦象分布**：64卦中各卦的凸显程度

## 目录结构

```
├── tai_lite.py          # 主程序
├── LICENSE             # MIT许可证
├── requirements.txt     # Python依赖
├── README.md           # 说明文档
├── data/               # 数学常量数据
├── data2/              # 地震数据
└── _archive/           # 存档数据
```

## 许可证

MIT License - 详见 LICENSE 文件

## 注意事项

本版本为公开版，适合学术研究和论文发表使用。
