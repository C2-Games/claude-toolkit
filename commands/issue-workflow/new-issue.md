---
description: File a new GitHub issue, with milestone assignment
argument-hint: <freeform description of the issue>
---

Dispatch the `issue-drafter` agent (`agents/issue-drafter/issue-drafter.md`) with the request:
**$ARGUMENTS**

`issue-drafter` cannot ask the user directly — `AskUserQuestion` is unavailable inside subagents in
this environment. Expect it to return its draft(s) plus a list of open questions and then stop. Ask
those questions yourself with `AskUserQuestion`, then resume `issue-drafter` via `SendMessage` with
the answers and an explicit go-ahead so it can create the issue(s).

This command only files the issue — if this repo's workflow has a "start work on an issue" command
(e.g. `/start-issue`), run it afterward to begin coding against the new issue.

The same dispatch also triggers without the user typing `/new-issue`: when a change is requested
directly, with no issue on record yet, dispatch `issue-drafter` with that request before proceeding,
then run the same round trip — ask its open questions directly, resume it with the answers and
confirmation, and only then does it create the issue.
