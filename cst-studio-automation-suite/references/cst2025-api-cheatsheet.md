# CST 2025 API 速查表

> 所有写法均经实战验证（2026-10-01）。标注 ✅=已验证成功，❌=已验证失败/死路，⚠️=语法接受但效果待确认。

---

## 1. 连接与项目

```python
# ✅ 连接 CST（自动启动 GUI 实例）
de = ci.DesignEnvironment()

# ✅ 新建 MWS 项目
mws = de.new_mws()
m3d = mws.model3d

# ✅ 打开已有项目
mws = de.open_project(r"E:\path\to\project.cst")

# ✅ 保存（纯英文路径！）
mws.save(r"<工作目录>\project.cst")

# ✅ 关闭
de.close()
```

---

## 2. VBA 执行

```python
# ✅ 首选：分步 add_to_history，每步可独立报错定位
m3d.add_to_history("step_name", '''With Units
    .Geometry "mm"
    .Frequency "GHz"
End With
''')

# ✅ 执行完整 Sub（用于文件输出等）
m3d._execute_vba_code('sub main\n...\nend sub')

# ❌ 不要用：pywin32 COM RunMacro(path)
```

---

## 3. 单位与参数

```vba
' ✅
With Units
    .Geometry "mm"
    .Frequency "GHz"
    .Time "ns"
End With
MakeSureParameterExists "P", "6.10"
MakeSureParameterExists "L1", "5.20"
```

---

## 4. 频率与背景

```vba
' ✅
Solver.FrequencyRange "2", "18"
With Background
    .Reset
    .Type "Normal"
    .Epsilon "1"
    .Mu "1"
    .XminSpace "0.0"
    .XmaxSpace "0.0"
    .YminSpace "0.0"
    .YmaxSpace "0.0"
    .ZminSpace "0.0"      ' 背板紧贴 electric 边界时设 0
    .ZmaxSpace "1.0"
End With
```

---

## 5. 材料

```vba
' ✅
With Material
    .Reset
    .Name "RO4003C"
    .Type "Normal"
    .Epsilon "3.55"
    .Mu "1"
    .Kappa "0"
    .TanD "0.0027"
    .TanDFreq "0.0"
    .Create
End With
' Copper 为内置材料，直接 .Material "Copper" 引用
```

---

## 6. 几何（Brick + Solid.Subtract）

```vba
' ✅ 创建实体
With Brick
    .Reset
    .Name "o_solid"
    .Component "metamaterial"
    .Material "Copper"
    .Xrange "-L1/2", "L1/2"
    .Yrange "-L1/2", "L1/2"
    .Zrange "h", "h+tcu"
    .Create
End With

' ✅ 创建工具实体（用于挖空）
With Brick
    .Reset
    .Name "o_hole"
    .Component "tool"
    .Material "Vacuum"
    .Xrange "-L1/2+w1", "L1/2-w1"
    .Yrange "-L1/2+w1", "L1/2-w1"
    .Zrange "h", "h+tcu"
    .Create
End With

' ✅ 布尔减（单冒号！）
Solid.Subtract "metamaterial:o_solid", "tool:o_hole"

' ✅ 重命名
Solid.Rename "metamaterial:o_solid", "ring_outer"

# ✅ 全部几何/物理命令追加进历史后，必须一次性全历史重建（Neil2DP 实测硬规则）：
#    model3d 对象只有 Get 查询方法没有 Create——创建一律走 add_to_history + full_history_rebuild
m3d.full_history_rebuild()

# ⚠️ 注意：add_to_history 是"写历史并尝试执行"，写历史不可逆——
#    命令失败也会留在历史里，静默成功（返回 True 但模型无变化）是最难排查的失败模式
#    （valenZW/cst-sim-agent 实测）
```

---

## 7. 边界条件

```vba
' ✅ 单元胞吸波体标准配置
With Boundary
    .Xmin "unit cell"
    .Xmax "unit cell"
    .Ymin "unit cell"
    .Ymax "unit cell"
    .Zmin "electric"       ' 背板侧
    .Zmax "expanded open"  ' 入射侧（Floquet 端口会覆盖）
    .XPeriodicShift "0"
    .YPeriodicShift "0"
    .ZPeriodicShift "0"
End With
' ❌ Boundary.Reset 不存在
```

---

## 8. Floquet 端口

```vba
' ✅
With FloquetPort
    .Reset
    .Port "Zmax"              ' 用 "Zmax"/"Zmin"，不是 "1"
    .SetNumberOfModesConsidered "1"
End With
' 取 2 个模式时设 "2"，可对比两个正交极化的 S11
```

---

## 9. 网格（四面体）

```vba
' ✅ MeshSettings：切换四面体类型（无 Reset！）
With MeshSettings
    .SetMeshType "Unstr"     ' CST 2025 用 "Unstr"，不是 "Tet"
End With

' ✅ MeshAdaption3D：自适应网格（无 Reset！）
With MeshAdaption3D
    .SetType "HighFrequencyTet"
    .SetAdaptionStrategy "ExpertSystem"
    .MinPasses "3"
    .MaxPasses "8"
End With

' ❌ 网格密度 VBA 命令经 COM/add_to_history 通道全部静默失效（2026-10-02 外部三仓库实锤）：
'    .StepsPerWavelengthTet / .LinesPerWavelength / .MinimumStepNumber /
'    .MinimumLineNumber / Mesh.AddAutomeshFixpoint —— 全部不报错但 GetNumberOfMeshCells 纹丝不动。
' ✅ 唯一可控密度通道 = Solver.FrequencyRange 的 Fmax（λ@Fmax 驱动自动网格）：
'    300mm WR62 实测 Fmax 13.6→67,410 | 15.6→106,272 | 17.6→136,344 单元。
'    加密=抬高 Fmax（TD 为脉冲响应 FFT，带外求解不影响带内有效性）。
' ❌ MeshSettings.Set "StepsPerWaveNear","20" —— CST 2026 API，2025 报 Unknown setting
' ❌ MeshSettings.Reset / MeshAdaption3D.Reset —— 2025 无此方法
```

---

## 10. 频域求解器

```vba
' ✅ CST 2025 正确配置
With FDSolver
    .Reset
    .SetMethod "Tetrahedral", "General purpose"
    .OrderTet "Second"
    .SetRecordUnitCellScanFarfield "Auto"
End With

' ✅ 启动（关键！不是 m3d.run_solver()）
FDSolver.Start

' ❌ m3d.run_solver() —— 默认时域，极慢
' ❌ FDSolver.Accuracy / .FrequencyMin / .FrequencyMax / .Samples / .SweepType —— 2026 API
' ❌ .Method "Frequency" —— 只接受 Hexahedral/Hexahedral TLM
```

---

## 11. S 参数导出

```python
# ✅ 唯一可靠方案
from cst.post_processing.s_parameters import export_touchstone

de = ci.DesignEnvironment()
mws = de.open_project(r"E:\path\to\solved_project.cst")

export_touchstone(
    mws,                          # 传 Project 对象，不是 DesignEnvironment！
    r"E:\path\to\output.s1p",
    impedance=50,
    export_type='S',
    format="RI",
    frequency_range="Full",
    renormalize=False
)
# 生成文件：output.s1p.s1p（CST 自动追加后缀）
```

---

## 12. 求解等待

```python
# ✅ 轮询
import time
deadline = time.monotonic() + 900
while m3d.is_solver_running():
    if time.monotonic() > deadline:
        break
    time.sleep(10)
```

---

## 13. 诊断文件

求解后检查这些文件：

| 文件 | 位置 | 用途 |
|------|------|------|
| Model.log | `<project_dir>\Result\Model.log` | 网格数、pass 数、收敛、警告 |
| output.txt | `<project_dir>\Result\output.txt` | 求解过程详细输出 |
| meshrelated.info | `<project_dir>\Result\` | 几何实体统计、端口数 |
| MeshErrorsGraphicalFeedback | `<project_dir>\Result\` | 网格错误 |
