# INIT — tailor this workflow to the current repo

You (Claude) are running this once, right after someone copied the `todo-gated`
workflow into their project and renamed it to `.claude/`. Every file here is
generic and carries `<!-- INIT: ... -->` placeholders or `INIT:` comments. Your job:
inspect the repo, confirm the specifics with the user, fill everything in, then
**delete this file**.

Do not skip the confirmation step — several of these values (the default branch, the
check commands, the source globs) break the workflow silently if wrong.

---

## 1. Inspect the repo (no edits yet)

Gather, without asking:

- **Language(s) and package manager** — from `pyproject.toml` / `package.json` /
  `go.mod` / `Cargo.toml` / `pom.xml` / `Gemfile`, etc. Also note research
  languages by extension (`.R`, `.do`/`.ado`, `.jl`, ...).
- **Existing format / lint / test / build tooling** — `Makefile` / `justfile`
  targets, `package.json` scripts, `pyproject.toml` `[tool.*]` sections,
  `.pre-commit-config.yaml`, and any CI workflow files under `.github/workflows/`
  (these usually name the exact commands the project already trusts — prefer them).
  If the project has no real test suite, note whatever "does this file still run"
  smoke command exists instead.
- **`.github/PULL_REQUEST_TEMPLATE.md`** — present or not.
- **`.claude/CLAUDE.md`** — present or not.
- **Default branch** — `git symbolic-ref refs/remotes/origin/HEAD` or
  `git remote show origin`. If there is no remote, ask.
- **`gh` availability** — is the GitHub CLI on `PATH`? (`/finish` offers
  `gh pr create` only if it is.)
- **Branch-name and commit-message conventions** — skim `git log --oneline -30`
  and `git branch -a` for the prefixes actually in use.
- **Source layout** — which top-level dirs hold code vs. docs/config, and the file
  extensions for the language(s).
- **Language style skills** — any under `.claude/skills/`, or the user's global
  Claude directory.

## 2. Confirm with the user (`AskUserQuestion`, batch into a few calls)

- **Default branch**, if not `main`.
- **Format command** — in-place, e.g. `ruff format .`, `gofmt -w .`, `cargo fmt`,
  `npm run format`.
- **Lint command** — e.g. `ruff check .`, `golangci-lint run`,
  `cargo clippy -- -D warnings`.
- **Test / build command** — e.g. `pytest -q`, `go test ./...`, `cargo test`,
  `npm test`. Or the smoke command from step 1 if there is no suite.
- **Source globs** — the `find` expression for `/check`'s freshness hash and
  `reviewer`'s scope, e.g. `find src -type f \( -name "*.py" \)`. Offer one built
  from step 1.
- **Language → style skill mapping** — which skill to invoke before touching each
  language's files, if any.
- **Architecture rules** — configure `architecture-checker` now, or leave it? If
  now, gather the project's real dependency-direction / module-boundary rules (2–5
  concrete, checkable statements). If later, leave the template untouched — the
  agent no-ops until it's filled.
- **Extra `doc_drift` watch paths** — build config, CI files, source dirs the
  project wants flagged for `CLAUDE.md` drift (only meaningful if a `CLAUDE.md`
  exists or will).

## 3. Apply

| File | What to change |
|---|---|
| `settings.json` | Add the format / lint / test / build commands to `permissions.allow` (e.g. `"Bash(pytest*)"`, `"Bash(ruff*)"`). |
| `commands/check.md` | Replace every `<!-- INIT: ... -->` with the real format / lint / test commands and the source globs in the two `find` lines. Delete the `> **INIT:**` note block. |
| `commands/finish.md` | Replace the `<!-- INIT: ... -->` in step 2's `find` with the *same* source globs as `check.md`. |
| `agents/reviewer.md` | Replace the `<!-- INIT: source globs -->` in the two `git diff` / `git status` lines with the same globs. |
| `hooks/todo_gate.py` | Set `MAIN_BRANCH` if the default branch is not `main`. |
| `hooks/doc_drift.py` | Set `BASE_BRANCH` to match. Append any extra watch paths to `WATCHED`. |
| all `commands/*.md` + `agents/*.md` | If the default branch is not `main`, replace the literal `origin/main`. `grep -rn 'origin/main' .claude/` to find them all. |
| `agents/implementer.md`, `agents/reviewer.md`, `agents/todo-drafter.md` | If the project has a language style skill, name it where each file says "the project's language style skill" / "the matching language style skill". Otherwise leave as-is. |
| `ARCHITECTURE.md` | If the user gave rules: replace the `## Rules` examples with them, update the intro paragraph and the Dependency Diagram, and **delete the `<!-- ARCHITECTURE-TEMPLATE-UNFILLED -->` marker line**. If not: leave the file exactly as-is. |
| `WORKFLOW.md` | Fix the `doc_drift` watch-list sentence in rule 4 if you added paths. Otherwise no edit needed. |

## 4. CLAUDE.md

If `.claude/CLAUDE.md` does not exist, tell the user: the workflow runs fine without
it, but `reviewer`, `implementer`, and the `doc_drift` hook all get more useful with
one — they can run `/init` (Claude Code's built-in) to create it later.

## 5. Housekeeping

- Confirm `.claude/.gitignore` is present (it ships with the workflow). If the repo
  has a root `.gitignore`, optionally add `.claude/.current-todo`,
  `.claude/.last-check`, `.claude/.pr-body.md`, `.claude/.doc-drift-ack` there too.
- `.claude/todos.json` **is** tracked — leave it as the blank template
  (`{"next_id": 1, "todos": []}`) unless the project wants to seed it with
  already-known work. If so, use `todos.py add` (through Bash), not a hand-edit.
- Remove any leftover runtime files (`.current-todo`, `.last-check`, `.pr-body.md`,
  `.doc-drift-ack`) — they should not have been copied, but check.
- Confirm `python3` (or `python`) is on `PATH` — the hooks and `todos.py` need it,
  and nothing else.

## 6. Finish

- **Delete this file** (`.claude/INIT.md`).
- Report a summary: every file changed and what was set, plus anything the user
  still needs to do (install a linter, run `/init` for CLAUDE.md, fill in
  `ARCHITECTURE.md` later, etc.).
- Point them at `.claude/WORKFLOW.md` for how the workflow operates day to day, and
  tell them to start with `/todos` or `/create-todo`.
