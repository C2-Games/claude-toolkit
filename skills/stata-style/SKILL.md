---
name: stata-style
description: Enforces a consistent Stata code style — mandatory structured file headers, section/subsection banners, an 80-character line limit, tab indentation, strict lowercase/period comments with a fine-grained one-action-one-topic commenting style, uppercase-only globals, typed gen/egen, mandatory lab var labels, human-readable date-variable display formats, quiet (never quietly), a fixed categorical-encoding pattern, compress before every export, env-derived path globals, a centralized logging routine, and a fixed script preamble order. Use this skill whenever writing, editing, or reviewing any .do or .ado file, including small one-line edits, new cleaning/table scripts, or new .ado programs; apply it by default without waiting for the user to mention style.
---

# Stata style guide

Every rule below applies to all Stata code you write or edit. Match
these exactly — do not substitute generic Stata conventions. When
editing an existing file, keep new code consistent with the file
around it.

## 1. Mandatory `.do` file header

Every `.do` file opens with this banner. Fields are **Title-Case
labels**, each on its own line, with the value on the next line
indented by a tab, and a blank line between fields. `File:` is the
repo-relative path.

```stata
/*

--------------------------------------------------------------------------------

Created: 
	<date>

Author: 
	<author>

File: 
	<relative/path/to/file.do>

Purpose: 
	<one-line (or multi-line) description of what the script does>

Dependencies:
	<dependency>
	<dependency>

--------------------------------------------------------------------------------

*/
```

Divider lines are exactly 80 hyphens. `Dependencies:` lists each
`.ado` program and any external package on its own tab-indented line.
`.ado` files use a different, fuller header — see rule 13.

## 2. Section and subsection banners

**Top-level sections** use a full-width `=` banner block, header
centered with leading tabs:

```stata
/* 
================================================================================
								SECTION NAME 
================================================================================
*/
```

**Subsections** use a lighter `-` banner block:

```stata
/* 
--------------------------------------------------------------------------------
			      SUBSECTION NAME
--------------------------------------------------------------------------------
*/
```

**Fine-grained subheaders** use an inline single-line rule followed by
a short lowercase label:

```stata
*-------------------------------------------------------------------------------
* topic label.
```

Every top-level and subsection banner is separated from the code above
and below it by **2 blank lines**.

## 3. Line length

All code, comments, and banners stay within **80 characters** per
line. Wrap long statements with Stata's `///` continuation, indenting
the continued line so it lines up under (or just past) the opening
construct:

```stata
lab def edu_bin 1 "Less than High School" 2 "High School" ///
                3 "Some College" 4 "Bachelors" 5 "Masters +"
```

The wrapped value defs align under the first one (`3` lines up with
`1`), not under the command name. See `examples/line-length.md` for
more wrapping cases (long conditionals, long function calls).

## 4. Inline comments

Comments are lowercase and end with a period. The one uppercase
exception is the `NOTE:` emphasis tag. Two comment markers exist, each
with a distinct role:

- `*` — a standalone remark. Sits on the line(s) **immediately above**
  the code it describes.
- `//` — a **sub-comment**: a short, subordinate annotation trailing on
  the same line as the code (never on its own line above code, except
  the narrow sub-header exception described below).

```stata
* appending ado directory.
adopath ++ "../ado"
```

```stata
gen byte age_bin = 1 if inrange(age, 18, 24)  // census age bin.
```

**Default granularity: one action, one topic.** Treat almost every
discrete action — even a single `rename` or `gen` — as its own
`* topic.` comment block, fully set off by blank lines (see the
blank-line rule below). A script reads as a narrated sequence of small
steps, not a few paragraphs of code under sparse headers. Reserve a
single topic covering multiple statements for the case where those
statements are visibly building up **one** thing together — e.g. a
`gen` → `format` → `lab var` sequence for the same variable, or a
`count` → `logger` → `drop` sequence checking and reporting on the
same operation.

**Tone: short phrases, not descriptive sentences.** A comment names
the action, it doesn't narrate what the code obviously already shows:
`* label.`, `* rename.`, `* calculate error.`, `* sort & order.`
Save full sentences for the cases that actually need explaining —
background, a non-obvious choice, or a real aside. In those cases a
first-person hedge or a candid remark is fine; it signals genuine
uncertainty or a real observation about the data, which is more useful
to a future reader than a flattened, falsely-confident description:

```stata
* i beleive this is the actuals?
rename rlz_pcpi4 pcpi_actual
```

```stata
* combining the 4 forecast-quarter columns into a single 1-year-ahead
* median cpi expectation -- why they havent done this for us? the world
* will never know...
gen double spf_pcpi = ///
	100 * ((1 + cpi3 / 100) * (1 + cpi4 / 100) * (1 + cpi5 / 100) * ///
	(1 + cpi6 / 100)) ^ (1 / 4) - 100
```

Multi-line notes wrap with a leading `*` on each line and may use the
uppercase `NOTE:` tag for emphasis:

```stata
* NOTE: this raw file ships with a trailing blank column that stata
* misreads as a string variable full of missing values. drop it before
* any type coercion below.
```

**Decision-bullet pattern.** When a multi-line comment first gives
background and then has to state the concrete choice made because of
it, close with an indented `*    -- <choice>.` bullet rather than
folding the choice into the prose:

```stata
* the michigan survey preliminary release is roughly mid-month, and final is
* end of month. data pulled is the final released number.
*    -- will use the lagged month release.
gen int mich_date = dofm(mofd(greenbook_date) - 1)
```

This is worth the extra line whenever the "why" and the "what we did"
are separable — a reader skimming for the decision can jump straight
to the bullet without rereading the background.

This rule covers standalone (`*`) and sub- (`//`) comments only —
banner text (section 2) and header field labels (section 1) follow
their own casing. See `examples/comments.md`.

**Blank-line spacing between comments.** A new `* topic.` block — one
that introduces a distinct piece of logic — is always set off from
whatever precedes it by **2 blank lines**. Within that same topic, if
the code splits into related-but-separate statement groups (each
carrying its own trailing `//` sub-comment rather than a new `*`
header), separate those groups by only **1 blank line**. See
`examples/comments.md` for the full pattern.

**Exception: `//` as a standalone sub-header.** The one case where
`//` may stand alone above code (instead of trailing it) is labeling
parallel, repeated sub-blocks that all fall under one shared `* topic.`
header — e.g. the same merge-check pattern repeated once per data
source. Each sub-block gets a `// <label>.` line directly above its
first line of code, with no blank line in between; leave exactly **1
blank line** between sub-blocks, and 2 blank lines before the shared
`* topic.` header itself:

```stata
* merge.

// mcs data.
quiet merge m:1 mich_date using `mich_clean', keep(master match)

quiet count if _merge == 3
logger "Michigan matches: `r(N)'", l("INFO")
drop _merge

// sce data.
quiet merge m:1 sce_date using `sce_clean', keep(master match)
...
```

Outside of this parallel-sub-block case, `//` standing alone above
code is still wrong — use a `*` topic comment instead. See
`examples/comments.md`.

## 5. Script structure order

The preamble runs in a fixed order before any data is loaded:

1. `clear all` then `discard` at the very top.
2. `adopath ++ "../ado"` so custom `.ado` programs resolve.
3. Env-derived globals — **never hardcode a literal data path**:
   ```stata
   global RAWDIR : env PROJECT_RAW_PATH
   global BASEDIR : env PROJECT_BASE_PATH
   ```
4. Only then load data (`use "$..."`).

Scripts that read raw input need both a raw-data global and a
base-data global. Scripts that only read already-cleaned or merged
data only need the base-data global (often plus a derived global for
their specific output directory, e.g.
`global TABDIR = "$BASEDIR/output/tables"`).

## 6. Global variables

Every global's name is **entirely uppercase**, at both declaration and
every reference:

```stata
global CONSTANT = "test"
global RAWDIR : env PROJECT_RAW_PATH
global TABDIR = "$BASEDIR/output/tables"
```

Never declare or reference a lowercase or mixed-case global (`global
rawdir`, `$basedir`). See `examples/globals.md`.

## 7. Logging

Route progress/status/count messages through a centralized logging
routine instead of bare `display`. Set a log-file global once near the
top of a script, then have the logging routine write to it:

```stata
set logtype text, perm
global LOGFILE = "$BASEDIR/output/logs/script_name.txt"
logger "Log initialized.", l("INFO") replace
```

Levels are passed via `l("INFO"|"WARNING"|"ERROR")`. Use `replace`
only on the first call (initializing the log); subsequent calls append
by default. Typical count-logging pattern:

```stata
quiet count if DROP_miss_age
logger "Missing age: -`r(N)'", l("INFO")
```

When you need raw command output (e.g. `tab`, `sum`) in the log, wrap
it in a `quiet { log using "$LOGFILE", append ... noisily ... log
close }` block rather than routing it through the logging routine.

## 8. `quiet` prefix

Prefix routine data operations (`use`, `count`, and similar) with
`quiet` to keep the console and log clean; surface the meaningful
result through the logging routine afterward. `quiet` is the only
accepted form — **never** spell out `quietly`, even in new code
touching files that still use the long form. Larger noisy blocks use
`quiet { ... }` with `noisily` on the specific lines whose output you
actually want.

```stata
quiet use "$RAWDIR/data/raw_survey.dta", clear
quiet count
logger "Initial count: `r(N)'", l("INFO")
```

## 9. Typed `gen`/`egen`

Every generated variable declares an explicit storage type — never a
bare `gen`/`egen`:

```stata
gen byte condition = (var == "cond")
egen double total_pay = sum(pay)
```

Pick the narrowest type that fits the data (`byte` for 0/1 indicators
and small encoded categoricals, `int`/`long` for counts and IDs,
`float`/`double` for continuous or summed values). See
`examples/variable-typing.md`.

## 10. Categorical variable encoding

For a mutually exclusive encoded categorical, build it with a single
multiplicative-sum `gen`, not an if/replace chain:

```stata
gen byte category = ( ///
	1 * (cat_var == "category 1") + ///
	2 * (cat_var == "category 2") + ///
	3 * (cat_var == "category 3") ///
)
```

Each `(cat_var == ...)` term evaluates to 0/1, so exactly one term
contributes when the categories are truly mutually exclusive. Rows
matching none of the listed categories resolve to `0` — treat that
deliberately, either as an intentional catch-all category or by
following up with an explicit missing-value fix. See
`examples/categorical-encoding.md`.

## 11. Variable labels

Every variable — generated or renamed — gets a label, assigned with
the abbreviation `lab var` (never the fully spelled `label var`):

```stata
lab var age_bin "Age group"
```

See `examples/variable-labels.md`.

## 12. `compress` before every export

Any command that writes data to disk (`save`, `export delimited`,
`export excel`, `outsheet`, etc.) is immediately preceded by a bare
`compress` call:

```stata
compress
save "$BASEDIR/data/output/main.dta", replace
```

See `examples/compress-export.md`.

## 13. `.ado` program header style

`.ado` files use a **different, fuller header** than `.do` files — a
docstring block with **lowercase field labels** (contrast the `.do`
header's Title-Case), placed before the program definition:

```stata
/*
--------------------------------------------------------------------------------

created:
	<date>

author:
	<author>

program:
	<program name>

version:
	v1.0.0

	Note: see below for version history

description:
	<what the program does>

syntax:
	<syntax diagram>

arguments:
	<each positional arg documented>

options:
	<each option documented, one block per option>

returns:
	<each r() / e() return documented>

notes:
	- <caveats>

version history:
	v1.0.0 (<date>): Initial release.

--------------------------------------------------------------------------------
*/

cap program drop program_name
program define program_name, rclass
	version 14.0
	...
end
```

Not every field is required in every program, but keep the
lowercase-label style, the leading `cap program drop <name>`, and an
explicit `version 14.0` line inside the program.

## 14. Indentation

Indent continuation lines and code bodies with tabs, not spaces —
consistent with the header and banner alignment shown above.

## 15. Date-variable display format

Any date variable built for matching, inspection, or output gets an
explicit human-readable display format rather than a bare `%td`:

```stata
gen int mich_date = dofm(mofd(greenbook_date) - 1)
format mich_date %tdnn/dd/CCYY
```

`%tdnn/dd/CCYY` renders as `MM/DD/YYYY`, which is far easier to
eyeball in `list`/`browse` output or a log than Stata's default
`%td` (days-since-epoch-derived) display — worth the one extra line
on every date variable you generate.
