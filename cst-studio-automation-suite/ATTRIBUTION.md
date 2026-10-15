# 来源与改动声明（ATTRIBUTION）

本技能包为多上游仓库的知识整合产物，整合日期 2026-10-02，本地克隆核实。

## 逐文件来源

| 本包文件 | 来源 | 改动 |
|---|---|---|
| scripts/cst_session.py | javanaa/skills_tools v3（MIT） | 原样（本就支持 CST_HOME/CST_WORK_DIR） |
| scripts/build_unitcell.py | 同上 | L41-42 占位符路径改为环境变量优先；2026-10-15 真机验证修复 12 处写法（见 CHANGELOG D15：FrequencyRange/Xrange/FrqType/材料顺序/Solid.Rename/去多余 Delete/Boundary 去 Space） |
| scripts/run_simulation.py | 同上 | L21-22 同上 |
| scripts/batch_sweep.py | 同上 | L22-23 同上 |
| scripts/parse_s11.py | 同上 | L13 同上 |
| data/substrates.json / common_metals.json / common_dielectrics.json | 同上 | 原样 |
| references/cst2025-api-cheatsheet.md | 同上 | 原样；2026-10-14 增补 §14 场监视器正确写法（来自 valenZW/Neil2DP）；2026-10-15 增补真机验证教训（FrqType 合法值 / Subtract 自动删工具 / Boundary 无 Space） |
| references/common-pitfalls.md | valenZW/cst-sim-agent（Apache-2.0） | 通用避坑清单 A-I 提炼；标注 vba_syntax/ 属外挂资源 |
| references/simulation-handbook.md | valenZW/cst-sim-agent（Apache-2.0） | 35 官方案例提炼的仿真经验手册（边界/求解器/网格/端口速查） |
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
| references/mcp-onboarding-checklist.md | 本次整合新写 | valenZW/jame-ri 命令已核对；ismailakdag 标待复核；2026-10-15 并入 woson-L/cst-studio-suite-mcp 专项（来自 cst-automation 技能包，上游 woson-L，CST 2026 stdio MCP） |
| scripts/validate_environment.py | cst-automation 技能包（2026-10-15 并入） | 原样（纯 stdlib 环境健康检查，上游指向 woson-L/cst-studio-suite-mcp） |
| scripts/generate_job.py | cst-automation 技能包（2026-10-15 并入） | 原样（生成待审查 Python 脚手架 + manifest） |
| scripts/cst2025_bridge.py | 2.0 版新增（2026-10-15 并入） | 原样（窄接口本地桥接器核心：健康/脚手架/S1P 分析/经审批单元胞执行；stdlib only） |
| mcp_server_2025.py | 2.0 版新增（2026-10-15 并入） | 原样（FastMCP stdio 服务器，注册 cst2025_health/generate_job/analyze_s1p/run_unitcell，需 mcp 包） |
| references/v2-execution.md | 2.0 版新增（2026-10-15 并入） | 原样（2.0 执行层：Windows 安装/环境变量/审批口令/范围与注意事项） |
| tests/test_bridge.py | 2.0 版新增（2026-10-15 并入） | 原样（7 个离线单元测试，本机已跑通） |
| examples/mcp-2025.example.json | 2.0 版新增（2026-10-15 并入） | 原样（MCP host 配置示例，路径为占位需按本机改） |
| README-2.0.md / agents/openai.yaml | 2.0 版新增（2026-10-15 并入） | 原样（快速开始 / Agent 元数据） |
| SKILL.md | 本次整合新写 | 四步路径为全部来源结论的压缩；2026-10-15 并入 2.0 MCP 执行层章节 + 资源地图补全至 38 文件 |
| references/capability-router.md | 本次整合新写 | 2026-10-15 本地 MCP 桥接器档位 🟡→🟢（真机验证通过） |

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
