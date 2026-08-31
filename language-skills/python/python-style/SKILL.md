---
name: python-style-guide
description: Enforces a specific Python code style for Python projects — numpy-style docstrings, static typing with mypy, black formatting at 80 characters, strict naming conventions, and comment discipline. Use this skill whenever writing, editing, reviewing, or refactoring any Python code (.py files) for this user, including new functions, classes, modules, or scripts — even for small snippets or single-function edits. Also use it when the user asks to "clean up," "format," "lint," or "make this more idiomatic" for any Python file. Do not wait for the user to explicitly mention style guidelines; apply these rules by default to all Python output. For pytest test files specifically, also load the companion `python-tests` skill.
---

# Python style guide

A consistent style makes a codebase easier to scan, review, and
maintain. Apply every rule below to all Python code you write or edit
for this user, not just when asked to "clean up" — inconsistency
between old and new code in the same file is its own kind of mess.

For worked before/after examples of any rule, read
`references/examples.md`. Don't guess at edge cases from the summary
below — the reference file has the concrete version.

## Docstrings

Use numpy-style docstrings, but scope them to how much a reader
actually needs:

- **Public functions, methods, and class `__init__`s**: full numpy
  docstring — summary line, `Parameters`, `Returns` (skip either
  section if genuinely not applicable, e.g. a function with no
  params). A `Notes` section is fine for context that helps a caller,
  but never document exception/error types there — that's what the
  type signature and tests are for, and duplicating it in prose tends
  to drift out of sync with the actual code.
- **Never include a `Raises` section.** Same reasoning as excluding
  exceptions from `Notes`: which exceptions a function can raise is
  determined by its body and the functions it calls, so a `Raises`
  list is prose duplicating code — it drifts the moment a call site
  changes and nothing forces it back in sync. Let the implementation
  and tests be the source of truth.
- **Private functions/methods** (leading underscore): a one-line
  description only. No `Parameters` or `Returns` — the point of a
  private helper is that its contract is local and small enough not
  to need one.
- **Dataclasses**: a one-line (or short) summary only. No `Parameters`
  section — the field names, types, and defaults in the class body
  already are the contract; a `Parameters` block just restates them in
  prose and drifts the moment a field is added, renamed, or removed.

After each docstring, there should be a whitespace before the next line of code.

## Typing

Assume static typing throughout: every function signature gets
parameter and return annotations. Use `X | None` rather than
`Optional[X]` — same meaning, less to import, and it reads closer to
how the type actually behaves. Reach for `@overload` (from `typing`)
when a function's return type depends on which argument type was
passed in, rather than trying to express that with a union return
type that forces callers to narrow it themselves. Also add a whitespace after each overload definition.

Code should type-check cleanly under `mypy`. If you're not able to run
`mypy` in the current environment, still write code as if it will be
checked — fully annotated, no implicit `Any`.

## Formatting

Format with `black`, configured to an 80-character line length rather
than black's 88-character default. `assets/pyproject.toml` has the
config to drop into the project (`[tool.black] line-length = 80`,
plus matching `mypy` and `isort` settings) — copy it in if the project
doesn't already have one, or merge the relevant keys if it does.

When a line would exceed 80 characters — function definitions, calls,
or long conditionals — use a hanging indent: nothing follows the
opening `(`, the closing `)` starts its own line at the original
indent level, and each argument gets its own line. This applies
symmetrically to definitions and call sites. See
`references/examples.md` for the exact shape.

## Constants

Default to inlining a literal value. Promote it to a named constant
only when it's genuinely necessary (a magic number that needs a name
to be understood) or it recurs 3+ times in the same file — at that
point a single named constant is less risky than three copies that
could drift. Never introduce a module-private (`_SOMETHING`) constant
— if a value is genuinely necessary as a named constant, make it
public instead. A private constant adds a layer of indirection a
reader has to jump through for no benefit over just inlining the
value.

## Naming

`snake_case` for functions and variables. `PascalCase` (what's
sometimes called "CamelCase" colloquially) for classes and type
aliases.

## Whitespace before `return`

In any function or method, leave a blank line between the last line of
logic and the `return` statement — it visually sets the return apart
from the setup/computation above it. Exception: if `return` is the
only statement in the body (nothing precedes it), there's nothing to
separate it from, so no extra blank line is needed there — the blank
line already required after the docstring (see Docstrings) covers it.

## Comments

Every comment and docstring ends in a period, and comment text is
lowercase throughout (including the first word) — this keeps the
visual weight of comments low relative to code. Use comments to
explain *why* something is done a particular way, not to restate what
well-named variables and straightforward operations already make
obvious. A comment on self-explanatory code is noise the next reader
has to filter out.

## Strings, logging, and imports

- Build strings with f-strings; avoid `.format()` and `%`-formatting
  in ordinary code.
- **Exception**: logging calls should use `%`-style placeholders
  (`log.info("user %s logged in.", user_id)`, not an f-string). This
  keeps the interpolation lazy, so it's skipped entirely when the log
  level would filter the message out anyway — an f-string argument
  gets built regardless of whether it's ever used.
- Group imports into three blocks separated by a blank line: standard
  library, then third-party, then local/first-party. Within each
  block, alphabetical order is fine but not required.

## Exceptions

Never use a bare `except:`. Catch the specific exception type(s) you
expect and know how to handle — a bare `except` (or `except Exception`
used as a catch-all) silently swallows bugs and makes failures harder
to trace.

## Tests

Test-writing conventions (pytest structure, test classes, fixtures,
`tests/resources/`, `conftest.py`, `tests/utils.py`) live in the
separate `python-tests` skill — use that skill whenever writing or
editing test files. The rules in this skill still apply to test code
where they're not superseded there (e.g. typing, formatting, naming).

## After writing code

If `black`, `mypy`, and `isort` are available in the environment, run
them against any file you've written or edited before considering the
task done:

```bash
black --line-length 80 <file>
isort --profile black --line-length 80 <file>
mypy <file>
```

Fix anything they flag rather than leaving it for the user to catch.
