# INIT -- tailor this workflow to the current repo

You (Claude) are running this once, right after someone copied the `str8-2-main`
workflow into their project and renamed it to `.claude/`. Every file here is
generic and carries `<!-- INIT: ... -->` placeholders. Your job: inspect the repo,
confirm the specifics with the user, fill everything in, then **delete this file**.

Do not skip the confirmation step -- the default branch, the check commands, and
the source globs break the workflow silently if wrong.

---

## 1. Inspect the repo (no edits yet)

Gather, without asking:

- **Language(s) and package manager** -- from `pyproject.toml` / `package.json` /
  `go.mod` / `Cargo.toml` / `pom.xml` / `Gemfile`, etc. Also note research
  languages by extension (`.R`, `.do`/`.ado`, `.jl`, ...).
- **Existing format / lint / test / build tooling** -- `Makefile` / `justfile`
  targets, `package.json` scripts, `pyproject.toml` `[tool.*]` sections,
  `.pre-commit-config.yaml`, and any CI workflow files under `.github/workflows/`
  (these usually name the exact commands the project already trusts -- prefer
  them). If the project has no real test suite, note whatever "does this file
  still run" smoke command exists instead.
- **`.claude/CLAUDE.md`** -- present or not.
- **Default branch** -- `git symbolic-ref refs/remotes/origin/HEAD` or
  `git remote show origin`. If there is no remote, ask.
- **Branch-name and commit-message conventions** -- skim `git log --oneline -30`
  for the prefixes actually in use.
- **Source layout** -- which top-level dirs hold code vs. docs/config, and the
  file extensions for the language(s).
- **Language style skills** -- any under `.claude/skills/`, or the user's global
  `~/.claude/skills/` directory.

## 2. Confirm with the user (`AskUserQuestion`, batch into a few calls)

- **Default branch**, if not `main`.
- **Format command** -- in-place, e.g. `ruff format .`, `gofmt -w .`, `cargo fmt`,
  `npm run format`.
- **Lint command** -- e.g. `ruff check .`, `golangci-lint run`,
  `cargo clippy -- -D warnings`.
- **Test / build command** -- e.g. `pytest -q`, `go test ./...`, `cargo test`,
  `npm test`. Or the smoke command from step 1 if there is no suite.
- **Source globs** -- the `find` expression for `/check`'s freshness hash, e.g.
  `find src -type f \( -name "*.py" \)`. Offer one built from step 1.
- **Language -> style skill mapping** -- which skill to invoke before touching
  each language's files, if any.

## 3. Apply

| File | What to change |
|---|---|
| `settings.json` | Add the format / lint / test / build commands to `permissions.allow` (e.g. `"Bash(pytest*)"`, `"Bash(ruff*)"`). The `git add` / `git commit` / `git push` entries are already there -- leave them. |
| `commands/check.md` | Replace every `<!-- INIT: ... -->` with the real format / lint / test commands and the source globs in the `find` line. Delete the `> **INIT:**` note block. |
| `commands/ship.md` | Replace the `<!-- INIT: same source globs as /check -->` in step 1's `find` with the *same* source globs as `check.md`. |
| all `commands/*.md` + `agents/*.md` | If the default branch is not `main`, replace the literal `origin/main`. `grep -rn 'origin/main' .claude/` to find them all. |
| `agents/implementer.md` | If the project has a language style skill, name it where the file says "the project's language style skill" / "a language style skill for the files you're editing". Otherwise leave as-is. |

## 4. CLAUDE.md

If `.claude/CLAUDE.md` does not exist, tell the user: the workflow runs fine
without it, but the `implementer` agent and plan mode both get more useful with
one. This workflow has **no** `doc_drift` hook, so nothing will nag them to keep it
current -- that is on them. They can run `/init` (Claude Code's built-in) to
create one later.

## 5. Housekeeping

- Confirm `.claude/.gitignore` is present (it ships with the workflow). If the repo
  has a root `.gitignore`, optionally add `.claude/.last-check` there too.
- Remove any leftover runtime file (`.last-check`) -- it should not have been
  copied, but check.
- Confirm `python3` (or `python`) is on `PATH` -- the one hook needs it, and
  nothing else.

## 6. Finish

- **Delete this file** (`.claude/INIT.md`).
- Report a summary: every file changed and what was set, plus anything the user
  still needs to do (install a linter, run `/init` for CLAUDE.md, etc.).
- Point them at `.claude/WORKFLOW.md` for how the workflow operates day to day, and
  tell them to start with `/send-it <request>` -- or just make a request.
