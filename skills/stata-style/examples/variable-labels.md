# Variable labels

Every variable — generated or renamed — gets a label, assigned with the
abbreviation `lab var`.

## Correct

```stata
gen byte is_renter = (tenure == "renter")
lab var is_renter "Renter household"

rename Q12 age_years
lab var age_years "Respondent age (years)"
```

## Categorical with value labels

Value labels (`lab def` / `lab val`) are a separate mechanism from the
variable label and both are still required — all `label` subcommands are
abbreviated:

```stata
gen byte edu_bin = ( ///
	1 * (edu == "less than hs") + ///
	2 * (edu == "hs") ///
)
lab var edu_bin "Education level (binned)"
lab def edu_bin 1 "Less than HS" 2 "HS"
lab val edu_bin edu_bin
```

## Avoid

```stata
gen byte is_renter = (tenure == "renter")
label var is_renter "Renter household"
```

Uses the fully spelled `label var` instead of the required `lab var`
abbreviation.
