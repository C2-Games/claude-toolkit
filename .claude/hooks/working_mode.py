#!/usr/bin/env python3
"""SessionStart hook: state the working mode this workflow imposes.

str8-2-main is the relaxed workflow -- no work branch, no issue/todo record, no
edit gate. The one thing that keeps it honest is /check before /ship, so the
session should be reminded of the shape up front (and of how much uncommitted
work is already sitting in the tree).

Pure git, no toolchain. If git is unavailable the hook still emits a usable
message -- it never blocks the session.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _hooklib import git, git_branch  # noqa: E402


def dirty_count():
    """Number of changed/untracked entries in the working tree, or 0."""
    out = git("status", "--porcelain")
    return len([line for line in out.splitlines() if line.strip()])


def main():
    branch = git_branch() or "the default branch"
    context = (
        "str8-2-main workflow: changes land directly on `{branch}` -- no work "
        "branch, no issue/todo tracking, no edit gate. Non-trivial work goes "
        "through plan mode with a task breakdown, then /check (JSON validation + "
        "Markdown lint), then /ship -- which makes a header-only commit "
        "(`type: description`, no body, no trailers) and pushes to `{branch}`. "
        "/check is the only gate between a request and origin.".format(branch=branch)
    )
    dirty = dirty_count()
    if dirty:
        context += " {} uncommitted change(s) in the tree right now.".format(dirty)

    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": context,
            }
        },
        sys.stdout,
    )
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
