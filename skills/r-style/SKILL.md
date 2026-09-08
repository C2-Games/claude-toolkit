---
name: r-style
description: Enforces a consistent R code style — mandatory ##-banner file headers, roxygen-style function docs, section/subsection banners, T/F boolean literals, the native |> pipe, a centralized dependency-loading pattern, centralized path constants, snake_case naming, double-quoted strings, 2-space indentation, and lowercase-period inline comments. Use this skill whenever writing, editing, reviewing, or refactoring any R code (.R files) — top-level scripts, shared utility modules, or any new .R file — even for small snippets or single-function edits. Apply these rules by default; do not wait for the user to mention style.
---

# R style guide

Apply every rule below to all R code you write or edit for this user.
Consistency across old and new code in the same file matters more than
any external style guide — when editing, if you spot code that
violates a rule below (e.g. a stray `TRUE` or `%>%`), fix it to match.

## 1. Mandatory file header

Every `.R` file opens with a `##`-banner block. The dividers are a `##`
followed by dashes out to ~80 columns. Fields appear in this fixed
order, each label on its own line, its value indented on the following
`##` line(s). `Purpose` may wrap across multiple `##` lines;
`Dependencies` lists one package per `##` line (leave the line blank
when the file has none).

Template:

```r
##------------------------------------------------------------------------------
##
## Created:
##    <date>
##
## Author:
##    <author>
##
## File:
##    <relative/path/to/file.R>
##
## Purpose:
##    <one-line (or multi-line) description of what the file does>
##
## Dependencies:
##    <package>
##    <package>
##
##------------------------------------------------------------------------------
```

The `File:` value is the repo-relative path. Preserve this header when
editing an existing file; add it when creating a new one.

## 2. Function documentation

Every function is preceded by a roxygen-style `#'` block with **no blank
line** between the doc block and the `function` definition. Use `@title`,
`@description`, one `@param` per argument, and `@returns` only when the
function returns a value. Document type/meaning inline, note defaults for
non-obvious params, and wrap long descriptions across multiple `#'`
lines.

Example:

```r
#' @title Filter rows in range
#' @description Keeps rows whose value falls within a numeric bound.
#' @param df The dataframe to filter.
#' @param low The lower bound. If None, defaults to 0.
#' @param high The upper bound.
#' @param inclusive Whether the bounds are inclusive. Defaults to TRUE.
#' @returns A filtered dataframe.
filter_rows_in_range <- function(df, low, high, inclusive = T) {
```

## 3. Section banners

Top-level sections in top-level scripts use a heavy `=` banner: a
`##===...===##`-style divider, a blank `##`, the header indented under
`##`, a blank `##`, then the closing divider:

```r
##==============================================================================
##                              SECTION NAME
##==============================================================================
```

Subsections use a lighter `#`-and-`-` form:

```r
#-------------------------------------------------------------------------------
#                   SUBSECTION NAME
#-------------------------------------------------------------------------------
```

## 4. Booleans

Use the base-R `T` / `F` literals, never spelled-out `TRUE` / `FALSE`.
For example, `na.rm = T`, `stringsAsFactors = F`. Introducing
`TRUE`/`FALSE` is an inconsistency — fix it to `T`/`F`.

## 5. Piping

Use the native pipe `|>`, never the magrittr `%>%`:

```r
df |> drop_na(col)
bind_rows(result_list) |> mutate(total = a + b)
```

## 6. Dependency loading

Two distinct patterns — do not mix them:

- **Top-level scripts** declare their own `deps <- c(...)` character
  vector immediately after any `source(...)` calls, call an
  install-if-missing helper on it, then remove the variable:

  ```r
  source("constants.R")
  source("utils.R")

  deps <- c("tidyverse", "scales")
  install_deps(deps = deps)

  rm(deps)
  ```

- **Helper functions** that need a package call a require-style helper
  at the top of the function body instead — it errors if the package
  is missing rather than forcing a top-level install:

  ```r
  save_plot <- function(plot, path) {
    require_deps(c("ggplot2"))
    ...
  }
  ```

Never write a bare `install.packages()` outside the shared
install-if-missing helper.

## 7. Path resolution

Route all paths through constants defined once in a single constants
file, each built from an environment variable via `file.path(...)`:

```r
BASE_PATH <- Sys.getenv("PROJECT_PATH")
DATA_PATH <- file.path(BASE_PATH, "data")
OUTPUT_PATH <- file.path(BASE_PATH, "output")
```

Reference these constants elsewhere (e.g.
`read_dta(file.path(DATA_PATH, "main.dta"))`). Never hardcode a
literal path, and never call `Sys.getenv` outside the constants file.

## 8. Inline comments

Lowercase, ending with a period, placed on their own line directly above
the code they describe:

```r
# install & load dependencies.
deps <- c("tidyverse", "scales")
install_deps(deps = deps)
```

## 9. Naming

`snake_case` for variables and functions (`filter_rows_in_range`,
`install_deps`), matching how packages, arguments, and local variables
are named throughout.

## 10. String quotes

Use double quotes for string literals (`"renter"`, not `'renter'`).

## 11. Indentation

Indent code bodies with 2 spaces, not tabs.

## Full example

All of the above combined in one file:

```r
##------------------------------------------------------------------------------
##
## Created:
##    2026-01-15
##
## Author:
##    jdoe
##
## File:
##    analysis/filter_ranges.R
##
## Purpose:
##    Filter a dataframe to rows whose value falls within a numeric
##    bound, then write the result to disk.
##
## Dependencies:
##    tidyverse
##
##------------------------------------------------------------------------------

source("constants.R")

deps <- c("tidyverse")
install_deps(deps = deps)

rm(deps)

##==============================================================================
##                                  FILTERING
##==============================================================================

#' @title Filter rows in range
#' @description Keeps rows whose value falls within a numeric bound.
#' @param df The dataframe to filter.
#' @param low The lower bound.
#' @param high The upper bound.
#' @param inclusive Whether the bounds are inclusive. Defaults to TRUE.
#' @returns A filtered dataframe.
filter_rows_in_range <- function(df, low, high, inclusive = T) {
  if (inclusive) {
    df |> filter(value >= low, value <= high)
  } else {
    df |> filter(value > low, value < high)
  }
}

#-------------------------------------------------------------------------------
#                   WRITE RESULTS
#-------------------------------------------------------------------------------

# write the filtered rows to the output path.
result <- filter_rows_in_range(raw_data, low = 0, high = 100)
write_csv(result, file.path(OUTPUT_PATH, "filtered.csv"))
```
