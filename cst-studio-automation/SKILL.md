---
name: cst-studio-automation
description: '[DEPRECATED v1] CST Studio Suite 自动化工具选型指南。已被 cst-studio-automation-v3 取代，v3 含5个可运行脚本+9份参考+3个材料数据库+W1实战验证。仅保留作历史参考。'
---

> ⚠️ **DEPRECATED — 本版本为 v1 选型文档版，无代码。**
> 
> 推荐使用 **[cst-studio-automation-v3](../cst-studio-automation-v3/)**：
> - 5个独立可运行 Python 脚本（会话管理/建模/求解/解析/批量扫描）
> - 9份参考文档（CST2025 API速查/Floquet端口/故障排查/材料库等）
> - 3个材料数据库 JSON
> - 基于 W1 实战验证的 CST 2025 正确 API 写法
> - 含三条已验证死路，避免重试

# CST Studio Suite 自动化工具集（v1 · Legacy）

## 概述

本 Skill 汇总了当前可用的 CST Studio Suite 自动化工具，包括 **MCP Server**（AI 直接控制 CST）、**Python 库**（脚本自动化）、**VBA 宏**（传统参数化）和**官方 Python API**，帮助研究者根据场景快速选型、安装与落地。

**适用场景**：
- 参数化建模（超材料单元、天线、滤波器等）
- 批量仿真与数据集生成（数百至数千样本）
- AI 对话式控制 CST（自然语言 → 建模 / 求解 / 提取结果）
- Python 后处理与闭环优化

**目标用户**：使用 CST 进行电磁仿真的研究者，尤其是需要大规模参数扫描和数据驱动设计的场景。

---

## 工具全景

| 类别 | 工具 | 核心优势 | 适用阶段 |
|---|---|---|---|
| MCP Server | **cst-mcp** (AndersOnLin4) | 内置 square ring 吸波体 + Floquet 端口一键模板 | 快速建模、AI 对话控制 |
| MCP Server | **cst-studio-mcp** (ismailakdag) | 180+ 工具，最全面，支持 CST 2024–2026 | 全流程自动化 |
| MCP Server | **CST Studio Orchestrator** (guardianer9) | 场路协同、PCB/SI 功能强 | 复杂系统级仿真 |
| MCP Server | **mcp-cst-studio** (rfingadam) | 轻量，天线/RF 为主 | 天线设计 |
| Python 库 | **py4cst** (Arri0) | VBA 方法的 Python 封装，`pip install` 即用 | 批量脚本、数据集生成 |
| 官方 API | **CST Python** | CST 内置，2023+ 支持，与 VBA 同源 | 内部脚本、后处理 |
| 传统 | **VBA 宏** | 最成熟，学术圈主流，CST 原生 | 基准建模、参数化 |

---

## 快速选型决策

```
你要做什么？
├─ 单结构基准建模（W1）
│   └─ → VBA 宏（最稳定，已有 W1 宏可直接用）
├─ 批量参数扫描 / 生成数据集（W3–W6）
│   ├─ 想要 Python 脚本控制 → py4cst
│   └─ 想要 AI 对话控制 → cst-mcp（有 square ring 模板）或 cst-studio-mcp
├─ AI 对话式全流程控制（长期）
│   └─ → cst-studio-mcp（180+ 工具最全面）
└─ 复杂系统 / 场路协同
    └─ → CST Studio Orchestrator
```

---

## 应用示例（通用参数化模板）

**结构**：双环嵌套开口方环 + RO4003C 介质（εr=3.55）+ 铜背板  
**频段**：2–18 GHz（可自定义）

- **cst-mcp** 内置的 square ring absorber + Floquet port 一键模板，与本结构高度匹配，可能直接省去手写宏的部分工作
- **py4cst** 可在现有 VBA 宏基础上扩展为批量参数扫描脚本（改参数 → 跑 → 导出 S 参数循环）
- **cst-studio-mcp** 的 180+ 工具覆盖几何 / 材料 / 端口 / 求解器 / 结果提取全流程，适合大规模自动化
- 所有工具均需 CST 已安装且 license 可用（本机 CST 2025.1 装在 `<CST安装目录>\`）

---

## 分阶段落地建议

| 阶段 | 推荐工具 | 理由 |
|---|---|---|
| **W1 基准建模** | VBA 宏 | 已写好并修复三轮，别中途换工具 |
| **W2 标定+收敛** | VBA 宏 + 手动 | 单结构微调，宏足够 |
| **W3–W6 批量数据集** | py4cst 或 cst-mcp | 500–1000+ 样本必须自动化，手点不现实 |
| **W7–W10 代理模型** | py4cst + Python | 在线数据生成 / 主动学习 / 闭环优化 |
| **长期** | cst-studio-mcp | AI 对话控制，提升迭代效率 |

---

## 详细参考文档

| 文档 | 内容 |
|---|---|
| [MCP Server 详细对比](references/mcp-servers-comparison.md) | 4 个 MCP Server 的功能、安装、兼容性、优缺点逐项对比 |
| [py4cst 使用指南](references/py4cst-guide.md) | 安装、基本用法、与 VBA 的对应关系、批量仿真示例 |
| [VBA 宏最佳实践](references/vba-macro-best-practices.md) | 基于 W1 宏三轮修复经验总结的避坑指南 |
| [安装配置清单](references/installation-checklist.md) | 环境变量、依赖、验证步骤的 checklist |

---

## 注意事项

1. 所有 MCP Server 均为**第三方开源项目**，使用前需验证与本地 CST 版本（2025.1）的兼容性
2. **不建议在 W1 基准建模阶段中途换工具**，先跑通 VBA 宏拿到第一条 S11 曲线
3. MCP Server 配置通常需要 `CST_PATH`、`CST_WORK_DIR` 等环境变量
4. 批量仿真前务必先做**单样本验证**和**网格收敛**，再放大规模
5. 第三方工具的更新可能滞后于 CST 版本，遇到不兼容回退到 VBA 宏

---

## 信息来源

- cst-mcp: https://github.com/AndersOnLin4/cst-mcp
- cst-studio-mcp: https://github.com/ismailakdag/cst-studio-mcp
- CST Studio Orchestrator: https://github.com/guardianer9/debug-cst-studio-orchestrator-mcp
- mcp-cst-studio: https://github.com/rfingadam/mcp-cst-studio
- py4cst: https://github.com/Arri0/py4cst
- CST 官方 Python API: CST Studio Suite 2023+ 内置

> 本 Skill 仅汇总文档与配置说明，不包含第三方工具的源代码。安装与使用请参考各项目官方仓库。