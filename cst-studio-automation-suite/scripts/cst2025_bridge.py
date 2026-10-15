"""Narrow, auditable CST 2025 executor; stdlib only."""
import ast
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import threading

ROOT = Path(__file__).resolve().parents[1]
_LOCK = threading.Lock()

def health():
    home = Path(os.environ.get('CST_HOME', '')) if os.environ.get('CST_HOME') else None
    work = Path(os.environ.get('CST_WORK_DIR', '')) if os.environ.get('CST_WORK_DIR') else None
    exe = Path(os.environ.get('CST_PYTHON_EXE', '')) if os.environ.get('CST_PYTHON_EXE') else None
    return {'platform': sys.platform, 'cst_home_exists': bool(home and home.is_dir()),
            'work_dir_exists': bool(work and work.is_dir()),
            'cst_python_exists': bool(exe and exe.is_file()),
            'execution_configured': bool(sys.platform=='win32' and home and home.is_dir() and work and work.is_dir() and exe and exe.is_file())}

def generate_job(name, frequency_ghz):
    if not name or not name.replace('_','').replace('-','').isalnum():
        raise ValueError('Job name must be alphanumeric, underscore or hyphen')
    f=float(frequency_ghz)
    if not math.isfinite(f) or not 0<f<1000: raise ValueError('Frequency must be finite and in (0,1000) GHz')
    code=f"""# CST 2025 review-only scaffold; not a solved model.
NAME = {name!r}
FREQUENCY_GHZ = {f!r}

def main():
    print("REVIEW REQUIRED: implement verified CST 2025 geometry and solver calls")

if __name__ == "__main__":
    main()
"""
    ast.parse(code)
    return {'status':'generated_not_executed','filename':name+'.py','source':code}

def analyze_s1p(path):
    p=Path(path).resolve(strict=True)
    if p.suffix.lower()!='.s1p' or not p.is_file(): raise ValueError('Require a .s1p file')
    if p.stat().st_size>20_000_000: raise ValueError('File too large')
    from parse_s11 import parse_s1p, compute_absorption
    freq,a,b,fmt=parse_s1p(str(p))
    if fmt not in ('RI','DB','MA') or not freq: raise ValueError('Unsupported or empty Touchstone data')
    absorption,db=compute_absorption(freq,a,b,fmt)
    if not all(math.isfinite(x) for x in freq+db+absorption): raise ValueError('Nonfinite result')
    i=min(range(len(db)),key=lambda j:db[j])
    return {'status':'parsed_not_simulated','points':len(freq),'format':fmt,'frequency_units':'as_in_file_header_unverified',
            'minimum_s11_db':db[i],'frequency_at_minimum_raw':freq[i],
            'reflection_only_absorption_at_minimum':absorption[i],
            'warning':'Absorption assumes S21=0; verify ground plane and Touchstone frequency units.'}

def run_unitcell(approval_token, timeout_seconds=900):
    expected=os.environ.get('CST_APPROVAL_TOKEN','')
    if not expected or approval_token!=expected: raise PermissionError('Explicit local approval token required')
    status=health()
    if not status['execution_configured']: raise RuntimeError('CST 2025 execution environment not configured')
    timeout=int(timeout_seconds)
    if not 30<=timeout<=7200: raise ValueError('timeout_seconds must be 30..7200')
    if not _LOCK.acquire(blocking=False): raise RuntimeError('CST operation already running')
    try:
        work=Path(os.environ['CST_WORK_DIR']).resolve()
        # Prevent silent overwrite of known output project.
        if (work/'unitcell_benchmark.cst').exists(): raise FileExistsError('Project exists; back it up or choose a clean work directory')
        script=ROOT/'scripts'/'build_unitcell.py'
        cmd=[os.environ['CST_PYTHON_EXE'],str(script)]
        result=subprocess.run(cmd,cwd=str(work),capture_output=True,text=True,timeout=timeout,check=False)
        return {'status':'process_completed' if result.returncode==0 else 'process_failed',
                'returncode':result.returncode,'stdout_tail':result.stdout[-6000:],
                'stderr_tail':result.stderr[-6000:],
                'project_exists':(work/'unitcell_benchmark.cst').exists(),
                'note':'Solver validity and outputs still require manual or programmatic verification'}
    finally:
        _LOCK.release()
