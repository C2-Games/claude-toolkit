# claude-toolkit

Organization library of generic Claude Code skills, agents, commands, and hooks. Nothing here runs on its own — each item is meant to be copied (or symlinked) into another project's `.claude/` to change how Claude behaves *there*.

## Layout

| Dir | What's in it |
|---|---|
| `skills/<language>/<skill-name>/` | Code style/test conventions Claude applies when writing that language, anywhere. |
| `agents/<agent-name>/<agent-name>.md` | Subagents a main session can dispatch (implement a plan task, review a diff, draft an issue). |
| `commands/<category>/*.md` | Slash commands, grouped by the workflow they belong to. |
| `hooks/<category>/*.py` | Hook scripts a target repo can wire into its own `settings.json`. |
| `docs/` | Longer guides for multi-file features (e.g. how to adopt a whole pipeline). |

## Current contents

- **Skills**: `cpp-style`, `python-style`, `python-tests` — style guides Claude auto-invokes
  when writing C++ or Python.
- **Issue-workflow pipeline**: `agents/{implementer,reviewer,issue-drafter}`,
  `commands/issue-workflow/*`, `hooks/issue-workflow/issue_gate.py`, `hooks/toolchain/*` — an
  issue → branch → plan → implement → review flow. See `docs/ISSUE_WORKFLOW.md` for what it
  does and how to configure it in a target repo.

## Adding something new

Everything here must be generic — usable in any target repo, not hard-wired to one project's
paths, usernames, or architecture. If it only makes sense for one specific repo, it belongs
in that repo's own `.claude/`, not here. See `CLAUDE.md` for the layout conventions to follow
when adding a skill/agent/command/hook.

## This repo's own `.claude/settings.json`

Denies `git commit`/`git push` here — nothing in this repo should be committed or pushed by
Claude without the user doing it directly.
