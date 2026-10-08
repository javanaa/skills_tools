# 来源与改动声明（ATTRIBUTION）

本技能包为多上游仓库的知识整合产物，整合日期 2026-10-02，本地克隆核实。

## 逐文件来源

| 本包文件 | 来源 | 改动 |
|---|---|---|
| scripts/cst_session.py | javanaa/skills_tools v3（MIT） | 原样（本就支持 CST_HOME/CST_WORK_DIR） |
| scripts/build_unitcell.py | 同上 | L41-42 占位符路径改为环境变量优先 |
| scripts/run_simulation.py | 同上 | L21-22 同上 |
| scripts/batch_sweep.py | 同上 | L22-23 同上 |
| scripts/parse_s11.py | 同上 | L13 同上 |
| data/substrates.json / common_metals.json / common_dielectrics.json | 同上 | 原样 |
| references/cst2025-api-cheatsheet.md | 同上 | 原样 |
| references/cross-repo-lessons.md | 同上 | 原样 |
| references/floquet-port-guide.md | 同上 | 原样 |
| references/troubleshooting.md | 同上 | 原样 |
| references/vba-macro-best-practices.md | 同上 | 原样 |
| references/installation-checklist.md | javanaa/skills_tools v3（MIT） | 原样；补充 C4 环境变量命名提醒 |
| references/material-database.md | javanaa/skills_tools v3（MIT） | 原样；"本课题"等表述改为通用措辞 |
| references/mcp-servers-comparison.md | javanaa/skills_tools v3（MIT） | 原样；补充版本关提醒 |
| references/py4cst-guide.md | javanaa/skills_tools v3（MIT） | 原样；措辞通用化 |
| references/session-management.md | javanaa/skills_tools v3（MIT） | 原样 |
| references/conflict-register.md | 本次整合新写 | C1 裁定依据 = run_simulation.py 源码 + SKILL.md/troubleshooting/cross-repo-lessons 原文 |
| references/cst-2025-api-playbook.md | 本次整合新写 | 合并 javanaa + Neil2DP 实测结论 + xixiheni 最小信息集要求 |
| references/upstream-ecosystem-snapshot.md | 本次整合新写 | 本地克隆 17 仓库核实；3 处链接勘误 |
| references/upstream-install-catalog.md | 本次整合新写 | 环境变量名逐字 grep 核实 |
| references/mcp-onboarding-checklist.md | 本次整合新写 | valenZW/jame-ri 命令已核对；ismailakdag 标待复核 |
| SKILL.md | 本次整合新写 | 四步路径为全部来源结论的压缩 |

## 未纳入内容（有意排除）
- javanaa v1（cst-studio-automation）：2 份文档与 v3 md5 相同、2 份近似分叉，且 description 抢触发（见 conflict-register C6）。
- five-brain-council：科研评审技能，与仿真自动化身份不同，需要可单独装。
- jame-ri 官方文档本地副本 1444 文件、xinhong 724KB VBA 参考表：外挂资源，用到再去取。
- 各 MCP server 源码：不内联，接入方式见 mcp-onboarding-checklist。

## 许可
- javanaa/skills_tools：MIT（LICENSE 见原仓库）。
- valenZW/cst-sim-agent：Apache-2.0（仅引用其 README 结论与工具名清单）。
- Neil2DP、MuziIsabel：MIT。
- 其余未标注许可者，本包仅引用其公开文档结论，不含其代码。
- CST Studio Suite、SIMULIA 为达索系统（Dassault Systèmes）注册商标。

## 免责
实测结论主要来自单一作者机器（CST 2025.1），本次整合未重复真机验证；标注"待复核/⚠️待核"的条目执行前必须本机验证。
