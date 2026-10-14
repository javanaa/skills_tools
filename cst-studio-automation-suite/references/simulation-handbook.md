# CST 仿真经验手册

> 来源：valenZW/cst-sim-agent（35 个官方案例深度分析）
> 面向吸波体/FSS/超材料仿真实战

---

## 0. 拿到任务先问四个问题

```
① 结构是开放还是封闭？        → 决定边界条件
② 电尺寸多大（几个波长）？     → 决定求解器
③ 关心宽带还是窄带？           → 决定 TD 还是 FD
④ 要什么输出量？               → 决定端口/监视器怎么放
```

---

## 1. 边界条件速查

| 物理场景 | 边界设置 |
|----------|----------|
| 周期结构（FSS/吸波体） | X/Y = `unit cell`，Zmax = `expanded open`，Zmin = `electric`（背板） |
| 封闭金属结构 | 六面全 `electric` |
| 辐射结构（天线） | 六面 `open (add space)` |
| 自由空间散射（RCS） | 六面全 `expanded open` |

**金规则：**
- 对称面是免费加速：`magnetic` = E场平行；`electric` = E场垂直
- 每用一个对称面计算量减半

---

## 2. 求解器选型

| 场景 | 求解器 |
|------|--------|
| 宽带 S 参数（吸波体） | **频域 FD + Tet 二阶**（首选，我们用的就是这个） |
| 窄带高 Q（滤波器） | FD + MOR |
| RCS 散射 | TD 或 Asymptotic SBR |
| 谐振频率与 Q | Eigenmode 本征模 |

**吸波体标准配置：**
```vba
With FDSolver
    .Reset
    .SetMethod "Tetrahedral", "General purpose"
    .OrderTet "Second"
End With
```

---

## 3. 网格

- FD ↔ Tet 二阶单元 + 自适应
- 优化循环内必须关自适应——保证每轮迭代网格拓扑一致
- 局部加密：馈线、间隙等小特征单独建 MeshGroup

---

## 4. 端口与激励

| 激励方式 | 适用 |
|----------|------|
| FloquetPort | FSS/周期吸波体（我们用的就是这个） |
| WaveguidePort | 波导/微带 |
| DiscretePort | 快速激励 |

**Floquet 端口要点：**
- `.Port "Zmax"` 不是 `.Port "1"`
- `.SetNumberOfModesConsidered "1"`（吸波体单模式足够）

---

## 5. 建模哲学

1. **最少图元原则**：能少画一个体就少画
2. **恒定顺序**：背景件（衬底）→ 金属结构 → 馈电
3. **参数化从第一个 Brick 开始**：要扫参的模型，第一个几何就参数化
4. **官方工程师也是迭代试错的**：建模从来不是一步到位

---

## 6. FSS / 周期结构速查（我们的场景）

- X/Y = `unit cell` 边界
- Zmax = `expanded open` + Floquet 端口
- Zmin = `electric`（铜背板）
- 入射角参数化 theta/phi
- **参考官方案例：TID 354/360（FSS 环 FD/TD）**

---

## 7. 通用习惯

- **单位**：mm + GHz 是绝对主流
- **监视器命名**：`ef_/hf_/ff_ + 频率`
- **单位分离**：E/H/Loss 同频点挂三件套便于诊断
- **模型做成求解器无关**：几何/端口/边界/监视器共用，只改网格和求解器设置
