import argparse
import ast
import json
from pathlib import Path

TEMPLATE = '''# CST job scaffold; adapt to installed CST Python API before execution.
# This scaffold intentionally performs no CST mutations.
from pathlib import Path

JOB_NAME = {name!r}
PROJECT_PATH = Path({project!r})
FREQUENCY_GHZ = {freq!r}

def main():
    if FREQUENCY_GHZ <= 0:
        raise ValueError("Frequency must be positive")
    print("REVIEW REQUIRED:", JOB_NAME, PROJECT_PATH, FREQUENCY_GHZ)
    print("Implement CST project creation, geometry, materials, ports, mesh and solve using verified installed API.")

if __name__ == "__main__":
    main()
'''

def generate(output, name, project, freq):
    if not name.strip():
        raise ValueError("name must not be empty")
    if not (0 < freq < 1e6):
        raise ValueError("frequency must be positive and reasonable")
    code=TEMPLATE.format(name=name,project=project,freq=freq)
    ast.parse(code)
    out=Path(output)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(code,encoding="utf-8")
    manifest={"name":name,"project":project,"frequency_ghz":freq,"status":"generated_not_executed"}
    out.with_suffix(".json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    p.add_argument("--name",required=True)
    p.add_argument("--project",default="C:/cst_projects/example.cst")
    p.add_argument("--frequency-ghz",type=float,default=2.45)
    a=p.parse_args()
    print(generate(a.output,a.name,a.project,a.frequency_ghz))

if __name__=="__main__":
    main()
