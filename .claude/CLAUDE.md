# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A personal library of Claude Code building blocks, and the **central store** the
`bin/wf` CLI links them into other repos from. Two product lines:

- `language-skills/<lang>/<skill>/` -- per-language code-style skills, each a
  `SKILL.md` plus optional `assets/`, `scripts/`, `references/`. Copied to
  `~/.claude/skills/` (personal) or a project's `.claude/skills/` (team).
- `workflows/<name>/` -- complete `.claude/` setups that impose one way of
  working on a repo. A repo **adopts** a workflow with `wf adopt <name>`, which
  symlinks the workflow's `core/` into the repo's `.claude/` and copies its
  `local/` templates in as real files.

## The store / overlay / sync model (the load-bearing structure)

Each `workflows/<name>/` has two layers:

- **`core/`** -- every file that is identical for every repo running the
  workflow: `commands/*.md`, `agents/*.md`, `hooks/*.py`, `WORKFLOW.md`,
  `settings.core.json`. An adopting repo **symlinks** these into `.claude/`
  (`.claude/commands` -> `<store>/workflows/<name>/core/commands`, etc.), so a
  `git pull` of the store upgrades every adopter at once. `core/` files carry
  **zero per-project values** -- see "Parameter discipline" below.
- **`local/`** -- templates copied into `.claude/` as real, committed files at
  adopt time and owned by the repo thereafter: `project.json` (the one
  config file -- source glob, format/lint/test commands, and workflow knobs),
  `settings.local.json` (the repo's lint/test allows, `GH_REPO`), `CLAUDE.md`
  stub, `ARCHITECTURE.md` (issue/todo-gated), `todos.json` (todo-gated),
  `.gitignore`.

Plus, per workflow: `VERSION` (an integer, bumped on any `core/` change) and
`MIGRATIONS.md` (append-only; one block per change that needs an already-adopted
repo to do something -- a new `project.json` key, a `settings.local.json` entry,
a re-`wf link`). A pure-prose `core/` change adds no migration block; the
symlink delivers it.

`workflows/_shared/` holds files identical **across** workflows --
`hooks/_hooklib.py`, `hooks/doc_drift.py`, `agents/{implementer,reviewer,
architecture-checker}.md`, `ARCHITECTURE.md` -- and each workflow's `core/`
**symlinks (relative) to `_shared/`**. Edit the `_shared/` copy and every
workflow gets it. Do not un-share by replacing a symlink with a copy unless a
real divergence forces it.

### The three workflows

- `workflows/issue-gated/` is canonical: every change traces to a GitHub issue,
  goes through plan mode, is built by scoped `implementer` subagents, and passes
  `/check` (format, lint, tests, `reviewer` agent) before `/pr` hands the human
  the commit/push commands. Hooks: `issue_gate.py` (PreToolUse edit gate),
  `doc_drift.py` (Stop), SessionStart.
- `workflows/todo-gated/` is issue-gated with GitHub swapped for a
  version-controlled `.claude/todos.json`, mutated **only** through
  `scripts/todos.py` (never hand-edited; `validate_todos_json.py` enforces this
  PostToolUse). `/pr` becomes `/finish`.
- `workflows/str8-2-main/` is the stripped subset -- no work branch, no edit
  gate, no `reviewer`/`architecture-checker`, no `doc_drift`. One SessionStart
  hook (`working_mode.py`). `/ship` commits a header-only message and pushes to
  the default branch itself.

### `bin/wf`

Stdlib Python. `wf adopt <workflow> [dir]` sets up `.claude/`; `wf link [dir]`
recreates the symlinks from `.claude/.workflow` after a fresh clone; `wf status`
/ `wf sync` compare each registered repo's recorded `core_version` to the
store's `VERSION` and print the pending `MIGRATIONS.md` blocks; `wf projects`
lists the registry (`.projects`, gitignored). Adopting repos are registered in
`.projects`.

## Parameter discipline (what keeps `core/` shareable)

- **Default branch** is never stored -- hooks call `_hooklib.default_branch()` /
  `base_ref()` (`git symbolic-ref refs/remotes/origin/HEAD`, fallback `main`);
  command bodies derive it inline with the same `git symbolic-ref` one-liner.
- **Source glob + format/lint/test commands** live in `.claude/project.json`.
  Command bodies read them (`cfg()` helper / a `python3 -c` line); hooks read
  them via `_hooklib.load_project_config()`. `find_expr` is a shell command that
  emits the file set **NUL-separated**; `/check` and `/ship`|`/pr`|`/finish` hash
  it with an identical `eval "$FIND" | sort -z | xargs -0 sha256sum` line -- keep
  those lines byte-identical between the two files.
- **`GH_REPO`** and the repo's lint/test `permissions.allow` entries go in
  `.claude/settings.local.json`; hook wiring + the commit/push `deny` list stay
  in `core/settings.core.json`. Claude Code merges them (deny beats allow).
- **Architecture rules** stay in the repo's real `.claude/ARCHITECTURE.md`
  (keeps the `<!-- ARCHITECTURE-TEMPLATE-UNFILLED -->` marker until filled).
- **`doc_drift` extra watch paths**, **issue assignees**, **milestones** are
  `project.json` keys (`doc_drift_watch`, `issue_assignees`, `uses_milestones`).

If you find yourself adding an `<!-- INIT -->` / `# INIT:` placeholder to a
`core/` file, stop -- route it through `project.json` or `settings.local.json`
instead, and update the relevant `INIT.md` and this section.

## Conventions when editing templates

- **Commands** (`core/commands/*.md`): YAML frontmatter `description:` + optional
  `argument-hint:`; body addresses Claude in the second person and uses
  `$ARGUMENTS`.
- **Agents** (`core/agents/*.md`): frontmatter `name:` / `description:` /
  `tools:` (comma list). The shared ones are symlinks to `_shared/agents/`.
- **Hooks** (`_shared/hooks/*.py`, `*/core/hooks/*.py`): Python **stdlib only**.
  Wired in `settings.core.json` as
  `python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/X.py" || python "..."` with
  `"shell": "bash"` and a 15-20s `timeout`. Must resolve state against
  `$CLAUDE_PROJECT_DIR` (not `__file__`), since `hooks/` is a symlink into the
  store. Never fatally block a session -- except the gate hooks, which deny edits
  by design.
- **Skills** (`language-skills/*/SKILL.md`): frontmatter is `name:` + a
  trigger-phrase `description:` only; body is plain Markdown rules and
  before/after examples.
- Prose style across the repo's docs: `--` not em-dash; tables and Mermaid
  `flowchart TD` for lifecycle diagrams.

`workflows/README.md` is the adoption guide, the sync guide, and the per-workflow
"use it when / don't bother when" selector. `workflows/_shared/README.md`
documents the cross-workflow dedup.

## This repo runs `str8-2-main` on itself

`.claude/` here is an **adopter** of `workflows/str8-2-main/`: its
`commands/` / `agents/` / `hooks/` / `WORKFLOW.md` / `settings.json` are
**relative symlinks** into `workflows/str8-2-main/core/` (same repo), gitignored
and recreated by `wf link`. The real committed files are `.claude/project.json`,
`.claude/settings.local.json`, `.claude/CLAUDE.md`, `.claude/.workflow`.
Behavior changes to the workflow are made in `workflows/str8-2-main/core/`
directly -- they take effect here immediately (same clone).

- Day-to-day operating manual: `.claude/WORKFLOW.md`.
- Entry point: `/send-it <request>`, or just make a request. Non-trivial work
  goes through plan mode with a `### Task N` breakdown dispatched to
  `implementer` agents. Single-file doc edits and true one-liners skip formal
  plan mode.
- `/check` (the only gate, must end every plan) reads `.claude/project.json`:
  `lint_cmd` here validates every tracked/new `.json` then runs
  `python3 -m pymarkdown --config .pymarkdown.json scan -r .`; `test_cmd` is
  `git ls-files '*.py' | xargs python3 -m py_compile`; the freshness hash covers
  all tracked Markdown. `.pymarkdown.json` disables the stylistic rules the
  pre-existing docs don't follow; tighten it as docs are rewritten.
- `/ship`: re-hashes, refuses on mismatch, then makes a header-only commit and
  pushes to the default branch. `git commit`/`push` are allowed here (unlike the
  other two workflows).
- One-time setup on a fresh machine: `pipx install pymarkdownlnt` (or
  `pip install --user --break-system-packages pymarkdownlnt`), then `wf link`.

## Validating changes locally

- Python: `git ls-files '*.py' | xargs python3 -m py_compile` -- and the moved
  `core/` hooks are untracked until committed, so also
  `python3 -m py_compile workflows/_shared/hooks/*.py workflows/*/core/hooks/*.py workflows/todo-gated/core/scripts/todos.py bin/wf`
- `todos.py`: `py_compile` covers syntax; behavior needs an adopted repo --
  `cd <adopter> && python3 .claude/scripts/todos.py validate`
- Markdown: `python3 -m pymarkdown --config .pymarkdown.json scan -r <path>`
- Symlinks resolve: `find workflows .claude -xtype l` prints nothing
- `wf` round-trip: `wf adopt str8-2-main <scratch>/r && wf status`
