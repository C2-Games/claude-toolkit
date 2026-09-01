---
description: Take a request through plan mode with a task breakdown, then implement it
argument-hint: <what you want done>
---

Work the request: **$ARGUMENTS**

This workflow has no branch step and no edit gate -- work lands directly on the
default branch. What it keeps is plan-mode discipline: read the code, agree a
plan, break it into isolated tasks, then implement.

## Enter plan mode

Call `EnterPlanMode`, then read the code the request touches and produce an
implementation plan before writing anything. Do not start editing straight from
the request text -- requests are often terse and understate which files move.

**Exception -- small changes skip formal plan mode.** A single-file edit that is
purely documentation/comment text, or a genuine one-line fix, does not need
`EnterPlanMode`: state the change in one sentence and proceed. Keep the bar
genuinely small and single-file.

**Ask before finalizing.** Ask clarifying implementation questions rather than
guessing. Design and architecture decisions are the developer's to drive -- the
plan's job is to implement that precisely, not to invent architecture unprompted.

The plan should name the specific files and symbols to change, follow the
conventions in `.claude/CLAUDE.md` if the repo has one, and **must end with
`/check`**. Nothing is checked while you write -- there is no write-time hook --
so a plan without `/check` ships unverified code. Present it with `ExitPlanMode`
for approval.

## Break the plan into isolated tasks

Write each task with this structure so parallel-dispatch eligibility is obvious at
a glance:

```
### Task <N>: <short title>
**Subagent:** implementer
**Depends on:** Task <M> | independent
```

followed by the task's description. Once approved (`ExitPlanMode`), dispatch every
task marked `independent` (relative to what's already landed) in parallel to the
`implementer` agent (`.claude/agents/implementer.md`) -- multiple `Agent` tool
calls in a single message. Run a task with a `Depends on` marker only after that
dependency's implementer call has returned and been folded in.

**Mirror the breakdown as tracked tasks.** Before calling `ExitPlanMode`, call
`TaskCreate` once per task (`subject` = the short title, `description` = the
task's description) and follow with `TaskUpdate` to set `owner` to the subagent
name and `addBlockedBy` to the ids of the tasks it depends on. Mark each task
`completed` as its implementer dispatch returns. Skip this for a single-task plan.

**Include a `CLAUDE.md` step when the change earns one** -- only if the repo has a
`.claude/CLAUDE.md`. Update it for: a new subsystem or file-layout change,
ownership moving between modules, a changed convention, or a placeholder becoming
a real implementation. Skip it for renames, small refactors, and bugfixes -- it is
a map, not a changelog. State either way in the plan.

**If implementation surfaces something that would change the approved plan** --
not a small in-scope detail, but a real departure from what was approved -- stop,
explain the hurdle, and ask the developer how to proceed. Do not improvise past
it.

## After implementation

The plan ends at `/check`. Once `/check` passes, `/ship` makes the commit and
pushes -- do not commit mid-plan, and do not run `git commit` / `git push`
yourself before `/ship`.
