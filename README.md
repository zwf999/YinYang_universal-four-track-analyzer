# 常数分析与预测系统 v2.0

一个功能强大的数学常数和物理常数分析与预测系统，基于四轨分析理论和先进的机器学习算法。

## 系统功能

- **四轨分析系统**：基于九和配对和阴阳理论的深度分析
- **智能模式识别**：自动检测常数中的重复、序列和配对模式
- **高级统计分析**：熵值计算、相关性分析、运行检验等
- **多策略预测引擎**：集成统计、模式和混合预测策略
- **智能分类系统**：基于规则和特征的常数分类
- **大规模数据管理**：高效处理和缓存大规模常数数据集
- **可视化用户界面**：直观的分析结果展示和交互

## 系统架构

### 核心组件

1. **分析引擎** (`core/analyzers/`)
   - `base_analyzer.py` - 基础分析器类
   - `four_track_analyzer.py` - 四轨分析器
   - `pattern_analyzer.py` - 模式识别分析器
   - `statistical_analyzer.py` - 统计分析器
   - `composite_analyzer.py` - 复合分析器

2. **预测引擎** (`core/predictors/`)
   - `base_predictor.py` - 基础预测器类
   - `statistical_predictor.py` - 统计预测器
   - `pattern_predictor.py` - 模式预测器
   - `hybrid_predictor.py` - 混合预测器
   - `ensemble_predictor.py` - 集成预测引擎

3. **分类系统** (`core/classifiers/`)
   - `base_classifier.py` - 基础分类器类
   - `rule_based_classifier.py` - 基于规则的分类器
   - `feature_based_classifier.py` - 基于特征的分类器
   - `ensemble_classifier.py` - 集成分类器

4. **数据管理** (`core/data/`)
   - `data_manager.py` - 数据管理器
   - `data_reader.py` - 数据读取器
   - `data_writer.py` - 数据写入器
   - `cache_manager.py` - 缓存管理器

5. **用户界面** (`core/ui/`)
   - `main_window.py` - 主用户界面

## 安装指南

### 系统要求

- Python 3.7+
- 依赖库：
  - numpy
  - matplotlib
  - tkinter (标准库)
  - mpmath (用于高精度计算)

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置环境**
   - 确保数据目录 (`./data/`) 存在
   - 确保缓存目录 (`./cache/`) 存在

## 使用指南

### 启动用户界面

```bash
python run_ui.py
```

### 命令行使用

```bash
# 分析常数
python -m core.analyzers.composite_analyzer --constant pi --max-digits 1000

# 预测常数
python -m core.predictors.ensemble_predictor --constant pi --max-digits 1000 --predict-length 100

# 分类常数
python -m core.classifiers.ensemble_classifier --constant pi --max-digits 1000
```

### 编程接口

```python
from core.data.data_manager import DataManager
from core.analyzers.composite_analyzer import CompositeAnalyzer
from core.predictors.ensemble_predictor import EnsemblePredictor
from core.classifiers.ensemble_classifier import EnsembleClassifier

# 初始化组件
data_manager = DataManager()
analyzer = CompositeAnalyzer()
predictor = EnsemblePredictor()
classifier = EnsembleClassifier()

# 加载常数
digits = data_manager.load_constant('pi', 1000)

# 分析常数
analysis_result = analyzer.analyze(digits)

# 预测常数
prediction = predictor.predict(digits, length=100)

# 分类常数
classification = classifier.classify('pi', digits)
```

## 数据格式

### 常数文件格式

常数文件应该是文本文件，格式如下：

```
3.14159265358979323846264338327950288419716939937510...
```

或者：

```
314159265358979323846264338327950288419716939937510...
```

### 支持的常数类型

- **数学常数**：pi, e, phi, sqrt2, sqrt3, zeta3, catalan, apery
- **物理常数**：speed_of_light, fine_structure_constant, planck_constant, elementary_charge, electron_mass, proton_mass, neutron_mass, gravitational_constant, boltzmann_constant, avogadro_constant, rydberg_constant, bohr_radius, planck_length, planck_mass, planck_time, standard_gravity, astronomical_unit, light_year, hubble_constant, vacuum_permeability, vacuum_permittivity, impedance_free_space, compton_wavelength, classical_electron_radius

## 性能优化

### 缓存管理

系统使用内存缓存和磁盘缓存来提高性能：
- 内存缓存：存储最近使用的常数数据
- 磁盘缓存：持久化缓存数据，减少重复计算

### 并行处理

对于大规模常数分析，系统支持并行处理：
- 多线程分析
- 批量处理模式

## 测试与验证

### 运行测试

```bash
python -m unittest discover tests
```

### 测试覆盖

- 数据管理系统测试
- 分析器组件测试
- 预测器组件测试
- 分类器组件测试
- 边界情况测试

## 扩展系统

### 添加新的分析器

```python
from core.analyzers.base_analyzer import BaseAnalyzer

class MyAnalyzer(BaseAnalyzer):
    def analyze(self, digits):
        # 实现分析逻辑
        pass

# 注册到复合分析器
from core.analyzers.composite_analyzer import CompositeAnalyzer

composite_analyzer = CompositeAnalyzer()
composite_analyzer.add_analyzer('my_analyzer', MyAnalyzer())
```

### 添加新的预测器

```python
from core.predictors.base_predictor import BasePredictor

class MyPredictor(BasePredictor):
    def predict(self, digits, length):
        # 实现预测逻辑
        pass

# 注册到集成预测器
from core.predictors.ensemble_predictor import EnsemblePredictor

ensemble_predictor = EnsemblePredictor()
ensemble_predictor.add_predictor('my_predictor', MyPredictor())
```

## 配置选项

### 数据管理配置

- `data_dir`：数据目录路径
- `cache_dir`：缓存目录路径
- `cache_expire_time`：缓存过期时间（秒）

### 分析器配置

- `window_size`：滑动窗口大小
- `min_pattern_length`：最小模式长度
- `max_pattern_length`：最大模式长度

### 预测器配置

- `markov_order`：马尔可夫链阶数
- `prediction_strategy`：预测策略

## 故障排除

### 常见问题

1. **无法加载常数**
   - 检查常数文件是否存在
   - 检查文件格式是否正确
   - 检查文件编码是否为UTF-8

2. **分析速度慢**
   - 减少分析的位数
   - 增加缓存大小
   - 检查系统内存是否充足

3. **预测准确性低**
   - 增加训练数据长度
   - 调整预测策略
   - 检查常数类型是否正确

4. **界面无响应**
   - 减少分析的位数
   - 检查系统资源使用情况
   - 重启应用程序

## 贡献指南

1. **报告问题**：在GitHub Issues中报告bug和功能请求
2. **提交代码**：创建Pull Request
3. **文档改进**：更新README和其他文档
4. **测试贡献**：添加新的测试用例

## 许可证

MIT License

## 联系方式

- 项目主页：<repository-url>
- 问题反馈：<repository-url>/issues

## 版本历史

### v2.0 (当前版本)
- 完整的四轨分析系统
- 集成预测引擎
- 智能分类系统
- 可视化用户界面
- 大规模数据管理

### v1.0
- 基础分析功能
- 简单预测功能
- 命令行界面

---

**常数分析与预测系统** - 探索数学常数的奥秘
