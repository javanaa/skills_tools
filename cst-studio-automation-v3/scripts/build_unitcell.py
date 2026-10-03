# -*- coding: utf-8 -*-
"""
build_unitcell.py — 一键构建双环嵌套开口方环吸波体单元胞

基于 W1 实战验证的 CST 2025 正确 API：
- 几何：Brick + Solid.Subtract（单冒号语法）
- 边界：X/Y unit cell, Zmin electric, Zmax expanded open
- 端口：Floquet Zmax 单端口 1模式
- 网格：MeshSettings Unstr + MeshAdaption3D ExpertSystem
- 求解器：FDSolver Tetrahedral + FDSolver.Start

用法（必须用 CST 自带 Python）：
    <CST>\AMD64\python\python.bat build_unitcell.py

修改 PARAMS 即可改变结构参数。
"""
import os
import sys
import time

# ------------------------------------------------------------------
# 参数区（修改这里即可）
# ------------------------------------------------------------------
PARAMS = {
    # 结构参数 (mm)
    "P":  6.10,   # 周期
    "L1": 5.20,   # 外环边长
    "L2": 3.88,   # 内环边长
    "w1": 0.35,   # 外环线宽
    "w2": 0.25,   # 内环线宽
    "g1": 0.35,   # 外环开口
    "g2": 0.35,   # 内环开口
    "h":  1.524,  # 介质厚度 (60mil)
    "tcu": 0.035, # 铜厚 (35um)
    "fmin": 2.0,  # GHz
    "fmax": 18.0, # GHz
    "substrate_epsr": 3.55,
    "substrate_tand": 0.0027,
}

CST_ROOT = r"<CST安装目录>"
WORK_DIR = r"<工作目录>"
PROJECT_NAME = "unitcell_benchmark"
PROJECT_PATH = os.path.join(WORK_DIR, PROJECT_NAME + ".cst")

# ------------------------------------------------------------------
def main():
    lib = os.path.join(CST_ROOT, "AMD64", "python_cst_libraries")
    if os.path.isdir(lib):
        sys.path.insert(0, lib)
    os.makedirs(WORK_DIR, exist_ok=True)
    os.chdir(CST_ROOT)

    import cst.interface as ci

    print("[1/7] 连接 CST...")
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
            print(f"  连接尝试 {attempt+1} 失败: {e}")
            time.sleep(5)
    if de is None:
        raise RuntimeError("CST 连接失败")

    print("[2/7] 新建 MWS 项目...")
    project = de.new_mws()
    m3d = project.model3d

    print("[3/7] 设置单位与频率范围...")
    m3d.add_to_history("set_units", """
With Units
  .Geometry "mm"
  .Frequency "GHz"
  .Time "ns"
End With
""")
    m3d.add_to_history("set_freq", f"""
With Frequency
  .SetFmin "{PARAMS['fmin']}"
  .SetFmax "{PARAMS['fmax']}"
End With
""")

    print("[4/7] 构建几何（双环嵌套开口方环）...")
    _build_geometry(m3d)

    print("[5/7] 定义材料...")
    _define_materials(m3d)

    print("[6/7] 设置边界/端口/网格/求解器...")
    _setup_boundaries(m3d)
    _setup_floquet_port(m3d)
    _setup_mesh(m3d)
    _setup_fd_solver(m3d)

    print("[7/7] 保存项目...")
    project.save(PROJECT_PATH)
    print(f"\n✅ 项目已保存: {PROJECT_PATH}")
    print(f"   几何: 双环嵌套开口方环 P={PARAMS['P']}mm")
    print(f"   频率: {PARAMS['fmin']}-{PARAMS['fmax']} GHz")
    print(f"   下一步: run_simulation.py 跑求解")

    de.close()


# ------------------------------------------------------------------
def _build_geometry(m3d):
    """双环嵌套开口方环 + 介质 + 铜背板。
    用 Brick 建实体，Solid.Subtract 挖开口（单冒号语法）。
    """
    P = PARAMS["P"]
    L1, L2 = PARAMS["L1"], PARAMS["L2"]
    w1, w2 = PARAMS["w1"], PARAMS["w2"]
    g1, g2 = PARAMS["g1"], PARAMS["g2"]
    h = PARAMS["h"]
    tcu = PARAMS["tcu"]
    half = P / 2.0

    m3d.add_to_history("substrate", f"""
With Brick
  .Reset
  .Name "substrate"
  .Component "component1"
  .Material "RO4003C"
  .Range "{-half}", "{half}", "{-half}", "{half}", "0", "{h}"
  .Create
End With
""")

    m3d.add_to_history("backplate", f"""
With Brick
  .Reset
  .Name "backplate"
  .Component "component1"
  .Material "Copper (annealed)"
  .Range "{-half}", "{half}", "{-half}", "{half}", "{-tcu}", "0"
  .Create
End With
""")

    m3d.add_to_history("outer_ring_outer", f"""
With Brick
  .Reset
  .Name "o_outer"
  .Component "metamaterial"
  .Material "Copper (annealed)"
  .Range "{-L1/2}", "{L1/2}", "{-L1/2}", "{L1/2}", "{h}", "{h+tcu}"
  .Create
End With
""")
    m3d.add_to_history("outer_ring_inner", f"""
With Brick
  .Reset
  .Name "o_inner"
  .Component "tool"
  .Material "PEC"
  .Range "{-(L1/2-w1)}", "{(L1/2-w1)}", "{-(L1/2-w1)}", "{(L1/2-w1)}", "{h-0.01}", "{h+tcu+0.01}"
  .Create
End With
""")
    m3d.add_to_history("outer_gap", f"""
With Brick
  .Reset
  .Name "o_gap"
  .Component "tool"
  .Material "PEC"
  .Range "{-g1/2}", "{g1/2}", "{(L1/2-w1)}", "{L1/2}", "{h-0.01}", "{h+tcu+0.01}"
  .Create
End With
""")
    m3d.add_to_history("outer_ring_subtract1",
        'Solid.Subtract "metamaterial:o_outer", "tool:o_inner"')
    m3d.add_to_history("outer_ring_subtract2",
        'Solid.Subtract "metamaterial:o_outer", "tool:o_gap"')
    m3d.add_to_history("rename_outer",
        'With Solid .Name "metamaterial:o_outer", "outer_ring" End With')

    m3d.add_to_history("inner_ring_outer", f"""
With Brick
  .Reset
  .Name "i_outer"
  .Component "metamaterial"
  .Material "Copper (annealed)"
  .Range "{-L2/2}", "{L2/2}", "{-L2/2}", "{L2/2}", "{h}", "{h+tcu}"
  .Create
End With
""")
    m3d.add_to_history("inner_ring_inner", f"""
With Brick
  .Reset
  .Name "i_inner"
  .Component "tool"
  .Material "PEC"
  .Range "{-(L2/2-w2)}", "{(L2/2-w2)}", "{-(L2/2-w2)}", "{(L2/2-w2)}", "{h-0.01}", "{h+tcu+0.01}"
  .Create
End With
""")
    m3d.add_to_history("inner_gap", f"""
With Brick
  .Reset
  .Name "i_gap"
  .Component "tool"
  .Material "PEC"
  .Range "{-g2/2}", "{g2/2}", "{(L2/2-w2)}", "{L2/2}", "{h-0.01}", "{h+tcu+0.01}"
  .Create
End With
""")
    m3d.add_to_history("inner_ring_subtract1",
        'Solid.Subtract "metamaterial:i_outer", "tool:i_inner"')
    m3d.add_to_history("inner_ring_subtract2",
        'Solid.Subtract "metamaterial:i_outer", "tool:i_gap"')
    m3d.add_to_history("rename_inner",
        'With Solid .Name "metamaterial:i_outer", "inner_ring" End With')

    m3d.add_to_history("delete_tools",
        'With Solid .Delete "tool:o_inner" .Delete "tool:o_gap" .Delete "tool:i_inner" .Delete "tool:i_gap" End With')


# ------------------------------------------------------------------
def _define_materials(m3d):
    m3d.add_to_history("mat_ro4003c", f"""
With Material
  .Reset
  .Name "RO4003C"
  .FrqType "Frequency independent"
  .Type "Normal"
  .Epsilon "{PARAMS['substrate_epsr']}"
  .TanD "{PARAMS['substrate_tand']}"
  .TanDFreq "0"
  .Create
End With
""")


# ------------------------------------------------------------------
def _setup_boundaries(m3d):
    """X/Y unit cell, Zmin electric(背板), Zmax expanded open。"""
    m3d.add_to_history("boundaries", """
With Boundary
  .Xmin "unit cell"
  .Xmax "unit cell"
  .Ymin "unit cell"
  .Ymax "unit cell"
  .Zmin "electric"
  .Zmax "expanded open"
  .XminSpace "0.0"
  .XmaxSpace "0.0"
  .YminSpace "0.0"
  .YmaxSpace "0.0"
  .ZminSpace "0.0"
  .ZmaxSpace "0.0"
End With
""")


# ------------------------------------------------------------------
def _setup_floquet_port(m3d):
    """仅 Zmax 单端口，1模式（背板完全覆盖，Zmin透射为零）。"""
    m3d.add_to_history("floquet_zmax", """
With FloquetPort
  .Reset
  .Port "Zmax"
  .SetNumberOfModesConsidered "1"
End With
""")


# ------------------------------------------------------------------
def _setup_mesh(m3d):
    """四面体非结构化网格 + ExpertSystem 自适应。
    CST 2025 无 MeshSettings.Reset / MeshAdaption3D.Reset。
    """
    m3d.add_to_history("mesh_settings", """
With MeshSettings
  .SetMeshType "Unstr"
End With
""")
    m3d.add_to_history("mesh_adaption", """
With MeshAdaption3D
  .SetType "HighFrequencyTet"
  .SetAdaptionStrategy "ExpertSystem"
  .MinPasses "3"
  .MaxPasses "8"
End With
""")


# ------------------------------------------------------------------
def _setup_fd_solver(m3d):
    """CST 2025 写法：SetMethod + OrderTet + SetRecordUnitCellScanFarfield。
    注意：不在这里 Start，由 run_simulation.py 启动。
    """
    m3d.add_to_history("fd_solver_config", """
With FDSolver
  .Reset
  .SetMethod "Tetrahedral", "General purpose"
  .OrderTet "Second"
  .SetRecordUnitCellScanFarfield "Auto"
End With
""")


if __name__ == "__main__":
    main()