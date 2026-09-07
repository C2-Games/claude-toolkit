# todo-gated migrations

Append-only. One block per core change that an **already-adopted** repo must
act on beyond what `wf sync` copies in automatically -- a new `project.json`
key, a new `settings.local.json` allow entry. A change confined to `core/`
prose, or one `wf sync` delivers as a plain file copy, adds no block here.

`wf status` prints every block newer than a repo's recorded `core_version`;
`wf sync --accept <repo>` records the new version once you've worked through
them.

<!-- Template for a new block:

## <YYYY-MM-DD> -- v<N> -> v<N+1>

- [ ] <what the adopting repo must do>

-->

## 2026-09-03 -- v0 -> v1

Initial `core/` + `local/` split. Repos adopted before this used a flat
`.claude/` copy. `wf link` registers such a repo with `core_version 0`, so this
block still shows -- work through it, then `wf sync --accept <repo>`.

- [ ] Re-adopt with `wf adopt todo-gated` into a scratch dir, then move your
      filled `project.json` / `settings.local.json` / `ARCHITECTURE.md` and your
      `todos.json` backlog across, or run `wf link` if the layout already
      matches.
- [ ] `todos.json` stays a real committed file in `.claude/`; `scripts/` is now
      a symlink into the store.
- [ ] The default branch is no longer hardcoded in `todo_gate.py` /
      `doc_drift.py` -- it is derived from `origin/HEAD`. Drop any local edit
      that set `MAIN_BRANCH` / `BASE_BRANCH`.
- [ ] `doc_drift` now watches `settings.local.json` + `project.json` and reads
      extra paths from `project.json`'s `doc_drift_watch`.

## 2026-09-07 -- v1 -> v2

New shared `SessionStart` hook `workflow_notify.py`: it reports (never applies)
when this repo is behind the claude-toolkit store, or when the local store
clone has not fetched in a while. `wf sync` delivers both the hook file and the
`settings.json` wiring.

- [ ] Make sure `bin/wf` is on your PATH on every machine you open this repo on
      (toolkit root README) -- the hook is silent without it. No other action if
      your `settings.json` was unmodified.
- [ ] If you had locally edited `.claude/settings.json`, `wf sync` leaves a
      `settings.json.core-new`. Merge the new second `SessionStart` entry
      (the `workflow_notify.py` block) into your `settings.json` and delete the
      `.core-new` file.
