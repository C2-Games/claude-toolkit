# Typed `gen`/`egen`

Every generated variable declares an explicit storage type. Pick the narrowest
type that safely fits the data.

## Indicators and small encoded categoricals → `byte`

```stata
gen byte is_renter = (tenure == "renter")
gen byte edu_bin = 1 if edu == "hs"
```

## Counts, IDs → `int` or `long`

```stata
egen int n_county = count(id), by(county_fips)
gen long respondent_id = _n
```

## Continuous or summed values → `float`/`double`

```stata
egen double total_pay = sum(pay)
gen float wage_ratio = wage / county_mean_wage
```

## Avoid

```stata
gen is_renter = (tenure == "renter")
egen total_pay = sum(pay)
```

Both omit the type — always name one explicitly, even when Stata's default
inference would happen to pick the same type.
