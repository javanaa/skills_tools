# 跨仓库经验库（7 仓库对照吸收）

> 2026-10-02 精读千问发现的 7 个 CST 相关 GitHub 仓库后，逐份对照吸收。
> 与 v3 已有 references 互补：**本文件只收录 v3 原包没有、且经外部真机实测验证的新增经验**。
> 每条标注来源仓库，未验证的标 ⚠️。已有条目（如网格密度失效）已在 troubleshooting.md / cst2025-api-cheatsheet.md 同步修正。

---

## 一、来源仓库与吸收判定

| 仓库 | ⭐ | 价值判定 | 吸收内容 |
|------|----|---------|---------|
| Neil2DP/cst-paper-sim-skills | 3 | ★★★★★ 最高（CST 2025 真机实测，17 条坑） | 网格 Fmax 结论、run_solver、批量导出、远场无头导出、场监视器套件、结果状态标签、视觉自查、开工/收尾纪律 |
| valenZW/cst-sim-agent | 7 | ★★★★ 高（Claude Code 插件，Apache-2.0） | 写历史不可逆、静默失败、save 显式路径、参数读写正解、DE-ZIP、错误分类、弹窗处理 |
| jame-ri/cst2026-skill-mcp | 11 | ★★★★ 高（无依赖 MCP + 双语 SKILL） | 参数化顺序、历史树可见性、结果合理性门禁、错误五分类、长任务 checkpoint |
| MuziIsabel/CST-Studio-Suite-Help | 5 | ★★★ 中 | 本地 Help 建 SQLite FTS5 索引离线检索（待装 CST 机器可用） |
| xixiheni/matlab-cst-simulation-skill | 3 | ★★ 低-中 | 检查工程/解析日志的 ps1 脚本思路（通道为 MATLAB，本包不主用） |
| xinhong-li999/cst-antenna-skill | 3 | ★★ 低-中 | 408 VBA 对象参考索引思路；面向 CST 2026，兼容性存疑 |
| Albert-tru/AntennaResearchAI- | 4 | ★ 低 | FastAPI+LangGraph 文献问答架构，仅作未来 agent 参考（控 CST 仍是待做） |

**已舍弃**：CST 2026 专属 API 写法（2025 不认）、MATLAB 通道、作者私有模块依赖、探地雷达文献问答系统。

---

## 二、建模纪律（吸收）

### 2.1 几何创建唯一正解 = add_to_history + full_history_rebuild（Neil2DP）
- `model3d` 的 Solid/Port/Boundary 对象**只有 Get 查询方法，没有 Create**——创建一律写 VBA 命令字符串进历史。
- **add_to_history 是"写历史并尝试执行"，写历史不可逆**（valenZW A3）：命令再怪也会留在历史里；
  **静默成功（返回 True 但模型无变化）是最难排查的失败模式**。
- 凡官方 Python API 有的操作（参数、求解器 start/abort、full_history_rebuild）**直接调 API，不要拼 VBA 字符串**。

### 2.2 参数化顺序铁律（jame-ri）
units → StoreParameter → frequency range → materials → geometry → ports → mesh → monitors → solver。
**在 geometry 之前未定义参数 → 打开模态提示框卡死自动化**。

### 2.3 历史树可见性 = 交付物（jame-ri）
- 每个物理对象/紧耦合操作一条 `add_to_history`，用具体 caption（`define brick: stack:lower_dielectric`），
  不要一大坨 `create geometry`。
- 保存后回读 `Model/3D/ModelHistory.json` 验证历史已持久化，不把 add_to_history 返回 True 当成功。

### 2.4 显式保存纪律（valenZW I2 + jame-ri）
- `proj.save()` 无路径实测报 `Failed to save project`——**永远显式传** `proj.save(path, include_results=False, allow_overwrite=True)`。
- 另存到中文文件名不可靠（GBK vs UTF-8 乱码）——**另存/快照目标用纯 ASCII**（open 读中文路径 OK）。
- 新建工程未保存就退出 → 触发 "Do you want to save changes to 'Untitled_0.cst'?" 模态框卡死。
  辅助脚本持有的工程要么显式 save 要么 `Project.close()`，**先关工程再关 DE**（`de.close()` 不负责关工程）。

### 2.5 参数读写正解（valenZW I1）
- 参数存 `Model/Parameters.json`（不是 ModelHistory.json）。
- 写：`MakeSureParameterExists(name, expr)`；读：`DoesParameterExist` + `GetNumberOfParameters` + `GetParameterNValue(i)`。
- **读参数必须按索引传参**，传名字抛 `bad lexical cast`。
- 走 execute_vba 拼字符串的参数不真正进模型（返回 success 但 Parameters.json 为 null）——静默失败。

### 2.6 结果状态标签（Neil2DP，v3 新增）
`.cst` 只是模型不是证明。汇报末尾必须附标签：
`template` / `model-built-not-solved` / `solver-failed` / `export-failed` /
`CST-incomplete` / `CST-validated` / `CST-regressed`（扫参退步专用）。
扫参排名只认有真实导出的曲线；缺导出如实说 "对比 pending"，绝不拿解析公式/电路级结果冒充。

---

## 三、求解器纪律（吸收）

### 3.1 start_solver 吞真实错误 → 用 run_solver（Neil2DP 坑 5）
- `start_solver()` 异步，pre-dispatch 失败时只抛 "Simulation could not be started. Unknown error"。
- 改用 `run_solver()`（同步）阻塞到完成并抛真实错误——最常见的真实根因是
  "ERROR: No valid excitation sources defined"（模型缺端口/激励）。
- 异步启动后必须轮询 `is_solver_running()` 直到 False 再校验产物；返回成功 ≠ 求解完成（valenZW E2）。
- `abort_solver()` 同为异步（1-7s 消化延迟），abort 后也要轮询。

### 3.2 Solver.Method 有效值是 "Hexahedral" 不是 "Time Domain"（Neil2DP 坑 1）
CST 2025 把求解器类型从方法名改成网格类型。`.Method("Time Domain")` 报错。

### 3.3 频域求解器不支持的方法（valenZW C2，2025 同理）
`.MinimumFrequency`/`.MaximumFrequency` → 用全局 `Solver.FrequencyRange`；
`.MeshAdaptionFDS` → `.MeshAdaptionTet`；`.StoreTDResultsInCache`(FDSolver) → 删行。

### 3.4 扫频配置顺序（valenZW E3）
先 `Solver.FrequencyRange fmin fmax` → 再 `ChangeSolverType` → 再扫频频点/观察角表，
否则 `&H8000ffff` "Upper frequency bound larger than global maximum"。

### 3.5 求解器完成判据（valenZW K1 精神 + jame-ri）
- 用产物文件行数/存在性判完成，不用 Model.log 关键词（SBR 的 log 没有 "completed" 字样）。
- TD 求解后读 `<proj>/<proj>/Result/output.json` 判 `steady_state`（truncated/ok），
  截断数据禁入设计结论（Neil2DP 坑 15：默认脉冲宽度上限会截断长结构 ring-down）。

---

## 四、端口纪律（吸收）

### 4.1 波导端口 TM 模式误识别（valenZW F2）
馈线太细（< 端口宽 1/10）时端口模式求解器可能把 Quasi-TEM 识别为 TM（Z-wave 3000Ω 而非 50Ω）。
修复：端口宽 ≥ 馈线+10h、高 ≥ 6h+导体；或 DiscretePort 50Ω 激励。
微带 50Ω 线宽 ≈ 2×h（εr≈3.5）。

### 4.2 端口物理正确性门禁（jame-ri）
- 端口树项/历史命令/选中面只证明"有端口对象"，不证明物理正确。
- **不要静默把分布式馈电（waveguide Port）降级成 DiscretePort**——结果会偏移且不代表原物理馈电。
- 周期单元用 FloquetPort + Unit Cell 边界，不用普通集总馈电。

---

## 五、结果导出纪律（吸收）

### 5.1 1D 结果批量导出四坑（Neil2DP 坑 9，v3 已内置 export_result 按此实现）
- `ResultTree.IsResult` 报 bad lexical cast，不能用来判断结果存在。
- **批量把多条 ASCIIExport 攒进 history 一次 rebuild = 全部导成同一个当前选中结果**。
  安全路线 = 逐条 SelectTreeItem → add → 立即 rebuild 出文件。
- `p1.spi` 是 CST 内部二进制缓存，不是 Touchstone。
- 先 `RefreshView()`/`UpdateTree()` 刷新结果树，用 `GetFirstChildName`/`GetNextItemName` 遍历拿真实名称。

### 5.2 远场无头导出（Neil2DP 坑 13/14，v3 增加）
- 3D 远场结果不能直接 ASCIIExport（"No plot data available"）——只认 1D 树项。
- quiet 模式绘图引擎不加载远场数据；`de.quiet_mode_disabled()` 开 GUI 会死锁——**远场自动化禁用 GUI**。
- 无头全 3D 唯一可靠路线：quiet 模式裸 `ASCIIExportAsSource`（**不调 .Plot**）→ .ffd 文件，
  离线重积分 D=4π|E|²max/∮|E|²dΩ。
- 切面导出唯一可靠路线 = 单个 `Sub Main()` 原子块内顺序执行 plot+export（`_execute_vba_code` 通道）。

### 5.3 3D 场监视器导出（Neil2DP 坑 17，v3 已内置 export_field_ascii）
- `.Step("0.25")`（mm）**必填**，缺失 = 只有表头 2 行的零数据文件。
- 树路径叶子名带 `[N]` 运行号后缀，必须枚举拿真名。
- quiet 模式可导（3D 场走结果树不走绘图引擎，与 5.2 远场不同）。

---

## 六、环境与进程纪律（吸收）

### 6.1 模态框 = 自动化杀手（jame-ri + valenZW）
- CST Update Manager 启动弹窗 "License details are required to check for updates"：
  **不是建模错误**，是自动更新配置问题——让用户禁自动更新，别反复重试建模命令。
- 保存确认弹窗 "Do you want to save changes..."：显式 close/save 策略避免。
- **弹窗已出现且卡住时：停阶段、报告弹窗文本、请用户 UI 操作或按 PID 清理；不要按进程名杀 CST**。

### 6.2 GBK 编码陷阱（valenZW B2）
Windows 控制台 print 中文/emoji（✓✗🔴）报 GBK 编解码错误——先
`sys.stdout.reconfigure(encoding="utf-8", errors="replace")`。

### 6.3 .cst 是 DE-ZIP 容器（valenZW J1）
标准 zipfile 打不开（BadZipFile 是正常现象，不是文件损坏）。本地头 `DE\x03\x04`、
中央目录 `DE\x01\x02`、压缩字段存 CRC。离线读用 valenZW 的 DEZipFile 思路
（`zlib.decompress(raw, -15)` 裸 deflate）。

### 6.4 长任务 checkpoint（jame-ri）
求解/扫参/优化前：preflight（进程/内存/磁盘）→ 记录 checkpoint → 复制工程操作 →
分阶段打 `preflight/structure_inspect/geometry_mutation/.../finalize` 标记。
失败恢复 = 查最后完成 checkpoint，不盲目重跑破坏性阶段。

### 6.5 结果合理性门禁（jame-ri Result Sanity Gate，v3 增加）
- 无源结构出现 `|S11| > 0 dB` = 非物理，除非显式非标准归一化。
- 远场报 gain 必须说明是 gain / realized gain / directivity。
- 自适应收敛未达容差要如实报告；参数/几何改动后结果要与上一版对比。
- sanity 过不了就报"未验证数据"，不报物理结论。

---

## 七、待验证/暂缓吸收

| 项 | 来源 | 状态 |
|----|------|------|
| 本地 CST Help 建 SQLite FTS5 索引离线检索 | MuziIsabel | 待装 CST 的 Windows 机器上验证（`install.py` 一键建索引 + `search.py` 检索 + 引用） |
| MATLAB 通道（actxserver + AddToHistory） | xixiheni | 本包走 Python 通道，不主用；其 `check-cst-project.ps1`/`parse-cst-log.ps1` 检查思路可借鉴 |
| 408 个 VBA 对象参考索引 | xinhong-li999 | 面向 CST 2026；2025 兼容性未验证，暂不并入 |
| 弹窗 Qt-aware watchdog 自动 dismiss | xinhong-li999 | 与 6.1"请用户 UI 操作"策略冲突，自动化安全优先，暂缓 |
| 文献问答系统（FastAPI+LangGraph+Chroma） | Albert-tru | 与 CST 自动化无关，仅作未来 agent 架构参考 |

---

## 八、对 W1 复盘结论的最终修正

**W1 未解之谜（网格密度 VBA 命令不生效）现已实锤闭环**：
- 现象完全一致（StepsPerWavelengthTet 语法接受、无报错、网格数纹丝不动）。
- 根因 = CST COM/自动化历史通道对网格密度类命令的**系统性静默失效**（Neil2DP 十三轮探针 + 本机 W1 独立验证）。
- **唯一有效旋钮 = Fmax**。W1 S11 全反射的网格侧修正方案 = 抬高 Fmax（如 18→30 GHz 档）
  而非继续试密度命令；同时配合 MeshAdaption3D 自适应（MaxPasses 提高）。
- 该结论已回写 v3 的 troubleshooting.md 与 cst2025-api-cheatsheet.md。
