# 上游生态快照（upstream-ecosystem-snapshot）

整合所依据的仓库全景。星标/更新等信息为整合时点快照，**属易变数据，引用前建议复核**。

## 一、核心 CST 技能来源（8 家）
| 仓库 | 定位 | 体量/形态 | 许可 | 对本包的独有贡献 |
|---|---|---|---|---|
| javanaa/skills_tools | 实测脚本+踩坑沉淀，吸波超材料场景 | 5 脚本+3 材料 JSON+参考文档 | MIT | 可运行脚本骨架、材料库、三条死路、2025/2026 断层结论 |
| Neil2DP/cst-paper-sim-skills | 论文复现全链路方法论 | 10 skill/39 文件 | MIT | 读论文→公式扫雷→仿真→三方验证→创新提炼流程、17 条实测坑、场监视器约定、结果状态标签、开工/收尾纪律 |
| jame-ri/cst2026-skill-mcp | 官方文档本地副本+宏索引+无依赖 MCP | 1444 文件 | —— | 2026 面向的宏索引；2025 用户只有"文档检索"这部分可用 |
| valenZW/cst-sim-agent | Claude Code 插件，对话式 CST | 82 文件，server.py 单文件大 | Apache-2.0 | MCP 工具集（30+ 个 cst_* 工具）、防 LLM 编 VBA 方法名机制、写历史不可逆/静默失败/save 显式路径等纪律 |
| MuziIsabel/CST-Studio-Suite-Help | 本机 Help 离线检索问答 | 13 文件 | MIT | 建 SQLite FTS5 索引检索本机 Documentation、引用出处、覆盖参数 help-root |
| xinhong-li999/cst-antenna-skill | 天线自动化（CST 2026） | 13 文件，724KB VBA 对象参考 | —— | 408 个 VBA 对象参考表（天线场景价值高，无可执行代码） |
| xixiheni/matlab-cst-simulation-skill | MATLAB→COM 驱动 CST | 21 文件，PowerShell | —— | 最小建模信息集要求、检查工程/解析日志脚本思路（依赖 MATLAB 授权） |
| Albert-tru/AntennaResearchAI- | 探地雷达天线科研平台 | FastAPI+LangGraph+Chroma | —— | "用 skill 直接控 CST"仍是 TODO，非现成能力 |

## 二、周边底层库
| 库 | 作用 | 备注 |
|---|---|---|
| renanmav/pycst | CST 官方 Python API 封装 | 会话/参数/求解/后处理/优化 |
| bbl21/cst-runtime-cli | 命令行封装 | 批处理 |
| JustArri/py4cst | VBA 文本级控制（剪贴板驱动） | ⚠️ 真实 owner 是 JustArri，非 Arri0 |
| zhaosih/ChatEM | 自然语言控 CST/HFSS 平台 | 已停更多时，引用需注明 |
| ismailakdag/cst-studio-mcp | 180+ MCP 工具 | 自称支持 CST 2024–2026；安装命令**待复核** |
| guardianer9-debug/cst-studio-orchestrator-mcp | MCP 编排 | ⚠️ 上游文档把用户名/仓库名连字符写反 |
| cclyliuyi/mcp-cst-studio | 同类 MCP | ⚠️ 上游文档误写为 rfingadam/mcp-cst-studio（不存在） |
| woson-L/cst-studio-suite-mcp | MCP（专做 2026） | 2025 用户不适用 |
| JOEYZYC/cst-studio-mcp-cli | MCP CLI | 上游选型文档未纳入，本包已补 |

## 三、三处链接勘误（C5，本地克隆已核实存在）
1. `Arri0/py4cst` → 实际 **`JustArri/py4cst`**
2. `guardianer9/debug-cst-studio-orchestrator-mcp` → 实际 **`guardianer9-debug/cst-studio-orchestrator-mcp`**（用户名与仓库名的连字符写反）
3. `rfingadam/mcp-cst-studio` → 该仓库**不存在**，同名最接近 **`cclyliuyi/mcp-cst-studio`**

## 四、按场景选型矩阵
| 用户场景 | 主选 | 叠加 |
|---|---|---|
| CST 2025 + 吸波/超材料单元 + 批量出数据集 | 本包（=v3 脚本+playbook） | MuziIsabel Help 问答补文档 |
| 端到端论文复现（含读论文/验证/创新） | Neil2DP 流程 | 本包脚本作 cst-automation 加速件 |
| CST 2026 或对话式控制 | valenZW/cst-sim-agent 或 jame-ri | 先过版本关 |
| 天线（阵列/Vivaldi/波导） | xinhong 的 VBA 对象参考表 | 本包模板只贴合方环类结构 |

## 五、能力缺口（本包有意不做）
1. 未内联各家官方文档本地副本/宏索引/724KB VBA 参考表——属外挂资源，用到再去对应仓库取。
2. 不覆盖天线远场、优化闭环、多设计环境管理（各家均未验证）。
3. 2026 API 差异只到调用风格层，**无逐 API 对照表**。
4. MCP 接入命令中 ismailakdag 一家未核对原文。
5. 本包脚本只在原作者 CST 2025.1 真机跑通过，本整合未重复真机验证。
6. 材料库不含铁氧体、相变材料等特种介质。

## 六、合规声明
CST Studio Suite、SIMULIA 为达索系统商标；本包为知识整合，不含其源码。各家代码遵循其自身许可（MIT/Apache-2.0 等，未标注者见原仓库）。
