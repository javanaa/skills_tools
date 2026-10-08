# 各上游仓库安装要求与路线图（upstream-install-catalog）

> 依据 2026-10-02 本地克隆的仓库文件核实。环境变量名以逐字grep为准；标注"待复核"的条目不得当作可执行命令。

## 一、环境变量命名对照（最容易踩的坑）

| 来源 | 变量名 | 说明 |
|---|---|---|
| 本包 scripts（含 cst_session.py） | `CST_HOME`（安装目录）+ `CST_WORK_DIR`（工作目录） | 代码实测读这两个 |
| javanaa v3 installation-checklist.md 文档 | `CST_PATH` + `CST_WORK_DIR` | ⚠ 文档写 `CST_PATH`，与代码读的 `CST_HOME` 不一致——以代码为准，文档待上游修正 |
| jame-ri/cst2026-skill-mcp | `CST_INSTALL_DIR` + `CST_PYTHON_EXE` + `CST_MACRO_ROOT` + `CST_DESIGN_ENV_EXE`（共 4 个） | 未设时可自动探测 |
| valenZW/cst-sim-agent | `CST_INSTALL_DIR`（仅此一个） | |
| MuziIsabel/CST-Studio-Suite-Help | 无环境变量；自动探测本机 Help，`--help-root` 参数可覆盖路径 | |

**纪律：两套命名体系不要混写进同一个脚本/配置文件。**

## 二、逐家安装要点

### javanaa/skills_tools（本包脚本基底，MIT）
- 前置：Windows + CST 2025 + **CST 自带 Python**（`<CST_HOME>\AMD64\python\python.bat`；系统 Python 无法 `import cst`）；纯英文路径。
- 动作：clone 后把 skill 目录放进 agent 技能目录；或直接用 scripts/（先设 `CST_HOME`/`CST_WORK_DIR`）。
- 路线图：README 自列未完成项含"MCP 实际试用与兼容性验证、py4cst 批量模板、本地 Help 检索验证、演示截图、Release 发布"。
- 演示资源：**无演示截图**（可信度打折，结论以实测文本为准）。

### Neil2DP/cst-paper-sim-skills（MIT，10 skill）
- 形态：10 个 SKILL.md 覆盖论文→仿真→验证→提炼全链路，CST 2025 真机实测。
- 前置：支持 SKILL.md 的 agent；无强制外部依赖。
- 独特资产：17 条实测坑、场监视器硬约定、结果状态标签 7 类、开工/收尾纪律（已吸收进 playbook 与本包冲突登记）。

### jame-ri/cst2026-skill-mcp（1444 文件，含官方文档本地副本+宏索引）
- 面向 **CST 2026**（属性式 API）；2025 用户**只有文档检索/宏索引部分可用**。
- 启动：需上述 4 个环境变量，未设时自动探测；README 提及 `run-cst2026-mcp.cmd`（具体命令**待复核**，接入前以本机 README 原文为准）。
- 配置示例覆盖 Codex/Claude/Cursor 三家。

### valenZW/cst-sim-agent（Apache-2.0，Claude Code 插件）
- 依赖：`mcp` + `pywin32`；环境变量 `CST_INSTALL_DIR`。
- 安装：`claude plugin marketplace add <本地目录>` → 重启 → `/plugins` 确认 → 出现 `cst_*` 工具（本包本地 grep 到 30+ 个 `cst_*` 工具名，如 cst_connect/cst_execute_vba/cst_is_solver_running/cst_dismiss_popup 等）。
- 机制：工具白名单防 LLM 编造 VBA 方法名。

### MuziIsabel/CST-Studio-Suite-Help（MIT）
- 原理：对本机 CST Documentation 建 SQLite FTS5 索引，离线检索问答带引用出处；Cursor/Codex/Claude Code 通用。
- 本机可用：`<CST安装目录>\Documentation` 有全套 PDF，此方案可直接落地。

### xinhong-li999/cst-antenna-skill
- 面向 **CST 2026** 天线；5 个 SKILL.md + 724KB VBA 对象参考（408 对象）；**无可执行脚本**。

### xixiheni/matlab-cst-simulation-skill
- 通道：MATLAB→COM（PowerShell），**依赖 MATLAB 授权**；本包不主用，其"最小建模信息集"要求已并入 playbook §9。

### ismailakdag/cst-studio-mcp
- 自述 180+ 工具、覆盖 CST 2024–2026；安装走 docs/AGENT_SETUP.md（本轮未核原文，**待复核**，不得猜命令）。

## 三、已停更/风险提示
- zhaosih/ChatEM：约一年未更新，引用需注明时效。
- JustArri/py4cst：上游仓库文档链接写错 owner（见 conflict-register C5）。
- 除 javanaa/Neil2DP 外，各家对 CST 2025 兼容性**均未声明**——2025 用户接任何 MCP 前先过版本关。
