# Issue-driven development workflow

`agents/`, `commands/issue-workflow/`, and `hooks/issue-workflow/` together implement one
pipeline: pick or file an issue, start work on it (branch + plan), implement the plan's tasks
(in parallel where independent), then review the diff. None of it runs against *this* repo —
it's a template to copy into a target project and wire up there.

```
/issues  →  /new-issue  →  /start-issue  →  implementer (parallel)  →  reviewer
  ↓             ↓               ↓                                        ↑
browse       issue-drafter    branch + plan,                    dispatched manually or
issues        agent           EnterPlanMode                     from a repo's own /check
```

## What to copy into a target repo

- `commands/issue-workflow/*.md` → the target repo's `.claude/commands/`
- `agents/*/​*.md` → the target repo's `.claude/agents/`
- `hooks/issue-workflow/issue_gate.py` (+ `hooks/toolchain/_toolchain.py`, which it imports)
  → the target repo's `.claude/hooks/`, if you want the edit-gate behavior

## What to configure per target repo

- **`GH_REPO`** (optional): set in the target repo's `.claude/settings.json` if its remote
  uses a non-default git host alias (e.g. an SSH config alias instead of `github.com`). All
  three commands and the `issue-drafter` agent check for it and skip `-R`/remote-parsing when
  it's set; otherwise `gh` infers the repo from the remote as normal.
- **Issue templates** (optional): `.github/ISSUE_TEMPLATE/{bug,feature,refactor,docs,test}.yml`
  (or `.md` equivalents). `issue-drafter` uses them when present and falls back to a plain
  Summary/Motivation/Possible-Implementation body when they're not.
- **Edit-gate hook** (optional): wire `hooks/issue-workflow/issue_gate.py` as a `PreToolUse`
  hook on `Edit`/`Write`, and its `--session-start` mode as a `SessionStart` hook, if the repo
  should refuse edits until an issue is on record. It gates every tracked file outside
  `.claude/`; nothing in it assumes a particular language, directory layout, or toolchain.
- **Conventions doc**: if the target repo has a `CLAUDE.md`/`AGENTS.md`, `implementer` and
  `reviewer` both read it before acting — architecture/module boundaries, naming, and any other
  repo-specific rules live there, not in the agent files.
- **Close-out command**: `start-issue.md`'s plan template ends with "run this repo's
  format/lint/test step." If the target repo has one (a `/check` command, `make check`, a CI
  script), name it explicitly in the plan; `hooks/toolchain/toolchain_run.py` is available as a
  cross-platform way to invoke it (falls back to WSL on Windows if no native POSIX shell).
- **Style skills**: `implementer` and `reviewer` both invoke whichever language-specific style
  skill applies (e.g. this toolkit's `cpp-style`, `python-style-guide`) if one is loaded — no
  extra wiring needed beyond having the skill available.

## What's deliberately not templated

- Branch-naming and issue-title conventions default to `<type>/<kebab-description>` /
  `<type>: <description>` (Conventional-Commit style); `start-issue.md` says to match the
  target repo's actual history instead if it differs.
- Assignees, milestones, and parent/sub-issue linkage are always asked, never assumed —
  `issue-drafter` has no hardcoded default assignee.
- There is no `architecture-checker`-style agent here: architectural rules are too
  project-specific to generalize usefully. If a target repo wants a plan checked against a
  documented architecture, that's a repo-specific addition, not part of this toolkit.
