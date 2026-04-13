"""Verify that server startup emits nothing on stdout.

stdout is reserved for MCP stdio transport. Any output there
(log messages, dotenv warnings, etc.) breaks the JSON-RPC framing.
"""

import subprocess
import sys
from pathlib import Path

SERVER_PY = Path(__file__).resolve().parents[1] / "src" / "server.py"


def test_no_stdout_on_import():
    """Importing server.py must not write to stdout."""
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; sys.path.insert(0, 'src'); import server",
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=SERVER_PY.parent.parent,
        env={
            **dict(__import__("os").environ),
            "DOTENV_CONFIG_QUIET": "true",
            "PYTHONIOENCODING": "utf-8",
        },
    )
    assert result.stdout == "", (
        f"stdout must be empty for stdio transport, got: {result.stdout!r}"
    )
