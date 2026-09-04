# issue-gated migrations

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
`.claude/` copy.

- [ ] Re-adopt with `wf adopt issue-gated` into a scratch dir, then move your
      filled `project.json` / `settings.local.json` / `ARCHITECTURE.md` values
      across, or run `wf link` if the layout already matches.
- [ ] `GH_REPO` moved from `settings.json` to `settings.local.json`.
- [ ] The default branch is no longer hardcoded in `issue_gate.py` /
      `doc_drift.py` -- it is derived from `origin/HEAD`. Drop any local edit
      that set `MAIN_BRANCH` / `BASE_BRANCH`.
- [ ] `doc_drift` now watches `settings.local.json` + `project.json` and reads
      extra paths from `project.json`'s `doc_drift_watch` (previously appended
      to `WATCHED` by hand).
