# CST 2025 实测 API 手册（cst-2025-api-playbook）

成功通路 + 正误对照 + 分主题细节。所有"✅ 实测"结论来自 CST 2025.1 真机验证仓库；标注"⚠️待核"的条目动手前先用本机 Help/小样本验证。

## 0. 成功通路总览（正确姿势）
```
cst.interface  →  DesignEnvironment(连接/新建)  →  open_project  →  model3d(m3d)
    ├─ 几何/求解/端口/材料等"建模动作"  →  m3d.add_to_history("<id>", "<VBA 语句>")   # 注入 VBA，走宏引擎
    ├─ 等待求解                          →  while m3d.is_solver_running(): sleep()
    └─ 导出 S 参数                        →  export_touchstone(mws, path, ...)          # 传 mws 不传 de
```
关键：**Python 管会话与流程，几何/求解等建模细节注入 VBA 执行**。不要试图用纯 Python 逐对象建几何（见死路 D3）。

## 1. 三条已验证死路（D1-D3）
- **D1 命令行加载宏**：`CST ... -m macro.bas -q` 在 2025 里的 `-m` 是启动主程序参数，不是"无头跑宏"。别指望命令行直接执行宏。
- **D2 COM RunMacro**：pywin32 走 `Application.RunMacro` 报 `Macro not found`。宏要在 CST 内部注册/或改走 `add_to_history`。
- **D3 逐对象 COM 建几何**：用 COM 一个个创建几何对象报 `Shape does not exist`。几何统一走 `add_to_history` 注入 VBA。

## 2. 几何与布尔
- 布尔运算用**单冒号**引用组件名：`Solid.Subtract "comp:solid1","comp:solid2"`（双冒号/写法错会找不到对象）。
- 命名与引用：先建带名字的实体，再用 `comp:` 前缀引用；名字含空格要处理。
- 材料：VBA `.Material "<名>"`；材料库取用见 §7。

## 3. 频域求解器（重点，C1 落点）
```vba
With FDSolver
    .Reset                          ' 2025 有；注意 MeshSettings 在 2025 无 Reset
    .SetMethod "Tetrahedral","General purpose"
    .OrderTet "Second"
End With
FDSolver.Start
```
- ✅ 启动频域：VBA `FDSolver.Start`（Python 侧用 `add_to_history("start_fd","FDSolver.Start")`）。
- ❌ 不要用 `m3d.run_solver()` 触发求解——**默认走时域(FD-TD)，频域四面体场景极慢**（>30 分钟常态）。
- ⚠ 2025 **没有** `FDSolver.Accuracy/.FrequencyMin/.FrequencyMax/.Samples/.SweepType`（这些是 2026 属性式 API）；`.Method "Frequency"` 只接受 Hexahedral/Hexahedral TLM。
- **等待/诊断统一用 Python `is_solver_running()` 轮询**；"API 返回成功 ≠ 求解完成"，必须轮询到 False 再校验产物。
- 若必须用 Python 原生触发而非 VBA 注入：优先同步 `run_solver()`（能抛真实错误，如"缺端口/激励"），避免异步 `start_solver()` 只报 "Unknown error" 吞掉根因。

## 4. 网格与收敛（C2）
- 2025 网格密度命令常**静默失效**（不报错但没生效）；实际主控旋钮是 **Fmax**。调网格优先动 Fmax，改完要复核网格数确实变了。
- ⚠️ `MeshSettings` 在 2025 **无 `Reset`**（照 2026 写法会报错）。
- 网格收敛判据（P3）：同一结构逐级加密，关键指标（谐振频率/带宽/|S11| 峰值）连续两档变化 < 阈值才算收敛；未收敛的数据只能标"趋势参考"。

## 5. 端口与 Floquet / 周期单元（"看着正常但全错"重灾区）
- 周期单元边界需 **X/Y 成对**设置，只设一个方向不报错但结果错。
- Floquet 端口三大错因：**贴面位置、极化方向、坐标系**任一不匹配 → 结果数值合理但物理全错。建模后先做一次已知解析/文献点核对再批量。
- 缺激励/端口是求解失败最常见真根因（`ERROR: No valid excitation sources defined`）。

## 6. 导出与后处理
- `export_touchstone` **第一个参数传 `mws`（工程对象），不是 `de`（设计环境对象）**，传错失败。
- 输出常带双扩展名（`xxx.s1p.s1p`），解析前先按实际文件名匹配。
- 结果存 `WORK_DIR/<项目名>/Result/Model.log`，报错诊断从这里提取。

## 7. 材料库取用
- `data/substrates.json`（基板：含 εr、tanδ、厚度）、`data/common_metals.json`（金属：电导率等）、`data/common_dielectrics.json`（介质）。
- 通用商板材牌号（如 Rogers RO4003C 等）可直接取；换材料只改参数不改拓扑。

## 8. 2025 ↔ 2026 迁移要点
| 维度 | CST 2025 | CST 2026 |
|---|---|---|
| 配置风格 | `Set` 前缀方法 | 直接属性赋值 |
| FDSolver 属性 | 多为方法调用 | `.Accuracy/.FrequencyMin/...` 属性 |
| MeshSettings.Reset | 无 | 有 |
| 第三方 MCP 默认 | —— | 多数按 2026 写，**2025 不兼容** |

## 9. P1 结构化参数清单模板（论文/需求 → 可跑）
一份最小建模信息集（缺任一项先问用户，不臆造）：
- 结构拓扑（层数、图形类型、对称性）
- 几何尺寸（周期 P、环宽 w、开口 g、厚度 h、铜厚 t）
- 材料（基板 εr/tanδ、金属电导率）
- 频段（fmin/fmax）、极化、入射条件
- 边界类型（周期/Floquet/开放）、端口类型与位置
- 求解目标（S11/吸收率/带宽）、输出格式（Touchstone/CSV）

## 10. 报错 → 首查对照
| 报错/现象 | 首查 |
|---|---|
| `Macro not found` | 是否误走 COM RunMacro（死路 D2）→ 改 `add_to_history` |
| `Shape does not exist` | 逐对象建几何（死路 D3）或 `comp:` 引用名/冒号写错 |
| 求解极慢 (>30min) | 误入时域 → 确认用 `FDSolver.Start`，非 `run_solver()` |
| 结果合理但物理错 | Floquet 贴面/极化/坐标系、周期边界 X/Y 未成对 |
| `No valid excitation sources` | 端口/激励缺失 |
| `mws.save` 失败 | 路径含中文 → 改纯英文 |
| 改网格无反应 | 2025 网格命令静默失效 → 动 Fmax 并复核网格数 |
| 中文乱码/存不上 | 全程纯英文路径与命名 |
