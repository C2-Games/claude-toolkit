---
description: Draft new todos.json item(s) from a freeform description by dispatching the todo-drafter agent to analyze the codebase and append properly-scoped entries.
argument-hint: <freeform description of the work>
---

You are drafting one or more new tracked items for `.claude/todos.json` from a
freeform description: **$ARGUMENTS**

Unlike `/start-todo`, this command does **not** enter plan mode, does **not** create
or switch git branches, and does **not** open the edit gate — drafting a todo is not
itself implementation work, so it runs entirely on the current branch. Do not check
out, create, or switch branches.

## 1. Dispatch the todo-drafter agent

Dispatch the `todo-drafter` agent (`.claude/agents/todo-drafter.md`) via the `Agent`
tool. Pass it the full freeform description verbatim, plus enough surrounding context
that it can explore the codebase and ground its drafting in the current code state.
You do not need to restate the agent's own instructions — it explores the repo with
Read/Grep/Glob, applies the one-session-per-todo scoping convention to decide whether
the work is one item, one item with subtasks, or several separate items, and appends
the result to `.claude/todos.json` via `todos.py add` (run through Bash). It touches
no other file.

## 2. Relay the drafter's report to the user

Once `todo-drafter` reports back, relay its final report:

- The exact new todo id(s) it created (e.g. `5`, or with subtasks `5.1`, `5.2`).
- The full header/description of each new item.
- Any scoping rationale it flagged (why it split the work into N items, or folded it
  into one), and any hurdle it hit if it stopped short of appending.

## 3. Point to the next step

Note explicitly that this command does not implement anything — it only drafts and
appends the todo item(s). To start work on one, the user runs `/start-todo <id>`
with the id(s) the drafter reported.

---

**The same dispatch also triggers without `/create-todo`.** When a change is
requested directly, with no todo on record yet and no `/start-todo` run, dispatch
`todo-drafter` with that request first, relay its report, then have the user run
`/start-todo` on the drafted id — never edit tracked files straight from a bare
request.
