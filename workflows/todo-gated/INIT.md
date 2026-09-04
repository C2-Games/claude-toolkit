# INIT -- tailor this workflow to the current repo

`wf adopt todo-gated` has already run here: `.claude/` exists, the `core/`
subtrees (`commands/`, `agents/`, `hooks/`, `scripts/`, `WORKFLOW.md`,
`settings.json`) are symlinked into the central store, and the `local/`
templates (`project.json`, `settings.local.json`, `CLAUDE.md`,
`ARCHITECTURE.md`, `todos.json`) are copied in. Nothing in `core/` is ever
edited per-project -- your job is to fill the local files, then **delete this
file**.

Do not skip the confirmation step -- the check commands break the workflow
silently if wrong.

---

## 1. Inspect the repo (no edits yet)

Gather, without asking:

- **Language(s) and package manager** -- from `pyproject.toml` / `package.json` /
  `go.mod` / `Cargo.toml` / `pom.xml` / `Gemfile`, etc. Note research languages
  by extension (`.R`, `.do`/`.ado`, `.jl`, ...).
- **Existing format / lint / test / build tooling** -- `Makefile` / `justfile`
  targets, `package.json` scripts, `pyproject.toml` `[tool.*]` sections,
  `.pre-commit-config.yaml`, CI workflow files under `.github/workflows/`. If
  there is no real test suite, note whatever smoke command exists.
- **`.github/PULL_REQUEST_TEMPLATE.md`** -- present or not.
- **Branch / commit conventions** -- skim `git log --oneline -30`.
- **Source layout** -- code vs. docs/config dirs, and the file extensions.
- **Language style skills** -- any under `.claude/skills/` or `~/.claude/skills/`.

The default branch is **not configured** -- every command and hook derives it at
runtime from `origin/HEAD`. If there is no remote, tell the user `/finish` needs
one for the PR step.

## 2. Confirm with the user (`AskUserQuestion`, batch into a few calls)

- **Format command** -- in-place, or blank if none.
- **Lint command**. May be a compound (`a && b`).
- **Test / build command**, or the smoke command from step 1.
- **Source glob** -- `find_expr`, a shell command emitting the source files
  **NUL-separated** (`/check`'s freshness hash and `reviewer`'s scope). Usually
  `find src -type f \( -name "*.py" \) -print0`. Offer one built from step 1.
- **Architecture rules** -- configure `architecture-checker` now, or leave it? If
  now, gather 2-5 concrete, checkable dependency-direction / module-boundary
  statements.
- **Extra `doc_drift` watch paths** -- build config, CI files, source dirs to
  flag for `CLAUDE.md` drift.

## 3. Apply

| File | What to set |
|---|---|
| `.claude/project.json` | `find_expr`, `format_cmd`, `lint_cmd`, `test_cmd` (blank = skip), `doc_drift_watch` (list) |
| `.claude/settings.local.json` | add the format / lint / test executables to `permissions.allow` (e.g. `"Bash(pytest*)"`). The `git` / `todos.py` allows and the commit/push denies live in the symlinked `settings.json` -- do not duplicate them. |
| `.claude/ARCHITECTURE.md` | If the user gave rules: replace the `## Rules` examples, update the intro and diagram, and **delete the `<!-- ARCHITECTURE-TEMPLATE-UNFILLED -->` marker line**. If not: leave it exactly as-is. |
| `.claude/todos.json` | Leave as `{"next_id": 1, "todos": []}` unless seeding a backlog -- and if so, do it via `python3 .claude/scripts/todos.py add`, never by hand. It is a tracked file. |

Do **not** edit anything under `.claude/commands/`, `.claude/agents/`,
`.claude/hooks/`, `.claude/scripts/`, or `.claude/WORKFLOW.md` -- they are
symlinks into the store.

## 4. CLAUDE.md

`.claude/CLAUDE.md` is a stub. `reviewer`, `implementer`, `architecture-checker`,
and the `doc_drift` hook all get more useful with a real one -- `/init` generates
it from the codebase.

## 5. Housekeeping

- Confirm `python3` (or `python`) is on `PATH` -- the hooks, `todos.py`, and the
  `project.json` reads in `/check` all need it.
- `git status` should show `.claude/project.json`,
  `.claude/settings.local.json`, `.claude/ARCHITECTURE.md`, `.claude/todos.json`,
  `.claude/CLAUDE.md`, and `.claude/.workflow` as the only new tracked files --
  the symlinks are gitignored.

## 6. Finish

- **Delete this file** (`.claude/INIT.md`).
- Report a summary: what was set, plus anything the user still needs to do
  (install a linter, run `/init`, fill `ARCHITECTURE.md` later).
- Point them at `.claude/WORKFLOW.md` and tell them to start with `/todos` or
  `/create-todo`.
