# -*- coding: utf-8 -*-
"""
run_simulation.py — 启动频域四面体求解 + 等待 + Touchstone 导出

基于 W1 实战验证：
- FDSolver.Start 启动频域（非 m3d.run_solver 默认时域）
- is_solver_running 轮询等待
- export_touchstone 导出 S 参数（传 mws 而非 de）
- Model.log 诊断信息提取

用法：
    <CST>\AMD64\python\python.bat run_simulation.py
"""
import os
import sys
import time

# ------------------------------------------------------------------
# 配置
# ------------------------------------------------------------------
CST_ROOT = os.environ.get("CST_HOME", r"<CST安装目录>")   # 或设环境变量 CST_HOME
WORK_DIR = os.environ.get("CST_WORK_DIR", r"<工作目录>")   # 或设环境变量 CST_WORK_DIR
PROJECT_PATH = os.path.join(WORK_DIR, "unitcell_benchmark.cst")
EXPORT_PATH = os.path.join(WORK_DIR, "unitcell_S11.s1p")
SOLVER_TIMEOUT = 3600  # 秒

# ------------------------------------------------------------------
def main():
    lib = os.path.join(CST_ROOT, "AMD64", "python_cst_libraries")
    if os.path.isdir(lib):
        sys.path.insert(0, lib)
    os.chdir(CST_ROOT)

    import cst.interface as ci
    from cst.post_processing.s_parameters import export_touchstone

    print("[1/4] 连接 CST...")
    de = None
    for attempt in range(3):
        try:
            des = ci.running_design_environments()
            if des:
                de = ci.DesignEnvironment.connect(des[0])
            else:
                de = ci.DesignEnvironment()
                time.sleep(5)
            break
        except Exception as e:
            print(f"  尝试 {attempt+1}: {e}")
            time.sleep(5)
    if de is None:
        raise RuntimeError("连接失败")

    print(f"[2/4] 打开项目: {PROJECT_PATH}")
    if not os.path.exists(PROJECT_PATH):
        raise FileNotFoundError(f"项目不存在: {PROJECT_PATH}，先跑 build_unitcell.py")
    mws = de.open_project(PROJECT_PATH)
    m3d = mws.model3d

    print("[3/4] 启动频域四面体求解...")
    m3d.add_to_history("start_fd", "FDSolver.Start")

    t0 = time.monotonic()
    while m3d.is_solver_running():
        elapsed = time.monotonic() - t0
        if elapsed > SOLVER_TIMEOUT:
            raise RuntimeError(f"求解超时 ({SOLVER_TIMEOUT}s)")
        if int(elapsed) % 60 == 0:
            print(f"  求解中... {int(elapsed)}s")
        time.sleep(10)
    elapsed = time.monotonic() - t0
    print(f"  求解完成，耗时 {int(elapsed)}s")

    print(f"[4/4] 导出 Touchstone: {EXPORT_PATH}")
    export_touchstone(
        mws,
        EXPORT_PATH,
        impedance=50,
        export_type='S',
        format="RI",
        frequency_range="Full",
        renormalize=False,
    )
    actual_path = EXPORT_PATH + ".s1p" if not EXPORT_PATH.endswith(".s1p") else EXPORT_PATH
    if os.path.exists(actual_path):
        size = os.path.getsize(actual_path)
        print(f"\n✅ 导出成功: {actual_path} ({size} bytes)")
    else:
        for f in os.listdir(WORK_DIR):
            if "S11" in f or "s1p" in f:
                fp = os.path.join(WORK_DIR, f)
                print(f"  找到导出文件: {fp} ({os.path.getsize(fp)} bytes)")

    log_path = os.path.join(WORK_DIR, "unitcell_benchmark", "Result", "Model.log")
    if os.path.exists(log_path):
        print(f"\n--- Model.log 关键信息 ---")
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        for line in lines:
            if any(k in line for k in ["mesh cells", "Delta S", "converged", "pass", "adaption"]):
                print(f"  {line.strip()}")

    de.close()
    print("\n✅ 全部完成")


if __name__ == "__main__":
    main()
