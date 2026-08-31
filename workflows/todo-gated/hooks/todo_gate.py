#!/usr/bin/env python3
"""PreToolUse hook: no edit to tracked project files without a tracked todo.

Every change in this repo traces to an entry in .claude/todos.json. This
enforces that mechanically instead of relying on remembering it.

/start-todo records the active todo(s) in .claude/.current-todo; until it does,
Edit and Write on tracked files are denied. It also refuses any edit made on the
default branch, and refuses a record written for a different branch.

.claude/todos.json itself may only be changed through .claude/scripts/todos.py
(so the schema and the .current-todo sidecar stay in sync) -- a direct Edit/Write
on it is denied here too.

Run with --session-start to instead print the active todo as session context.

Deliberately NOT gated:
  * paths outside the repo (scratchpad, ~/.claude/plans)
  * .claude/** -- otherwise this config could never be set up or repaired
    (todos.json is the one exception, funnelled through todos.py)

Known gap: this covers Edit/Write, not shell redirection through Bash. Gating
all of Bash would cost far more than the loophole is worth.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _hooklib import (  # noqa: E402
    git_branch,
    project_dir,
    read_payload,
    relative_to_project,
    target_path,
)

RECORD_NAME = os.path.join(".claude", ".current-todo")
TODOS_NAME = ".claude/todos.json"
# INIT: set to the repo's default branch if it is not "main".
MAIN_BRANCH = "main"
EXEMPT_PREFIXES = (".claude/",)


def record_path():
    return os.path.join(project_dir(), RECORD_NAME)


def load_record():
    try:
        with open(record_path(), "r", encoding="utf-8") as handle:
            record = json.load(handle)
    except (OSError, ValueError):
        return None
    if not isinstance(record, dict) or not record.get("todos"):
        return None
    return record


def todo_list(record):
    return ", ".join("#{}".format(n) for n in record.get("todos", []))


def deny(reason):
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


def session_start():
    record = load_record()
    if not record:
        context = (
            "No tracked todo is on record for this repo. Every change here must "
            "trace to an entry in .claude/todos.json: run /start-todo <id> "
            "before editing any tracked file, or /create-todo <description> to "
            "draft one first. Edits are blocked until then."
        )
    else:
        context = (
            "Active todo(s): {todos} on branch `{branch}` (recorded {when}). "
            "Keep the work scoped to these todos; run /start-todo again to "
            "change them.".format(
                todos=todo_list(record),
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


def main():
    if "--session-start" in sys.argv:
        return session_start()

    abs_path = target_path(read_payload())
    if not abs_path:
        return 0

    rel = relative_to_project(abs_path)
    if rel is None:
        return 0

    if rel == TODOS_NAME:
        return deny(
            "`{}` is only changed through `.claude/scripts/todos.py "
            "<subcommand>`, never Edit/Write -- that keeps the file and the "
            "`.claude/.current-todo` session record in sync. Run the CLI "
            "instead (`todos.py add`, `todos.py update-status`, ...).".format(rel)
        )

    if rel.startswith(EXEMPT_PREFIXES):
        return 0

    record = load_record()
    if not record:
        return deny(
            "No tracked todo on record, so `{}` cannot be edited. Every change "
            "in this repo must trace to a todo. Run `/start-todo <id>` first, "
            "or `/create-todo <description>` to draft one if none covers this "
            "work.".format(rel)
        )

    branch = git_branch()
    if branch == MAIN_BRANCH:
        return deny(
            "Refusing to edit `{}` on `{}`. Work happens on a "
            "`<type>/<description>` branch -- run `/start-todo <id>` to create "
            "one.".format(rel, MAIN_BRANCH)
        )

    recorded_branch = record.get("branch")
    if branch and recorded_branch and branch != recorded_branch:
        return deny(
            "The todo record is stale: {todos} was recorded for branch "
            "`{recorded}`, but HEAD is `{actual}`. Run `/start-todo <id>` to "
            "record the todo(s) for this branch.".format(
                todos=todo_list(record),
                recorded=recorded_branch,
                actual=branch,
            )
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
