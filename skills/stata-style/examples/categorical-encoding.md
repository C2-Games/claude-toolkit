# Categorical variable encoding

Build a mutually exclusive encoded categorical with a single multiplicative-sum
`gen`, not an if/replace chain. The closing parenthesis goes on its own line.

## Correct

```stata
gen byte edu_bin = ( ///
	1 * (edu == "less than hs") + ///
	2 * (edu == "hs") + ///
	3 * (edu == "some college") + ///
	4 * (edu == "bachelors") + ///
	5 * (edu == "masters+") ///
)
```

Each `(edu == ...)` term evaluates to 0/1. Because the categories are mutually
exclusive, exactly one term contributes to the sum for any given row.

## Handling the unmatched case

Rows matching none of the listed categories resolve to `0`. Decide
deliberately whether that's a real category or a missing value:

```stata
* rows with an unrecognized edu string become an explicit missing category.
gen byte edu_bin = ( ///
	1 * (edu == "less than hs") + ///
	2 * (edu == "hs") + ///
	3 * (edu == "some college") + ///
	4 * (edu == "bachelors") + ///
	5 * (edu == "masters+") ///
)
replace edu_bin = . if edu_bin == 0
```

## Avoid

```stata
gen edu_bin = 1 if edu == "less than hs"
replace edu_bin = 2 if edu == "hs"
replace edu_bin = 3 if edu == "some college"
replace edu_bin = 4 if edu == "bachelors"
replace edu_bin = 5 if edu == "masters+"
```

Untyped, and an if/replace chain instead of the multiplicative-sum pattern.
