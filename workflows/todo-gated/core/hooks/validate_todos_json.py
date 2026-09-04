#!/usr/bin/env python3
"""PostToolUse hook: re-validate todos.json after a todos.py call.

Runs after every Bash tool call. If the command invoked todos.py, it re-runs the
CLI's own `validate` subcommand and surfaces a schema error immediately -- this
catches a bug in the CLI (or a hand-edit that slipped past the PreToolUse gate)
before the broken state is built on.

Deliberately narrow: it only fires when "todos.py" appears in the command, and
it never rewrites anything -- it reports and lets the session fix it.
"""

import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _hooklib import project_dir, read_payload  # noqa: E402

# Resolve against the consuming repo (via $CLAUDE_PROJECT_DIR), not the script's
# own location -- scripts/ is a symlink into the shared store.
TODOS_CLI = Path(project_dir()) / ".claude" / "scripts" / "todos.py"


def main():
    """Validate todos.json if the just-run command invoked todos.py."""
    command = (read_payload().get("tool_input") or {}).get("command", "")
    if "todos.py" not in command:
        return 0

    result = subprocess.run(
        [sys.executable, str(TODOS_CLI), "validate"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(
            "todos.json failed validation after a todos.py call:\n"
            + result.stderr,
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
