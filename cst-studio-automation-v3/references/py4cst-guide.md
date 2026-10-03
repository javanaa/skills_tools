# py4cst 使用指南

> py4cst 是 CST Studio Suite VBA 方法的 Python 封装库，让你用 Python 脚本控制 CST，适合批量仿真和数据集生成。
> 项目地址：https://github.com/Arri0/py4cst ｜ PyPI：https://pypi.org/project/py4cst/

---

## 一、基本信息

| 项 | 内容 |
|---|---|
| **作者** | Samuel Travnicek (Arri0) |
| **最新版本** | 0.1.10（2025-09-05） |
| **安装** | `pip install py4cst` |
| **原理** | 所有方法都是 CST VBA 方法的封装，snake_case 命名 |
| **依赖** | CST Studio Suite 已安装且可被 Python COM 接口调用 |

---

## 二、安装

```bash
# 建议在独立虚拟环境中
python -m venv venv
# Windows 激活
venv\Scripts\activate
# 安装
pip install py4cst
```

**验证安装**：
```python
import py4cst
print(py4cst.__version__)
```

---

## 三、核心概念

### 3.1 与 VBA 的对应关系

py4cst 的方法名是 VBA 方法的 snake_case 版本：

| VBA | py4cst |
|---|---|
| `With Brick ... .Create` | `project.brick(...)` |
| `Solid.Subtract` | `project.solid.subtract(...)` |
| `MakeSureParameterExists` | `project.parameter(...)` |
| `Solver.FrequencyRange` | `project.solver.frequency_range(...)` |

> 在源码中搜索 VBA 方法名即可找到对应的 py4cst 封装。

### 3.2 基本流程

```python
import py4cst

# 1. 连接 CST（打开新工程或连接已有实例）
mws = py4cst.interface.DesignEnvironment.connect_to_any_or_new().new_mws()

# 2. 设置单位
mws.units.geometry("mm")
mws.units.frequency("GHz")

# 3. 建几何（以 Brick 为例）
brick = mws.brick()
brick.name("substrate")
brick.material("RO4003C")
brick.x_range(-3, 3)
brick.y_range(-3, 3)
brick.z_range(0, 1.524)
brick.create()

# 4. 跑求解器
mws.solver.start()

# 5. 保存
mws.save("result.cst")
```

---

## 四、批量仿真示例（伪代码）

> 适用于 W3–W6 阶段：遍历参数组合，每个样本建一次模、跑一次仿真、导出 S 参数。

```python
import py4cst
import itertools
import os

# 参数空间
L1_values = [4.8, 5.0, 5.2, 5.4, 5.6]  # mm
L2_values = [3.5, 3.7, 3.9, 4.1]
g_values  = [0.25, 0.35, 0.45]

work_dir = r"<工作目录>\03_仿真数据集"

for L1, L2, g in itertools.product(L1_values, L2_values, g_values):
    sample_id = f"L1_{L1}_L2_{L2}_g_{g}"
    cst_file = os.path.join(work_dir, f"{sample_id}.cst")
    s11_file = os.path.join(work_dir, f"{sample_id}_S11.txt")

    # 跳过已完成的样本（断点续跑）
    if os.path.exists(s11_file):
        continue

    # 新建工程
    mws = py4cst.interface.DesignEnvironment.connect_to_any_or_new().new_mws()

    # 建几何（封装为函数）
    build_model(mws, L1=L1, L2=L2, g=g)

    # 跑频域求解器
    mws.solver.start()

    # 导出 S11
    mws.result.export_s_parameters(s11_file)

    # 保存并关闭
    mws.save(cst_file)
    mws.close()

    print(f"[OK] {sample_id}")
```

---

## 五、与现有 W1 VBA 宏的关系

| 方面 | W1 VBA 宏 | py4cst |
|---|---|---|
| **语言** | VBA | Python |
| **运行方式** | CST 内部 Import Macro → Run | 外部 Python 脚本调用 CST COM 接口 |
| **适合** | 单结构建模、手动检查 | 批量循环、数据集生成 |
| **调试** | CST Macro Editor | Python IDE / 断点 |
| **与 W1 宏的关系** | 基准模板 | 可把 W1 宏的几何逻辑翻译成 Python，作为批量脚本基础 |

**迁移策略**：
1. W1 宏跑通后，把其中的几何构建逻辑（Brick / Solid.Subtract / 材料 / 边界 / 端口）逐行翻译成 py4cst
2. 先用 1 个参数验证翻译后的脚本和 VBA 宏结果一致
3. 验证通过后，加参数循环做批量仿真

---

## 六、注意事项

1. **CST 必须在运行状态**：py4cst 通过 COM 接口连接 CST，需要 CST 已启动或可被启动
2. **单线程**：CST COM 接口通常一次只能跑一个仿真，批量样本需串行
3. **错误处理**：批量脚本必须加 try/except，单个样本失败不影响整体
4. **断点续跑**：检查输出文件是否已存在，跳过已完成样本
5. **版本兼容**：py4cst 0.1.10 发布于 2025-09，需验证与 CST 2025.1 的兼容性
6. **license**：批量仿真会持续占用 CST license，确保不与其他用户冲突

---

## 七、参考资源

- GitHub: https://github.com/Arri0/py4cst
- PyPI: https://pypi.org/project/py4cst/
- CST 官方 VBA 文档：CST 安装目录下 `VBA Help`
- 学术参考：IEEE《Customized Inverse Design of Metamaterial Absorber》用 CST 自动脚本生成 20000 样本

---

## 验证记录（待补充）

| 日期 | py4cst版本 | CST版本 | 验证内容 | 结果 |
|---|---|---|---|---|
| — | — | — | — | — |