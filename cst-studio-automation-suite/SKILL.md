---
name: cst-studio-automation-suite
description: CST Studio Suite（达索 SIMULIA 电磁仿真软件）自动化助手。当用户要用脚本/宏/MCP 自动驱动 CST 建模、求解、参数扫描出数据集、导出 S 参数或排查 CST 报错时使用。核心面向 CST 2025（Set 前缀 API），并给出 2026 迁移提示。触发词：CST、CST Studio、电磁仿真自动化、FDSolver、add_to_history、Touchstone 导出、S11、参数扫描、批量仿真、RunMacro、Floquet 端口、网格收敛、CST MCP。
---

# CST 电磁仿真自动化助手

整合多个 CST 自动化仓库（实测脚本 + 踩坑经验 + 生态选型）而成的单一决策入口。目标是让助手在帮用户驱动 CST 时，先判版本、再选通路、按阶段推进、用实测写法避开已知死路，而不是凭空编 API。

## 适用与边界

- 适用：用 Python 脚本、VBA 宏或 MCP 连接本机 CST，做建模 / 频域求解 / 参数扫描 / S 参数导出 / 报错定位。
- 主战场为 **CST 2025**（本机已装 2025.1）。CST 只能跑在 Windows；本助手只产出代码、宏、排错与批量方案，**不代跑仿真**——执行由用户在本机完成。
- 无把握的 API 名或安装命令，必须标注"待本机 Help/源码确认"，不得臆造。

## 四步执行路径

> 任何一步拿不准"这个活归谁、用哪个工具、现在能不能用"→ 查 `references/capability-router.md`（逐技能/工具组路由表，含可用性四档：已内联/本机可装/待装待复核/仅登记）。

### 第 1 步 · 定版本（决定 API 写法，最优先）
- **2025**：对象配置多用 **`Set` 前缀方法**（如 `FDSolver.SetMethod`）；`MeshSettings` 无 `Reset`。
- **2026**：多用**直接属性**（如 `FDSolver.Method = ...`、`.FrequencyMin`）。
- ⚠ 多数第三方 MCP（jame-ri、woson-L、ismailakdag 等）按 2026 写，**在 2025 上不兼容**——先确认版本再谈 MCP。详见 `references/cst-2025-api-playbook.md` 与 `references/upstream-ecosystem-snapshot.md`。

### 第 2 步 · 选通路（决策树）
| 场景 | 首选通路 |
|---|---|
| 单结构建模+求解，要稳 | VBA 宏注入（`add_to_history`），Python 只管会话 |
| 数百~数千样本批量出数据集 | `scripts/batch_sweep.py`（断点续跑+指纹守卫） |
| 只做会话连接/自愈/超时 | `scripts/cst_session.py`（COM 单例+文件锁+看门狗） |
| 问操作/查参数含义、要引用出处 | 检索本机 `CST\Documentation` 的 Help（离线，不出本机） |
| 2026 + 想要对话式控制 | MCP（先过版本关，见 `references/mcp-onboarding-checklist.md`） |
| 有 MATLAB 授权 | 走 MATLAB→COM 通道（本包不主用） |

已验证的**三条死路**（别再走）：命令行 `-m macro.bas` 在 2025 实为启动主程序而非跑宏；pywin32 `RunMacro` 报 `Macro not found`；逐对象 COM 建几何报 `Shape does not exist`。

### 第 3 步 · 按 P0→P6 流程推进
P0 查本机 Help → P1 需求转结构化参数清单 → P2 公式/参数扫雷 → P3 单样本建模+网格收敛 → P4 极端参数点先试跑再批量 → P5 三方验证（仿真↔理论↔文献；只有两方才写"趋势参考"）→ P6 汇报/代理模型。

### 第 4 步 · 用实测写法避坑（高频）
- 几何布尔用单冒号引用：`Solid.Subtract "comp:solid1","comp:solid2"`。
- 频域四面体启动走 VBA：`add_to_history("start_fd","FDSolver.Start")`，**不要**用 `m3d.run_solver()`（默认时域，极慢）。等待用 `is_solver_running()` 轮询。
- 导出 `export_touchstone` 传工程对象 `mws`，不传设计环境 `de`。
- Floquet/周期单元：边界需 X/Y 成对；端口贴面/极化/坐标系不匹配会"看着正常但全错"。
- 保存路径**纯英文**（中文路径致 `mws.save` 失败）；重跑前按进程归属判断再决定是否杀进程，不确定=不杀。

## 冲突裁定（务必读）
关于"用哪个求解启动 API"存在两处看似相反的建议，实为不同调用层、不同关注点。**统一口径见 `references/conflict-register.md`**，动手前先看它。

## 环境三条硬约束
1. 必须用 **CST 自带 Python**（`<CST_HOME>\AMD64\python\python.bat`），系统 Python 无法 `import cst`。
2. 路径纯英文。
3. 脚本配置走环境变量 `CST_HOME` / `CST_WORK_DIR`（不再硬编码个人路径）。注意：MCP 生态另有 `CST_INSTALL_DIR` / `CST_PYTHON_EXE`，与脚本的 `CST_HOME` 命名不统一，同一脚本内混用会踩坑。

## 资源地图
- `references/capability-router.md` — 能力路由表：各库技能/工具组归属+可用性四档（**不知道用谁时先查**）
- `references/conflict-register.md` — C1~C6 冲突登记与裁定（**先读**）
- `references/cst-2025-api-playbook.md` — 实测 API 正误对照、死路、网格/Floquet/导出/迁移
- `references/paper-to-sim-workflow.md` — P0~P6 每阶段可执行判据：model_spec 契约、公式扫雷、求解器选型树、17 坑全文、开工/收尾纪律与状态标签、三方验证分级、图文汇报五步
- `references/upstream-ecosystem-snapshot.md` — 8 来源+周边库生态对比、3 处链接勘误
- `references/upstream-install-catalog.md` — 各家前置/安装/环境变量对照/路线图完成度
- `references/mcp-onboarding-checklist.md` — MCP 本机接入清单与共存约定
- `references/installation-checklist.md` — 环境配置与验证 checklist（MCP/py4cst）
- `references/material-database.md` — 材料数据库使用说明（基板/金属/介质）
- `references/mcp-servers-comparison.md` — 4 个 MCP Server 功能/安装/兼容性对比
- `references/py4cst-guide.md` — py4cst 安装与批量仿真示例
- `references/session-management.md` — COM 会话管理详解（锁/自愈/看门狗）
- `scripts/` — 5 个 CST 2025 实测脚本（会话/建模/求解导出/S11 解析/批量扫描），已参数化
- `data/` — 3 个材料库 JSON（基板/金属/介质）
- `ATTRIBUTION.md` — 逐文件来源与改动、许可声明

## 回答要求
- 用户没说 CST 版本时，先问版本再给 API 写法。
- 拿不准的 API/命令标注"待本机确认"，不臆造。
- 不承诺代跑仿真；给的是能本机执行的脚本/宏/排错方案。
