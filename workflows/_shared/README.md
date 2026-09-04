# `_shared/` -- files identical across workflows

Each workflow's `core/` **symlinks** (relative) to the files here, so an edit in
one place reaches every workflow:

| file | used by |
|---|---|
| `hooks/_hooklib.py` | all three workflows |
| `hooks/doc_drift.py` | issue-gated, todo-gated |
| `agents/implementer.md` | all three |
| `agents/reviewer.md` | issue-gated, todo-gated |
| `agents/architecture-checker.md` | issue-gated, todo-gated |
| `ARCHITECTURE.md` | issue-gated, todo-gated (as a `local/` template) |

## Rules

- These files must stay **workflow-agnostic**. A line that only makes sense for
  one workflow (a specific command name, "GitHub issue" vs "todo") gets
  generalized -- see the existing phrasings ("the workflow's start command",
  "the project's tracker", "`.claude/.current-issue` or `.claude/.current-todo`,
  whichever exists").
- No per-project values either -- same discipline as `core/`. Branch is derived
  (`_hooklib.default_branch()`); config comes from `.claude/project.json` via
  `_hooklib.load_project_config()`.
- If a genuine divergence is unavoidable, replace that workflow's symlink with a
  real file and note why in the workflow's `core/` -- do not fork `_shared/`.
- `_hooklib.py` and any hook here resolves repo state through
  `$CLAUDE_PROJECT_DIR`, never `__file__` (these run through a symlinked
  `.claude/hooks/`).
