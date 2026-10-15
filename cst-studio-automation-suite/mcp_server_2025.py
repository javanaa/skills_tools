"""Local stdio MCP adapter for CST 2025. Install the optional `mcp` package."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'scripts'))
from cst2025_bridge import health, generate_job, analyze_s1p, run_unitcell
try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:
    raise SystemExit('Missing MCP SDK: install the Python mcp package in this environment') from exc
mcp=FastMCP('cst2025-local')
mcp.tool(name='cst2025_health')(health)
mcp.tool(name='cst2025_generate_job')(generate_job)
mcp.tool(name='cst2025_analyze_s1p')(analyze_s1p)
mcp.tool(name='cst2025_run_unitcell')(run_unitcell)
if __name__=='__main__':
    mcp.run(transport='stdio')
