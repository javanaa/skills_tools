# -*- coding: utf-8 -*-
"""
cst_session.py — CST 会话管理模块
从 cst-mcp (AndersOnLin4) 提取精华，去掉私有模块依赖，独立可运行。

功能：
- COM 单例锁（防止多进程冲突）
- 环境自愈（WinError 11 / ERROR_BAD_FORMAT 修复）
- 懒连接（优先连已运行 DE，否则拉起新 CST）
- 看门狗（带超时的调用封装）
- 安全路径校验

用法：
    from cst_session import CSTSession
    sess = CSTSession(cst_root=r"<CST安装目录>", work_dir=r"<工作目录>")
    m3d = sess.open_project(r"<工作目录>\project.cst")
    m3d.add_to_history("step", "...")
    sess.close()
"""
import os
import sys
import time
import threading
import subprocess

# 默认配置（可通过环境变量覆盖）
DEFAULT_CST_ROOT = os.environ.get("CST_HOME", r"<CST安装目录>")
DEFAULT_WORK_DIR = os.environ.get("CST_WORK_DIR", r"<工作目录>")


class CSTSession:
    """CST 会话管理：连接、锁、自愈、看门狗。"""

    def __init__(self, cst_root=None, work_dir=None, lock_timeout=120):
        self.cst_root = cst_root or DEFAULT_CST_ROOT
        self.work_dir = work_dir or DEFAULT_WORK_DIR
        self.lock_file = os.path.join(self.work_dir, "cst.lock")
        self.lock_timeout = lock_timeout
        self.de = None
        self.project = None
        self.m3d = None
        self._lock_held = False

    # ------------------------------------------------------------------
    # 环境自愈
    # ------------------------------------------------------------------
    def _bootstrap_env(self):
        """修复 CST COM 加载常见问题：
        - cwd 不在 CST 根目录 → WinError 11 (ERROR_BAD_FORMAT)
        - PATH 被宿主 scrub 导致 DLL 找不到
        - 当前线程未 CoInitialize
        """
        lib = os.path.join(self.cst_root, "AMD64", "python_cst_libraries")
        if os.path.isdir(lib) and lib not in sys.path:
            sys.path.insert(0, lib)

        try:
            if os.path.isdir(self.cst_root):
                os.chdir(self.cst_root)
        except Exception:
            pass

        try:
            import winreg as _wr
            with _wr.OpenKey(_wr.HKEY_LOCAL_MACHINE,
                             r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment") as k:
                syspath, _ = _wr.QueryValueEx(k, "Path")
            cur = os.environ.get("PATH", "")
            missing = [p for p in syspath.split(";") if p and p not in cur]
            if missing:
                os.environ["PATH"] = cur + ";" + ";".join(missing)
        except Exception:
            pass

        os.environ.setdefault("SystemRoot", r"C:\Windows")
        os.environ.setdefault("COMSPEC", r"C:\Windows\system32\cmd.exe")
        os.environ.setdefault("PROCESSOR_ARCHITECTURE", "AMD64")

        try:
            import pythoncom
            pythoncom.CoInitialize()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # COM 单例锁
    # ------------------------------------------------------------------
    def _acquire_lock(self):
        """获取 CST 独占锁。cst.lock 存在且持有进程活着 → 拒绝；否则写入本进程 PID。"""
        if os.path.exists(self.lock_file):
            old_pid = -1
            try:
                old_pid = int(open(self.lock_file).read().strip() or 0)
            except (ValueError, OSError):
                pass
            if old_pid > 0:
                alive = True
                try:
                    os.kill(old_pid, 0)
                except (ProcessLookupError, PermissionError):
                    alive = False
                except Exception:
                    alive = False
                if alive:
                    raise RuntimeError(
                        f"CST 被 PID {old_pid} 占用(cst.lock)；"
                        f"确认无批处理后删除 {self.lock_file} 再试"
                    )
            try:
                os.remove(self.lock_file)
            except OSError:
                pass
        os.makedirs(self.work_dir, exist_ok=True)
        with open(self.lock_file, "w") as f:
            f.write(str(os.getpid()))
        self._lock_held = True

    def _release_lock(self):
        if self._lock_held and os.path.exists(self.lock_file):
            try:
                os.remove(self.lock_file)
            except OSError:
                pass
            self._lock_held = False

    # ------------------------------------------------------------------
    # 连接
    # ------------------------------------------------------------------
    def connect(self, force_restart=False, retries=2):
        """连接 CST Design Environment。
        优先连已运行 DE，否则拉起新 CST。含自动重试。
        """
        self._bootstrap_env()

        if force_restart:
            self._kill_cst()
            time.sleep(5)

        self._acquire_lock()

        import cst.interface as ci
        last_err = None

        for attempt in range(retries + 1):
            try:
                if attempt > 0:
                    time.sleep(5)
                des = ci.running_design_environments()
                if des:
                    self.de = ci.DesignEnvironment.connect(des[0])
                    self.de.get_open_projects()
                else:
                    self.de = ci.DesignEnvironment()
                    time.sleep(5)
                return self.de
            except Exception as e:
                last_err = e
                self._kill_cst()
                time.sleep(6)

        raise RuntimeError(f"CST 连接失败({retries+1}次): {str(last_err)[:300]}")

    def _kill_cst(self):
        """杀掉 CST 进程树。"""
        subprocess.run(
            ["taskkill", "/IM", "CST DESIGN ENVIRONMENT_AMD64.exe", "/F", "/T"],
            capture_output=True
        )

    def is_healthy(self):
        """轻量探活。"""
        if self.de is None:
            return False
        try:
            self.de.get_open_projects()
            return True
        except Exception:
            return False

    # ------------------------------------------------------------------
    # 项目操作
    # ------------------------------------------------------------------
    def open_project(self, path):
        """打开 .cst 项目，返回 model3d。"""
        if self.de is None:
            self.connect()
        safe = self._safe_path(path, must_exist=True)
        self.project = self.de.open_project(safe)
        self.m3d = self.project.model3d
        return self.m3d

    def new_project(self):
        """新建 MWS 项目，返回 model3d。"""
        if self.de is None:
            self.connect()
        self.project = self.de.new_mws()
        self.m3d = self.project.model3d
        return self.m3d

    def save(self, path=None):
        """保存项目。path 必须纯英文。"""
        if self.project is None:
            raise RuntimeError("无打开的项目")
        if path:
            safe = self._safe_path(path)
            self.project.save(safe)
        else:
            self.project.save()

    def rebuild(self):
        """重建模型（参数修改后调用）。"""
        if self.m3d:
            self.m3d.Rebuild()
            time.sleep(2)

    # ------------------------------------------------------------------
    # 看门狗
    # ------------------------------------------------------------------
    def watch(self, fn, timeout=900, *args, **kwargs):
        """带超时的调用封装。超时抛 RuntimeError（不杀进程）。"""
        box = {}

        def worker():
            try:
                box["r"] = fn(*args, **kwargs)
                box["ok"] = True
            except Exception as e:
                box["ok"] = False
                box["err"] = str(e)[:300]

        th = threading.Thread(target=worker, daemon=True)
        th.start()
        th.join(timeout)
        if "ok" not in box:
            raise RuntimeError(f"操作超时(>{timeout}s)，建议重启 CST 会话后重试")
        if not box["ok"]:
            raise RuntimeError(box["err"])
        return box.get("r")

    def solve_and_wait(self, timeout=1800):
        """启动求解器并等待空闲。"""
        if self.m3d is None:
            raise RuntimeError("无打开的项目")
        self.m3d.add_to_history("start_fd", "FDSolver.Start")
        deadline = time.monotonic() + timeout
        while self.m3d.is_solver_running():
            if time.monotonic() > deadline:
                raise RuntimeError(f"求解器 >{timeout}s 未空闲")
            time.sleep(10)

    # ------------------------------------------------------------------
    # 安全路径
    # ------------------------------------------------------------------
    def _safe_path(self, path, must_exist=False):
        """校验路径必须位于 work_dir 下，防止路径遍历。"""
        if not path or not isinstance(path, str):
            raise ValueError("路径不能为空")
        if "://" in path or path.startswith("\\\\"):
            raise ValueError("不允许网络路径或 URL")
        if os.path.isabs(path):
            resolved = os.path.realpath(path)
        else:
            resolved = os.path.realpath(os.path.join(self.work_dir, path))
        work_real = os.path.realpath(self.work_dir)
        if resolved != work_real and not resolved.startswith(work_real + os.sep):
            raise ValueError(f"路径越界：必须位于 {self.work_dir} 下")
        if must_exist and not os.path.exists(resolved):
            raise ValueError(f"路径不存在：{resolved}")
        return resolved

    # ------------------------------------------------------------------
    # 清理
    # ------------------------------------------------------------------
    def close(self, kill_cst=False):
        """关闭会话。kill_cst=True 时杀掉 CST 进程。"""
        try:
            if self.project:
                self.project.close()
        except Exception:
            pass
        try:
            if self.de:
                self.de.close()
        except Exception:
            pass
        self._release_lock()
        if kill_cst:
            self._kill_cst()
        self.de = None
        self.project = None
        self.m3d = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.close()


# ------------------------------------------------------------------
# 便捷函数
# ------------------------------------------------------------------
def quick_connect(cst_root=None, work_dir=None):
    """快速连接 CST，返回 CSTSession。"""
    sess = CSTSession(cst_root=cst_root, work_dir=work_dir)
    sess.connect()
    return sess


if __name__ == "__main__":
    # 自检
    print("CST Session 模块自检")
    print(f"  CST_ROOT: {DEFAULT_CST_ROOT}")
    print(f"  WORK_DIR: {DEFAULT_WORK_DIR}")
    print("  用法: from cst_session import CSTSession")