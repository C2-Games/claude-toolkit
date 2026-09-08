# Line length

All lines — code, comments, banners — stay within 80 characters. Wrap with
`///`, indenting the continuation to align under (or just past) the opening
construct.

## Long conditional

```stata
gen byte low_income_renter = ( ///
	inc_bin == 1 & tenure == "renter" & !missing(rent_burden) ///
)
```

## Long function call

```stata
egen double county_mean_wage = mean(wage), by(county_fips year_month)
```

If a single-line `egen ... by()` call would exceed 80 characters, wrap before
`by()`:

```stata
egen double county_mean_wage = ///
	mean(wage), by(county_fips year_month)
```

## Long `lab def`

Wrapped value defs align under the first one, not under the command name:

```stata
lab def edu_bin 1 "Less than High School" 2 "High School" ///
                3 "Some College" 4 "Bachelors" 5 "Masters +"
```

## Avoid

```stata
gen byte low_income_renter = (inc_bin == 1 & tenure == "renter" & !missing(rent_burden))
```
