"""Shared helpers for running shell commands consistently across platforms.

A repo may be worked on from two very different environments:

  * macOS / Linux -- a POSIX shell (bash/sh) is on PATH, so commands run directly.
  * Windows -- native Windows has no POSIX shell by default; WSL is the common
    fallback for repos whose scripts assume one.

Everything that needs a shell goes through `toolchain_argv()`, so the issue gate
and any slash commands make that decision exactly once and identically.
"""

import os
import shlex
import shutil
import subprocess
import sys

# Nothing here may hang the session waiting on a subprocess.
TOOL_TIMEOUT_SECONDS = 45


def project_dir() -> str:
    """Absolute path to the repo root."""

    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return os.path.abspath(env)
    # hooks/toolchain/_toolchain.py -> repo root
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def to_wsl_path(win_path: str) -> str:
    """Converts `C:\\Users\\me\\repo` to `/mnt/c/Users/me/repo`; passes POSIX paths through."""

    path = os.path.abspath(win_path).replace("\\", "/")
    if len(path) > 1 and path[1] == ":":
        return "/mnt/" + path[0].lower() + path[2:]
    return path


def _wsl_binary() -> str | None:
    """Path to `wsl.exe`, or None if WSL isn't installed."""

    return shutil.which("wsl.exe") or shutil.which("wsl")


def has_posix_shell() -> bool:
    """True when a native POSIX shell (bash or sh) is on PATH here."""

    return bool(shutil.which("bash") or shutil.which("sh"))


def needs_wsl() -> bool:
    """True only on Windows when no native POSIX shell is available."""

    return sys.platform == "win32" and not has_posix_shell()


def toolchain_argv(
    script: str, cwd: str | None = None
) -> tuple[list[str] | None, str | None, str | None]:
    """Resolves `script` to an (argv, run_cwd, error) triple for the right shell.

    Parameters
    ----------
    script : str
        The shell command to run.
    cwd : str | None
        Working directory to run it in. Defaults to the repo root.

    Returns
    -------
    tuple[list[str] | None, str | None, str | None]
        `(argv, run_cwd, error)`. On macOS/Linux, or Windows with a native POSIX
        shell, this is plain `bash -c <script>`. On Windows without one, it
        becomes `wsl.exe -e bash -c "cd <translated cwd> && <script>"`.

    `bash -c`, not `-lc`: sourcing login profiles roughly doubles an already-
    expensive WSL spawn, and most repo scripts don't need a login shell.
    """

    cwd = cwd or project_dir()

    if not needs_wsl():
        shell = shutil.which("bash") or shutil.which("sh")
        if not shell:
            return None, None, "no POSIX shell (bash/sh) found on PATH"
        return [shell, "-c", script], cwd, None

    wsl = _wsl_binary()
    if not wsl:
        return None, None, "no POSIX shell on PATH and wsl.exe not found"
    inner = "cd {} && {}".format(shlex.quote(to_wsl_path(cwd)), script)
    return [wsl, "-e", "bash", "-c", inner], None, None


def git_branch() -> str | None:
    """Current branch name, or None if git is unavailable / detached HEAD."""

    try:
        done = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=project_dir(),
            capture_output=True,
            text=True,
            errors="replace",
            timeout=TOOL_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if done.returncode != 0:
        return None
    branch = done.stdout.strip()
    return branch or None


def read_payload() -> dict:
    """Parses the hook payload from stdin. Returns {} when absent or malformed."""

    import json

    try:
        raw = sys.stdin.read()
    except (OSError, ValueError):
        return {}
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except ValueError:
        return {}


def target_path(payload: dict) -> str | None:
    """The file a Write/Edit payload acts on, as an absolute path, or None."""

    tool_input = payload.get("tool_input") or {}
    response = payload.get("tool_response") or {}
    path = tool_input.get("file_path") or response.get("filePath")
    if not path:
        return None
    return os.path.abspath(path)


def relative_to_project(abs_path: str) -> str | None:
    """Project-relative POSIX path, or None if `abs_path` is outside the repo."""

    root = project_dir()
    try:
        rel = os.path.relpath(abs_path, root)
    except ValueError:  # different drive on Windows
        return None
    if rel.startswith(".."):
        return None
    return rel.replace("\\", "/")
