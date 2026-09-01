---
description: Run the local check sweep (JSON validation, Markdown lint)
---

This is the **only** place linting runs, and the only gate between a change and
`main`. There is no write-time hook -- nothing has been checked until this runs,
so it is the final step of every plan and must pass before `/ship`.

This repo is docs plus a little stdlib Python. There is no autoformatter -- the
sweep validates and reports; it never rewrites files.

## 1. Validate JSON

Every tracked `.json` (the workflow `settings.json` files, `todos.json`, the
`.vscode` sample) must parse. A broken `settings.json` silently breaks whichever
workflow ships it.

```bash
git ls-files -z --cached --others --exclude-standard '*.json' | xargs -0 -I{} sh -c 'python3 -m json.tool "{}" > /dev/null || { echo "invalid JSON: {}"; exit 1; }'
```

Any non-zero exit is a failure -- name the file and fix it.

## 2. Lint Markdown

```bash
python3 -m pymarkdown --config .pymarkdown.json scan -r .
```

Needs PyMarkdown once: `pipx install pymarkdownlnt` (or
`pip install --user --break-system-packages pymarkdownlnt` on a
PEP-668 system). The `--config` flag is required -- PyMarkdown does not
auto-load `.pymarkdown.json`. That file (repo root) already disables the
stylistic rules the pre-existing docs don't follow (`md007`, `md013`,
`md029`, `md031`, `md032`, `md033`, `md040`, `md041`) and enables the
front-matter extension. Disable a further rule there only when it is purely
stylistic and fires on already-committed docs; fix genuine findings (broken
link fragments, malformed tables, stray tabs) in the file. Tighten the config
back up as docs get rewritten.

Any non-zero exit is a failure -- report the failing files and fix them, then
re-run this command from step 1.

Once both steps pass, stamp the Markdown tree so `/ship` can confirm freshness:

```bash
git ls-files -z --cached --others --exclude-standard '*.md' | sort -z | xargs -0 sha256sum | sha256sum | cut -d" " -f1 > .claude/.last-check
```

That is the whole sweep. This workflow has no review pass -- if you want a
structural review before shipping, ask for one explicitly. Otherwise, proceed to
`/ship`.
