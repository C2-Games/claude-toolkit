#!/usr/bin/env python3
"""Runs a shell command through the best available shell, wherever that lives.

    python3 hooks/toolchain/toolchain_run.py 'bash scripts/ci-local.sh'

On macOS/Linux, or Windows with a native POSIX shell, this runs the command
directly. On Windows without one, it re-execs through WSL. Slash commands can
call this instead of naming a shell directly, so a single command file works
across platforms.

Output streams live (some commands are slow and silence is unhelpful) and the
child's exit status is propagated. `--where` prints the resolved environment
instead of running anything.
"""

import os
import subprocess
import sys
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _toolchain import needs_wsl, project_dir, toolchain_argv  # noqa: E402


def main(argv: Sequence[str]) -> int:
    """Parses `argv` and either prints the resolved environment or runs the command."""

    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__.strip())
        return 0

    if argv[0] == "--where":
        print("platform : {}".format(sys.platform))
        print("root     : {}".format(project_dir()))
        print(
            "shell    : {}".format("WSL (wsl.exe)" if needs_wsl() else "native")
        )
        return 0

    # Accept either one quoted script or several words to join.
    script = argv[0] if len(argv) == 1 else " ".join(argv)

    cmd, run_cwd, error = toolchain_argv(script, project_dir())
    if error:
        sys.stderr.write(
            "toolchain_run: {}\n"
            "Install a POSIX shell (bash/sh) or, on Windows, ensure WSL is "
            "available.\n".format(error)
        )
        return 127

    assert cmd is not None  # error is None, so toolchain_argv resolved a command.

    try:
        # No capture: stream straight through to the caller.
        return subprocess.call(cmd, cwd=run_cwd)
    except OSError as exc:
        sys.stderr.write("toolchain_run: {}\n".format(exc))
        return 127


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
