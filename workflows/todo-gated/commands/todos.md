---
description: List backlogged and in-progress todo items with their IDs, headers, status, and subtasks.
argument-hint: (no arguments)
---

List every backlogged and in-progress item tracked in `.claude/todos.json`. Run:

```bash
python3 "$CLAUDE_PROJECT_DIR/.claude/scripts/todos.py" list \
  || python "$CLAUDE_PROJECT_DIR/.claude/scripts/todos.py" list
```

Render its output to the user as-is — one line per top-level item
(`[status] id: header`), with any subtasks indented beneath their parent. Do not
filter, reformat, or summarize further; this command has no side effects and does
not enter plan mode or touch git.

If the user wants completed items too, re-run the same command with
`--status completed` appended. To pick something to work on, hand off to
`/start-todo <id> [more...]` — that is what records the todo and cuts the branch.
No tracked file can be edited until it runs.
