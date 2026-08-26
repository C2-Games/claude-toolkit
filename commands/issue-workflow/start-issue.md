---
description: Record the GitHub issue(s) for this work and cut the branch
argument-hint: <issue-number> [more-issue-numbers...]
---

Start work on issue(s): **$ARGUMENTS**

If this repo has an edit-gate hook tied to issue-tracking (see
`hooks/issue-workflow/issue_gate.py`), nothing under tracked files outside `.claude/` can be edited
until this command has recorded an issue — the hook's `PreToolUse` gate denies those edits outright.
Run this first, every time, in a repo that has that hook wired up.

## Steps

1. **Fetch each issue.** For every number in `$ARGUMENTS`:
   `gh issue view <n> --json number,title,labels,body,milestone`
   If this repo sets `GH_REPO` in `.claude/settings.json`, `gh` resolves the repo automatically
   despite any non-default remote alias. If `gh` is not installed, say so once, accept the bare
   numbers, and ask the user for a one-line description to name the branch from.

1.5. **Load milestone context.** Take the *first* issue's milestone. If it has none, or `gh`
   errors, say so in one line and skip to step 2 — no blocking question for an edge case
   nothing was asked about. Otherwise fetch the full milestone set, both states:
   `gh issue list --state all --milestone "<name>" --json number,title,state,labels,body --limit 200`
   Closed issues in the set are implementation-pattern context (reused again in step 7); open
   ones (excluding the issue(s) being started) feed a lightweight relatedness pass —
   title/label/body overlap for "looks related enough to combine," and dependency language
   ("depends on," "blocks," "after #n") or same-area overlap for "looks like a prerequisite."

   If candidates surface, present them via `AskUserQuestion` — one question per candidate (or
   grouped if several point the same direction) — options: "combine onto this branch," "do
   the other issue first instead," "proceed as-is." Do not continue past this step until
   answered. "Combine" adds that issue's number to the working set used from step 3 onward
   (branch name still derives from the *first* originally-requested issue); "do first" stops
   here and tells the user to run `/start-issue` on that issue instead.

   If nothing surfaces, say so in one sentence and continue automatically — never merge or
   reorder silently, but don't ask when there's nothing to flag.

2. **Confirm scope.** Summarise each issue in a sentence. If the issues do not plausibly
   belong on one branch, say so and ask before continuing.

3. **Derive the branch name** from the *first* issue's title, using the convention
   `<type>/<kebab-description>`:

   | Issue title prefix | Branch prefix |
   |---|---|
   | `feat:` | `feat/` |
   | `fix:` | `fix/` |
   | `refactor:` | `refactor/` |
   | `docs:` | `docs/` |
   | `test:` | `test/` |
   | anything else | `chore/` |

   If this repo has an existing convention that differs (check recent branch names with
   `git branch -a` or past PR titles), match that instead.

   Keep the `<kebab-description>` short: at most 4 words, ideally 2-3. This holds even
   when the issue title is longer — pick the shortest phrase that still identifies the change,
   don't mechanically truncate the title.

3.5. **Decide whether to isolate this in a worktree.** Ask the user explicitly — do not decide
   silently — when either signal fires:
   - the request itself said "parallel", "worktree", or "isolated", or
   - `.claude/.current-issue` already exists and records a *different* branch than the one just
     derived (another issue is already active in this checkout).

   If neither fires, skip straight to step 4 as today — single-track is the default.

4. **Create the branch.**

   **No worktree (default):** from an up-to-date default branch (usually `main`, but confirm
   with `git remote show origin` or the repo's own docs if unsure):
   `git fetch origin && git switch -c <branch> origin/<default-branch>`
   If the branch already exists, `git switch <branch>` instead.

   **Worktree (only if step 3.5 confirmed isolation):** call `EnterWorktree(name: <branch>)`
   instead. Confirm the branch it actually created — if it differs from `<branch>`, record the
   real name in step 5, don't force a rename.

5. **Write the record** to `.claude/.current-issue` (gitignore this file if it isn't already):

   ```json
   {"issues": [108, 112], "branch": "feat/enemy-spawn-tables", "recorded": "<YYYY-MM-DD>"}
   ```

6. **Confirm** the issue numbers, the branch, and (if the edit-gate hook is in use) that the gate
   is now open.

7. **Enter plan mode** — call `EnterPlanMode`, then read the code the issue(s) touch and
   produce an implementation plan before writing anything. Do not start editing straight
   from the issue text: issues are often terse and understate which files move.
   Read the milestone issue list loaded in step 1.5 alongside the target issue's own text:
   closed siblings show established patterns/conventions for this area of the code, open
   ones flag upcoming work the plan shouldn't conflict with.

   **Exception — small changes skip formal plan mode.** A single-file edit that is purely
   documentation/comment text, or a genuine one-line fix, does not need `EnterPlanMode`: state
   the change in one sentence and proceed directly. Keep the bar genuinely small and
   single-file — anything touching real behavior, spanning multiple files, or otherwise
   non-trivial still requires the full flow below.

   **Ask before finalizing.** Ask clarifying implementation questions rather than guessing.
   Design decisions are the developer's to drive — they may hand you intent at the
   pseudo-code level — and the plan's job is to implement that precisely, not to invent
   architecture unprompted. Plans should be made collaboratively, not unilaterally.

   The plan should name the specific files and symbols to change and follow this repo's own
   conventions doc (`CLAUDE.md`/`AGENTS.md`) if one exists. **Include a close-out step**: if this
   repo has a documented format/lint/test command (a `/check`-style slash command, a CI script,
   `make check`, etc.), the plan should end by running it; if none is documented, ask the
   developer what to run, or state explicitly that nothing was found and confirm before finishing
   unverified.

   Present it with `ExitPlanMode` for approval.

   **Break the plan into isolated tasks**, each written with this structure so parallel-dispatch
   eligibility is obvious at a glance instead of inferred from prose:

   ```
   ### Task <N>: <short title> — issue #<issue-number>
   **Subagent:** implementer
   **Depends on:** Task <M> | independent
   ```

   followed by the task's description. `Depends on: Task <M>` names the task whose output this one
   needs; `independent` means it can run in parallel with any other independent task. Once approved
   (`ExitPlanMode`), dispatch every task marked `independent` (relative to what's already landed) in
   parallel to the `implementer` agent (`agents/implementer/implementer.md`) — multiple `Agent` tool
   calls in a single message. Run a task with a `Depends on` marker only after that dependency's
   implementer call has returned and been folded in, one after another.

   **Mirror the breakdown as tracked tasks.** Before calling `ExitPlanMode`, call `TaskCreate`
   once per task (`subject` = the short title, `description` = the task's description) and follow
   with `TaskUpdate` to set `owner` to the subagent name and `addBlockedBy` to the IDs of the
   tasks it depends on — mapping directly from each task's `Depends on: Task <M>` marker. This
   keeps the breakdown as inspectable tool state (`TaskList`) in addition to the plan text. As
   each implementer dispatch returns and its output is folded in, mark that task `completed` via
   `TaskUpdate` before dispatching whichever task it was blocking. Skip this for a plan with only
   a single task — `TaskCreate`'s own guidance advises against use for one trivial task.

   **Include a conventions-doc step when the change earns one.** A repo's `CLAUDE.md`/`AGENTS.md`
   is the map a future session reads before touching code, so it should be updated as part of the
   work, not retrofitted after. Update it for: a new subsystem or file-layout change, ownership
   moving between units, a changed convention, or a placeholder becoming a real implementation.
   Skip it for renames, small refactors, and bugfixes — it is a map, not a changelog, and `git log`
   already records what changed. State either way in the plan so the reviewer can disagree.

   If the issues are several small independent changes on one branch, one plan covering all
   of them is fine — say which issue each step closes.

   **If implementation surfaces something that would change the approved plan** — not a small
   in-scope detail, but a real departure from what was approved — stop and explain the hurdle
   clearly, then ask the developer how to proceed. Do not improvise past it.

Do not commit or push unless the developer explicitly asks — those are the developer's to run.
