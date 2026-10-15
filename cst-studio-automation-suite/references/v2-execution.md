# CST 2025 Agent execution layer

The local MCP bridge uses the optional official Python `mcp` package (`mcp.server.fastmcp.FastMCP`).
The bridge is deliberately narrow: environment health, offline script generation, Touchstone analysis, and a single approved unit-cell workflow.

## Windows setup
1. Extract this Skill to your Agent's skills folder and load SKILL.md.
2. Install CST Studio Suite 2025 and confirm the bundled `AMD64\python\python.bat` works.
3. In a Python environment compatible with your MCP host, install `mcp` (using your organization's trusted package source). The host need not be the CST-bundled interpreter: the bridge launches the CST script using `CST_PYTHON_EXE`.
4. Set `CST_HOME`, `CST_WORK_DIR`, `CST_PYTHON_EXE` and a random `CST_APPROVAL_TOKEN`. Keep this token private and do not put it in chat transcripts or committed config.
5. Adapt `examples/mcp-2025.example.json` and register the server in your Agent MCP host.
6. Call health first; for a live test review `scripts/build_unitcell.py`, back up existing files, and call `cst2025_run_unitcell` only with explicit authorization.

## Scope and caveats
- `cst2025_run_unitcell` runs the original local `build_unitcell.py` with its predefined PARAMS, not arbitrary AI-generated code. It may create a project and invoke CST; requires explicit approval.
- Offline generated job is a scaffold and is not a solved CST model.
- The parser reports S11 and reflection-only inferred absorption. The latter is physically valid only if transmission is negligible; otherwise A=1-|S11|^2-|S21|^2.
- Do not trust reported success unless CST produced the expected saved project and logs are reviewed.
- This package has offline tests only; CST runtime testing must be performed on your Windows machine.
- Never use two executors against the same CST project concurrently.
