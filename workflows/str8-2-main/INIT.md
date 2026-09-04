# INIT -- tailor this workflow to the current repo

`wf adopt str8-2-main` has already run here: `.claude/` exists, the `core/`
subtrees are symlinked into the central store, and the `local/` templates
(`project.json`, `settings.local.json`, `CLAUDE.md`) are copied in. Nothing in
`core/` is ever edited per-project -- your job is to fill the two local files,
then **delete this file**.

Do not skip the confirmation step -- the check commands and the source glob break
the workflow silently if wrong.

---

## 1. Inspect the repo (no edits yet)

Gather, without asking:

- **Language(s) and package manager** -- from `pyproject.toml` / `package.json` /
  `go.mod` / `Cargo.toml` / `pom.xml` / `Gemfile`, etc. Also note research
  languages by extension (`.R`, `.do`/`.ado`, `.jl`, ...).
- **Existing format / lint / test / build tooling** -- `Makefile` / `justfile`
  targets, `package.json` scripts, `pyproject.toml` `[tool.*]` sections,
  `.pre-commit-config.yaml`, and any CI workflow files under
  `.github/workflows/` (these usually name the exact commands the project
  already trusts -- prefer them). If there is no real test suite, note whatever
  "does this still run" smoke command exists instead.
- **Source layout** -- which top-level dirs hold code vs. docs/config, and the
  file extensions for the language(s).
- **Language style skills** -- any under `.claude/skills/`, or the user's global
  `~/.claude/skills/`.

Note: the **default branch is not configured** -- every command derives it at
runtime from `origin/HEAD`. If the repo has no remote yet, tell the user `/ship`
needs one.

## 2. Confirm with the user (`AskUserQuestion`, batch into a few calls)

- **Format command** -- in-place, e.g. `ruff format .`, `gofmt -w .`,
  `cargo fmt`, `npm run format`. Leave blank if the project has no autoformatter.
- **Lint command** -- e.g. `ruff check .`, `golangci-lint run`,
  `cargo clippy -- -D warnings`. May be a compound (`a && b`).
- **Test / build command** -- e.g. `pytest -q`, `go test ./...`, `cargo test`,
  `npm test`, or the smoke command from step 1.
- **Source glob** -- `find_expr`, a shell command that emits the source files
  **NUL-separated** for `/check`'s freshness hash. Usually
  `find src -type f \( -name "*.py" \) -print0`; a docs repo might use
  `git ls-files -z --cached --others --exclude-standard '*.md'`. Offer one built
  from step 1.

## 3. Apply

Two files only:

- **`.claude/project.json`** -- set `find_expr` (the confirmed `find`
  expression, as a single string), `format_cmd`, `lint_cmd`, `test_cmd`. A blank
  string means "skip that step".
- **`.claude/settings.local.json`** -- add the format / lint / test executables
  to `permissions.allow` (e.g. `"Bash(pytest*)"`, `"Bash(ruff*)"`). The core
  `git` allows live in the symlinked `settings.json`; do not duplicate them.

Do **not** edit anything under `.claude/commands/`, `.claude/agents/`,
`.claude/hooks/`, or `.claude/WORKFLOW.md` -- they are symlinks into the shared
store.

## 4. CLAUDE.md

`.claude/CLAUDE.md` is a stub. Tell the user: the workflow runs fine without one,
but the `implementer` agent and plan mode both get more useful with a real one --
`/init` (Claude Code built-in) generates it from the codebase. This workflow has
**no** `doc_drift` hook, so nothing will nag them to keep it current.

## 5. Housekeeping

- Confirm `python3` (or `python`) is on `PATH` -- the one hook and the
  `project.json` reads in `/check` need it.
- `git status` should show `.claude/settings.local.json`, `.claude/project.json`,
  `.claude/CLAUDE.md`, and `.claude/.workflow` as the only new tracked files --
  the symlinks are gitignored.

## 6. Finish

- **Delete this file** (`.claude/INIT.md`).
- Report a summary: what was set in `project.json` and `settings.local.json`,
  plus anything the user still needs to do (install a linter, run `/init`).
- Point them at `.claude/WORKFLOW.md` and tell them to start with
  `/send-it <request>` -- or just make a request.
