# -*- coding: utf-8 -*-
"""
parse_s11.py — 解析 Touchstone S1P 文件 + 吸收率统计

用法：
    python parse_s11.py [s1p文件路径]
    默认读取 WORK_DIR/unitcell_S11.s1p.s1p
"""
import os
import sys
import math

WORK_DIR = os.environ.get("CST_WORK_DIR", r"<工作目录>")   # 或设环境变量 CST_WORK_DIR
DEFAULT_S1P = os.path.join(WORK_DIR, "unitcell_S11.s1p.s1p")
CSV_OUT = os.path.join(WORK_DIR, "unitcell_S11_data.csv")


def parse_s1p(path):
    """解析单端口 Touchstone (.s1p) 文件。
    支持 RI（实部虚部）和 DB（幅度相位）格式。
    返回 (freqs, s11_real, s11_imag) 或 (freqs, s11_db, s11_phase)。
    """
    freqs, c1, c2 = [], [], []
    fmt = None
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("!"):
                continue
            if line.startswith("#"):
                parts = line.upper().split()
                if "RI" in parts:
                    fmt = "RI"
                elif "DB" in parts:
                    fmt = "DB"
                elif "MA" in parts:
                    fmt = "MA"
                continue
            parts = line.split()
            if len(parts) >= 3:
                try:
                    freqs.append(float(parts[0]))
                    c1.append(float(parts[1]))
                    c2.append(float(parts[2]))
                except ValueError:
                    continue
    return freqs, c1, c2, fmt


def compute_absorption(freqs, c1, c2, fmt):
    """计算吸收率 A = 1 - |S11|^2（单端口、背板全反射时）。"""
    absorption = []
    s11_mag_db = []
    for i in range(len(freqs)):
        if fmt == "RI":
            mag = math.sqrt(c1[i]**2 + c2[i]**2)
        elif fmt == "DB":
            mag = 10 ** (c1[i] / 20.0)
        elif fmt == "MA":
            mag = c1[i]
        else:
            mag = abs(c1[i])
        s11_mag_db.append(20 * math.log10(max(mag, 1e-12)))
        absorption.append(1.0 - mag**2)
    return absorption, s11_mag_db


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_S1P
    if not os.path.exists(path):
        for f in os.listdir(WORK_DIR):
            if f.endswith(".s1p"):
                path = os.path.join(WORK_DIR, f)
                break
    if not os.path.exists(path):
        print(f"❌ 找不到 S1P 文件: {path}")
        return

    print(f"解析: {path}")
    freqs, c1, c2, fmt = parse_s1p(path)
    print(f"  频点数: {len(freqs)}")
    print(f"  格式: {fmt}")
    if freqs:
        print(f"  频率范围: {freqs[0]:.2f} - {freqs[-1]:.2f}")

    absorption, s11_db = compute_absorption(freqs, c1, c2, fmt)

    if absorption:
        max_a = max(absorption)
        max_idx = absorption.index(max_a)
        min_s11 = min(s11_db)
        min_idx = s11_db.index(min_s11)

        print(f"\n=== 关键指标 ===")
        print(f"  最大吸收率: {max_a*100:.2f}% @ {freqs[max_idx]:.3f} GHz")
        print(f"  最小 |S11|: {min_s11:.2f} dB @ {freqs[min_idx]:.3f} GHz")

        above50 = [(freqs[i], absorption[i]) for i in range(len(freqs)) if absorption[i] > 0.5]
        above90 = [(freqs[i], absorption[i]) for i in range(len(freqs)) if absorption[i] > 0.9]
        if above50:
            print(f"  A>50% 频段: {above50[0][0]:.2f}-{above50[-1][0]:.2f} GHz ({len(above50)}点)")
        else:
            print(f"  A>50% 频段: 无")
        if above90:
            print(f"  A>90% 频段: {above90[0][0]:.2f}-{above90[-1][0]:.2f} GHz")

    with open(CSV_OUT, "w") as f:
        f.write("freq_GHz,S11_dB,absorption\n")
        for i in range(len(freqs)):
            f.write(f"{freqs[i]},{s11_db[i]:.6f},{absorption[i]:.6f}\n")
    print(f"\n✅ CSV 已导出: {CSV_OUT}")


if __name__ == "__main__":
    main()
