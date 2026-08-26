#!/usr/bin/env python3
"""PreToolUse hook: no edit to tracked project files without a GitHub issue on record.

Optional pattern for a repo that wants every change to trace to an issue. Pair it with
an issue-tracking workflow (e.g. this toolkit's `commands/issue-workflow/start-issue.md`)
that writes `.claude/.current-issue`; until that file exists, Edit and Write on tracked
files are denied.

Run with --session-start to instead print the active issue as session context.

Deliberately NOT gated:
  * paths outside the repo (scratchpad, ~/.claude/plans)
  * .claude/** -- otherwise this config could never be set up or repaired

Known gap: this covers Edit/Write, not shell redirection through Bash. Gating all of
Bash would cost far more than the loophole is worth.
"""

import json
import os
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _toolchain import (  # noqa: E402
    git_branch,
    project_dir,
    read_payload,
    relative_to_project,
    target_path,
)

RECORD_NAME = os.path.join(".claude", ".current-issue")
MAIN_BRANCH = "main"
EXEMPT_PREFIXES = (".claude/",)


def record_path() -> str:
    """Absolute path to the current-issue record file."""

    return os.path.join(project_dir(), RECORD_NAME)


def load_record() -> dict[str, Any] | None:
    """Parses the current-issue record, or None if missing/invalid/empty."""

    try:
        with open(record_path(), "r", encoding="utf-8") as handle:
            record = json.load(handle)
    except (OSError, ValueError):
        return None
    if not isinstance(record, dict) or not record.get("issues"):
        return None
    return record


def issue_list(record: dict[str, Any]) -> str:
    """Formats a record's issue numbers as a comma-separated `#n, #m` string."""

    return ", ".join("#{}".format(n) for n in record.get("issues", []))


def deny(reason: str) -> int:
    """Writes a PreToolUse deny decision with `reason` to stdout."""

    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        },
        sys.stdout,
    )
    sys.stdout.write("\n")
    return 0


def session_start() -> int:
    """Writes SessionStart context describing the active issue record, if any."""

    record = load_record()
    if not record:
        context = (
            "No issue is on record for this repo. If this repo requires every "
            "change to trace to an issue, run the repo's start-work command "
            "(e.g. /start-issue <number>) before editing any tracked file."
        )
    else:
        context = (
            "Active issue(s): {issues} on branch `{branch}` (recorded {when}). "
            "Keep the work scoped to these issues; re-run the start-work command "
            "to change them.".format(
                issues=issue_list(record),
                branch=record.get("branch", "?"),
                when=record.get("recorded", "?"),
            )
        )
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


def main() -> int:
    """Entry point: dispatches to --session-start or the PreToolUse deny check."""

    if "--session-start" in sys.argv:
        return session_start()

    abs_path = target_path(read_payload())
    if not abs_path:
        return 0

    rel = relative_to_project(abs_path)
    if rel is None or rel.startswith(EXEMPT_PREFIXES):
        return 0

    record = load_record()
    if not record:
        return deny(
            "No issue on record, so `{}` cannot be edited. Every change in this "
            "repo must trace to an issue. Run the repo's start-work command "
            "(e.g. /start-issue <number>) first, opening one from this repo's "
            "issue templates if none covers this work.".format(rel)
        )

    branch = git_branch()
    if branch == MAIN_BRANCH:
        return deny(
            "Refusing to edit `{}` on `{}`. Work happens on a "
            "`<type>/<description>` branch -- run the repo's start-work command "
            "to create one.".format(rel, MAIN_BRANCH)
        )

    recorded_branch = record.get("branch")
    if branch and recorded_branch and branch != recorded_branch:
        return deny(
            "The issue record is stale: {issues} was recorded for branch "
            "`{recorded}`, but HEAD is `{actual}`. Re-run the repo's start-work "
            "command to record the issue(s) for this branch.".format(
                issues=issue_list(record),
                recorded=recorded_branch,
                actual=branch,
            )
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
