---
description: Commit the change with a header-only message and push it straight to the default branch
---

This is the chaotic bit: `/ship` commits and pushes to the default branch itself.
`/check` is the only thing between the change and `origin` -- so this command
refuses to run if `/check` is not current.

## Steps

1. **Confirm `/check` is current.** Recompute the same hash `/check` stamps -- use
   the identical Markdown globs from `/check`:

   ```bash
   git ls-files -z --cached --others --exclude-standard '*.md' | sort -z | xargs -0 sha256sum | sha256sum | cut -d" " -f1
   ```

   Compare it to `.claude/.last-check` (gitignored, written by `/check`). If the
   file is missing, or the hash differs, **stop** -- tell the user source has
   changed since `/check` last passed (or `/check` has never run here) and to run
   it before `/ship`.

2. **Verify the branch.** Confirm `git rev-parse --abbrev-ref HEAD` is `main`.
   That is expected here; this workflow does not use work branches. If HEAD is on some other branch, say so
   and ask whether to push that branch instead or switch back.

3. **Show what would ship.** `git status --short` and
   `git diff --stat origin/main...HEAD`.

   Name any file that should **not** go in -- unrelated untracked files, scratch
   files, editor cruft -- so it is left out of the `git add`. Stage only the files
   this change actually touched.

4. **Draft the commit message.** Header only:

   ```text
   type: Sentence-case description
   ```

   `type` is one of `feat` / `fix` / `refactor` / `docs` / `test` / `chore`,
   matching the nature of the change. An optional scope is allowed
   (`fix(build):`). **No body. No `Co-Authored-By` trailer. No `Claude-Session`
   or any other trailer.** A single `-m`. Draft a real message -- do not leave a
   placeholder.

5. **Commit and push.**

   ```bash
   git add <the specific files from step 3>
   git commit -m "<type>: <Sentence-case description>"
   git push
   ```

   Report the resulting commit hash and confirm it is on `origin/main` (or
   whatever the default branch is).

   If `git push` fails -- non-fast-forward, protected branch, no upstream -- stop
   and show the exact error. Do not force-push and do not retry with `--force`;
   hand the situation back to the user.
