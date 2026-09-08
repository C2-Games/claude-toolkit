# `compress` before every export

Any command that writes data to disk is immediately preceded by a bare
`compress` call — no options, no arguments.

## `save`

```stata
compress
save "$BASEDIR/data/output/main.dta", replace
```

## `export delimited`

```stata
compress
export delimited "$BASEDIR/output/tables/summary.csv", replace
```

## `export excel`

```stata
compress
export excel "$BASEDIR/output/tables/summary.xlsx", firstrow(variables) replace
```

## Avoid

```stata
save "$BASEDIR/data/output/main.dta", replace
```

Missing the `compress` call immediately before the export — this applies even
when the dataset was just loaded and "should already be compressed."
