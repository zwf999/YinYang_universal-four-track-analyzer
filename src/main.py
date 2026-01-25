from core_engine import calculate_Omega

def main():
    print("🔬 FD-JTMS v2.0 启动...")
    print("正在分析圆周率π (1,000,000位)...\n")
    
    # 加载数据
    pi_digits = load_pi_digits()
    
    # 计算四维Ω值
    Omega, Delta_R = calculate_Omega(pi_digits)
    
    # 输出结果
    print("✅ 验证结果:")
    print(f"  Ω值       = {Omega:.3f}")
    print(f"  ΔR_小大   = {Delta_R['小大']:.4f}")
    print(f"  ΔR_上下   = {Delta_R['上下']:.4f}")
    print(f"  ΔR_奇偶   = {Delta_R['奇偶']:.4f}")
    print(f"  ΔR_AB     = {Delta_R['AB']:.4f}")

    # 结论判断
    if Omega >= 0.15:
        print(f"\n🌟 结论: π序列存在强拓扑结构！符合'阴阳不均质'理论。")
    elif Omega >= 0.01:
        print(f"\n🔹 结论: π序列存在弱结构。")
    else:
        print(f"\n🔸 结论: 未检测到显著结构（随机性主导）。")

if __name__ == "__main__":
    main()
