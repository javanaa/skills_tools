# CST 通用避坑清单

> 来源：valenZW/cst-sim-agent（已验证）
> 汇集真实 CST 自动化仿真中沉淀的通用操作经验。

---

## A. 元规则（纪律）

### A1. 写 VBA 前必查语法库
写任何 VBA 之前，先查 `vba_syntax/` 对应域文件。凭训练记忆写 CST VBA 属于违规操作。
- **反例代价**：凭记忆造对象名/方法名 → `Method or property not found`
- ⚠️ `vba_syntax/` 是 valenZW/cst-sim-agent 仓库的内部目录，**本包不含此目录**——需使用前 clone 该仓库获取（外挂资源）。本包内的等价物：`references/cst2025-api-cheatsheet.md`（已验证写法速查）+ 本机 `<CST安装目录>\Help\VBA` 官方文档。

### A2. add_to_history 写入历史并尝试执行；写历史不可逆
- `add_to_history(header, code)` = 创建新历史块 **并执行 vba_code**
- **静默成功（返回 True 但模型无变化）是最难排查的失败模式**
- 官方 API 有的操作直接调 API，不要走 execute_vba 拼 VBA 字符串

---

## B. Python 驱动 CST

### B1. 正确模式
```python
from cst import interface
design_env = interface.DesignEnvironment()
proj = design_env.open_project(PROJECT_FILE)  # 或 new_mws()
m3d = proj.model3d
m3d.add_to_history("操作描述", vba_code_string)
m3d.start_solver()  # 异步！
proj.save(PROJECT_FILE)  # 必须显式传路径
```

### B2. GBK 编码陷阱
Windows 下 Python 输出中文/emoji 前先 `sys.stdout.reconfigure(encoding="utf-8")`

---

## C. 频域求解器死路清单

| 假方法 | 正确替代 |
|--------|---------|
| `.MinimumFrequency` / `.MaximumFrequency` | `Solver.FrequencyRange` |
| `.MeshAdaptionFDS` | `.MeshAdaptionTet` |
| `m3d.run_solver()`（默认时域） | `FDSolver.Start` VBA |

---

## D. 求解器启动唯一正解

1. **正确**：`m3d.start_solver()`（官方 Python API，COM 层触发）
2. **`start_solver()` 是异步**（0.0s 立即返回）——返回成功 ≠ 求解完成
3. 必须轮询 `is_solver_running()` 直到 False
4. ⚠️ **启动前置失败时 `start_solver()` 只报 "Unknown error"（吞真实根因）**——遇此改用同步 `run_solver()` 拿真实错误（最常见：`No valid excitation sources` 缺端口/激励）。与 `conflict-register.md` C1 裁定对齐：**VBA 层启动用 `FDSolver.Start`，Python 层等待/诊断用轮询，二者不冲突。**

---

## E. 端口

### E1. 周期结构
- FloquetPort + Unit Cell 边界
- `.Port "Zmax"` 不是 `.Port "1"`

### E2. 波导端口 TM 模式误识别
馈线太细时 CST 可能把 Quasi-TEM 识别为 TM → 修复：端口宽 ≥ 馈线+10h

---

## F. 保存与路径

### F1. Project.save 必须显式传路径
无路径 `proj.save()` 报 `Failed to save project`。**永远显式传完整路径**。

### F2. 另存路径用纯 ASCII
中文文件名/路径保存不可靠（GBK vs UTF-8 编码错乱）。

---

## G. .cst 文件格式
- `.cst` 是 CST 私有 DE-ZIP 容器，标准 zipfile 打不开
- 离线读 .cst 内容需要特殊解包工具

---

## H. 参数读写
- 参数存 `Model/Parameters.json`
- **写**：`MakeSureParameterExists(name, expr)`（expr 字符串）
- 走 execute_vba 拼 VBA 字符串的参数可能静默失败

---

## I. 工程管理
- ModelHistory.json 无校验，可精确字符串替换路径
- STEP 导入后几何缓存为 `Model/3D/*.sab`，分发包必须含缓存
