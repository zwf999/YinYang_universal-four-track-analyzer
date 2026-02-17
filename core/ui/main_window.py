# core/ui/main_window.py
# 主用户界面

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from typing import Dict, List, Any
from core.data.data_manager import DataManager
from core.analyzers.composite_analyzer import CompositeAnalyzer
from core.predictors.ensemble_predictor import EnsemblePredictor
from core.classifiers.ensemble_classifier import EnsembleClassifier

# 设置matplotlib字体支持中文
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

class MainWindow:
    """主用户界面"""
    
    def __init__(self, root):
        """
        初始化主窗口
        
        Args:
            root: tkinter根窗口
        """
        self.root = root
        self.root.title("常数分析与预测系统 v2.0")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # 初始化组件
        self.data_manager = DataManager()
        self.analyzer = CompositeAnalyzer()
        self.predictor = EnsemblePredictor()
        self.classifier = EnsembleClassifier()
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建菜单栏
        self._create_menu()
        
        # 创建左侧控制面板
        self.control_panel = ttk.LabelFrame(self.main_frame, text="控制面板", padding="10")
        self.control_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # 创建右侧显示区域
        self.display_panel = ttk.LabelFrame(self.main_frame, text="分析结果", padding="10")
        self.display_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 初始化控制面板
        self._init_control_panel()
        
        # 初始化显示面板
        self._init_display_panel()
        
        # 加载可用常数
        self._load_available_constants()
    
    def _create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="退出", command=self.root.quit)
        menubar.add_cascade(label="文件", menu=file_menu)
        
        # 工具菜单
        tool_menu = tk.Menu(menubar, tearoff=0)
        tool_menu.add_command(label="清理缓存", command=self._clean_cache)
        tool_menu.add_command(label="刷新常数列表", command=self._load_available_constants)
        menubar.add_cascade(label="工具", menu=tool_menu)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="关于", command=self._show_about)
        menubar.add_cascade(label="帮助", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def _init_control_panel(self):
        """初始化控制面板"""
        # 常数选择
        ttk.Label(self.control_panel, text="选择常数:").pack(anchor=tk.W, pady=(0, 5))
        self.constant_var = tk.StringVar()
        self.constant_combo = ttk.Combobox(self.control_panel, textvariable=self.constant_var, width=30)
        self.constant_combo.pack(fill=tk.X, pady=(0, 10))
        
        # 分析参数
        ttk.Label(self.control_panel, text="分析参数:").pack(anchor=tk.W, pady=(0, 5))
        
        # 最大位数
        ttk.Label(self.control_panel, text="最大位数:").pack(anchor=tk.W)
        self.max_digits_var = tk.IntVar(value=10000)
        ttk.Entry(self.control_panel, textvariable=self.max_digits_var, width=10).pack(anchor=tk.W, pady=(0, 5))
        
        # 窗口大小
        ttk.Label(self.control_panel, text="窗口大小:").pack(anchor=tk.W)
        self.window_size_var = tk.IntVar(value=100)
        ttk.Entry(self.control_panel, textvariable=self.window_size_var, width=10).pack(anchor=tk.W, pady=(0, 10))
        
        # 操作按钮
        self.analyze_btn = ttk.Button(self.control_panel, text="分析常数", command=self._analyze_constant)
        self.analyze_btn.pack(fill=tk.X, pady=(0, 5))
        
        self.predict_btn = ttk.Button(self.control_panel, text="预测数字", command=self._predict_digits)
        self.predict_btn.pack(fill=tk.X, pady=(0, 5))
        
        self.evaluate_btn = ttk.Button(self.control_panel, text="评估预测", command=self._evaluate_prediction)
        self.evaluate_btn.pack(fill=tk.X, pady=(0, 5))
        
        self.classify_btn = ttk.Button(self.control_panel, text="分类常数", command=self._classify_constant)
        self.classify_btn.pack(fill=tk.X, pady=(0, 10))
        
        # DNA输入
        ttk.Label(self.control_panel, text="DNA输入:").pack(anchor=tk.W, pady=(10, 5))
        self.dna_var = tk.StringVar()
        self.dna_entry = ttk.Entry(self.control_panel, textvariable=self.dna_var, width=30)
        self.dna_entry.pack(fill=tk.X, pady=(0, 5))
        self.dna_entry.insert(0, "输入DNA序列 (如: ACGTACGT)")
        
        self.analyze_dna_btn = ttk.Button(self.control_panel, text="分析DNA", command=self._analyze_dna)
        self.analyze_dna_btn.pack(fill=tk.X, pady=(0, 10))
        
        # 缓存信息
        ttk.Label(self.control_panel, text="缓存信息:").pack(anchor=tk.W, pady=(0, 5))
        self.cache_info = ttk.Label(self.control_panel, text="", font=('Arial', 8))
        self.cache_info.pack(anchor=tk.W, pady=(0, 10))
        
        # 更新缓存信息
        self._update_cache_info()
    
    def _init_display_panel(self):
        """初始化显示面板"""
        # 创建笔记本组件
        self.notebook = ttk.Notebook(self.display_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 创建基本信息标签页
        self.info_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.info_tab, text="基本信息")
        
        # 创建分析结果标签页
        self.analysis_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.analysis_tab, text="分析结果")
        
        # 创建预测结果标签页
        self.prediction_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.prediction_tab, text="预测结果")
        
        # 创建分类结果标签页
        self.classification_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.classification_tab, text="分类结果")
        
        # 创建评估结果标签页
        self.evaluation_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.evaluation_tab, text="评估结果")
        
        # 初始化标签页内容
        self._init_info_tab()
        self._init_analysis_tab()
        self._init_prediction_tab()
        self._init_classification_tab()
        self._init_evaluation_tab()
    
    def _init_info_tab(self):
        """初始化基本信息标签页"""
        self.info_text = tk.Text(self.info_tab, wrap=tk.WORD, height=20)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        self.info_scroll = ttk.Scrollbar(self.info_text, command=self.info_text.yview)
        self.info_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.info_text.config(yscrollcommand=self.info_scroll.set)
    
    def _init_analysis_tab(self):
        """初始化分析结果标签页"""
        # 创建分析结果框架
        self.analysis_frame = ttk.Frame(self.analysis_tab)
        self.analysis_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建分析结果文本
        self.analysis_text = tk.Text(self.analysis_frame, wrap=tk.WORD, height=10)
        self.analysis_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.analysis_scroll = ttk.Scrollbar(self.analysis_text, command=self.analysis_text.yview)
        self.analysis_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.analysis_text.config(yscrollcommand=self.analysis_scroll.set)
        
        # 创建图表框架
        self.chart_frame = ttk.Frame(self.analysis_frame)
        self.chart_frame.pack(fill=tk.BOTH, expand=True)
    
    def _init_prediction_tab(self):
        """初始化预测结果标签页"""
        self.prediction_text = tk.Text(self.prediction_tab, wrap=tk.WORD, height=20)
        self.prediction_text.pack(fill=tk.BOTH, expand=True)
        self.prediction_scroll = ttk.Scrollbar(self.prediction_text, command=self.prediction_text.yview)
        self.prediction_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.prediction_text.config(yscrollcommand=self.prediction_scroll.set)
    
    def _init_classification_tab(self):
        """初始化分类结果标签页"""
        self.classification_text = tk.Text(self.classification_tab, wrap=tk.WORD, height=20)
        self.classification_text.pack(fill=tk.BOTH, expand=True)
        self.classification_scroll = ttk.Scrollbar(self.classification_text, command=self.classification_text.yview)
        self.classification_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.classification_text.config(yscrollcommand=self.classification_scroll.set)
    
    def _init_evaluation_tab(self):
        """初始化评估结果标签页"""
        self.evaluation_text = tk.Text(self.evaluation_tab, wrap=tk.WORD, height=20)
        self.evaluation_text.pack(fill=tk.BOTH, expand=True)
        self.evaluation_scroll = ttk.Scrollbar(self.evaluation_text, command=self.evaluation_text.yview)
        self.evaluation_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.evaluation_text.config(yscrollcommand=self.evaluation_scroll.set)
    
    def _load_available_constants(self):
        """加载可用常数列表"""
        constants = self.data_manager.list_constants()
        constant_names = [const['name'] for const in constants]
        self.constant_combo['values'] = constant_names
        if constant_names:
            self.constant_var.set(constant_names[0])
    
    def _analyze_constant(self):
        """分析常数"""
        constant_name = self.constant_var.get()
        if not constant_name:
            messagebox.showerror("错误", "请选择一个常数")
            return
        
        max_digits = self.max_digits_var.get()
        window_size = self.window_size_var.get()
        
        # 显示加载状态
        self.analysis_text.delete(1.0, tk.END)
        self.analysis_text.insert(tk.END, f"正在分析 {constant_name}...\n")
        self.root.update()
        
        try:
            # 加载常数
            digits = self.data_manager.load_constant(constant_name, max_digits)
            if not digits:
                messagebox.showerror("错误", f"无法加载常数 {constant_name}")
                return
            
            # 分析常数
            result = self.analyzer.analyze(digits)
            
            # 显示分析结果
            self._display_analysis_result(constant_name, result)
            
            # 绘制图表
            self._plot_analysis_chart(result)
            
            # 更新基本信息
            self._update_constant_info(constant_name, digits)
            
        except Exception as e:
            messagebox.showerror("错误", f"分析失败: {str(e)}")
    
    def _predict_digits(self):
        """预测数字"""
        constant_name = self.constant_var.get()
        if not constant_name:
            messagebox.showerror("错误", "请选择一个常数")
            return
        
        max_digits = self.max_digits_var.get()
        
        # 显示加载状态
        self.prediction_text.delete(1.0, tk.END)
        self.prediction_text.insert(tk.END, f"正在预测 {constant_name} 的数字...\n")
        self.root.update()
        
        try:
            # 加载常数
            digits = self.data_manager.load_constant(constant_name, max_digits)
            if not digits:
                messagebox.showerror("错误", f"无法加载常数 {constant_name}")
                return
            
            # 预测数字
            prediction = self.predictor.predict(digits, length=100)
            
            # 显示预测结果
            self._display_prediction_result(constant_name, prediction)
            
        except Exception as e:
            messagebox.showerror("错误", f"预测失败: {str(e)}")
    
    def _classify_constant(self):
        """分类常数"""
        constant_name = self.constant_var.get()
        if not constant_name:
            messagebox.showerror("错误", "请选择一个常数")
            return
        
        max_digits = self.max_digits_var.get()
        
        # 显示加载状态
        self.classification_text.delete(1.0, tk.END)
        self.classification_text.insert(tk.END, f"正在分类 {constant_name}...\n")
        self.root.update()
        
        try:
            # 加载常数
            digits = self.data_manager.load_constant(constant_name, max_digits)
            if not digits:
                messagebox.showerror("错误", f"无法加载常数 {constant_name}")
                return
            
            # 分类常数
            classification = self.classifier.classify(digits, constant_name)
            
            # 显示分类结果
            self._display_classification_result(constant_name, classification)
            
        except Exception as e:
            messagebox.showerror("错误", f"分类失败: {str(e)}")
    
    def _evaluate_prediction(self):
        """评估预测结果"""
        constant_name = self.constant_var.get()
        if not constant_name:
            messagebox.showerror("错误", "请选择一个常数")
            return
        
        max_digits = self.max_digits_var.get()
        predict_length = 100
        
        # 显示加载状态
        self.evaluation_text.delete(1.0, tk.END)
        self.evaluation_text.insert(tk.END, f"正在评估 {constant_name} 的预测结果...\n")
        self.root.update()
        
        try:
            # 加载完整数据
            full_digits = self.data_manager.load_constant(constant_name, max_digits + predict_length)
            if not full_digits:
                messagebox.showerror("错误", f"无法加载常数 {constant_name}")
                return
            
            # 检查数据长度
            if len(full_digits) < max_digits + predict_length:
                messagebox.showerror("错误", f"数据长度不足，需要 {max_digits + predict_length} 位，但只有 {len(full_digits)} 位")
                return
            
            # 分割数据
            train_data = full_digits[:max_digits]
            real_data = full_digits[max_digits:max_digits + predict_length]
            
            # 预测数据
            prediction = self.predictor.predict(train_data, length=predict_length)
            
            # 评估预测结果
            correct_count = sum(1 for pred, real in zip(prediction, real_data) if pred == real)
            accuracy = (correct_count / predict_length) * 100
            
            # 生成评估报告
            self._display_evaluation_result(constant_name, max_digits, predict_length, train_data, prediction, real_data, accuracy)
            
        except Exception as e:
            messagebox.showerror("错误", f"评估失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _analyze_dna(self):
        """分析DNA序列"""
        dna_sequence = self.dna_var.get().strip()
        if not dna_sequence or dna_sequence == "输入DNA序列 (如: ACGTACGT)":
            messagebox.showerror("错误", "请输入有效的DNA序列")
            return
        
        max_digits = self.max_digits_var.get()
        window_size = self.window_size_var.get()
        
        # 显示加载状态
        self.analysis_text.delete(1.0, tk.END)
        self.analysis_text.insert(tk.END, f"正在分析 DNA序列...\n")
        self.root.update()
        
        try:
            # 验证DNA序列
            valid_bases = set('ACGT')
            if not all(char in valid_bases for char in dna_sequence.upper()):
                messagebox.showerror("错误", "DNA序列只能包含A,C,G,T")
                return
            
            # 将DNA转换为数字序列
            digits = self.data_manager.encode_dna(dna_sequence)
            if not digits:
                messagebox.showerror("错误", "DNA编码失败")
                return
            
            # 限制最大位数
            digits = digits[:max_digits]
            
            # 分析数字序列
            result = self.analyzer.analyze(digits)
            
            # 显示分析结果
            self._display_analysis_result("DNA序列", result)
            
            # 绘制图表
            self._plot_analysis_chart(result)
            
            # 更新基本信息
            self._update_dna_info(dna_sequence, digits)
            
        except Exception as e:
            messagebox.showerror("错误", f"分析失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _display_analysis_result(self, constant_name: str, result: Dict[str, Any]):
        """显示分析结果"""
        self.analysis_text.delete(1.0, tk.END)
        
        analysis_str = f"常数: {constant_name}\n"
        analysis_str += f"分析结果:\n\n"
        
        # 统计分析
        if 'statistical' in result:
            stats = result['statistical']
            analysis_str += "统计分析:\n"
            analysis_str += f"  长度: {stats.get('total_digits', 0)}\n"
            analysis_str += f"  平均值: {stats.get('mean', 0):.4f}\n"
            analysis_str += f"  标准差: {stats.get('std', 0):.4f}\n"
            analysis_str += f"  熵值: {stats.get('entropy', 0):.4f}\n"
            analysis_str += "\n"
        
        # 四轨分析（包含正向和反向）
        if 'four_track' in result:
            four_track = result['four_track']
            analysis_str += "四轨分析:\n"
            for i in range(1, 5):
                track = four_track.get(f'track{i}', {})
                if 'forward' in track and 'backward' in track and 'symmetry' in track:
                    forward = track['forward']
                    backward = track['backward']
                    symmetry = track['symmetry']
                    
                    # 符号配对分析
                    forward_symbol_ratio = forward.get('symbol_pairs', {}).get('pair_ratio', 0)
                    backward_symbol_ratio = backward.get('symbol_pairs', {}).get('pair_ratio', 0)
                    
                    # 数字配对分析
                    forward_digit_ratio = forward.get('digit_pairs', {}).get('pair_ratio', 0)
                    backward_digit_ratio = backward.get('digit_pairs', {}).get('pair_ratio', 0)
                    
                    overall_symmetry = symmetry.get('overall_symmetry', 0)
                    
                    analysis_str += f"  轨道{i}:\n"
                    analysis_str += f"    正向符号配对率: {forward_symbol_ratio:.4f}\n"
                    analysis_str += f"    反向符号配对率: {backward_symbol_ratio:.4f}\n"
                    analysis_str += f"    正向数字配对率: {forward_digit_ratio:.4f}\n"
                    analysis_str += f"    反向数字配对率: {backward_digit_ratio:.4f}\n"
                    analysis_str += f"    对称性: {overall_symmetry:.4f}\n"
            analysis_str += "\n"
        
        # 反向分析摘要
        if 'four_track' in result:
            # 检查是否有反向分析结果
            has_reverse_analysis = False
            for track in ['track1', 'track2', 'track3', 'track4']:
                track_data = four_track.get(track, {})
                if 'symmetry' in track_data:
                    has_reverse_analysis = True
                    break
            
            if has_reverse_analysis:
                analysis_str += "反向分析摘要:\n"
                
                # 计算整体对称性
                symmetry_scores = []
                for track in ['track1', 'track2', 'track3', 'track4']:
                    track_data = four_track.get(track, {})
                    if 'symmetry' in track_data:
                        symmetry = track_data['symmetry'].get('overall_symmetry', 0)
                        symmetry_scores.append(symmetry)
                
                if symmetry_scores:
                    avg_symmetry = sum(symmetry_scores) / len(symmetry_scores)
                    analysis_str += f"  整体对称性: {avg_symmetry:.4f}\n"
                    
                    # 分析对称性分布
                    high_symmetry = sum(1 for s in symmetry_scores if s > 0.8)
                    medium_symmetry = sum(1 for s in symmetry_scores if 0.4 < s <= 0.8)
                    low_symmetry = sum(1 for s in symmetry_scores if s <= 0.4)
                    
                    analysis_str += f"  高对称性轨道: {high_symmetry}\n"
                    analysis_str += f"  中等对称性轨道: {medium_symmetry}\n"
                    analysis_str += f"  低对称性轨道: {low_symmetry}\n"
            analysis_str += "\n"
        
        # 模式分析
        if 'pattern' in result:
            pattern = result['pattern']
            analysis_str += "模式分析:\n"
            analysis_str += f"  总模式数: {pattern.get('total_patterns', 0)}\n"
            analysis_str += f"  模式密度: {pattern.get('pattern_density', 0):.4f}\n"
            analysis_str += "\n"
        
        # 综合评分
        if 'scores' in result:
            scores = result['scores']
            analysis_str += "综合评分:\n"
            analysis_str += f"  随机性: {scores.get('randomness', 0):.4f}\n"
            analysis_str += f"  模式复杂度: {scores.get('pattern_complexity', 0):.4f}\n"
            analysis_str += f"  对称性: {scores.get('symmetry', 0):.4f}\n"
            analysis_str += f"  可预测性: {scores.get('predictability', 0):.4f}\n"
            analysis_str += f"  总体评分: {scores.get('overall', 0):.4f}\n"
            analysis_str += "\n"
        
        self.analysis_text.insert(tk.END, analysis_str)
    
    def _plot_analysis_chart(self, result: Dict[str, Any]):
        """绘制分析图表"""
        # 清空图表框架
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        # 创建图表
        fig, axes = plt.subplots(2, 2, figsize=(10, 8))
        fig.tight_layout(pad=3.0)
        
        # 绘制数字频率分布
        ax1 = axes[0, 0]
        if 'statistical' in result and 'digit_distribution' in result['statistical']:
            distribution = result['statistical']['digit_distribution']
            digits = list(range(10))
            frequencies = [distribution.get(d, 0) for d in digits]
            ax1.bar(digits, frequencies)
            ax1.set_title('数字频率分布')
            ax1.set_xlabel('数字')
            ax1.set_ylabel('频率')
        
        # 绘制四轨分析
        ax2 = axes[0, 1]
        if 'four_track' in result:
            four_track = result['four_track']
            tracks = ['轨道1', '轨道2', '轨道3', '轨道4']
            pair_ratios = []
            for i in range(1, 5):
                track = four_track.get(f'track{i}', {})
                nine_sum = track.get('nine_sum_pairs', {})
                pair_ratios.append(nine_sum.get('pair_ratio', 0))
            ax2.bar(tracks, pair_ratios)
            ax2.set_title('四轨配对率')
            ax2.set_ylabel('配对率')
        
        # 绘制综合评分
        ax3 = axes[1, 0]
        if 'scores' in result:
            scores = result['scores']
            score_names = ['随机性', '模式复杂度', '对称性', '可预测性']
            score_values = [
                scores.get('randomness', 0),
                scores.get('pattern_complexity', 0),
                scores.get('symmetry', 0),
                scores.get('predictability', 0)
            ]
            ax3.bar(score_names, score_values)
            ax3.set_title('综合评分')
            ax3.set_ylabel('评分')
            ax3.set_ylim(0, 1)
        
        # 绘制模式分布
        ax4 = axes[1, 1]
        if 'pattern' in result and 'pattern_distribution' in result['pattern']:
            pattern_dist = result['pattern']['pattern_distribution']
            pattern_names = list(pattern_dist.keys())
            pattern_counts = list(pattern_dist.values())
            ax4.bar(pattern_names, pattern_counts)
            ax4.set_title('模式分布')
            ax4.set_ylabel('数量')
        
        # 显示图表
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _update_constant_info(self, constant_name: str, digits: List[int]):
        """更新常数基本信息"""
        self.info_text.delete(1.0, tk.END)
        
        info = self.data_manager.get_constant_info(constant_name)
        
        info_str = f"常数名称: {constant_name}\n"
        info_str += f"描述: {info.get('description', '未知')}\n"
        info_str += f"文件路径: {info.get('file_path', '未知')}\n"
        info_str += f"估计长度: {info.get('estimated_length', 0)}\n"
        info_str += f"实际长度: {len(digits)}\n"
        info_str += "\n"
        
        # 显示前20位数字
        if digits:
            info_str += "前20位数字:\n"
            info_str += ' '.join(map(str, digits[:20])) + "...\n"
        
        self.info_text.insert(tk.END, info_str)
    
    def _update_dna_info(self, dna_sequence: str, digits: List[int]):
        """更新DNA序列基本信息"""
        self.info_text.delete(1.0, tk.END)
        
        info_str = f"类型: DNA序列\n"
        info_str += f"原始序列长度: {len(dna_sequence)}\n"
        info_str += f"编码后长度: {len(digits)}\n"
        info_str += "\n"
        
        # 显示原始DNA序列
        info_str += "原始DNA序列 (前50位):\n"
        info_str += dna_sequence[:50] + ("..." if len(dna_sequence) > 50 else "") + "\n"
        info_str += "\n"
        
        # 显示编码后的数字序列
        if digits:
            info_str += "编码后数字序列 (前20位):\n"
            info_str += ' '.join(map(str, digits[:20])) + ("..." if len(digits) > 20 else "") + "\n"
        
        self.info_text.insert(tk.END, info_str)
    
    def _display_prediction_result(self, constant_name: str, prediction: List[int]):
        """显示预测结果"""
        self.prediction_text.delete(1.0, tk.END)
        
        pred_str = f"常数: {constant_name}\n"
        pred_str += "预测结果:\n\n"
        
        pred_str += f"预测数字: {' '.join(map(str, prediction))}\n"
        pred_str += f"预测长度: {len(prediction)}\n"
        
        self.prediction_text.insert(tk.END, pred_str)
    
    def _display_classification_result(self, constant_name: str, classification: Dict[str, Any]):
        """显示分类结果"""
        self.classification_text.delete(1.0, tk.END)
        
        class_str = f"常数: {constant_name}\n"
        class_str += "分类结果:\n\n"
        
        if 'type' in classification:
            class_str += f"分类类型: {classification['type']}\n"
        
        if 'confidence' in classification:
            class_str += f"置信度: {classification['confidence']:.4f}\n"
        
        if 'features' in classification:
            features = classification['features']
            class_str += "\n特征分析:\n"
            for feature, value in features.items():
                class_str += f"  {feature}: {value}\n"
        
        if 'reasoning' in classification:
            class_str += "\n分类依据:\n"
            class_str += classification['reasoning'] + "\n"
        
        self.classification_text.insert(tk.END, class_str)
    
    def _display_evaluation_result(self, constant_name: str, max_digits: int, predict_length: int, 
                                   train_data: list, prediction: list, real_data: list, accuracy: float):
        """显示评估结果"""
        self.evaluation_text.delete(1.0, tk.END)
        
        eval_str = f"常数: {constant_name}\n"
        eval_str += f"评估参数:\n"
        eval_str += f"  训练数据长度: {max_digits}\n"
        eval_str += f"  预测长度: {predict_length}\n"
        eval_str += "\n"
        
        eval_str += f"训练数据的最后20位:\n"
        eval_str += ' '.join(map(str, train_data[-20:])) + "\n"
        eval_str += "\n"
        
        eval_str += f"预测结果 (前30位):\n"
        eval_str += ' '.join(map(str, prediction[:30])) + "...\n"
        eval_str += "\n"
        
        eval_str += f"真实数据 (前30位):\n"
        eval_str += ' '.join(map(str, real_data[:30])) + "...\n"
        eval_str += "\n"
        
        correct_count = sum(1 for pred, real in zip(prediction, real_data) if pred == real)
        eval_str += f"预测准确性: {accuracy:.2f}% ({correct_count}/{predict_length})\n"
        eval_str += "\n"
        
        # 分析错误模式
        errors = [(i, p, r) for i, (p, r) in enumerate(zip(prediction, real_data)) if p != r]
        if errors:
            eval_str += "错误分析:\n"
            eval_str += f"  错误总数: {len(errors)}\n"
            error_rate = (len(errors) / predict_length) * 100
            eval_str += f"  错误率: {error_rate:.2f}%\n"
            eval_str += "  前10个错误:\n"
            for i, p, r in errors[:10]:
                eval_str += f"    位置 {i+1}: 预测={p}, 真实={r}\n"
            if len(errors) > 10:
                eval_str += f"    ... 还有 {len(errors) - 10} 个错误\n"
        else:
            eval_str += "预测完全正确！\n"
        
        # 分析预测结果的多样性
        unique_predicted = len(set(prediction))
        unique_real = len(set(real_data))
        eval_str += "\n多样性分析:\n"
        eval_str += f"  预测结果唯一数字: {unique_predicted}\n"
        eval_str += f"  真实结果唯一数字: {unique_real}\n"
        eval_str += f"  预测多样性: {'高' if unique_predicted > 8 else '中' if unique_predicted > 5 else '低'}\n"
        
        self.evaluation_text.insert(tk.END, eval_str)
    
    def _clean_cache(self):
        """清理缓存"""
        count = self.data_manager.clean_cache()
        messagebox.showinfo("信息", f"已清理 {count} 个缓存项")
        self._update_cache_info()
    
    def _update_cache_info(self):
        """更新缓存信息"""
        stats = self.data_manager.get_cache_stats()
        cache_info_str = f"缓存项: {stats.get('total_items', 0)}\n"
        cache_info_str += f"缓存大小: {stats.get('cache_size_mb', 0):.2f} MB\n"
        self.cache_info.config(text=cache_info_str)
    
    def _show_about(self):
        """显示关于对话框"""
        about_text = "常数分析与预测系统 v2.0\n"
        about_text += "\n"
        about_text += "功能:\n"
        about_text += "- 常数分析与统计\n"
        about_text += "- 四轨分析系统\n"
        about_text += "- 模式识别与分析\n"
        about_text += "- 数字序列预测\n"
        about_text += "- 常数智能分类\n"
        about_text += "\n"
        about_text += "版本: 2.0\n"
        messagebox.showinfo("关于", about_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()