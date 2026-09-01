# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A personal library of copy-in Claude Code building blocks. **Nothing here runs
in place** -- every artifact is copied into *another* repo's `.claude/` (or into
`~/.claude/skills/`) to change how Claude behaves there. Two product lines:

- `language-skills/<lang>/<skill>/` -- per-language code-style skills, each a
  `SKILL.md` plus optional `assets/`, `scripts/`, `references/`. Copied to
  `~/.claude/skills/` (personal) or a project's `.claude/skills/` (team).
- `workflows/<name>/` -- complete `.claude/` templates that impose one way of
  working on a repo.

## The workflow family (the load-bearing structure)

The three workflows are variations on one design, not independent programs:

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

**Cross-file invariants -- a change in one place usually needs mirroring:**

- `hooks/_hooklib.py` is **byte-identical** in all three workflows. Edit one,
  edit all three.
- The `### Task <N>` breakdown block (`**Subagent:**` / `**Depends on:**`), the
  two-part `/check` structure, `agents/implementer.md`'s scope-discipline rules,
  and the header-only commit convention (`type: Sentence-case description`, no
  body, no trailers) each appear in multiple workflows. Keep them in sync unless
  a divergence is deliberate.
- `agents/implementer.md` is shared by all three; `reviewer.md` and
  `architecture-checker.md` by issue-gated + todo-gated; `ARCHITECTURE.md` by
  those same two (byte-identical template).

**Templates stay generic.** Project specifics are filled in only by a copy's
`INIT.md` at adoption time, then `INIT.md` deletes itself. Placeholder
conventions to preserve when editing templates:

- `<!-- INIT: ... -->` in Markdown, `# INIT:` comments in Python
- `<!-- ARCHITECTURE-TEMPLATE-UNFILLED -->` as line 1 of `ARCHITECTURE.md`
  (the `architecture-checker` agent no-ops while it is present)
- `env.GH_REPO: "OWNER/REPO"` in issue-gated's `settings.json`

`workflows/README.md` is the adoption guide and the per-workflow "use it
when / don't bother when" selector. It gets a new `##` section per workflow.

## Conventions when editing templates

- **Commands** (`commands/*.md`): YAML frontmatter `description:` + optional
  `argument-hint:`; body addresses Claude in the second person and uses
  `$ARGUMENTS`.
- **Agents** (`agents/*.md`): frontmatter `name:` / `description:` / `tools:`
  (comma list).
- **Hooks** (`hooks/*.py`): Python **stdlib only**. Wired in `settings.json` as
  `python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/X.py" || python "..."` with
  `"shell": "bash"` and a 15-20s `timeout`. Never fatally block a session --
  except the gate hooks, which deny edits by design.
- **Skills** (`language-skills/*/SKILL.md`): frontmatter is `name:` + a
  trigger-phrase `description:` only; body is plain Markdown rules and
  before/after examples.
- Prose style across the repo's docs: `--` not em-dash; tables and Mermaid
  `flowchart TD` for lifecycle diagrams.

## This repo runs `str8-2-main` on itself

`.claude/` here is a **filled-in copy** of `workflows/str8-2-main/`. The generic
template still lives at `workflows/str8-2-main/` -- behavior changes to the
workflow belong in the template first, then get re-merged here if they matter.
`.claude/INIT.md` is intentionally absent (adoption is already done).

- Day-to-day operating manual: `.claude/WORKFLOW.md`.
- Entry point: `/send-it <request>`, or just make a request. Non-trivial work
  goes through plan mode with a `### Task N` breakdown dispatched to
  `implementer` agents. Single-file doc edits and true one-liners skip formal
  plan mode.
- `/check` (the only gate, must end every plan): validates every tracked/new
  `.json` with `python3 -m json.tool`, then runs
  `python3 -m pymarkdown --config .pymarkdown.json scan -r .`, then stamps
  `.claude/.last-check` with a hash of all Markdown. `.pymarkdown.json` disables
  the stylistic rules the pre-existing docs don't follow and enables the
  front-matter extension; tighten it as docs are rewritten.
- `/ship`: re-hashes the Markdown, refuses on mismatch, then makes a
  header-only commit and pushes to `origin/main`. `git commit`/`push` are
  allowed here (unlike the other two workflows).
- One-time setup on a fresh machine: `pipx install pymarkdownlnt` (or
  `pip install --user --break-system-packages pymarkdownlnt`).

## Validating changes locally

- Python hooks/scripts: `git ls-files '*.py' | xargs python3 -m py_compile`
- `scripts/todos.py` (todo-gated): `python3 workflows/todo-gated/scripts/todos.py validate`
- Markdown: `python3 -m pymarkdown --config .pymarkdown.json scan -r <path>`
