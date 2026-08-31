# INIT — tailor this workflow to the current repo

You (Claude) are running this once, right after someone copied the `issue-gated`
workflow into their project and renamed it to `.claude/`. Every file here is
generic and carries `<!-- INIT: ... -->` placeholders or `INIT:` comments. Your job:
inspect the repo, confirm the specifics with the user, fill everything in, then
**delete this file**.

Do not skip the confirmation step — several of these values (the repo slug, the
default branch, the check commands) break the workflow silently if wrong.

---

## 1. Inspect the repo (no edits yet)

Gather, without asking:

- **Language(s) and package manager** — from `pyproject.toml` / `package.json` /
  `go.mod` / `Cargo.toml` / `pom.xml` / `Gemfile`, etc.
- **Existing format / lint / test / build tooling** — `Makefile` / `justfile`
  targets, `package.json` scripts, `pyproject.toml` `[tool.*]` sections, `.pre-commit-config.yaml`,
  and any CI workflow files under `.github/workflows/` (these usually name the exact
  commands the project already trusts — prefer them).
- **`.github/ISSUE_TEMPLATE/` and `.github/PULL_REQUEST_TEMPLATE.md`** — present or not.
- **`.claude/CLAUDE.md`** — present or not.
- **GitHub remote slug** — `git remote get-url origin`, reduced to `OWNER/REPO`.
- **Default branch** — `git symbolic-ref refs/remotes/origin/HEAD` or `git remote show origin`.
- **Branch-name and commit-message conventions** — skim `git log --oneline -30` and
  `git branch -a` for the prefixes actually in use.
- **Source layout** — which top-level dirs hold code vs. docs/config, and the file
  extensions for the language(s).

## 2. Confirm with the user (`AskUserQuestion`, batch into a few calls)

- **Repo slug** for `GH_REPO` (offer the detected `OWNER/REPO`).
- **Default branch**, if not `main`.
- **Format command** — in-place, e.g. `ruff format .`, `gofmt -w .`, `cargo fmt`,
  `npm run format`.
- **Lint command** — e.g. `ruff check .`, `golangci-lint run`, `cargo clippy -- -D warnings`.
- **Test / build command** — e.g. `pytest -q`, `go test ./...`, `cargo test`, `npm test`.
- **Source globs** — the `find` expression for `/check`'s freshness hash and
  `reviewer`'s scope, e.g. `src include -type f \( -name "*.py" \)`. Offer one built
  from step 1.
- **Issue assignees** — default `@me`, or an explicit comma-separated list.
- **Milestones** — does the project use them? (If not, `issue-drafter` and
  `start-issue` skip the milestone steps automatically, but confirm.)
- **Architecture rules** — configure `architecture-checker` now, or leave it? If now,
  gather the project's real dependency-direction / module-boundary rules (2–5
  concrete, checkable statements). If later, leave the template untouched — the agent
  no-ops until it's filled.
- **Extra `doc_drift` watch paths** — build config, CI files, source dirs the project
  wants flagged for `CLAUDE.md` drift (only meaningful if a `CLAUDE.md` exists or
  will).

## 3. Apply

Work through every file:

| File | What to change |
|---|---|
| `settings.json` | `env.GH_REPO` → real slug. Add the format / lint / test / build commands to `permissions.allow` (e.g. `"Bash(pytest*)"`, `"Bash(ruff*)"`). |
| `commands/check.md` | Replace every `<!-- INIT: ... -->` with the real format / lint / test commands and the source globs in the two `find` lines. Delete the `> **INIT:**` note block. |
| `commands/pr.md` | Replace the `<!-- INIT: ... -->` in step 2's `find` with the *same* source globs as `check.md`. |
| `agents/reviewer.md` | Replace the `<!-- INIT: source globs -->` in the two `git diff` / `git status` lines with the same globs. |
| `hooks/issue_gate.py` | Set `MAIN_BRANCH` if the default branch is not `main`. |
| `hooks/doc_drift.py` | Set `BASE_BRANCH` to match. Append any extra watch paths to `WATCHED`. |
| all `commands/*.md` + `agents/*.md` | If the default branch is not `main`, replace the literal `origin/main` (in `git switch`, `git diff origin/main...HEAD`, `git status` range lines) with `origin/<default>`. `grep -rn 'origin/main' .claude/` to find them all. |
| `agents/issue-drafter.md` | If the user gave an explicit assignee list, note it in step 2's assignee line. If the repo has no milestones, that's already handled — no edit needed. |
| `agents/implementer.md`, `agents/reviewer.md` | If the project has a language style skill in `.claude/skills/`, name it where each file says "the project's language style skill". Otherwise leave as-is. |
| `ARCHITECTURE.md` | If the user gave rules: replace the `## Rules` examples with them, update the intro paragraph and the Dependency Diagram, and **delete the `<!-- ARCHITECTURE-TEMPLATE-UNFILLED -->` marker line**. If not: leave the file exactly as-is. |
| `WORKFLOW.md` | Fix the `doc_drift` watch-list sentence in rule 4 if you added paths. Otherwise no edit needed. |

## 4. CLAUDE.md

If `.claude/CLAUDE.md` does not exist, tell the user: the workflow runs fine without
it, but `reviewer`, `implementer`, and the `doc_drift` hook all get more useful with
one — they can run `/init` (Claude Code's built-in) to create it later.

## 5. Housekeeping

- Confirm `.claude/.gitignore` is present (it ships with the workflow). If the repo
  has a root `.gitignore`, optionally add `.claude/.current-issue`,
  `.claude/.last-check`, `.claude/.pr-body.md`, `.claude/.doc-drift-ack` there too.
- Remove any leftover runtime files (`.current-issue`, `.last-check`, `.pr-body.md`,
  `.doc-drift-ack`) — they should not have been copied, but check.

## 6. Finish

- **Delete this file** (`.claude/INIT.md`).
- Report a summary: every file changed and what was set, plus anything the user still
  needs to do (`gh auth login`, install a linter, run `/init` for CLAUDE.md, fill in
  `ARCHITECTURE.md` later, etc.).
- Point them at `.claude/WORKFLOW.md` for how the workflow operates day to day, and
  tell them to start with `/issues` or `/new-issue`.
