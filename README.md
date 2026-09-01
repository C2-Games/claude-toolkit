# claude-toolkit

A personal library of Claude Code building blocks. Nothing here runs on its own —
each piece is copied into another project's `.claude/` to change how Claude behaves
*there*.

## `language-skills/`

Code-style skills, one per language. Each defines the naming, commenting, docstring,
and formatting conventions Claude applies when writing or editing that language —
auto-invoked, not waited on.

| Path | Skill |
|---|---|
| `language-skills/python/python-style/` | Python style — numpy docstrings, mypy typing, black at 80 |
| `language-skills/python/python-tests/` | pytest conventions (companion to `python-style`) |
| `language-skills/c++/cpp-style/` | C++ style — Google base + Allman braces, naming, Doxygen placement |

To use one: copy the skill directory into `~/.claude/skills/` so it applies across
every project you work on. Only put it in a project's own `.claude/skills/` when
the team shares a single style and it needs to travel with the repo — a
project-level skill overrides your personal one for that repo.

## `workflows/`

Complete `.claude/` setups — hooks, commands, agents, and docs that together impose
one way of working on a repo. They're generic until you run the workflow's
`INIT.md`, which tailors them to the project and then deletes itself.

See [`workflows/README.md`](workflows/README.md) for the list of workflows, what
each is for, and how to adopt one.

## This repo's own `.claude/settings.json`

Denies `git commit` / `git push` here — nothing in this repo should be committed or
pushed by Claude without the user doing it directly.
