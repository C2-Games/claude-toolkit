# str8-2-main migrations

Append-only. One block per core change that an **already-adopted** repo must act
on -- a new `project.json` key, a new `settings.local.json` allow entry, a
hook-wiring change that needs `wf link` re-run. A change confined to `core/`
prose adds no block here.

`wf status` prints every block newer than a repo's recorded `core_version`;
`wf sync` walks them with you and bumps the recorded version once you confirm.

<!-- Template for a new block:

## <YYYY-MM-DD> -- v<N> -> v<N+1>

- [ ] <what the adopting repo must do>

-->

## 2026-09-03 -- v0 -> v1

Initial `core/` + `local/` split. Repos adopted before this used a flat
`.claude/` copy.

- [ ] Re-adopt with `wf adopt str8-2-main` into a scratch dir, then move your
      filled `project.json` / `settings.local.json` values across, or run
      `wf link` if the layout already matches.
