#!/usr/bin/env python3
# run_ui.py
# 启动用户界面的脚本

import tkinter as tk
from core.ui.main_window import MainWindow

if __name__ == "__main__":
    # 创建根窗口
    root = tk.Tk()
    
    # 创建主窗口
    app = MainWindow(root)
    
    # 运行主循环
    root.mainloop()