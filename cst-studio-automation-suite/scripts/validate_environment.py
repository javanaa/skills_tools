import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path

def inspect(repo=None, require_cst=False):
    report = {
        "python": sys.version.split()[0],
        "platform": sys.platform,
        "mcp_importable": importlib.util.find_spec("mcp") is not None,
        "repo_exists": bool(repo and Path(repo).is_dir()),
        "server_exists": bool(repo and (Path(repo) / "mcp_server.py").is_file()),
        "cst_interface_importable": False,
    }
    try:
        report["cst_interface_importable"] = importlib.util.find_spec("cst.interface") is not None
    except (ImportError, ModuleNotFoundError, ValueError):
        pass
    report["ready_for_mcp_smoke"] = report["mcp_importable"] and report["server_exists"]
    report["ready_for_live_cst"] = report["ready_for_mcp_smoke"] and report["cst_interface_importable"] and sys.platform == "win32"
    report["ok"] = report["ready_for_live_cst"] if require_cst else True
    return report

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--repo")
    parser.add_argument("--require-cst",action="store_true")
    args=parser.parse_args()
    report=inspect(args.repo,args.require_cst)
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0 if report["ok"] else 2

if __name__ == "__main__":
    raise SystemExit(main())
