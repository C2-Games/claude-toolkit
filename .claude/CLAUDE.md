# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A personal library of Claude Code building blocks. Two channels, each with its
own delivery mechanism:

- `skills/<name>/` -- reusable skills, each a `SKILL.md` plus optional
  `assets/`, `scripts/`, `references/`. Shipped as the **`toolkit-skills`
  plugin** via the root `.claude-plugin/marketplace.json`; machines install it
  once and it auto-updates. No longer hand-copied into `~/.claude/skills/`. See
  "Skills ship as a plugin" below.
- `workflows/<name>/` -- complete `.claude/` setups that impose one way of
  working on a repo, delivered by the **`bin/wf` CLI**. A repo **adopts** a
  workflow with `wf adopt <name>` (or `wf link <name>` for a repo that already
  has a non-empty `.claude/`), which copies the workflow's `core/` and its
  `local/` templates into the repo's `.claude/` as real, committed files.
  Adopters are self-contained -- nothing in an adopted repo points back at this
  store.

### Skills ship as a plugin

- Layout is fixed by Claude Code: `skills/<name>/SKILL.md`, flat, **real files
  only** -- symlinks inside a plugin's skill dirs are not followed, so `skills/`
  cannot borrow from `_shared/` the way `workflows/*/core/` does. Each dir name
  must equal its `name:` frontmatter.
- `.claude-plugin/marketplace.json` and `.claude-plugin/plugin.json` both **omit
  `version`** -- the git commit SHA drives update detection, so any pushed change
  propagates.
- `marketplace.json` uses `source: "./"` -- the plugin root is the repo root, so
  only `skills/` is exposed today. A future top-level `commands/`, `agents/`, or
  `hooks/` directory would silently become plugin content; keep those under
  `workflows/` where they belong.
- `workflows/_shared/agents/*.md` are deliberately **not** in the plugin: they
  are workflow-coupled (they reference the gate hooks and `WORKFLOW.md`), and a
  plugin agent goes globally active in every project.
- Per-machine setup (marketplace add + install + `autoUpdate` +
  `enabledPlugins`) is in the root `README.md`.

## The store / overlay / sync model (the load-bearing structure)

Each `workflows/<name>/` has two layers:

- **`core/`** -- every file that is identical for every repo running the
  workflow: `commands/*.md`, `agents/*.md`, `hooks/*.py`, `WORKFLOW.md`,
  `settings.core.json`. `wf adopt` **copies** these into `.claude/`
  (`.claude/commands/`, etc., renaming `settings.core.json` ->
  `settings.json`). A `git pull` of the store does **not** by itself change an
  adopter -- run `wf sync` (see `bin/wf` below) to reconcile. `core/` files
  carry **zero per-project values** -- see "Parameter discipline" below.
- **`local/`** -- templates copied into `.claude/` as real, committed files at
  adopt time and owned by the repo thereafter: `project.json` (the one
  config file -- source glob, format/lint/test commands, and workflow knobs),
  `settings.local.json` (the repo's lint/test allows, `GH_REPO`), `CLAUDE.md`
  stub, `ARCHITECTURE.md` (issue/todo-gated), `todos.json` (todo-gated),
  `.gitignore`.

Plus, per workflow: `VERSION` (an integer, bumped on any `core/` change) and
`MIGRATIONS.md` (append-only; one block per change that needs an already-adopted
repo to do something beyond a file copy -- a new `project.json` key, a
`settings.local.json` entry). A pure-prose `core/` change adds no migration
block; `wf sync` alone delivers it.

`workflows/_shared/` holds files identical **across** workflows --
`hooks/_hooklib.py`, `hooks/doc_drift.py`, `agents/{implementer,reviewer,
architecture-checker}.md`, `ARCHITECTURE.md` -- and each workflow's `core/`
**symlinks (relative) to `_shared/`**. Edit the `_shared/` copy and every
workflow gets it. Do not un-share by replacing a symlink with a copy unless a
real divergence forces it.

### The three workflows

See [`workflows/README.md`](../workflows/README.md) for what each does and
when to use it -- `issue-gated` (canonical, GitHub-issue-traced),
`todo-gated` (same shape, backed by `.claude/todos.json` instead of GitHub),
`str8-2-main` (the stripped subset this repo runs on itself, no work branch
or edit gate).

### `bin/wf`

Stdlib Python. `wf adopt <workflow> [dir]` sets up `.claude/`, copying `core/`
and `local/` in and recording a hash of every core file in
`.claude/.workflow`. `wf sync [--accept] [dir ...]` git-pulls the store, then
for each registered repo reconciles core files against those hashes: copies
in an untouched update, leaves a locally-edited file alone, and -- when both
sides changed the same file -- leaves the repo's file untouched and writes
the store's version as `<file>.core-new` for a manual merge. `--accept`
additionally records the store's `VERSION` for named repos, once any
`MIGRATIONS.md` follow-up is done. `wf status [dir ...]` does the same
reconciliation read-only (no pull, no writes) and prints pending
`MIGRATIONS.md` blocks. `wf projects` lists the registry (`.projects`,
gitignored). Adopting repos are registered in `.projects`.

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
  `$CLAUDE_PROJECT_DIR` (not `__file__`), since `hooks/` is a real copy in
  every adopter, not this store. Never fatally block a session -- except the
  gate hooks, which deny edits by design.
- **Skills** (`skills/*/SKILL.md`): frontmatter is `name:` (must equal the
  directory name) + a trigger-phrase `description:`, plus
  `disable-model-invocation: true` for an explicit-invoke-only skill; body is
  plain Markdown rules and before/after examples. Real files only -- no symlinks
  (see "Skills ship as a plugin").
- Prose style across the repo's docs: `--` not em-dash; tables and Mermaid
  `flowchart TD` for lifecycle diagrams.

`workflows/README.md` is the adoption guide, the sync guide, and the per-workflow
"use it when / don't bother when" selector. `workflows/_shared/README.md`
documents the cross-workflow dedup.

## This repo runs `str8-2-main` on itself

`.claude/` here is an **adopter** of `workflows/str8-2-main/`, same as any
other project: `commands/` / `agents/` / `hooks/` / `WORKFLOW.md` /
`settings.json` are real, committed copies of
`workflows/str8-2-main/core/`, plus `.claude/project.json`,
`.claude/settings.local.json`, `.claude/CLAUDE.md`, `.claude/.workflow`.
Because it's the *same clone*, editing `workflows/str8-2-main/core/` and
running `wf sync .` here picks the change up immediately -- no separate pull
needed, but still not automatic; run `wf sync .` after a `core/` edit like
any other adopter would after a store pull.

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
  `pip install --user --break-system-packages pymarkdownlnt`).

## Validating changes locally

- Python: `git ls-files '*.py' | xargs python3 -m py_compile` -- covers
  `bin/wf`, `workflows/_shared/hooks/*.py`, `workflows/*/core/hooks/*.py`, and
  `workflows/todo-gated/core/scripts/todos.py` once committed; for uncommitted
  edits to those, `py_compile` them directly first.
- `todos.py`: `py_compile` covers syntax; behavior needs an adopted repo --
  `cd <adopter> && python3 .claude/scripts/todos.py validate`
- Markdown: `python3 -m pymarkdown --config .pymarkdown.json scan -r <path>`
- Symlinks resolve: `find workflows .claude -xtype l` prints nothing
- `wf` round-trip: `wf adopt str8-2-main <scratch>/r && wf status`
