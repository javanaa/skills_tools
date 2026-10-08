# MCP Server 详细对比

> 汇总 4 个可让 AI 直接控制 CST Studio Suite 的 MCP Server，按功能、安装、兼容性、优缺点逐项对比。
> 调研日期：2026-09-30

---

## 一、总览对比表

| 维度 | cst-mcp<br/>(AndersOnLin4) | cst-studio-mcp<br/>(ismailakdag) | CST Studio Orchestrator<br/>(guardianer9) | mcp-cst-studio<br/>(rfingadam) |
|---|---|---|---|---|
| **GitHub** | AndersOnLin4/cst-mcp | ismailakdag/cst-studio-mcp | guardianer9/debug-cst-studio-orchestrator-mcp | rfingadam/mcp-cst-studio |
| **语言** | Python | Python | Python | Python |
| **CST 版本** | 未明确（近期项目） | 2024–2026 | 未明确 | 未明确 |
| **工具数量** | 未明确（聚焦吸波体） | **180+** | 未明确（系统级） | 未明确（轻量） |
| **系统要求** | Windows | Windows 10/11, Python 3.10+ | Windows | Windows |
| **License** | 需 CST 已授权 | 需 CST 已授权 | 需 CST 已授权 | 需 CST 已授权 |
| **维护活跃度** | 2026-09 仍在更新 | 2026-09 活跃 | 2026-08 发布 | 2026-08 发布 |

---

## 二、逐项详解

### 1. cst-mcp (AndersOnLin4) ⭐ 与方环吸波单元最匹配

**核心亮点**：
- **One-shot unit-cell builder**：内置 MIM 吸波体堆叠模板，支持 square ring / patch / circular ring
- **自动生成 Floquet 端口**：配置 1 mode，脚本化完成，无需 GUI 点击
- 号称比手动操作快约 **50×** per point
- 可对接 Claude / Cursor / DSH 等 AI Agent

**与吸波超材料单元结构的匹配度**：
- 目标结构 = square ring（方环）+ 介质 + 背板 + Floquet 端口 → **几乎完全匹配**
- 双环嵌套可能需要在模板基础上扩展第二个环
- 适合批量生成 unit-cell 样本

**安装要点**：
- 需要配置 CST 安装路径和工作目录环境变量
- 建议在独立 Python 虚拟环境中安装

**潜在风险**：
- 项目较新，文档和社区支持可能不完善
- 双环嵌套结构是否开箱即用需验证

---

### 2. cst-studio-mcp (ismailakdag) ⭐ 最全面

**核心亮点**：
- **180+ 结构化 MCP 工具**：覆盖 workflows / geometry / antennas / solvers / results / PCB 等
- 支持打开工程、建几何、设材料和端口、跑求解器、读 S 参数和远场、生成设计报告
- Python-first，明确支持 CST 2024–2026
- 入口命令 `cst-studio-mcp`

**与吸波超材料单元结构的匹配度**：
- 工具最全，几何 / 材料 / 端口 / 求解 / 结果提取全流程覆盖
- 没有专门的吸波体模板，但可用通用几何工具搭建双环结构
- 适合作为长期主力工具

**安装要点**：
```bash
git clone https://github.com/ismailakdag/cst-studio-mcp.git
cd cst-studio-mcp
python -m venv venv
# 激活 venv 后安装依赖
```
- 环境变量：`CST_PATH`（CST 安装路径）、`CST_WORK_DIR`（工作目录）

**潜在风险**：
- 180+ 工具学习曲线较陡
- 需要验证与 CST 2025.1 的具体兼容性

---

### 3. CST Studio Orchestrator (guardianer9)

**核心亮点**：
- 开源 MCP server，把 CST 变成统一的 AI 可控仿真环境
- 支持 3D 电磁建模、天线和 RF 工作流、求解器设置、结果提取
- **PCB/SI 辅助功能**：信号完整性相关工具
- **场路协同**：直接控制 CST Design Studio schematic，做场路联合仿真

**与吸波超材料单元结构的匹配度**：
- 功能偏系统级和 PCB/SI，纯超材料 unit-cell 仿真不是其核心场景
- 场路协同功能对纯电磁仿真暂时用不上
- 适合未来扩展到电路级或系统级仿真

**潜在风险**：
- 仓库名含 "debug"，可能是开发/调试版本
- 超材料场景的文档和示例可能较少

---

### 4. mcp-cst-studio (rfingadam)

**核心亮点**：
- 轻量 MCP server，面向天线设计、RF/微波仿真、PCB 布局
- 需要 `CST_PATH` 和 `CST_WORK_DIR` 环境变量
- Connected Mode：需要 CST 已安装

**与吸波超材料单元结构的匹配度**：
- 天线为主，超材料吸波体不是核心场景
- 功能相对基础，适合简单结构

**潜在风险**：
- 功能可能不如 cst-studio-mcp 全面
- 超材料相关工具和模板可能缺失

---

## 三、选型建议

| 优先级 | 工具 | 理由 |
|---|---|---|
| **第一候选** | cst-mcp (AndersOnLin4) | square ring + Floquet 模板与吸波单元结构直接匹配，上手最快 |
| **第二候选** | cst-studio-mcp (ismailakdag) | 180+ 工具最全面，长期可扩展，版本兼容性明确 |
| **备选** | CST Studio Orchestrator | 场路协同强，但超材料不是核心场景 |
| **不推荐** | mcp-cst-studio (rfingadam) | 天线为主，功能较基础 |

**建议策略**：
1. 先用 VBA 宏跑通基准模型（不换工具）
2. 批量数据集开始前，花 1–2 天分别试用 cst-mcp 和 cst-studio-mcp，各建一个简单 square ring 验证兼容性
3. 选定一个作为批量数据集主力工具，另一个留作备选
4. 把试用结果写回本文件的「验证记录」 section

> ⚠ **版本关提醒**：多数第三方 MCP 按 CST 2026 API 编写，本机 2025 需先验证兼容性再接入（见 mcp-onboarding-checklist.md 第 0 关）。

---

## 四、验证记录（待补充）

> 实际安装试用后在此记录：版本兼容性、安装坑、功能验证结果、性能表现。

| 日期 | 工具 | CST版本 | 验证内容 | 结果 | 备注 |
|---|---|---|---|---|---|
| — | — | — | — | — | — |

---

## 信息来源

- https://glama.ai/mcp/servers/AndersOnLin4/cst-mcp
- https://glama.ai/mcp/servers/ismailakdag/cst-studio-mcp
- https://lobehub.com/mcp/guardianer9-debug-cst-studio-orchestrator-mcp
- https://lobehub.com/mcp/rfingadam-mcp-cst-studio
