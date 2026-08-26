---
description: Browse open GitHub issues for this repo
argument-hint: [search terms | label:refactor | assignee:@me]
---

List the open issues so we can pick what to work on. Filter: **$ARGUMENTS** (all open issues when
empty).

```bash
gh issue list --state open --limit 40 --json number,title,labels,assignees \
  --template '{{range .}}{{printf "%-5v" .number}} {{printf "%-10v" (index .labels 0).name}} {{.title}}{{"\n"}}{{end}}'
```

If this repo sets `GH_REPO` in `.claude/settings.json` (e.g. because the remote uses a non-default
host alias), `gh` resolves the repo from that automatically — don't pass `-R` or parse the git
remote yourself. Otherwise `gh` infers the repo from the remote as normal.

Pass `$ARGUMENTS` through as appropriate:
- bare words → `--search "<words>"`
- `label:x` → `--label x`
- `assignee:@me` → `--assignee @me`

## Presenting the results

Group by the type prefix in the title (`feat:`, `fix:`, `refactor:`, `docs:`, `test:`) if this
repo's issue titles follow that convention. Lead with the count, then a compact table of
number / type / title. Do not dump raw JSON.

To show one issue in full: `gh issue view <n>`.

## After picking

Hand off to `/start-issue <number> [more...]` — that is what records the issue and cuts the branch.

If `gh` reports it is not on PATH, the session's environment predates the install — restart Claude
Code. If it reports no authentication, run `gh auth login` (macOS: `brew install gh` first).
