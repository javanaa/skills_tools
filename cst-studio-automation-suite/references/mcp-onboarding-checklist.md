# MCP 本机接入清单（mcp-onboarding-checklist）

> 写给"以后在装了 CST 2025 的本机接 MCP"的场景。上游路线图挂着的那条"MCP 实际试用与兼容性验证"照此执行。云端/未装 CST 的机器只做资料准备，不做接入。

## 第 0 关 · 版本关（不过此关后面全免谈）
1. 确认本机 CST 版本（看主程序文件属性或 Help 首页）。
2. **2025 用户**：候选 MCP 必须先验证它是 2025 写法（Set 前缀）还是 2026 写法（直接属性）。生态现状：valenZW/jame-ri/ismailakdag/woson-L 等按 2026 或"2024–2026 自称"编写，**默认视为 2025 不兼容**，逐个冒烟后才可信。
3. 只有 Help/宏索引/文档检索类（如 MuziIsabel）不碰 API，2025 可直接用。

## 第 1 关 · 接入前准备
- 另存一份**基线工程**（.cst 副本）——接入新工具可能写坏工程，先留退路。
- 核对安装命令来源：**只用各仓库 README 原文里逐字核对过的命令**；本清单标注"待复核"的不许猜。
- 已核对可抄的两家：
  - valenZW/cst-sim-agent：`pip install mcp pywin32` → 设 `CST_INSTALL_DIR` → Claude Code: `claude plugin marketplace add <本地目录>` → 重启 → `/plugins` 确认。
  - jame-ri/cst2026-skill-mcp：设 `CST_INSTALL_DIR`/`CST_PYTHON_EXE`/`CST_MACRO_ROOT`/`CST_DESIGN_ENV_EXE`（或其自动探测）→ 按其 README 用 `run-cst2026-mcp.cmd` 启动。
- ismailakdag/cst-studio-mcp：安装命令**待复核**（需打开其 docs/AGENT_SETUP.md 逐字核对后再填这里）。

## 第 2 关 · 冒烟三步（接完必做，顺序执行）
1. **枚举工具对数**：让 agent 列出该 MCP 暴露的工具清单，数量与 README 自述不符 → 装错版本或配置错，停。
2. **三个不开求解器的安全工具**：`connect`（连上现有 DE）→ `get_model_tree`/查询类（读几何）→ `get_messages`/日志读取类。任何一步异常即断开排查，不许带病跑。
3. **最小闭环**：新建空工程 → 建一个砖块 → 窄带（如 1 个点频）频域求解 → 导出 S 参数 → 关工程。产出文件存在且数值非 NaN/全零才算通。

## 第 3 关 · 与脚本共存的硬约定
- **会话单主人**：COM 会话同一时刻只能有一个主人——MCP 占着 CST 时不要并行跑 batch_sweep 脚本，反之亦然（两边都会抢会话导致随机失败）。
- **双看门狗禁同开**：本包 cst_session.py 的环境自愈/进程守护 + 外部工具的自动重试（jame-ri/valenZW 类）同开会形成重试风暴。二选一。
- **弹窗策略**（C3 裁定）：批量无人值守可启用自动 dismiss（如 cst_dismiss_popup），但必须在日志留痕；调试期默认交给用户 UI 处理，避免静默吞错。
- **杀进程纪律**：重跑前先看进程归属（有无用户手动开的 GUI 会话、有无其他并行任务），不确定 = 不杀。

## 第 4 关 · 2025 特有的兼容降级路径
- MCP 工具在 2025 报方法不存在 → 优先改走"VBA 注入"类通用工具（execute_vba/add_to_history 等价物），绕开 2026 属性式封装。
- 完全不通时的保底组合：本包 scripts（2025 实测）做主力，MCP 只做查询/展示类辅助。

## 验证记录模板（每次接入后填写）
```
仓库 / commit 或版本：
CST 版本：
冒烟三步结果：1 工具数 __/__（自述） 2 安全工具 pass|fail 3 最小闭环 pass|fail
报错摘要：
结论：可用 / 仅查询可用 / 不兼容
```
