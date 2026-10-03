---
name: cst-studio-automation-v3
description: CST Studio Suite 自动化全栈工具集 v3.1——整合官方Python API脚本/VBA宏/MCP Server选型，含5个独立可运行脚本、10份参考文档、3个材料数据库。基于W1实战验证（CST2025）+ 7个外部CST仓库对照吸收。面向电磁超材料参数化建模、批量仿真与数据集生成。当用户需要自动化CST建模、批量跑仿真、用Python控制CST时使用。
version: 3.1
---

# CST Studio Suite 自动化全栈工具集

## 概述

本 Skill 整合了 **官方 Python API 脚本**（实测验证）、**VBA 宏**（传统参数化）、**MCP Server**（AI 对话控制）和 **py4cst**（第三方封装）四类工具，提供从单结构建模到批量数据集生成的全流程自动化能力。

**核心资产**：
- 5个独立可运行 Python 脚本（`scripts/`）
- 10份参考文档（`references/`）
- 3个材料数据库 JSON（`data/`）
- 基于 W1 实战验证的 CST 2025 正确 API 写法

**适用场景**：
- 参数化建模（超材料单元、天线、滤波器）
- 批量仿真与数据集生成（数百至数千样本）
- AI 对话式控制 CST
- Python 后处理与闭环优化

---

## 快速开始（3步跑通）

> 以下脚本基于 CST 2025.1 实测验证，必须用 CST 自带 Python 运行。

### Step 1：环境确认
```powershell
# 必须用 CST 自带 Python，不能用系统 Python
& "<CST安装目录>\AMD64\python\python.bat" --version
```

### Step 2：一键建模+仿真+导出
```powershell
cd <本skill目录>\scripts
& "<CST安装目录>\AMD64\python\python.bat" run_simulation.py `
  --work-dir "<工作目录>" `
  --project "W1_benchmark" `
  --freq-min 2 --freq-max 18
```

### Step 3：解析 S11
```powershell
& "<CST安装目录>\AMD64\python\python.bat" parse_s11.py `
  --input "<工作目录>\W1_benchmark.s1p" `
  --output "S11_result.csv"
```

---

## 脚本说明（scripts/）

| 脚本 | 功能 | 关键参数 |
|------|------|----------|
| `cst_session.py` | 会话管理：COM单例锁/环境自愈/懒连接/看门狗 | 作为模块导入 |
| `build_unitcell.py` | 一键构建双环嵌套开口方环吸波体 | --P --L1 --L2 --w1 --w2 --g1 --g2 --h |
| `run_simulation.py` | 建模+频域四面体求解+Touchstone导出 | --work-dir --project --freq-min --freq-max |
| `parse_s11.py` | 解析 .s1p 文件，计算吸收率，输出CSV | --input --output --threshold |
| `batch_sweep.py` | 参数扫描批量仿真，支持断点续跑 | --param-file --work-dir --resume |

**所有脚本独立可运行，不依赖作者私有模块。**

---

## 工具选型决策

```
你要做什么？
├─ 单结构基准建模（W1）
│   └─ → scripts/build_unitcell.py 或 VBA 宏（最稳定）
├─ 批量参数扫描 / 生成数据集（W3–W6）
│   ├─ 想要 Python 脚本控制 → scripts/batch_sweep.py 或 py4cst
│   └─ 想要 AI 对话控制 → cst-mcp（square ring 模板）或 cst-studio-mcp
├─ AI 对话式全流程控制（长期）
│   └─ → cst-studio-mcp（180+ 工具最全面）
└─ 复杂系统 / 场路协同
    └─ → CST Studio Orchestrator
```

---

## 实战验证：CST 2025 正确 API（W1 经验）

### 三条已验证的死路（不要重试）
1. 命令行 `-m macro.bas -q` → CST 2025 的 -m 是启动 MWS，不是运行宏
2. pywin32 COM `RunMacro(path)` → "Macro not found"
3. pywin32 COM 逐对象几何 → "Shape does not exist"

### 成功通路
```
cst.interface → DesignEnvironment → new_mws/open_project → model3d
→ add_to_history(name, VBA代码) → 建模/设置/求解
→ export_touchstone(mws, path) → S参数导出
```

### 关键正确写法
```vba
' 几何：单冒号语法
Solid.Subtract "comp:solid1", "comp:solid2"

' 求解器：FDSolver.Start（非 m3d.run_solver()，后者默认时域极慢）
With FDSolver .Reset .SetMethod "Tetrahedral","General purpose" .OrderTet "Second" End With
FDSolver.Start

' 导出：传 mws(Project) 不传 de
export_touchstone(mws, path, impedance=50, export_type='S', format="RI")

' 网格（CST 2025 无 Reset；⚠️ 密度类命令经自动化通道静默失效，唯一旋钮是 Fmax，见 troubleshooting）
With MeshSettings .SetMeshType "Unstr" End With
With MeshAdaption3D .SetType "HighFrequencyTet" .SetAdaptionStrategy "ExpertSystem" End With
' 网格加密 = 抬高 Solver.FrequencyRange 的 Fmax（λ@Fmax 驱动自动网格），不要试密度命令

' 边界 + Floquet 端口
With Boundary .Xmin "unit cell" .Zmin "electric" .Zmax "expanded open" End With
With FloquetPort .Reset .Port "Zmax" .SetNumberOfModesConsidered "1" End With
```

> 完整 API 速查见 [references/cst2025-api-cheatsheet.md](references/cst2025-api-cheatsheet.md)

---

## 应用示例（通用参数化模板）

**结构**：双环嵌套开口方环 + RO4003C 介质（εr=3.55, tanδ=0.0027）+ 铜背板（35μm）
**频段**：2–18 GHz（可自定义）
**示例参数**：见 build_unitcell.py 默认值（可自行修改）

- `build_unitcell.py` 内置双环嵌套单元模板，与吸波超材料单元结构直接匹配
- `batch_sweep.py` 支持参数扫描+断点续跑，适合生成 500–1000+ 样本数据集
- `parse_s11.py` 自动计算吸收率，可直接用于训练数据标注

---

## 分阶段落地建议

| 阶段 | 推荐工具 | 理由 |
|------|----------|------|
| **W1 基准建模** | scripts/build_unitcell.py + VBA 宏 | 已验证通路，别中途换工具 |
| **W2 标定+收敛** | scripts/run_simulation.py + 手动检查 | 单结构微调 |
| **W3–W6 批量数据集** | scripts/batch_sweep.py | 500–1000+ 样本必须自动化 |
| **W7–W10 代理模型** | Python + 导出的 CSV | 在线数据生成 / 主动学习 |
| **长期** | cst-studio-mcp | AI 对话控制，提升迭代效率 |

---

## 详细参考文档

| 文档 | 内容 |
|------|------|
| [cst2025-api-cheatsheet.md](references/cst2025-api-cheatsheet.md) | CST 2025 API 速查（✅正确/❌错误/⚠️注意） |
| [floquet-port-guide.md](references/floquet-port-guide.md) | Floquet 端口完整配置指南 |
| [session-management.md](references/session-management.md) | COM 会话管理详解（锁/自愈/看门狗） |
| [troubleshooting.md](references/troubleshooting.md) | 故障排查（按报错分类） |
| [cross-repo-lessons.md](references/cross-repo-lessons.md) | ★7仓库对照吸收经验库（建模/求解/端口/导出/进程纪律） |
| [material-database.md](references/material-database.md) | 材料数据库使用说明 |
| [mcp-servers-comparison.md](references/mcp-servers-comparison.md) | 4个 MCP Server 功能/安装/兼容性对比 |
| [py4cst-guide.md](references/py4cst-guide.md) | py4cst 安装与批量仿真示例 |
| [vba-macro-best-practices.md](references/vba-macro-best-practices.md) | VBA 宏最佳实践（含 W1 三轮修复记录） |
| [installation-checklist.md](references/installation-checklist.md) | 环境配置与验证 checklist |

---

## 材料数据库（data/）

| 文件 | 内容 |
|------|------|
| `substrates.json` | 基板材料（RO4000系列/FR4/RT系列等） |
| `common_metals.json` | 金属材料（铜/金/铝/银等，含电导率） |
| `common_dielectrics.json` | 介质材料（石英/蓝宝石/硅等） |

使用方式：脚本启动时自动加载，也可手动扩展新材料。

---

## 注意事项

1. **必须用 CST 自带 Python**：`<CST安装目录>\AMD64\python\python.bat`，系统 Python 无法 import cst
2. **纯英文路径**：中文路径导致 `mws.save` 失败
3. **export_touchstone 传 mws 不传 de**：传 de 会失败
4. **FDSolver.Start 而非 m3d.run_solver()**：后者默认时域，极慢
5. **重跑前清理 CST 进程需先判归属**：确认无用户手动 GUI 会话/其他并行会话再杀
   （`taskkill /IM CST* /F /T` 前先查 `Get-Process | Where-Object { $_.Name -like 'CST*' }`，
   不确定 = 不杀，见 cross-repo-lessons.md §6）
6. **CST 2025 vs 2026 API 差异**：2025 用 Set 前缀方法，2026 用直接属性
7. **第三方 MCP Server 均需验证兼容性**：cst-studio-mcp 按 2026 API 写，2025 不兼容
8. **批量仿真前务必先做单样本验证和网格收敛**

---

## 信息来源

- 官方 Python API：CST Studio Suite 2023+ 内置（`<CST安装目录>\AMD64\python_cst_libraries`）
- cst-mcp: https://github.com/AndersOnLin4/cst-mcp
- cst-studio-mcp: https://github.com/ismailakdag/cst-studio-mcp
- py4cst: https://github.com/Arri0/py4cst
- W1 实战经验：2026-09-30 至 2026-10-01 自主控制 CST 2025 全流程验证
- 7 仓库对照吸收（2026-10-02，详见 cross-repo-lessons.md）：
  - Neil2DP/cst-paper-sim-skills（CST 2025 真机实测 17 坑）
  - valenZW/cst-sim-agent（Claude Code 插件避坑清单）
  - jame-ri/cst2026-skill-mcp（CST Python 自动化知识库）
  - MuziIsabel/CST-Studio-Suite-Help（本地 Help 离线检索）
  - xixiheni/matlab-cst-simulation-skill、xinhong-li999/cst-antenna-skill、Albert-tru/AntennaResearchAI-（低价值/待验证）