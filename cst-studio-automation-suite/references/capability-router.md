# 能力路由表（capability-router）

目标：回答"这个活归谁、什么时候去取、现在手上有没有"。粒度到**技能/工具组级**。

**可用性四档**：
- 🟢 **已内联**——能力文本已在本包内，直接照做，无需外部仓库
- 🔵 **本机可装**——依赖已就绪（Windows+CST 2025），按目录内步骤装完即用
- 🟡 **待装/待复核**——需 clone/授权/版本验证后才可用，接入前别承诺
- ⚪ **仅登记**——知道存在与边界，未纳入使用计划

## 一、建模 / 求解 / 导出执行层
| 能力 | 何时取 | 版本限制 | 档 | 位置/来源 |
|---|---|---|---|---|
| VBA 注入建模通路（add_to_history） | 一切 2025 几何/求解/导出操作 | 2025✅ 2026需改 | 🟢 | playbook §0-§6 |
| 会话管理脚本（单例锁/自愈/看门狗） | 任何脚本连 CST 前 | 2025 | 🟢 | scripts/cst_session.py |
| 基准单元建模（双环吸波） | 方环类周期单元起步 | 2025 | 🟢 | scripts/build_unitcell.py |
| 频域四面体求解+Touchstone 导出 | 单样本跑通 | 2025 | 🟢 | scripts/run_simulation.py |
| S11 解析+吸收率统计 | 出数据后 | 通用 | 🟢 | scripts/parse_s11.py |
| 参数扫描断点续跑（指纹守卫） | ≥500 样本批量 | 2025 | 🟢 | scripts/batch_sweep.py |
| CSTRunner 通用执行器+场监视器一键套件 | 需要远场/E/H/坡印廷全套监视器 | 2025 | 🟡 | Neil2DP cst-em-sim（scripts/cst_runner.py），本包只内联了规范（workflow §4-§5），执行器本体在原仓库 |
| STEP/IGES/CAD 导入流程 | 外部 CAD 进 CST | 2025，须走 add_to_history（坑7） | 🟡 | 同上 step-import-guide |
| 远场/3D 场点云无头导出 | quiet 模式要方向图/场图 | 2025，坑 13/14/17 路线 | 🟢 | workflow §5（路线全文已内联）|
| 远程委托求解（局域网另一台 CST） | 本机资源紧张跑长任务 | 同版本 CST+OpenSSH | 🟡 | Neil2DP cst-automation 远程委托节 |
| 图元级 MCP 建模（brick/cyl/cone/sphere/布尔/变换/STEP 导入） | 2026 且对话式控制 | **2026 only** | 🟡 | valenZW cst-sim-agent（连接/建模/材质/求解/SBR/操作六组约 45 工具） |
| VBA 图元参考查询（408 对象/757KB 表） | 天线几何语法不确定 | 面向 2026，表可查 | 🟡 | xinhong references/cst_vba_reference.txt |
| 宏索引检索（415 宏 CSV）+ 官方文档本地副本（python/vba-3d/vba-des/advanced） | 查"官方有没有现成宏/原文怎么写" | 副本 2026 向，检索用法 2025 可用 | 🟡 | jame-ri macro-library + official-docs |

## 二、流程 / 方法论层（全 🟢，workflow 内联）
| 能力 | 何时取 | 位置 |
|---|---|---|
| 论文→model_spec.yaml 字段契约+完整度红黄绿评级 | P1 | workflow §2 |
| 公式扫雷：五类硬伤×四步×四实验×CLEARED 纪律 | P2，建模前必做 | workflow §3 |
| 求解器选型树（TD 宽带/FD 窄带+插值伪影警示+双求解器交叉验证） | P3 | workflow §4 |
| 端口六纪律+对称面判断+场监视器硬约定 | P3 | workflow §4 |
| 网格唯一旋钮 Fmax 实测结论（n_cells 复核） | P3/P4 | workflow §5 坑2 + C2 |
| 开工/收尾纪律、7 类结果状态标签 | 每轮 CST 任务 | workflow §6 |
| 视觉自查四图+能力边界（不像素级测量） | 建模后/出图后 | workflow §7 |
| 图文汇报五步+固定章节+内嵌图规范 | P6 验收 | workflow §8 |
| 三方验证偏差分级（5%/15%）+六查归因表 | P5 | workflow §9 |
| 创新点提炼五维空白法 | 选题延伸 | workflow §10 |
| 评审类请求（批判性审稿/模拟答辩） | 与仿真无关→不属本技能 | ⚪ javanaa five-brain-council 单独装 |

## 三、问答 / 排错层
| 能力 | 何时取 | 档 | 位置/来源 |
|---|---|---|---|
| 报错→首查对照表（Macro not found/Shape does not exist/慢/保存失败…） | 任何 CST 报错第一步 | 🟢 | playbook §10 |
| 本机 Help 离线检索问答（FTS5 索引+引用出处） | 写 API 前查权威原文（P0） | 🔵 | MuziIsabel：clone→python install.py→自动探测 `<CST安装目录>\Documentation`（本机 Help 全套已在，装完即用） |
| MCP 通用操作诊断（get_messages/check_status/detect_popups/dismiss_popup） | 接 MCP 后运维 | 🟡 | valenZW，2026 向+版本关 |
| Qt 弹窗看门狗钩子（PreToolUse/PostToolUse 自动修复重试≤3） | 接 xinhong 时 | 🟡 | ⚠ 与本包脚本看门狗**禁同开**（重试风暴） |
| 天线专项排错（patch/optimize/export 斜杠命令） | 天线且 2026 | 🟡 | xinhong |

## 四、登记不推荐（⚪）
| 条目 | 原因 |
|---|---|
| ismailakdag/cst-studio-mcp（180+ 工具，自称 2024–2026） | 安装命令待复核；2025 兼容未实测——接入前先过 mcp-onboarding 第 0 关 |
| woson-L/cst-studio-suite-mcp、cclyliuyi/mcp-cst-studio、JOEYZYC/cst-studio-mcp-cli、guardianer9-debug orchestrator、AndersOnLin4/cst-mcp | 体量小/无维护/面向 2026；按需再去 |
| zhaosih/ChatEM（REST 80+ 工具平台） | 停更约一年 |
| Albert-tru/AntennaResearchAI- | "控 CST"仍是 TODO，无实现 |
| renanmav/pycst(47★)、bbl21/cst-runtime-cli(35★)、JustArri/py4cst(23★) | 底层封装库：脚本路线已够用；批量模板需求再说 |
| xixiheni MATLAB 通道（15 步工作流+check_project.ps1 等） | 依赖 MATLAB 授权；已有 MATLAB 流程才评估 |

## 五、路由总原则
1. 先问版本：2025 → 只有 🟢/🔵 两档可用，🟡 全部先过版本关；2026 → 🟡 按 mcp-onboarding 流程转 🔵。
2. 会话单主人：🟢脚本与 🟡MCP 不同时驱动同一个 CST。
3. 工具链选定后不中途更换（选型铁律）；切换=最大时间黑洞。
4. 每轮执行完按 §二 的状态标签规则汇报，`.cst` 文件存在≠结果有效。
