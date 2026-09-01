---
description: Record the todo(s) for this work, cut the branch, and enter plan mode
argument-hint: <todo-id> [more-todo-ids...]
---

Start work on todo(s): **$ARGUMENTS**

No tracked project file can be edited until this command has recorded a todo — the
`PreToolUse` gate in `.claude/hooks/todo_gate.py` denies those edits outright
(`.claude/**` is exempt). Run this first, every time.

Every `todos.py` call below runs as
`python3 "$CLAUDE_PROJECT_DIR/.claude/scripts/todos.py" <args> || python "$CLAUDE_PROJECT_DIR/.claude/scripts/todos.py" <args>`
— never edit `.claude/todos.json` directly (a hook blocks that anyway).

## Steps

1. **Resolve the ids.** Run `todos.py list --json` and match each argument to an
   existing top-level todo id. `start-session` takes **top-level ids only** — if an
   argument is a subtask id (`3.1`), stop and tell the user to pass the parent
   (`3`). If any id cannot be found, stop and name the one that failed rather than
   guessing.

2. **Confirm scope.** Summarise each todo's `header`/`description` in a sentence. If
   the todos do not plausibly belong on one branch, say so and ask before
   continuing.

3. **Derive the branch name** from the *first* todo's `header`, as
   `<type>/<kebab-description>`:

   | Header prefix / nature | Branch prefix |
   |---|---|
   | `feat:` / new capability | `feat/` |
   | `fix:` / defect | `fix/` |
   | `refactor:` / internal restructure | `refactor/` |
   | `docs:` | `docs/` |
   | `test:` | `test/` |
   | `chore:` / anything else | `chore/` |

   Only ask the user via `AskUserQuestion` if the type is genuinely ambiguous.
   Match whatever the repo's history already uses (`feat/` vs `feature/` etc.).
   Keep `<kebab-description>` short: at most 4 words, ideally 2-3, derived from the
   todo header — not from the numeric id. When a session covers several todo ids,
   the slug summarises the combined work.

3.5. **Decide whether to isolate this in a worktree.** Ask the user explicitly — do
   not decide silently — when either signal fires:

   - the request itself said "parallel", "worktree", or "isolated", or
   - `.claude/.current-todo` already exists and records a *different* branch (another
     todo is already active in this checkout).

   If neither fires, skip to step 4 — single-track is the default.

4. **Create the branch.**

   **No worktree (default):** from an up-to-date default branch:
   `git fetch origin && git switch -c <branch> origin/main`
   If the branch already exists, `git switch <branch>` instead. (Use the repo's
   actual default branch if it is not `main`.)

   **Worktree (only if step 3.5 confirmed isolation):** call
   `EnterWorktree(name: <branch>)` instead. It creates the worktree under
   `.claude/worktrees/<branch>` off the default branch and switches the session into
   it. Confirm the branch it actually created — if it differs, record the real name
   in step 5.

5. **Record the session.** Run `todos.py start-session <ids> <branch>` with `<ids>`
   a comma-joined list of the resolved top-level ids (e.g. `3` or `3,4`). This flips
   each todo to `in_progress` in `todos.json` and writes `.claude/.current-todo`
   (`{"todos": [...], "branch": "<branch>", "recorded": "<date>", "started": "<ts>"}`)
   — the record the gate reads.

6. **Confirm** the todo ids, the branch, and that the gate is now open.

7. **Enter plan mode** — call `EnterPlanMode`, then read the code the todo(s) touch
   and produce an implementation plan before writing anything. Do not start editing
   straight from the todo text: todos are often terse and understate which files
   move.

   **Exception — small changes skip formal plan mode.** A single-file edit that is
   purely documentation/comment text, or a genuine one-line fix, does not need
   `EnterPlanMode`: state the change in one sentence and proceed. Keep the bar
   genuinely small and single-file.

   **Ask before finalizing.** Ask clarifying implementation questions rather than
   guessing. Design and architecture decisions are the developer's to drive — the
   plan's job is to implement that precisely, not to invent architecture unprompted.

   **Check the plan against architecture before presenting it.** Once the plan's
   tasks are drafted, if any touch source code, dispatch the `architecture-checker`
   agent (`.claude/agents/architecture-checker.md`) with the plan's task list before
   calling `ExitPlanMode`. It reads the plan against `.claude/ARCHITECTURE.md`'s
   rules and hands back any violation plus an architecture-preserving alternative —
   `AskUserQuestion` is unavailable inside subagents, so it hands the finding back.
   If it reports a violation, ask the developer via `AskUserQuestion` which way to
   go: adopt the alternative, proceed as planned and note the `ARCHITECTURE.md`
   update this will require, or revise the plan — then fold the answer in. If it
   reports no violations (or that `ARCHITECTURE.md` holds no rules yet), say so in
   one line and continue. Skip this step entirely when the plan touches no source.

   The plan should name the specific files and symbols to change, follow the
   conventions in `.claude/CLAUDE.md` if the repo has one, and **must end with
   `/check`**. Nothing is checked while you write — there is no write-time hook — so
   a plan without `/check` ships unverified code. Present it with `ExitPlanMode` for
   approval.

   **Break the plan into isolated tasks**, each written with this structure so
   parallel-dispatch eligibility is obvious at a glance:

   ```text
   ### Task <N>: <short title> — todo #<todo-id>
   **Subagent:** implementer
   **Depends on:** Task <M> | independent
   ```

   followed by the task's description. Once approved (`ExitPlanMode`), dispatch every
   task marked `independent` (relative to what's already landed) in parallel to the
   `implementer` agent (`.claude/agents/implementer.md`) — multiple `Agent` tool
   calls in a single message. Run a task with a `Depends on` marker only after that
   dependency's implementer call has returned and been folded in.

   **Mirror the breakdown as tracked tasks.** Before calling `ExitPlanMode`, call
   `TaskCreate` once per task (`subject` = the short title, `description` = the
   task's description) and follow with `TaskUpdate` to set `owner` to the subagent
   name and `addBlockedBy` to the ids of the tasks it depends on. Mark each task
   `completed` as its implementer dispatch returns. Skip this for a single-task
   plan.

   **Include a `CLAUDE.md` step when the change earns one** — only if the repo has a
   `.claude/CLAUDE.md`. Update it for: a new subsystem or file-layout change,
   ownership moving between modules, a changed convention, or a placeholder becoming
   a real implementation. Skip it for renames, small refactors, and bugfixes — it is
   a map, not a changelog. State either way in the plan so the reviewer can
   disagree.

   **If implementation surfaces something that would change the approved plan** —
   not a small in-scope detail, but a real departure from what was approved — stop,
   explain the hurdle, and ask the developer how to proceed. Do not improvise past
   it.

8. **Store the approved plan.** Right after `ExitPlanMode` is approved, run
   `todos.py set-plan <first-id> "<the plan text>"` so a later session picking the
   todo back up can see what was agreed.

Do not commit or push — those are denied by `.claude/settings.json` and are the
user's to run via `/finish`.
