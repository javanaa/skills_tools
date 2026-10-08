# Floquet 端口完整指南

> 从 cst-mcp (AndersOnLin4) 提取的 Floquet 端口套件，结合 W1 实战验证。

## 一、Floquet 端口是什么

Floquet 端口是 CST 中用于**周期性结构**（超材料、频率选择表面、光子晶体）的专用端口。它模拟无限大周期阵列，用平面波激励，计算反射/透射系数。

**吸波体场景**：
- 入射波从 Zmax 方向照射
- 结构有铜背板 → 透射为 0
- 只需 Zmax 单端口 → S11 = 反射系数
- 吸收率 A = 1 - |S11|²

---

## 二、CST 2025 正确写法

### 基础配置（1模式）
```vba
With FloquetPort
  .Reset
  .Port "Zmax"
  .SetNumberOfModesConsidered "1"
End With
```

### 关键参数
| 参数 | 方法 | 说明 |
|------|------|------|
| 端口位置 | `.Port "Zmax"` / `"Zmin"` | 必须用 Zmax/Zmin，不能用数字 |
| 模式数 | `.SetNumberOfModesConsidered "1"` | 吸波体通常 1 模式（TE+TM 合并） |
| 扫描角 θ | `.SetDialogTheta "0"` | 入射角（度） |
| 扫描角 φ | `.SetDialogPhi "0"` | 方位角（度） |
| 极化独立 | `.SetPolarizationIndependentOfScanAnglePhi "False"` | 极化与扫描角关系 |

### 双模式（TE/TM 分离）
```vba
With FloquetPort
  .Reset
  .Port "Zmax"
  .SetNumberOfModesConsidered "2"
End With
```
> 2 模式时 S 参数会有 S11(TE), S11(TM) 两个结果。

---

## 三、边界条件配合

Floquet 端口必须配合 **unit cell 边界**：

```vba
With Boundary
  .Xmin "unit cell"
  .Xmax "unit cell"
  .Ymin "unit cell"
  .Ymax "unit cell"
  .Zmin "electric"        ' 铜背板
  .Zmax "expanded open"   ' Floquet 端口所在面
  .ZminSpace "0"          ' 边界紧贴背板
  .ZmaxSpace "0"
End With
```

### 边界类型选择
| 面 | 类型 | 原因 |
|----|------|------|
| X/Y | unit cell | 周期性 |
| Zmin | electric | 铜背板是完纯导体 |
| Zmax | expanded open | Floquet 端口需要开放边界 |

---

## 四、常见错误

### ❌ 错误1：用数字端口
```vba
.Port "1"   ' ❌ Floquet 必须用 Zmax/Zmin
```

### ❌ 错误2：双端口
```vba
.Port "Zmax"
.Port "Zmin"  ' ❌ 有背板时 Zmin 透射为0，不需要
```

### ❌ 错误3：模式数太多
```vba
.SetNumberOfModesConsidered "4"  ' ❌ 吸波体1模式足够，多了浪费
```

### ❌ 错误4：ZminSpace 不为0
```vba
.ZminSpace "0.5"  ' ❌ 背板与边界间有空气层，导致结果错误
```

---

## 五、验证端口是否正确

### 方法1：检查历史树
建模后查看 Navigation Tree → Ports → Floquet Port，确认：
- 端口在 Zmax
- 模式数 = 1
- 边界 X/Y = unit cell

### 方法2：检查 Model.log
```
Floquet Port: Zmax, 1 mode(s)
Boundary: X=unit cell, Y=unit cell, Zmin=electric, Zmax=open
```

### 方法3：物理合理性检查
- 无结构（只有介质+背板）时，|S11| 应接近 1（全反射）
- 有谐振结构时，|S11| 在谐振频点应下降
- 吸收率 A = 1 - |S11|² 应在 [0, 1] 范围内

---

## 六、斜入射扩展

```vba
With FloquetPort
  .Reset
  .Port "Zmax"
  .SetNumberOfModesConsidered "2"  ' 斜入射需要 TE/TM 分离
  .SetDialogTheta "30"             ' 30度入射角
  .SetDialogPhi "0"
End With
```

> 斜入射时必须用 2 模式，分别得到 TE 和 TM 极化的反射系数。

---

## 七、与求解器配合

Floquet 端口 + 频域四面体求解器是吸波体仿真的黄金组合：

```vba
' 网格
With MeshSettings
  .SetMeshType "Unstr"
End With
With MeshAdaption3D
  .SetType "HighFrequencyTet"
  .SetAdaptionStrategy "ExpertSystem"
  .MinPasses "3"
  .MaxPasses "8"
End With

' 求解器
With FDSolver
  .Reset
  .SetMethod "Tetrahedral", "General purpose"
  .OrderTet "Second"
  .SetRecordUnitCellScanFarfield "Auto"
End With

' 启动
FDSolver.Start
```
