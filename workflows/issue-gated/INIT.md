# INIT -- tailor this workflow to the current repo

`wf adopt issue-gated` has already run here: `.claude/` exists, the `core/`
subtrees (`commands/`, `agents/`, `hooks/`, `WORKFLOW.md`, `settings.json`) are
symlinked into the central store, and the `local/` templates (`project.json`,
`settings.local.json`, `CLAUDE.md`, `ARCHITECTURE.md`) are copied in. Nothing in
`core/` is ever edited per-project -- your job is to fill the local files, then
**delete this file**.

Do not skip the confirmation step -- the repo slug and the check commands break
the workflow silently if wrong.

---

## 1. Inspect the repo (no edits yet)

Gather, without asking:

- **Language(s) and package manager** -- from `pyproject.toml` / `package.json` /
  `go.mod` / `Cargo.toml` / `pom.xml` / `Gemfile`, etc.
- **Existing format / lint / test / build tooling** -- `Makefile` / `justfile`
  targets, `package.json` scripts, `pyproject.toml` `[tool.*]` sections,
  `.pre-commit-config.yaml`, and any CI workflow files under
  `.github/workflows/` (prefer the commands the project already trusts).
- **`.github/ISSUE_TEMPLATE/` and `.github/PULL_REQUEST_TEMPLATE.md`** -- present
  or not.
- **GitHub remote slug** -- `git remote get-url origin`, reduced to `OWNER/REPO`.
- **Branch / commit conventions** -- skim `git log --oneline -30` and
  `git branch -a` for the prefixes in use.
- **Source layout** -- which top-level dirs hold code vs. docs/config, and the
  file extensions.
- **Language style skills** -- any under `.claude/skills/` or `~/.claude/skills/`.

The default branch is **not configured** -- every command and hook derives it at
runtime from `origin/HEAD`.

## 2. Confirm with the user (`AskUserQuestion`, batch into a few calls)

- **Repo slug** for `GH_REPO` (offer the detected `OWNER/REPO`).
- **Format command** -- in-place, or blank if none.
- **Lint command**. May be a compound (`a && b`).
- **Test / build command**, or a smoke command if there is no suite.
- **Source glob** -- `find_expr`, a shell command emitting the source files
  **NUL-separated** (`/check`'s freshness hash and `reviewer`'s scope). Usually
  `find src -type f \( -name "*.py" \) -print0`. Offer one built from step 1.
- **Issue assignees** -- default `@me`, or an explicit comma-separated list.
- **Milestones** -- does the project use them?
- **Architecture rules** -- configure `architecture-checker` now, or leave it? If
  now, gather 2-5 concrete, checkable dependency-direction / module-boundary
  statements.
- **Extra `doc_drift` watch paths** -- build config, CI files, source dirs to
  flag for `CLAUDE.md` drift.

## 3. Apply

| File | What to set |
|---|---|
| `.claude/project.json` | `find_expr`, `format_cmd`, `lint_cmd`, `test_cmd` (blank = skip), `issue_assignees`, `uses_milestones`, `doc_drift_watch` (list) |
| `.claude/settings.local.json` | `env.GH_REPO` -> real slug; add the format / lint / test executables to `permissions.allow` (e.g. `"Bash(pytest*)"`). The `git` / `gh issue` allows and the commit/push denies live in the symlinked `settings.json` -- do not duplicate them. |
| `.claude/ARCHITECTURE.md` | If the user gave rules: replace the `## Rules` examples, update the intro and diagram, and **delete the `<!-- ARCHITECTURE-TEMPLATE-UNFILLED -->` marker line**. If not: leave it exactly as-is (`architecture-checker` no-ops while the marker is present). |

Do **not** edit anything under `.claude/commands/`, `.claude/agents/`,
`.claude/hooks/`, or `.claude/WORKFLOW.md` -- they are symlinks into the store.
If the language style skill needs naming, that is a `.claude/CLAUDE.md` note, not
a core edit -- the agents check `.claude/skills/` themselves.

## 4. CLAUDE.md

`.claude/CLAUDE.md` is a stub. `reviewer`, `implementer`, `architecture-checker`,
and the `doc_drift` hook all get more useful with a real one -- `/init` (Claude
Code built-in) generates it from the codebase.

## 5. Housekeeping

- Confirm `gh` is on `PATH` and authenticated (`gh auth status`).
- Confirm `python3` (or `python`) is on `PATH`.
- `git status` should show `.claude/project.json`,
  `.claude/settings.local.json`, `.claude/ARCHITECTURE.md`, `.claude/CLAUDE.md`,
  and `.claude/.workflow` as the only new tracked files -- the symlinks are
  gitignored.

## 6. Finish

- **Delete this file** (`.claude/INIT.md`).
- Report a summary: what was set, plus anything the user still needs to do
  (`gh auth login`, install a linter, run `/init`, fill `ARCHITECTURE.md`
  later).
- Point them at `.claude/WORKFLOW.md` and tell them to start with `/issues` or
  `/new-issue`.
