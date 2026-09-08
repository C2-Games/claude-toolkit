# Comments

Comments are lowercase and end with a period. `*` is a standalone remark
sitting on the line(s) immediately above the code it describes. `//` is a
sub-comment — a short, subordinate note trailing on the same line as code,
never on its own line above code, except the narrow sub-header exception
shown near the end of this file.

## Standalone remark (`*`)

```stata
* dropping observations with implausible survey durations.
drop if duration_min < 6 | duration_min > 45
```

## Sub-comment (`//`)

```stata
replace county_fips = "51515" if county_fips == "51560"  // 2020 redistricting.
```

## Multi-line note with `NOTE:` emphasis

The `NOTE:` tag is the one uppercase exception; the rest of the note stays
lowercase.

```stata
* NOTE: the vendor's raw file ships with a trailing blank column that stata
* misreads as a string variable full of missing values. drop it before any
* type coercion below.
```

## Avoid

```stata
// Dropping bad durations
drop if duration_min < 6 | duration_min > 45
```

Wrong on three counts: `//` used as a standalone comment above code instead of
a trailing sub-comment, capitalized, and no ending period.

## Default granularity: one action, one topic

Comments read as a narrated sequence of small steps rather than a few
descriptive paragraphs. Give almost every discrete action — even a single
`rename` — its own `* topic.` block, fully set off by the 2-blank-line
spacing rule below:

```stata
* keeping only the 1y CPI proj. horizon.
quiet keep if horizon == 4
quiet keep greenbook_date pcpi rlz_pcpi4


* the raw file has multiple rows per date. drop dups.
quiet duplicates drop
quiet drop if missing(pcpi)


* i beleive this is the actuals?
rename rlz_pcpi4 pcpi_actual


* calculate error.
gen double pcpi_error = abs(pcpi - pcpi_actual)


* label.
lab var greenbook_date "Tealbook (Greenbook) publication date"
lab var pcpi "Tealbook 1-year-ahead CPI projection"
lab var pcpi_actual "Realized 1-year-ahead CPI inflation"
lab var pcpi_error "Tealbook 1-year-ahead CPI error"
```

Compare this to a version that lumps the dedup, rename, and error
calculation under one header — it reads faster at a glance but hides the
fact that `rename` was a judgment call worth flagging on its own line. The
finer granularity gives every decision room to carry its own aside.

Note the tone, too: `* label.`, `* calculate error.` name the action rather
than restating what the code already shows. `* i beleive this is the
actuals?` is a genuine, useful hedge — it tells the next reader (including
future-you) exactly which line to double check, which a flattened
description like `* rename realized inflation variable.` would bury.

## `* topic.` covering multiple statements building one thing

The exception to one-action-one-topic is a short run of statements that are
visibly assembling a single result together — group these under one topic
with **1 blank line** between sub-groups, not 2:

```stata
* the michigan survey preliminary release is roughly mid-month, and final is
* end of month. data pulled is the final released number.
*    -- will use the lagged month release.
gen int mich_date = dofm(mofd(greenbook_date) - 1)

format mich_date %tdnn/dd/CCYY

lab var mich_date "Matching Michigan survey month"
```

The `gen` → `format` → `lab var` sequence is all building the same
`mich_date` variable, so it stays one topic. The comment itself uses the
decision-bullet pattern: two lines of background, then an indented
`*    -- <choice>.` line stating what was actually done. Skip the bullet
when there's no separable "why" to explain — a bare `* label.` is enough
when the action needs no justification.

## Exception: `//` as a standalone sub-header

The one time `//` is allowed on its own line above code is labeling
parallel, repeated sub-blocks under one shared `* topic.` header — e.g. the
same check repeated once per data source. No blank line between the `//`
label and the code it introduces; **1 blank line** between sub-blocks:

```stata
* merge.

// mcs data.
quiet merge m:1 mich_date using `mich_clean', keep(master match)

quiet count if _merge == 3
logger "Michigan matches: `r(N)'", l("INFO")
drop _merge

// sce data.
quiet merge m:1 sce_date using `sce_clean', keep(master match)

quiet count if _merge == 3
logger "SCE matches: `r(N)'", l("INFO")
drop _merge
```

This does not relax the general rule — outside of labeling parallel
sub-blocks this way, a standalone `//` above code (the "Avoid" example
above) is still wrong.

## Spacing between comment blocks

A new `* topic.` block gets **2 blank lines** above it. Statement groups
inside the same topic — each carrying its own trailing `//` sub-comment
instead of a new `*` header — get only **1 blank line** between groups:

```stata
* import cleaned survey data.
use "$OUTPUT_DATA/survey.dta", clear


* create bin fracs based on 2024 acs census data.
gen frac_male = 0.5052 if male == 0  // est: 171,816,647
quiet replace frac_male = 0.4948 if male == 1  // est: 168,294,343

gen frac_inc = 0.1115 if inc_bin == 1  // est: 14,798,144
quiet replace frac_inc = 0.4769 if inc_bin == 2  // est: 63,305,611
quiet replace frac_inc = 0.2742 if inc_bin == 3  // est: 36,402,240
quiet replace frac_inc = 0.1374 if inc_bin == 4  // est: 18,231,151

gen frac_age = 0.1170 if age_bin == 1  // est: 31,270,959
quiet replace frac_age = 0.1729 if age_bin == 2  // est: 46,198,405
```

The `use` statement starts a fresh `* topic.` block, so 2 blank lines
separate it from what came before and from the next block below. The
`frac_male`, `frac_inc`, and `frac_age` groups all fall under the single
`* create bin fracs...` header, so only 1 blank line separates each group.
