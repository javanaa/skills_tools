<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0ea5e9,50:14b8a6,100:22c55e&height=190&section=header&text=skills_tools&fontSize=52&fontColor=ffffff&animation=fadeIn&desc=AI%20Agent%20Reusable%20Skills%20Collection&descSize=19&descAlignY=58" width="100%"/>

![Version](https://img.shields.io/badge/version-1.5-0ea5e9?style=for-the-badge)
![AI Agent](https://img.shields.io/badge/AI-Agent%20Skills-14b8a6?style=for-the-badge)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-22c55e?style=for-the-badge)
![Made with Markdown](https://img.shields.io/badge/Made%20with-Markdown-64748b?style=for-the-badge)

</div>

## 🧠 Skills · 技能一览

<div align="center">

| &nbsp; | Skill | 一句话简介 | Status |
| :---: | :--- | :--- | :---: |
| 🧠 | **[five-brain-council](five-brain-council/)** | 五人智囊天团：证据驱动的科研批判性评审（选题 / 仿真 / PINN / 超材料 / 论文审查 / 模拟答辩） | ![Ready](https://img.shields.io/badge/Ready-%E2%9C%93-success?style=flat-square) |
| 🛠️ | **[cst-studio-automation-suite](cst-studio-automation-suite/)** | CST 自动化全栈整合包（合并版）— 官方 Python API 脚本 / VBA 宏 / MCP Server 选型 + 7 仓库对照吸收，含 5 个可运行脚本、17 份参考文档、3 个材料数据库，基于 W1 实战验证（CST 2025） | ![Ready](https://img.shields.io/badge/Ready-suite-success?style=flat-square) |
| 🛠️ | **[cst-studio-automation-v3](cst-studio-automation-v3/)** | CST 自动化全栈工具集 v3.1（旧版，已被 suite 合并） | ![Legacy](https://img.shields.io/badge/Legacy-v3.1-lightgrey?style=flat-square) |
| 📚 | **[cst-studio-automation](cst-studio-automation/)** | CST 自动化工具集 v1（旧版，文档版无代码，已被 suite 合并） | ![Legacy](https://img.shields.io/badge/Legacy-v1-lightgrey?style=flat-square) |

</div>

> 💡 每个 skill 的**详细触发条件、使用方法、参考文档**见对应目录下的 `SKILL.md`。
>
> ⚡ **推荐使用 `cst-studio-automation-suite`**：v3.1 与 v1 的整合合并版，含实测可运行脚本、CST 2025 API 速查、17 份参考文档与 7 仓库对照吸收经验库（`cross-repo-lessons.md`）。v3.1 / v1 仅保留作历史参考。

## 📦 Installation · 安装

<details>
<summary><b>点击展开安装步骤</b></summary>

**方式一：界面上传**

1. 在支持 Skills 机制的 AI Agent 中，打开「技能」面板
2. 选择「上传本地文件夹 / zip」，选中对应 skill 目录

**方式二：放入目录**

将 skill 文件夹放入 Agent 工作空间的 `.user_skills` 目录：

```text
workspace/.user_skills/
├── five-brain-council/              # 科研评审
│   ├── SKILL.md
│   └── references/
├── cst-studio-automation-suite/     # CST 自动化（推荐，整合合并版）
│   ├── SKILL.md
│   ├── scripts/    (5 个可运行 Python 脚本)
│   ├── references/ (17 份参考文档，含 cross-repo-lessons.md)
│   └── data/       (3 个材料数据库 JSON)
├── cst-studio-automation-v3/        # CST 自动化 v3.1（旧版，Legacy）
│   ├── SKILL.md
│   └── ...
└── cst-studio-automation/           # CST 自动化 v1（旧版，Legacy）
    ├── SKILL.md
    └── references/
```

**CST suite 脚本运行要求**：必须使用 CST 自带 Python（如 `<CST安装目录>\AMD64\python\python.bat`），系统 Python 无法 `import cst`。详见 `cst-studio-automation-suite/SKILL.md` 的快速开始。

</details>

## 🚀 Quick Start · 快速上手

安装后无需记忆触发词，直接描述需求即可自动匹配：

> 💬 「帮我评审这个超表面吸波结构仿真方案」
>
> 💬 「用五人智囊天团审一下这篇论文能不能投」
>
> 💬 「用 CST suite 脚本一键建模双环嵌套开口方环吸波体」
>
> 💬 「CST 批量仿真参数扫描，支持断点续跑」
>
> 💬 「CST VBA 宏报错了，帮我排查」
>
> 💬 「CST 2025 的 FDSolver 怎么配置？」
>
> 💬 「CST 网格密度命令不生效怎么办？」（suite：唯一旋钮是 Fmax，见 troubleshooting）

详细用法与三档评审深度、CST suite 脚本参数、四类工具选型等，见各 skill 目录下的 **SKILL.md**。

## 🗺️ Roadmap · 路线图

- [x] five-brain-council — 五人智囊天团（evidence-driven 科研评审）
- [x] cst-studio-automation — CST 自动化工具集 v1（选型指南 + 4 份参考文档）
- [x] cst-studio-automation-v3 — CST 自动化全栈工具集 v3（5 脚本 + 9 参考 + 3 材料库，W1 实战验证，CST 2025 API 速查）
- [x] cst-studio-automation-v3.1 — 7 仓库对照吸收（网格 Fmax 实锤结论 + cross-repo-lessons.md 经验库 + 建模/求解/端口/导出/进程纪律）
- [x] cst-studio-automation-suite — v3.1 与 v1 整合合并（17 参考文档 + 冲突裁定 C1~C6 + 路径占位符化，公开仓库零隐私残留）
- [ ] CST MCP Server 实际试用与兼容性验证
- [ ] py4cst 批量仿真脚本模板（基于 W1 宏迁移）
- [ ] 本地 CST Help 离线检索（MuziIsabel 方案验证）
- [ ] 更多科研 / 办公技能
- [ ] 使用演示截图
- [ ] 发布 Release 版本

欢迎 Issue 反馈使用问题 👋

## 📄 License

本仓库技能可自由安装、修改与使用。第三方工具（MCP Server、py4cst 等）的代码不在本仓库中，使用时遵循各自项目的许可证。

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0ea5e9,50:14b8a6,100:22c55e&height=110&section=footer" width="100%"/>

</div>
