---
description: Close out the active todo, prepare a PR body, and hand the commit/push commands back to the user
---

**This command never touches the remote.** `git push` and `git commit` are denied
in `.claude/settings.json` — publishing is the user's call, always.

## Steps

1. **Require an active todo.** Read `.claude/.current-todo`. If it is missing, stop
   and tell the user to run `/start-todo <id>` — there is nothing to finish.

2. **Confirm `/check` is current.** Recompute the same hash `/check` stamps — use
   the identical find globs from `/check` step 2:

   ```bash
   <!-- INIT: same source globs as /check -->
   find src -type f \( -name "*.py" \) -print0 | sort -z | xargs -0 sha256sum | sha256sum | cut -d" " -f1
   ```

   Compare it to `.claude/.last-check` (gitignored, written by `/check`). If the file
   is missing, or the hash differs, stop — tell the user source has changed since
   `/check` last passed (or `/check` has never run here) and to run it before
   `/finish`.

3. **Verify the branch.** Confirm `git rev-parse --abbrev-ref HEAD` matches the
   `branch` recorded in `.claude/.current-todo`, and that it is not the default
   branch.

4. **Close out the todo.** Run:

   ```bash
   python3 "$CLAUDE_PROJECT_DIR/.claude/scripts/todos.py" end-session \
     || python "$CLAUDE_PROJECT_DIR/.claude/scripts/todos.py" end-session
   ```

   This marks the active todo(s) and any still-open subtasks `completed` with
   today's date in `todos.json`, and deletes `.claude/.current-todo`. `todos.json`
   is a tracked file — it goes in the same commit as the code so the backlog update
   ships with the change.

5. **Show what would ship.** `git status --short` and
   `git diff --stat origin/main...HEAD`.

   Read these together: the diffstat shows only *committed* work, so uncommitted
   changes are invisible in it. If `git status` is not clean, say so loudly —
   pushing at that point ships the previous commit and silently omits the session's
   work. Name any file that should **not** go in (unrelated untracked files, scratch
   files) so it is left out of the `git add`. `todos.json` **should** go in.

6. **Draft the title** as `type: Sentence-case description`, where `type` matches
   the branch prefix (`feat`, `fix`, `refactor`, `docs`, `test`, `chore`). A scope
   is optional, e.g. `fix(build):`.

7. **Write the body** to `.claude/.pr-body.md` (gitignored). If the repo has
   `.github/PULL_REQUEST_TEMPLATE.md`, follow it exactly. Otherwise use:

   ```markdown
   ## Summary
   <one or two plain sentences on what changed>

   ## Changes Made
   - <one bullet per meaningfully distinct change>
   ```

   **Keep it short.** A reviewer should read the whole thing in a few seconds.
   - **Summary**: one or two plain sentences on *what changed*. No "This PR aims
     to...", no narrating how the approach was chosen.
   - **Changes Made**: one bullet per meaningfully distinct change, not one per file
     and not a paragraph per bullet. Skip anything the diff already makes obvious.

8. **Print the handoff** and stop:

   ```text
   ! git add <the files from step 5, including .claude/todos.json>
   ! git commit -m "<type>: <Sentence-case description>"
   ! git push -u origin <branch>
   ```

   If `gh` is on `PATH` and the repo has a remote, add:

   ```text
   ! gh pr create --title "<title>" --body-file .claude/.pr-body.md
   ```

   If `gh` is not available, say so in one line and stop after the `push` line —
   the user opens the PR however their host expects.

   Draft a real commit message; do not leave a placeholder. Tell the user to run
   these with the `!` prefix so they execute in their session. `git commit` and
   `git push` are denied to you — they are the user's to run, which is also the
   last human review before anything leaves the machine.

   If this session is in a worktree (`.claude/worktrees/<branch>`), add a reminder:
   once merged, `cd` out and run `git worktree remove <path>` (or `ExitWorktree`) to
   clean it up — it is never called proactively.
