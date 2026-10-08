# 安装配置清单

> CST 自动化工具（MCP Server / py4cst）的环境配置与验证 checklist。
> 本机环境：Windows 11 + CST Studio Suite 2025.1（<CST安装目录>\）+ Python 3.14

---

## 一、前置条件（必须先确认）

- [ ] **CST 已安装且可正常启动**
  - 路径：`<CST安装目录>\AMD64\CST DESIGN ENVIRONMENT_AMD64.exe`
  - 版本：2025.1 + SP1
- [ ] **CST License 可用**
  - 打开 CST 后能新建工程并进入 Microwave Studio
  - License Manager：`<CST安装目录>\License Manager\CST License Manager.exe`
- [ ] **Python 已安装**
  - 推荐 3.10+（MCP server 要求 3.10+）
  - 本机 Python 3.14.7（需验证兼容性）
- [ ] **Git 已安装**（用于 clone 仓库）

---

## 二、环境变量配置

MCP Server 和 py4cst 通常需要以下环境变量：

| 变量名 | 值 | 说明 |
|---|---|---|
| `CST_PATH` | `<CST安装目录>` | CST 安装根目录 |
| `CST_WORK_DIR` | `<工作目录>` | 工作目录（仿真工程和结果存放处） |

**设置方法（PowerShell，用户级）**：
```powershell
[Environment]::SetEnvironmentVariable("CST_PATH", "<CST安装目录>", "User")
[Environment]::SetEnvironmentVariable("CST_WORK_DIR", "<工作目录>", "User")
```

> 设置后需重启终端 / AI Agent 才能生效。

> ⚠ **C4 裁定提醒**：本包脚本统一使用 `CST_HOME` / `CST_WORK_DIR`（见 conflict-register.md C4）。本清单中 MCP 生态的 `CST_PATH` 等变量名与其不统一，**不要在同一脚本内混用两套变量名**。

---

## 三、py4cst 安装

```powershell
# 1. 创建虚拟环境（建议在项目目录下）
cd <工作目录>
python -m venv .venv_cst

# 2. 激活
.venv_cst\Scripts\Activate.ps1

# 3. 安装
pip install py4cst

# 4. 验证
python -c "import py4cst; print('py4cst OK')"
```

- [ ] 虚拟环境创建成功
- [ ] py4cst 安装成功
- [ ] import 验证通过

---

## 四、MCP Server 安装（以 cst-studio-mcp 为例）

```powershell
# 1. Clone
cd <工作目录>\02_设计与仿真
git clone https://github.com/ismailakdag/cst-studio-mcp.git

# 2. 进入目录
cd cst-studio-mcp

# 3. 创建虚拟环境
python -m venv venv
venv\Scripts\Activate.ps1

# 4. 安装依赖（按项目 README）
pip install -e .
# 或
pip install -r requirements.txt

# 5. 配置环境变量（见第二节）

# 6. 启动 MCP server（按项目 README 的命令）
cst-studio-mcp
```

- [ ] Clone 成功
- [ ] 依赖安装成功
- [ ] 环境变量已设置
- [ ] MCP server 可启动
- [ ] MCP client 可连接并列出工具

---

## 五、功能验证（安装后必做）

### 5.1 py4cst 验证

```python
import py4cst

# 连接 CST
mws = py4cst.interface.DesignEnvironment.connect_to_any_or_new().new_mws()

# 设单位
mws.units.geometry("mm")
mws.units.frequency("GHz")

# 建一个简单方块
brick = mws.brick()
brick.name("test")
brick.material("Vacuum")
brick.x_range(-1, 1)
brick.y_range(-1, 1)
brick.z_range(0, 1)
brick.create()

print("py4cst 几何构建验证通过")
```

- [ ] CST 被自动启动或连接
- [ ] 方块出现在 CST 视图中
- [ ] 无报错

### 5.2 MCP Server 验证

- [ ] MCP client 能看到 CST 相关工具列表
- [ ] 调用「新建工程」工具成功
- [ ] 调用「建几何」工具成功
- [ ] 调用「跑求解器」工具成功（简单结构）
- [ ] 调用「导出 S 参数」工具成功

---

## 六、常见安装问题

| 问题 | 可能原因 | 解决 |
|---|---|---|
| `pip install py4cst` 失败 | Python 版本不兼容 | 试 Python 3.10/3.11 虚拟环境 |
| 连接 CST 失败 | CST 未启动或 COM 接口不可用 | 手动启动 CST 后再运行脚本 |
| MCP server 启动报错 | 缺少依赖或环境变量 | 检查 requirements.txt 和 CST_PATH |
| CST 路径找不到 | 环境变量未生效 | 重启终端，用 `echo $env:CST_PATH` 验证 |
| 中文路径报错 | 部分工具对中文路径支持不好 | 工作目录尽量用英文路径测试 |

---

## 七、本机特殊注意

1. **CST 装在非标准路径**（`<CST安装目录>\`），未写注册表——所有工具必须通过 `CST_PATH` 环境变量或手动指定路径找到 CST
2. **Python 3.14 较新**——py4cst 和 MCP server 可能未测试过 3.14，如遇兼容问题回退到 Python 3.11
3. **项目路径含中文**（`<工作目录>`）——部分第三方工具可能对中文路径支持不佳，批量仿真时建议输出目录用英文路径
4. **WSL 待用**——当前阶段在 Windows 原生环境跑 CST，W3–W9 训练模型时再启用 WSL

---

## 八、安装记录

| 日期 | 工具 | 版本 | 安装路径 | 验证结果 | 备注 |
|---|---|---|---|---|---|
| — | — | — | — | — | — |
