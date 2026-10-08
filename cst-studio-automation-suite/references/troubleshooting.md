# CST 2025 自动化故障排查

> 按报错信息分类，快速定位原因和修复方案。

---

## 建模阶段

### "Shape does not exist"（Solid.Subtract）

**原因**：pywin32 COM 逐对象操作，或组件名/实体名不匹配。
**修复**：用 `cst.interface` + `add_to_history`，`Solid.Subtract "metamaterial:o_solid", "tool:o_hole"`（单冒号）。

### mws.save() RuntimeError

**原因**：保存路径含中文字符。
**修复**：使用纯英文路径，如 `<工作目录>\project.cst`。

### "Identifier is already in use"（宏执行）

**原因**：在 CST 宏编辑器中重复运行包含 `Sub Main()` 的宏，或变量名冲突。
**修复**：关闭宏编辑器重新打开，或用 Python API 的 add_to_history 替代宏编辑器。

---

## 网格阶段

### ★ 网格密度控制：VBA 密度命令经 COM/add_to_history 通道全部静默失效（已实锤）

**现象**：设置了 `Mesh.StepsPerWavelengthTet "20"` 但 Model.log 显示网格数不变（W1 实测 4743→8268）。

**实锤结论（2026-10-02，外部 3 个实战仓库交叉验证，与 W1 现象完全同源）**：
- Neil2DP/cst-paper-sim-skills 用十三轮探针逐一验证：`With Mesh` 块经 `add_to_history` 全部无效——
  不报错、进历史、`GetNumberOfMeshCells` 纹丝不动。`.LinesPerWavelength`（With 块/裸语句/带引号/带括号全形态）、
  `.MinimumStepNumber`、`.MinimumLineNumber`、`Mesh.AddAutomeshFixpoint` 全部失效。
  `.MeshType "Hexahedral"` 报 10091（枚举值不存在，六面体叫 `"PBA"`）。
- **唯一可控密度通道 = 求解频率范围 Fmax**（λ@Fmax 驱动自动网格）：
  ```
  300mm WR62 波导实测: Fmax 13.6→67,410 | 15.6→106,272 | 17.6→136,344 单元
  R22 弯头实测:       Fmax 11.6→911,988 | 13.6→1,386,798 单元
  ```
- **加密网格** = 抬高 Fmax（TD 是脉冲响应 FFT，带外求解不影响带内有效性）。
- **缩规模防内存崩** = 压低 Fmax（单元数 ~(F/F₀)³ 关系）。
- 同批对比实验必须同 Fmax；网格档位标签一律以**实测单元数**为准，不以设置命令自报。

**修复方向**：
- 首选用 `set_frequency_range` 抬高 Fmax 驱动网格加密（唯一活通道）
- 建网格后读 Model.log "Number of mesh cells" 实测单元数，确认是否生效
- 检查是否有 "input reflection seems to be large" 警告（自适应停止信号，全反射死循环）

### "Unknown setting: StepsPerWaveNear"

**原因**：使用了 CST 2026 的 MeshSettings key，2025 不认。
**修复**：CST 2025 用 Mesh 对象，且注意——密度类设置经自动化通道本身就不生效（见上条目），
        不要继续尝试密度旋钮，直接用 Fmax 控制。

### "no such property or method (.Reset)"

**原因**：CST 2025 的 MeshSettings / MeshAdaption3D 没有 Reset 方法。
**修复**：删除 `.Reset` 行。

---

## 求解器阶段

### 求解极快（<1 分钟）但无结果

**现象**：FDSolver.Start 后 44 秒"空闲"，无 Touchstone 文件。
**原因**：求解器可能弹出错误对话框等待用户确认，或网格生成失败。
**排查**：
- 检查 `Result\Model.log` 是否有求解记录
- 检查 `Result\output.txt` 尾部
- 若 Model.log 无内容 → 求解器未真正启动，检查 FDSolver 配置
- 若 Model.log 有内容但无 S 参数 → 检查端口设置

### 求解极慢（>30 分钟）

**原因**：可能启动了时域求解器（`m3d.run_solver()` 默认时域）。
**修复**：用 `FDSolver.Start` 显式启动频域。

### "The input reflection seems to be large"

**原因**：自适应网格检测到某频点 |S11|≈1（全反射），认为不需要细化，停止该频点自适应。
**影响**：可能导致网格不足→环未谐振→持续全反射的死循环。
**修复**：手动设置网格密度打破循环。

---

## 导出阶段

### "The option is not available for current view (0) 'Components'"

**原因**：ASCIIExport 需要先选中 1D Results 树节点，但当前视图是 Components。
**修复**：不用 ASCIIExport，改用 `export_touchstone(Project, path)`。

### TOUCHSTONE VBA 块无报错但无文件

**原因**：VBA TOUCHSTONE 块在 add_to_history 上下文中可能未正确执行。
**修复**：用 Python 官方库 `cst.post_processing.s_parameters.export_touchstone`。

### export_touchstone 报 "'DesignEnvironment' object has no attribute 'model3d'"

**原因**：传了 DesignEnvironment（de）而非 Project（mws）。
**修复**：`export_touchstone(mws, path)`，传 open_project 返回的对象。

### 导出文件命名异常（.s1p.s1p）

**原因**：CST 自动追加 .s1p 后缀。
**修复**：正常现象，直接解析生成的文件即可。

---

## 命令行阶段

### EXITCODE_FAILED_TO_OPEN (4)

**原因**：CST 2025 命令行 `-m` 参数是"启动 MWS"不是"运行宏"。
**修复**：不要用命令行批处理运行宏，用 Python API。

### "Unknown command line option(s)"

**原因**：使用了不存在的命令行参数（如 `-h`）。
**修复**：CST 2025 帮助用 `-help`（单横杠）。

---

## 物理结果异常

### |S11| ≈ 1.0 全频段，无吸收峰

**排查清单**（按嫌疑排序）：
1. **网格密度**：检查 Model.log 网格数，0.35mm 缝隙是否被解析
2. **极化匹配**：取 2 个 Floquet 模式，对比 S11(mode1) 和 S11(mode2)
3. **边界条件**：Zmax 是否应为 `unit cell` 而非 `expanded open`
4. **几何正确性**：在 GUI 中检查环是否真正开口（缝隙是否被布尔减成功）
5. **材料参数**：RO4003C εr/tanδ 是否正确
6. **频率范围**：谐振峰是否在 2-18GHz 之外

### 相位线性旋转（无谐振特征）

**现象**：S11 相位从 +144° 线性变到 -144°，无突变。
**原因**：纯金属背板反射特征，环未参与响应。
**修复**：同上排查清单。
