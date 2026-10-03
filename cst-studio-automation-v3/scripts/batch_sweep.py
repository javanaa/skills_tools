# -*- coding: utf-8 -*-
"""
batch_sweep.py — 参数扫描批量仿真

从 cst-mcp (AndersOnLin4) absorber_batch 思路提取：
- 单参数/多参数扫描
- 断点续跑（指纹守卫，已完成的跳过）
- 结果自动汇总 CSV

用法：
    <CST>\AMD64\python\python.bat batch_sweep.py --param L1 --range 4.5 5.5 5
    <CST>\AMD64\python\python.bat batch_sweep.py --param L1 --values 4.8 5.0 5.2
    <CST>\AMD64\python\python.bat batch_sweep.py --multi L1=4.8,5.0,5.2 L2=3.5,3.88,4.2
"""
import os
import sys
import json
import time
import hashlib
import argparse

CST_ROOT = r"<CST安装目录>"
WORK_DIR = r"<工作目录>"
BASE_PROJECT = os.path.join(WORK_DIR, "unitcell_benchmark.cst")
RESULTS_DIR = os.path.join(WORK_DIR, "batch_results")
PROGRESS_FILE = os.path.join(RESULTS_DIR, "progress.json")
SUMMARY_CSV = os.path.join(RESULTS_DIR, "summary.csv")


def fingerprint(params):
    """参数组合的唯一指纹（用于断点续跑）。"""
    key = json.dumps(params, sort_keys=True)
    return hashlib.md5(key.encode()).hexdigest()[:12]


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {"done": {}, "failed": {}}


def save_progress(progress):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)


def run_single(m3d, mws, params, export_path):
    """修改参数 → 重建 → 求解 → 导出。"""
    from cst.post_processing.s_parameters import export_touchstone

    for name, value in params.items():
        m3d.StoreParameter(name, str(value))

    m3d.DeleteResults()
    m3d.Rebuild()
    time.sleep(2)

    m3d.add_to_history("start_fd", "FDSolver.Start")
    t0 = time.monotonic()
    while m3d.is_solver_running():
        if time.monotonic() - t0 > 3600:
            raise RuntimeError("求解超时")
        time.sleep(10)

    export_touchstone(mws, export_path, impedance=50, export_type='S',
                      format="RI", frequency_range="Full", renormalize=False)
    return time.monotonic() - t0


def parse_s1p_quick(path):
    """快速解析 S1P，返回 (peak_absorption, peak_freq, min_s11_db)。"""
    import math
    freqs, mags = [], []
    with open(path, "r", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("!") or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 3:
                try:
                    freqs.append(float(parts[0]))
                    mags.append(math.sqrt(float(parts[1])**2 + float(parts[2])**2))
                except ValueError:
                    continue
    if not freqs:
        return None
    absorptions = [1 - m**2 for m in mags]
    s11_db = [20 * math.log10(max(m, 1e-12)) for m in mags]
    peak_idx = absorptions.index(max(absorptions))
    min_idx = s11_db.index(min(s11_db))
    return {
        "peak_absorption": max(absorptions),
        "peak_freq_GHz": freqs[peak_idx],
        "min_s11_dB": min(s11_db),
        "min_s11_freq_GHz": freqs[min_idx],
        "n_points": len(freqs),
    }


def main():
    parser = argparse.ArgumentParser(description="CST 参数扫描批量仿真")
    parser.add_argument("--param", help="单参数名，如 L1")
    parser.add_argument("--range", nargs=3, type=float, metavar=("START", "STOP", "N"),
                        help="参数范围 start stop n_points")
    parser.add_argument("--values", nargs="+", type=float, help="显式参数值列表")
    parser.add_argument("--multi", nargs="+", help="多参数扫描，格式 name=v1,v2,v3")
    args = parser.parse_args()

    combos = []
    if args.param and args.range:
        start, stop, n = args.range
        values = [start + (stop - start) * i / (n - 1) for i in range(int(n))]
        combos = [{args.param: round(v, 4)} for v in values]
    elif args.param and args.values:
        combos = [{args.param: v} for v in args.values]
    elif args.multi:
        param_dict = {}
        for item in args.multi:
            name, vals = item.split("=")
            param_dict[name] = [float(v) for v in vals.split(",")]
        import itertools
        keys = list(param_dict.keys())
        for vals in itertools.product(*param_dict.values()):
            combos.append({k: round(v, 4) for k, v in zip(keys, vals)})
    else:
        print("用法: --param L1 --range 4.5 5.5 5")
        print("或:   --multi L1=4.8,5.0 L2=3.5,3.88")
        return

    print(f"共 {len(combos)} 组参数组合")
    for i, c in enumerate(combos):
        print(f"  [{i+1}] {c}")

    lib = os.path.join(CST_ROOT, "AMD64", "python_cst_libraries")
    if os.path.isdir(lib):
        sys.path.insert(0, lib)
    os.chdir(CST_ROOT)
    os.makedirs(RESULTS_DIR, exist_ok=True)

    import cst.interface as ci

    print("\n连接 CST...")
    de = ci.DesignEnvironment()
    time.sleep(5)
    mws = de.open_project(BASE_PROJECT)
    m3d = mws.model3d

    progress = load_progress()
    results = []

    for i, params in enumerate(combos):
        fp = fingerprint(params)
        label = "_".join(f"{k}{v}" for k, v in sorted(params.items()))

        if fp in progress["done"]:
            print(f"[{i+1}/{len(combos)}] 跳过(已完成): {label}")
            results.append(progress["done"][fp])
            continue
        if fp in progress["failed"]:
            print(f"[{i+1}/{len(combos)}] 跳过(之前失败): {label}")
            continue

        print(f"[{i+1}/{len(combos)}] 运行: {label}")
        export_path = os.path.join(RESULTS_DIR, f"s11_{label}.s1p")
        try:
            elapsed = run_single(m3d, mws, params, export_path)
            actual = export_path + ".s1p"
            stats = parse_s1p_quick(actual) if os.path.exists(actual) else None
            record = {
                "fingerprint": fp,
                "params": params,
                "elapsed_s": round(elapsed, 1),
                "stats": stats,
            }
            progress["done"][fp] = record
            results.append(record)
            if stats:
                print(f"  ✅ {elapsed:.0f}s | peak A={stats['peak_absorption']*100:.1f}% "
                      f"@ {stats['peak_freq_GHz']:.2f}GHz | min S11={stats['min_s11_dB']:.1f}dB")
        except Exception as e:
            print(f"  ❌ 失败: {str(e)[:100]}")
            progress["failed"][fp] = {"params": params, "error": str(e)[:200]}

        save_progress(progress)

    with open(SUMMARY_CSV, "w") as f:
        if results and results[0].get("params"):
            param_keys = sorted(results[0]["params"].keys())
            header = ",".join(param_keys) + ",peak_absorption,peak_freq_GHz,min_s11_dB,elapsed_s\n"
            f.write(header)
            for r in results:
                if r.get("stats"):
                    vals = [str(r["params"].get(k, "")) for k in param_keys]
                    s = r["stats"]
                    f.write(",".join(vals) + f",{s['peak_absorption']:.6f},"
                            f"{s['peak_freq_GHz']:.4f},{s['min_s11_dB']:.4f},"
                            f"{r['elapsed_s']}\n")
    print(f"\n✅ 汇总: {SUMMARY_CSV}")
    print(f"   完成: {len(progress['done'])}, 失败: {len(progress['failed'])}")

    de.close()


if __name__ == "__main__":
    main()