<!-- INIT: this is a stub. Run `/init` (Claude Code built-in) to generate a real
     one from the codebase, or flesh it out by hand. The `reviewer`,
     `implementer`, and `architecture-checker` agents and the `doc_drift` hook
     all get more useful with a real one. -->

# CLAUDE.md

This file provides guidance to Claude Code when working with code in this
repository.

## What this repo is

<!-- INIT: one paragraph -- what the project is, its main pieces. -->

## Architecture

<!-- INIT: the module/layer shape, and where responsibilities live. The
     checkable rules go in `.claude/ARCHITECTURE.md`, not here. -->

## Workflow

This repo runs the `todo-gated` workflow (`.claude/WORKFLOW.md`): every change
traces to a row in `.claude/todos.json` (mutated only through
`.claude/scripts/todos.py`), goes through plan mode with a `### Task N`
breakdown, is built by `implementer` agents, and passes `/check` (format, lint,
tests, `reviewer`) before `/finish`. Local config -- the check commands, source
glob, and architecture rules -- lives in `.claude/project.json`,
`.claude/settings.local.json`, and `.claude/ARCHITECTURE.md`.
