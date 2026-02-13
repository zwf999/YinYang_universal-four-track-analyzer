#!/usr/bin/env python3
# 快速评估预测结果的脚本

import tkinter as tk
from tkinter import ttk, messagebox
from core.data.data_manager import DataManager
from core.predictors.ensemble_predictor import EnsemblePredictor

class QuickPredictionEvaluator:
    """快速预测评估器"""
    
    def __init__(self, root):
        """
        初始化评估器
        
        Args:
            root: tkinter根窗口
        """
        self.root = root
        self.root.title("快速预测评估器")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        # 初始化组件
        self.data_manager = DataManager()
        self.predictor = EnsemblePredictor()
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建顶部控制面板
        self.control_panel = ttk.LabelFrame(self.main_frame, text="控制面板", padding="10")
        self.control_panel.pack(fill=tk.X, pady=(0, 10))
        
        # 创建左侧参数面板
        self.params_panel = ttk.Frame(self.control_panel)
        self.params_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        
        # 创建右侧说明面板
        self.info_panel = ttk.LabelFrame(self.control_panel, text="参数说明", padding="10")
        self.info_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 创建底部显示区域
        self.display_panel = ttk.LabelFrame(self.main_frame, text="评估结果", padding="10")
        self.display_panel.pack(fill=tk.BOTH, expand=True)
        
        # 初始化控制面板
        self._init_params_panel()
        self._init_info_panel()
        self._init_display_panel()
        
        # 加载可用常数
        self._load_available_constants()
    
    def _init_params_panel(self):
        """初始化参数面板"""
        # 常数选择
        ttk.Label(self.params_panel, text="选择常数:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.constant_var = tk.StringVar()
        self.constant_combo = ttk.Combobox(self.params_panel, textvariable=self.constant_var, width=20)
        self.constant_combo.grid(row=0, column=1, sticky=tk.W, pady=(0, 5))
        
        # 训练数据长度
        ttk.Label(self.params_panel, text="训练数据长度:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.train_length_var = tk.IntVar(value=1000)  # 默认为1000，加快加载速度
        ttk.Entry(self.params_panel, textvariable=self.train_length_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=(0, 5))
        
        # 预测长度
        ttk.Label(self.params_panel, text="预测长度:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.predict_length_var = tk.IntVar(value=100)
        ttk.Entry(self.params_panel, textvariable=self.predict_length_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=(0, 5))
        
        # 操作按钮
        self.evaluate_btn = ttk.Button(self.params_panel, text="评估预测结果", command=self._evaluate_prediction)
        self.evaluate_btn.grid(row=3, column=0, columnspan=2, sticky=tk.W+tk.E, pady=(10, 5))
        
        self.exit_btn = ttk.Button(self.params_panel, text="退出", command=self.root.quit)
        self.exit_btn.grid(row=4, column=0, columnspan=2, sticky=tk.W+tk.E, pady=(0, 5))
    
    def _init_info_panel(self):
        """初始化说明面板"""
        info_text = "参数说明:\n\n"
        info_text += "1. 训练数据长度: 使用多少位现有数据来训练预测模型。\n"
        info_text += "   - 示例: 1000 表示使用前1000位来预测后续数字。\n"
        info_text += "   - 建议: 1000-10000之间，太大可能会很慢。\n\n"
        info_text += "2. 预测长度: 预测多少位后续数字。\n"
        info_text += "   - 示例: 100 表示预测接下来的100位数字。\n"
        info_text += "   - 建议: 100-200之间，太大可能会降低准确性。\n\n"
        info_text += "3. 工作原理:\n"
        info_text += "   - 系统使用前N位数据训练模型\n"
        info_text += "   - 预测接下来的M位数字\n"
        info_text += "   - 将预测结果与真实数据比较\n"
        info_text += "   - 计算预测准确性\n"
        
        self.info_label = ttk.Label(self.info_panel, text=info_text, justify=tk.LEFT, font=('Arial', 9))
        self.info_label.pack(fill=tk.BOTH, expand=True)
    
    def _init_display_panel(self):
        """初始化显示面板"""
        # 创建结果文本
        self.result_text = tk.Text(self.display_panel, wrap=tk.WORD, height=20)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        self.result_scroll = ttk.Scrollbar(self.result_text, command=self.result_text.yview)
        self.result_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=self.result_scroll.set)
    
    def _load_available_constants(self):
        """加载可用常数列表"""
        constants = self.data_manager.list_constants()
        constant_names = [const['name'] for const in constants]
        self.constant_combo['values'] = constant_names
        if constant_names:
            self.constant_var.set(constant_names[0])
    
    def _evaluate_prediction(self):
        """评估预测结果"""
        constant_name = self.constant_var.get()
        if not constant_name:
            messagebox.showerror("错误", "请选择一个常数")
            return
        
        train_length = self.train_length_var.get()
        predict_length = self.predict_length_var.get()
        
        # 显示加载状态
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"正在评估 {constant_name} 的预测结果...\n")
        self.root.update()
        
        try:
            # 加载完整的常数数据
            full_digits = self.data_manager.load_constant(constant_name, train_length + predict_length)
            if not full_digits:
                messagebox.showerror("错误", f"无法加载常数 {constant_name}")
                return
            
            # 检查数据长度
            if len(full_digits) < train_length + predict_length:
                messagebox.showerror("错误", f"数据长度不足，需要 {train_length + predict_length} 位，但只有 {len(full_digits)} 位")
                return
            
            # 分割训练数据和真实数据
            train_data = full_digits[:train_length]
            real_data = full_digits[train_length:train_length + predict_length]
            
            # 预测数据
            prediction = self.predictor.predict(train_data, length=predict_length)
            
            # 评估预测结果
            correct_count = sum(1 for pred, real in zip(prediction, real_data) if pred == real)
            accuracy = (correct_count / predict_length) * 100
            
            # 生成评估报告
            report = self._generate_evaluation_report(
                constant_name, train_length, predict_length, 
                train_data, prediction, real_data, accuracy
            )
            
            # 显示评估结果
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, report)
            
        except Exception as e:
            messagebox.showerror("错误", f"评估失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _generate_evaluation_report(self, constant_name, train_length, predict_length, 
                                   train_data, prediction, real_data, accuracy):
        """生成评估报告"""
        report = f"常数: {constant_name}\n"
        report += f"评估参数:\n"
        report += f"  训练数据长度: {train_length}\n"
        report += f"  预测长度: {predict_length}\n"
        report += "\n"
        
        report += f"训练数据的最后20位:\n"
        report += ' '.join(map(str, train_data[-20:])) + "\n"
        report += "\n"
        
        report += f"预测结果 (前30位):\n"
        report += ' '.join(map(str, prediction[:30])) + "...\n"
        report += "\n"
        
        report += f"真实数据 (前30位):\n"
        report += ' '.join(map(str, real_data[:30])) + "...\n"
        report += "\n"
        
        correct_count = sum(1 for pred, real in zip(prediction, real_data) if pred == real)
        report += f"预测准确性: {accuracy:.2f}% ({correct_count}/{predict_length})\n"
        report += "\n"
        
        # 分析错误模式
        errors = [(i, p, r) for i, (p, r) in enumerate(zip(prediction, real_data)) if p != r]
        if errors:
            report += "错误分析:\n"
            report += f"  错误总数: {len(errors)}\n"
            error_rate = (len(errors) / predict_length) * 100
            report += f"  错误率: {error_rate:.2f}%\n"
        else:
            report += "预测完全正确！\n"
        
        return report

def main():
    """主函数"""
    root = tk.Tk()
    app = QuickPredictionEvaluator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
