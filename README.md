# claude-toolkit

A personal library of Claude Code building blocks — language-style skills and
full `.claude/` workflows — plus the `bin/wf` CLI that delivers them into
other repos. Nothing here runs on its own; each piece changes how Claude
behaves in the repo that adopts it.

## Where to put this repo

Clone it to `~/.claude/claude-toolkit` — it sits next to the other personal
Claude Code state under `~/.claude/`. `wf` doesn't actually care where the
repo lives (it finds the store from its own path), but pick one place and
stay there.

Put `wf` on your PATH, once per machine:

```bash
ln -s ~/.claude/claude-toolkit/bin/wf ~/.local/bin/wf   # if ~/.local/bin is on PATH
# otherwise: add `export PATH="$HOME/.claude/claude-toolkit/bin:$PATH"` to your shell rc
```

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

A workflow is a complete `.claude/` setup — commands, agents, hooks — that
imposes one way of working on a repo. Pick one in
[`workflows/README.md`](workflows/README.md), then adopt it:

```bash
cd your-project
wf adopt str8-2-main        # or: issue-gated, todo-gated
```

This copies the workflow's files into `.claude/` as real, committed files —
adopters are self-contained, not linked back to this store. Then, in Claude
Code in that project, say **"read `.claude/INIT.md` and follow it"** to fill
in the repo-specific config and delete the interview file.

## Keeping an adopted repo in sync

Pulling this store doesn't change an adopted repo by itself — you have to
sync:

```bash
wf sync              # git-pull the store, reconcile every registered repo's core files
wf status <repo>     # check one repo without pulling
```

For each core file, `wf sync` compares three versions — what the repo last
synced, what the store has now, and what's on disk in the repo — and acts
per file:

- Repo hasn't touched it, store moved on → copied in automatically.
- Repo edited it, store didn't change → left alone.
- **Both changed** → the repo's file is left untouched, and the store's new
  version is written next to it as `<file>.core-new`. Merge `.core-new`'s
  content into the real file by hand, delete `.core-new`, and run `wf sync`
  again — once the file matches the store, the conflict clears on its own.

`wf status` also surfaces any `MIGRATIONS.md` entries a repo hasn't
acknowledged yet — changes that need a manual step beyond copying a file
(a new `project.json` key, for example). `wf sync --accept <repo>` records
those as done once you've handled them.

## Editing this store

If you're changing a workflow's `core/`, or this repo's own setup, see
[`.claude/CLAUDE.md`](.claude/CLAUDE.md) — this repo adopts `str8-2-main` on
itself the same way any other project would.
