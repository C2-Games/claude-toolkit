# Global variables

Global names are entirely uppercase, at both declaration and every reference.

## Correct

```stata
global CONSTANT = "test"
global RAWDIR : env PROJECT_RAW_PATH
global TABDIR = "$BASEDIR/output/tables"

use "$RAWDIR/data/raw_survey.dta", clear
```

## Avoid

```stata
global rawdir : env PROJECT_RAW_PATH
global tabDir = "$basedir/output/tables"

use "$rawdir/data/raw_survey.dta", clear
```

Both the declaration and every later reference (`$RAWDIR`, not `$rawdir`) must
stay uppercase — a global that's declared uppercase but referenced in lowercase
is still wrong.
