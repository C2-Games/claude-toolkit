# claude-toolkit

A personal library of Claude Code building blocks — reusable skills and full
`.claude/` workflows. Nothing here runs on its own; each piece changes how
Claude behaves in the repo that adopts it. Two delivery channels:

| | Skills (`skills/`) | Workflows (`workflows/`) |
|---|---|---|
| Delivered by | the `toolkit-skills` plugin | the `bin/wf` CLI (`wf adopt` / `wf link`) |
| Lands as | a plugin, shared across every project | real, committed files in each repo's `.claude/` |
| Updates | automatically (plugin auto-update) | on demand (`wf sync`); a SessionStart hook tells you when you're behind |

Workflows land as committed files per repo — a teammate gets them from the
repo, not this store — so a bad auto-push would rewrite every adopter's
`.claude/` mid-session. Skills are advisory and identical everywhere, so they
update themselves.

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

## `skills/`

Reusable skills, one directory each. Most are code-style skills that define the
naming, commenting, docstring, and formatting conventions Claude applies when
writing or editing that language — auto-invoked, not waited on.

| Path | Skill |
|---|---|
| `skills/python-style/` | Python style — numpy docstrings, mypy typing, black at 80 |
| `skills/python-tests/` | pytest conventions (companion to `python-style`) |
| `skills/cpp-style/` | C++ style — Google base + Allman braces, naming, Doxygen placement |
| `skills/unslop/` | strip AI tells from prose — explicit-invoke only |

These ship as the `toolkit-skills` plugin (`.claude-plugin/marketplace.json`)
and update themselves — no `wf`, no hand-copying into `~/.claude/skills/`.

### One-time plugin setup, per machine

```bash
# 1. this repo is cloned at ~/.claude/claude-toolkit and wf is on PATH (above)
# 2. in any Claude Code session:
/plugin marketplace add C2-Games/claude-toolkit
/plugin install toolkit-skills@claude-toolkit
```

Then add to `~/.claude/settings.json` so new commits land without a manual
update:

```json
{
  "extraKnownMarketplaces": {
    "claude-toolkit": {
      "source": { "source": "github", "repo": "C2-Games/claude-toolkit" },
      "autoUpdate": true
    }
  },
  "enabledPlugins": { "toolkit-skills@claude-toolkit": true }
}
```

The repo is private, so the machine needs working GitHub git auth (`gh` or ssh)
before `/plugin marketplace add`. With `autoUpdate` on, Claude Code refreshes the
marketplace and installed plugin in the background a few minutes after launch;
pick the new version up with `/plugin` → reload or on the next launch.

If you still have loose `~/.claude/skills/{python-style,python-tests,unslop}`
copies from before, delete them once the plugin is confirmed loaded (`/plugin`
lists `toolkit-skills` and the skills invoke) — otherwise the names collide.

To change a skill: edit it in this repo, `/check` + `/ship`. Every machine gets
it on its next auto-update.

## `workflows/`

A workflow is a complete `.claude/` setup — commands, agents, hooks — that
imposes one way of working on a repo. Pick one in
[`workflows/README.md`](workflows/README.md), then adopt it:

```bash
cd your-project
wf adopt str8-2-main          # empty .claude/  — or: issue-gated, todo-gated
wf adopt str8-2-main --force  # non-empty .claude/, install the full workflow over it
wf link  str8-2-main          # non-empty .claude/, fill only missing files
```

This copies the workflow's files into `.claude/` as real, committed files —
adopters are self-contained, not linked back to this store. Then, in Claude
Code in that project, say **"read `.claude/INIT.md` and follow it"** to fill
in the repo-specific config and delete the interview file.

## Keeping an adopted repo in sync

Pulling this store doesn't change an adopted repo by itself — you sync:

```bash
wf sync              # git-pull the store, then REPORT only (writes nothing)
wf sync <repo>       # pull, then reconcile that repo   (--all for every repo)
wf status <repo>     # one repo's sync state, no pull
wf diff <repo>       # unified diff of every core file that repo has edited
wf backport <repo> <relpath>   # fold that edit back onto the store's core/
wf switch <workflow> [repo]    # already adopted — move it to another workflow
```

A bare `wf sync` writes nothing — every adopted repo you open enrolls itself
(via its `SessionStart` notify hook), so a blanket reconcile would touch repos
you aren't working in. Name the repo, or pass `--all`. That same hook is what
tells a session "this repo is behind the store, run `wf sync`" — it only
reports; it needs `wf` on PATH.

For each core file, `wf sync <repo>` compares three versions — what the repo
last synced, what the store has now, and what's on disk in the repo — and acts
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

`wf switch <workflow> <repo>` moves an already-adopted repo to a different
workflow: it installs the new core in full, removes the old workflow's
unique files, and writes `.claude/SWITCH.md` — a generated checklist for
Claude to work through, the way `wf adopt` writes `INIT.md` for a fresh
onboarding. See [`workflows/README.md`](workflows/README.md) for details.

To fold an ad-hoc fix from one repo back into the store: `wf diff <repo>` to
see it, `wf backport <repo> <relpath>` to copy it onto `core/` (a `_shared/`
file reaches every workflow — it warns you). Then review, add a `MIGRATIONS.md`
block if adopters must act, commit, and the next `wf sync <repo>` propagates it.

Across machines: clone this store once per machine (at `~/.claude/claude-toolkit`),
keep `wf` on PATH, and `wf sync` pulls it before reconciling.

## Editing this store

If you're changing a workflow's `core/`, or this repo's own setup, see
[`.claude/CLAUDE.md`](.claude/CLAUDE.md) — this repo adopts `str8-2-main` on
itself the same way any other project would.
