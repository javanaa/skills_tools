# 冲突登记与裁定（conflict-register）

整合多来源时发现的口径冲突，逐条登记并给出裁定。C1 最重要。

## C1 · 求解器启动 API 表面矛盾（已裁定）

**冲突现象**
- 用户仓库 `SKILL.md` 第 4 条 / `troubleshooting.md` / `cst2025-api-cheatsheet.md`：「用 `FDSolver.Start`，不要用 `m3d.run_solver()`，后者默认走时域、极慢」。
- 同仓库 `cross-repo-lessons.md` §3.1（引自 Neil2DP 坑 5）：「`start_solver()` 异步吞真实错误，改用 `run_solver()` 同步 + 轮询 `is_solver_running()`」。

字面相反，AI 取用时可能拿到反建议。

**裁定（脚本源码 + 双方文档原文证据；Help 未逐条复核，结论以源码行为为准）**
两条不矛盾，是**不同调用层、不同关注点**：
1. `FDSolver.Start` 是 **VBA 层**（宏里通过 `add_to_history` 注入执行），关注"**选对频域求解器**"——绕开 `m3d.run_solver()` 默认时域导致极慢的问题。
2. `run_solver()` / `start_solver()` 是 **官方 Python API 层**的方法，关注"**拿到真实错误**"——`start_solver()` 异步会在启动前置失败时只报 `Simulation could not be started. Unknown error`，`run_solver()` 同步能抛出真根因（最常见 `ERROR: No valid excitation sources defined` = 缺端口/激励）。
3. **本包 `scripts/run_simulation.py` 的实际做法把两者统一了**：用 `m3d.add_to_history("start_fd","FDSolver.Start")` 走 VBA 注入启动频域求解，再用 Python 侧 `m3d.is_solver_running()` 轮询等待，最后 `export_touchstone(mws, ...)` 导出。即：**启动选 VBA 的 FDSolver.Start，等待/诊断用 Python 轮询**，两层各司其职，不冲突。

**统一口径（写进 SKILL.md 与 playbook）**
- 在 CST 2025 用脚本驱动频域求解时：**启动一律 `add_to_history(...,"FDSolver.Start")`，不要用 Python 的 `m3d.run_solver()`（默认时域）**。
- 无论用哪层 API 触发，**等待都用 `is_solver_running()` 轮询到 False 再校验产物**；"返回成功 ≠ 求解完成"。
- 若必须用 Python 原生触发，优先同步 `run_solver()` 以拿到真实错误，避免异步 `start_solver()` 吞错误。

## C2 · 网格密度"静默失效 / 唯一旋钮 Fmax"标签
结论（v3.1）：CST 2025 网格密度命令常静默失效，实际主控旋钮是 Fmax。已在 `troubleshooting.md` 与 playbook 标注，需确认速查表条目已带此标签。

## C3 · 弹窗自动 dismiss vs 交给用户 UI
valenZW/cst-sim-agent 提供 `cst_detect_popups` / `cst_dismiss_popup`（自动关弹窗）。这与"遇到弹窗交给用户在本机 UI 处理"的策略冲突。**裁定**：接入 MCP 时重裁——批量无人值守可启用自动 dismiss，但必须在日志留痕；单样本/调试期默认交用户，避免静默吞掉真错误信号。

## C4 · 环境变量命名不统一
- 本包脚本 / `cst_session.py`：`CST_HOME` + `CST_WORK_DIR`。
- v3 `installation-checklist.md` 文档正文推荐 `CST_PATH`（**与代码实际读的 `CST_HOME` 冲突**——整合时统一为 `CST_HOME`）。
- jame-ri/cst2026-skill-mcp：`CST_INSTALL_DIR` + `CST_PYTHON_EXE` + `CST_MACRO_ROOT` + `CST_DESIGN_ENV_EXE`。
- valenZW/cst-sim-agent：仅 `CST_INSTALL_DIR`。
**裁定**：脚本层统一 `CST_HOME`/`CST_WORK_DIR`；接入 MCP 时按其官方变量名单独配，**不要把两套写进同一个脚本**。对照表见 `upstream-install-catalog.md`。

## C5 · 上游链接勘误（3 处）
用户仓库文档内 3 个仓库链接失效，已核实真实 owner（见 `upstream-ecosystem-snapshot.md`）：py4cst 真实 owner、orchestrator 库用户名/仓库名连字符写反、一个不存在的 mcp 库。

## C6 · v1 与 v3 重复抢触发
- v1（cst-studio-automation）4 份 references 中 2 份与 v3 **md5 完全相同**、2 份仅措辞级分叉；v3 另有 6 份独有文档。
- 两个 SKILL.md 的 description 都以"CST 自动化"起头，同装会互抢触发。
**裁定**：整合包**只保留 v3 内容**，v1 不纳入（本 suite 已是合并版）。若用户仓库要瘦身，建议删 v1 或只留一行指向 v3。

## 待复核（不臆造）
- ismailakdag/cst-studio-mcp 的安装命令：本轮未取到 README 原文核对，标"待复核"，不得凭印象填。
