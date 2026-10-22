#!/usr/bin/env python3
"""Gridline's opt-in, read-only local MCP server for revision-impact analysis.

Requires the official MCP Python SDK v2: python -m pip install 'mcp>=2,<3'
Requires GRIDLINE_MCP_PROJECT_ROOT to name an explicitly authorized project
directory. No write tools, shell execution, network listener, or host mutations.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from revision_impact import analyze, read_spec

MAX_SPEC_SIZE = 5_000_000


def project_file(path: str, root: Path) -> Path:
    if not isinstance(path, str) or not path or "\x00" in path:
        raise ValueError("A non-empty project-relative JSON path is required")
    root = root.expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Project root must be a directory")
    requested = Path(path)
    if requested.is_absolute() or ".." in requested.parts:
        raise ValueError("Only project-relative JSON files within the authorized directory are allowed")
    candidate = (root / requested).resolve(strict=False)
    if not candidate.is_relative_to(root) or candidate.suffix.lower() != ".json":
        raise ValueError("The path must be a JSON file within the authorized project directory")
    if not candidate.is_file():
        raise ValueError("The authorized project JSON file was not found")
    if candidate.stat().st_size > MAX_SPEC_SIZE:
        raise ValueError("Project JSON exceeds the 5 MB read limit")
    return candidate


def compare_revisions(before: str, after: str, project_root: str | None = None) -> dict:
    """Compare two explicitly provided project JSON files; never alter them."""
    root = project_root or os.environ.get("GRIDLINE_MCP_PROJECT_ROOT", "")
    if not root:
        raise ValueError("GRIDLINE_MCP_PROJECT_ROOT must be set explicitly")
    base = Path(root)
    return analyze(read_spec(project_file(before, base)), read_spec(project_file(after, base)))


def capabilities() -> dict:
    """Accurately describe what this server can and cannot verify."""
    return {
        "server": "Gridline Review",
        "scope": "read_only_local_project_json",
        "tools": ["compare_revisions", "capabilities"],
        "native_autocad_or_revit_connection": False,
        "reads_dxf_or_ifc": False,
        "edits_models": False,
        "coverage": "indexed spec references only; unindexed sheets require human review",
    }


def main() -> int:
    if not os.environ.get("GRIDLINE_MCP_PROJECT_ROOT"):
        print("ERROR: Set GRIDLINE_MCP_PROJECT_ROOT before launching Gridline MCP.", file=sys.stderr)
        return 2
    try:
        from mcp.server.mcpserver import MCPServer  # MCP official Python SDK v2
        from mcp.server.mcpserver.exceptions import ToolError
    except ImportError:
        print("ERROR: install official MCP Python SDK v2: pip install 'mcp>=2,<3'", file=sys.stderr)
        return 2
    server = MCPServer("Gridline Review")

    @server.tool()
    def compare_gridline_revisions(before: str, after: str) -> dict:
        """Read two building spec JSON files under the authorized project root; list impacted sheets and schedules."""
        try:
            return compare_revisions(before, after)
        except (ValueError, OSError, KeyError, TypeError) as exc:
            raise ToolError(str(exc)) from exc

    @server.tool()
    def get_gridline_capabilities() -> dict:
        """Describe read-only capabilities and verification limits."""
        return capabilities()

    server.run(transport="stdio")
    return 0


if __name__ == "__main__":
    sys.exit(main())
