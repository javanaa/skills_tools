# CST 会话管理详解

> 从 cst-mcp (AndersOnLin4) 提取的实战验证会话管理方案。

## 一、为什么需要会话管理

CST COM 接口有三个常见坑：
1. **多进程冲突**：两个脚本同时连 CST → 互相覆盖项目
2. **环境损坏**：宿主进程 scrub PATH → CST DLL 加载失败 (WinError 11)
3. **假死卡死**：CST 弹窗或求解器异常 → Agent 永久阻塞

会话管理模块一次性解决这三个问题。

---

## 二、COM 单例锁

### 原理
在工作目录创建 `cst.lock` 文件，写入当前进程 PID。新脚本启动时检查：
- lock 不存在 → 获取锁，写入自己的 PID
- lock 存在且持有进程活着 → 拒绝启动
- lock 存在但持有进程已死 → 清除死锁，获取锁

### 用法
```python
from cst_session import CSTSession
sess = CSTSession(work_dir=r"<工作目录>")
sess.connect()  # 内部自动获取锁
# ... 操作 ...
sess.close()    # 内部自动释放锁
```

### 手动清除死锁
```bash
del <工作目录>\cst.lock
```

---

## 三、环境自愈（WinError 11 修复）

### 症状
```
OSError: [WinError 11] 无法加载 DLL... (ERROR_BAD_FORMAT)
```

### 根因
- cwd 不在 CST 根目录 → 相对路径 DLL 找不到
- PATH 被宿主进程 scrub → 系统 DLL 找不到
- 当前线程未 CoInitialize → COM 初始化失败

### 修复步骤（_bootstrap_env）
1. **cwd 修正**：`os.chdir(CST_ROOT)`
2. **PATH 兜底**：从注册表读系统 PATH，补齐缺失项
3. **关键环境变量**：SystemRoot / COMSPEC / PROCESSOR_ARCHITECTURE
4. **CoInitialize**：当前线程 COM 初始化（幂等）

---

## 四、懒连接

### 策略
1. 先查 `ci.running_design_environments()`
2. 有已运行 DE → `connect()` 连上去（不启动新 CST）
3. 无已运行 DE → `DesignEnvironment()` 拉起新 CST，等待 5s 冷启动

### 好处
- 避免重复启动 CST（每次冷启动 10-30s）
- 可以在已打开的项目上继续操作
- 失败时自动重试（默认 2 次）

---

## 五、看门狗

### 原理
用 `threading.Thread` 包裹调用，`join(timeout)` 等待。超时不杀线程（daemon 线程随主进程退出），但抛异常告知 Agent。

### 用法
```python
result = sess.watch(some_long_operation, timeout=900, arg1, arg2)
```

### 求解器等待
```python
sess.solve_and_wait(timeout=1800)  # 内部 FDSolver.Start + 轮询
```

---

## 六、安全路径校验

所有传入路径必须位于 `work_dir` 下，防止：
- 路径遍历 (`../../`)
- 网络路径 (`\\server\share`)
- URL (`http://`)

```python
sess.open_project(r"<工作目录>\project.cst")  # ✅
sess.open_project(r"C:\Windows\system32\...")   # ❌ 越界
```

---

## 七、完整生命周期

```python
from cst_session import CSTSession

with CSTSession(cst_root=r"<CST安装目录>", work_dir=r"<工作目录>") as sess:
    m3d = sess.new_project()
    # ... 建模 ...
    sess.save(r"<工作目录>\my_project.cst")
    sess.solve_and_wait(timeout=3600)
    # ... 导出 ...
# with 退出自动 close + 释放锁
```

---

## 八、故障排查

| 现象 | 原因 | 解决 |
|------|------|------|
| "CST 被 PID xxx 占用" | 上一个脚本未正常退出 | 确认无批处理后删 cst.lock |
| WinError 11 | 环境损坏 | 重启终端，或手动 _bootstrap_env |
| 连接超时 | CST 冷启动慢 | 增加重试，或先手动打开 CST |
| 操作超时 | 求解器卡死 | kill CST 进程，删 lock，重试 |
| 路径越界 | 路径不在 work_dir | 把项目移到 work_dir 下 |
