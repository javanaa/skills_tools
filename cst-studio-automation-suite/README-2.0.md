# CST Studio Automation Suite 2.0 (CST 2025 first)
Preserves the original Skill, references, materials and scripts from the uploaded archive, adds a narrow optional MCP stdio bridge, tests and setup instructions.

## Quick start
- Extract this directory to the self-hosted Agent skills folder; register `SKILL.md` with your skill loader.
- On the Windows CST host, configure `CST_HOME`, `CST_WORK_DIR`, `CST_PYTHON_EXE`, and a private `CST_APPROVAL_TOKEN`.
- Install the `mcp` Python SDK in the bridge host environment.
- Adapt `examples/mcp-2025.example.json` and connect via your Agent's MCP host.
- Test: `python -m unittest discover -s tests -v` and `python scripts/validate_environment.py`.
- Invoke `cst2025_health`, then try `cst2025_generate_job` and `cst2025_analyze_s1p` offline.
- Only after local review and explicit approval, invoke `cst2025_run_unitcell` with a private token.

No live CST test was performed here. This is not a universal adapter for all GitHub CST repositories: those remain separate optional integrations subject to compatibility testing and license review.
