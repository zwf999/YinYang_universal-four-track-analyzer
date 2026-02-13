#!/usr/bin/env python3
# 评估预测结果的脚本
# 支持预测100位并自动处理不同常数，不需要用户手动修改命令

import tkinter as tk
from tkinter import ttk, messagebox
from core.data.data_manager import DataManager
from core.predictors.ensemble_predictor import EnsemblePredictor

class PredictionEvaluator:
    """预测评估器"""
    
    def __init__(self, root):
        """
        初始化评估器
        
        Args:
            root: tkinter根窗口
        """
        self.root = root
        self.root.title("预测结果评估器")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 初始化组件
        self.data_manager = DataManager()
        self.predictor = EnsemblePredictor()
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建左侧控制面板
        self.control_panel = ttk.LabelFrame(self.main_frame, text="控制面板", padding="10")
        self.control_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=(0, 10))
        
        # 创建右侧显示区域
        self.display_panel = ttk.LabelFrame(self.main_frame, text="评估结果", padding="10")
        self.display_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 初始化控制面板
        self._init_control_panel()
        
        # 初始化显示面板
        self._init_display_panel()
        
        # 加载可用常数
        self._load_available_constants()
    
    def _init_control_panel(self):
        """初始化控制面板"""
        # 常数选择
        ttk.Label(self.control_panel, text="选择常数:").pack(anchor=tk.W, pady=(0, 5))
        self.constant_var = tk.StringVar()
        self.constant_combo = ttk.Combobox(self.control_panel, textvariable=self.constant_var, width=30)
        self.constant_combo.pack(fill=tk.X, pady=(0, 10))
        
        # 训练数据长度
        ttk.Label(self.control_panel, text="训练数据长度:").pack(anchor=tk.W)
        self.train_length_var = tk.IntVar(value=10000)
        ttk.Entry(self.control_panel, textvariable=self.train_length_var, width=10).pack(anchor=tk.W, pady=(0, 5))
        
        # 预测长度
        ttk.Label(self.control_panel, text="预测长度:").pack(anchor=tk.W)
        self.predict_length_var = tk.IntVar(value=100)
        ttk.Entry(self.control_panel, textvariable=self.predict_length_var, width=10).pack(anchor=tk.W, pady=(0, 10))
        
        # 操作按钮
        self.evaluate_btn = ttk.Button(self.control_panel, text="评估预测结果", command=self._evaluate_prediction)
        self.evaluate_btn.pack(fill=tk.X, pady=(0, 5))
        
        self.exit_btn = ttk.Button(self.control_panel, text="退出", command=self.root.quit)
        self.exit_btn.pack(fill=tk.X, pady=(0, 5))
    
    def _init_display_panel(self):
        """初始化显示面板"""
        # 创建结果文本
        self.result_text = tk.Text(self.display_panel, wrap=tk.WORD, height=30)
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
        
        report += f"前20位训练数据:\n"
        report += ' '.join(map(str, train_data[-20:])) + "...\n"
        report += "\n"
        
        report += f"预测结果:\n"
        report += ' '.join(map(str, prediction)) + "\n"
        report += "\n"
        
        report += f"真实数据:\n"
        report += ' '.join(map(str, real_data)) + "\n"
        report += "\n"
        
        report += f"预测准确性: {accuracy:.2f}% ({sum(1 for p, r in zip(prediction, real_data) if p == r)}/{predict_length})\n"
        report += "\n"
        
        # 分析错误模式
        errors = [(i, p, r) for i, (p, r) in enumerate(zip(prediction, real_data)) if p != r]
        if errors:
            report += "错误分析:\n"
            report += f"  错误总数: {len(errors)}\n"
            report += "  错误位置和值:\n"
            for i, p, r in errors[:10]:  # 只显示前10个错误
                report += f"    位置 {i+1}: 预测={p}, 真实={r}\n"
            if len(errors) > 10:
                report += f"    ... 还有 {len(errors) - 10} 个错误\n"
        else:
            report += "预测完全正确！\n"
        
        return report

def main():
    """主函数"""
    root = tk.Tk()
    app = PredictionEvaluator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
