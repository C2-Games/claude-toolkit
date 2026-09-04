<!-- INIT: this is a stub. Run `/init` (Claude Code built-in) to generate a real
     one from the codebase, or delete it -- the workflow runs without it. This
     workflow has no doc_drift hook, so nothing will nag you to keep it current. -->

# CLAUDE.md

This file provides guidance to Claude Code when working with code in this
repository.

## What this repo is

<!-- INIT: one paragraph -- what the project is, its main pieces. -->

## Workflow

This repo runs the `str8-2-main` workflow (`.claude/WORKFLOW.md`). Non-trivial
work goes through plan mode with a `### Task N` breakdown, then `/check`, then
`/ship`. Local config -- the check commands and source globs -- lives in
`.claude/project.json`.
