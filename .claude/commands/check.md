---
description: Run the local check sweep (format, lint, tests/build)
---

This is the **only** place formatting, linting, and tests run, and the only gate
between a change and the default branch. There is no write-time hook -- nothing
has been checked until this runs, so it is the final step of every plan and must
pass before `/ship`.

The commands are not hardcoded here -- they live in `.claude/project.json`
(`format_cmd`, `lint_cmd`, `test_cmd`, and `find_expr`, a command that emits the
source files NUL-separated). Read each one with:

```bash
cfg() { python3 -c "import json,sys;print(json.load(open('.claude/project.json')).get(sys.argv[1],''))" "$1"; }
```

A blank value means "skip that step".

## 1. Apply formatting

```bash
FMT=$(cfg format_cmd); [ -n "$FMT" ] && eval "$FMT"
```

Skip with a one-line note when `format_cmd` is blank. Otherwise it edits in
place -- run it first (a `--check`-mode formatter later in the sweep would fail
on a file this fixes). Mention it in passing if it changed files; do not paste
diffs.

## 2. Run lint + tests

```bash
LINT=$(cfg lint_cmd); [ -n "$LINT" ] && eval "$LINT"
TEST=$(cfg test_cmd); [ -n "$TEST" ] && eval "$TEST"
```

Run a slow suite in the background -- `run_in_background: true` on the `Bash`
call, wait for its completion notification (don't poll with `sleep`), then read
the output. A fast one can run in the foreground.

Any non-zero exit is a failure -- report the failing section and fix it, then
re-run this command from step 1.

Once everything passes, stamp the freshness hash so `/ship` can confirm it later.
`/ship` recomputes this exact line -- keep them identical:

```bash
FIND=$(cfg find_expr)
eval "$FIND" | sort -z | xargs -0 sha256sum | sha256sum | cut -d" " -f1 > .claude/.last-check
```

That is the whole sweep. This workflow has no review pass -- if you want a
structural review before shipping, ask for one explicitly. Otherwise, proceed to
`/ship`.
