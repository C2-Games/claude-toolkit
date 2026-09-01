---
description: Run the local check sweep (format, lint, tests/build)
---

This is the **only** place formatting, linting, and tests run, and the only gate
between a change and `main`. There is no write-time hook -- nothing has been
checked until this runs, so it is the final step of every plan and must pass
before `/ship`.

> **INIT:** replace the `<!-- INIT: ... -->` placeholders below with this
> project's real commands and source globs. The globs must match the ones in
> `/ship` exactly -- both hash the same file set.

## 1. Apply formatting

Formatting has one correct answer, so fix it rather than report it. Run it
first: a formatter run in `--check` mode later in the sweep would fail on a file
this step would have fixed.

```bash
<!-- INIT: in-place formatter, e.g. `ruff format .` / `gofmt -w .` / `cargo fmt` -->
```

It edits in place. Mention it in passing if it changed files; do not paste diffs.

## 2. Run lint + tests

```bash
<!-- INIT: lint, e.g. `ruff check .` / `golangci-lint run` / `cargo clippy -- -D warnings` -->
<!-- INIT: tests/build, e.g. `pytest -q` / `go test ./...` / `cargo test` -->
```

Run a slow suite in the background -- use `run_in_background: true` on the `Bash`
call, wait for its completion notification (don't poll with `sleep`), then read
the output. A fast one can run in the foreground.

Any non-zero exit is a failure -- report the failing section and fix it, then
re-run this command from step 1.

Once everything passes, stamp it so `/ship` can confirm freshness later:

```bash
<!-- INIT: replace the find globs with this project's source dirs/extensions -->
find src -type f \( -name "*.py" \) -print0 | sort -z | xargs -0 sha256sum | sha256sum | cut -d" " -f1 > .claude/.last-check
```

That is the whole sweep. This workflow has no review pass -- if you want a
structural review before shipping, ask for one explicitly. Otherwise, proceed to
`/ship`.
