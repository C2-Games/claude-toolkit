# Style examples

Concrete before/after snippets for each rule in SKILL.md. Read this when
you want a worked example rather than a description of the rule.

## Docstrings: public vs. private

Public method — full numpy-style docstring:

```python
def compute_discount(
    self,
    price: float,
    rate: float,
) -> float:
    """Compute the discounted price for an item.

    Parameters
    ----------
    price : float
        The original price before discount.
    rate : float
        The discount rate, expressed as a fraction (e.g. 0.2 for 20%).

    Returns
    -------
    float
        The price after the discount is applied.

    Notes
    -----
    Callers are expected to pass a rate between 0 and 1.
    """

    return price * (1 - rate)
```

Private method — description only, no params/returns section:

```python
def _normalize_rate(self, rate: float) -> float:
    """Clamp a discount rate to the valid 0-1 range."""

    return max(0.0, min(rate, 1.0))
```

Note what's absent from the public docstring above: no "Raises" section,
even though this function could theoretically be given a negative price.
Error types belong in type signatures and tests, not docstrings, per the
project's convention. Also note that there is a whitespace after each docstring.

## Data-holder classes: no class docstring

`@dataclass`, Pydantic `BaseModel`, `Enum`, `NamedTuple`, `TypedDict` —
the field list is the contract, so no docstring:

```python
# yes.
@dataclass(frozen=True)
class Criterion:
    attr_key: str
    operator: Operator
    operand: object


class Operator(Enum):
    EQ = "eq"
    CONTAINS = "contains"


class TaskItem(BaseModel):
    id: int
    text: str
    status: Status = Status.TODO


# no — docstring restates the class name in prose.
@dataclass(frozen=True)
class Criterion:
    """A single attribute test: an operator applied to attr_key."""

    attr_key: str
    operator: Operator
    operand: object
```

A cross-field invariant does *not* earn a class docstring back — put it
on the field it constrains, or in the module docstring:

```python
# yes — the invariant lives on the fields it actually constrains.
@dataclass
class CommandResult:
    messages: list[str] = field(default_factory=list)
    exit_code: int = 0
    # at most one of item_view / tree_view is ever set: a command
    # echoes back either a flat list or a nested tree, never both.
    item_view: TaskList | None = None
    tree_view: TaskList | None = None


# no — "invariant" is not a licence for a class docstring.
@dataclass
class CommandResult:
    """Outcome of a mutating command. At most one of item_view /
    tree_view is set.
    """

    messages: list[str] = field(default_factory=list)
    ...
```

A `model_validator` / `field_validator` / `property` on a Pydantic model
does not make it a behavior class — still a data holder, still no
docstring. A class with real methods (a service, a parser assembler, an
exception type) keeps normal docstring rules, held to a summary line.

## Module docstrings: one line

```python
# yes.
"""Per-command orchestration between the CLI and storage/models."""

# no — multi-paragraph header duplicating ARCHITECTURE.md / CLAUDE.md.
"""Per-command orchestration between the CLI and storage/models.

Each function loads through taskli.storage, mutates via model methods,
saves, and returns plain data or a CommandResult. Nothing here imports
taskli.render or prints — the CLI layer turns these results into
console output.
"""
```

## Comments that restate architecture docs

```python
# yes — a pointer, if the reader needs one at all.
MODIFIER_FLAGS: dict[str, ModifierSpec] = {  # see ARCHITECTURE.md rule 2.
    ...
}

# no — a paragraph re-explaining a rule that already lives in the doc.
# attribute-backed modifier flags, keyed by the same field names the
# registry uses. argparse vocabulary (flag strings, metavar, choices)
# can't live in models/registry.py -- architecture rule 2 keeps it out
# of models/ -- so this half of the split table lives here.
MODIFIER_FLAGS: dict[str, ModifierSpec] = {
    ...
}
```

## Static typing and overloads

```python
from typing import overload


@overload
def parse_id(value: str) -> int: ...

@overload
def parse_id(value: int) -> int: ...

def parse_id(value: str | int) -> int:
    """Parse a user or resource id from a string or int."""
    
    return int(value)
```

Use `X | None`, not `Optional[X]`:

```python
# yes.
def find_user(user_id: int) -> User | None: ...

# no.
def find_user(user_id: int) -> Optional[User]: ...
```

## Hanging indents past 80 characters

```python
# yes.
def create_invoice(
    customer_id: int,
    line_items: list[LineItem],
    due_date: date,
    notes: str | None = None,
) -> Invoice:
    """Create an invoice for a customer."""
    ...


# no — packed onto one line past 80 chars, or a mixed indent style.
def create_invoice(customer_id: int, line_items: list[LineItem], due_date: date, notes: str | None = None) -> Invoice:
    ...
```

The same applies to function calls, not just definitions:

```python
# yes.
result = create_invoice(
    customer_id=42,
    line_items=items,
    due_date=today,
)

# no.
result = create_invoice(customer_id=42,
                         line_items=items,
                         due_date=today)
```

## Constants

Inline a one-off value; promote to a constant once it's used 3+ times in
a file (this applies doubly to module-private constants — a `_TIMEOUT`
that's used once just adds a layer of indirection with no payoff):

```python
# yes — used once, inline is clearer.
response = requests.get(url, timeout=30)

# yes — same value used 3+ times in this file, worth naming.
_MAX_RETRIES = 3

def fetch_with_retry(url: str) -> Response:
    """Fetch a url, retrying on failure."""

    for attempt in range(_MAX_RETRIES):
        ...
```

## Naming

```python
# yes.
def calculate_total_price(unit_price: float, quantity: int) -> float: ...

class InvoiceGenerator: ...

type UserId = int  # a type alias is a type, so PascalCase.

# no.
def CalculateTotalPrice(unit_price: float, quantity: int) -> float: ...

class invoice_generator: ...
```

## Comments

Lowercase, end with a period, and only where they add information the
code doesn't already convey:

```python
# yes — explains *why*, which the code alone can't.
# stripe requires amounts in cents, not dollars.
amount_cents = int(amount_dollars * 100)

total = price * quantity  # self-explanatory, no comment needed.

# no — restates what the code already says, wrong case, no period.
# Multiply price by quantity to get the total
Total = price * quantity
```

## f-strings, logging, and imports

```python
# yes — f-strings for ordinary string building.
message = f"user {user.id} placed order {order.id}."

# yes — %-style for logging calls specifically, so the interpolation
# is lazy and skipped entirely when the log level filters it out.
log.info("user %s placed order %s.", user.id, order.id)

# no — f-string in a logging call defeats lazy evaluation.
log.info(f"user {user.id} placed order {order.id}.")
```

Import grouping (stdlib, then third-party, then local, blank line
between each group):

```python
import json
from pathlib import Path

import requests
from pydantic import BaseModel

from myapp.models import User
from myapp.utils import format_currency
```

## Whitespace before `return`

```python
# yes.
def total_price(items: list[Item]) -> float:
    """Compute the total price across all items."""

    subtotal = sum(item.price * item.quantity for item in items)
    tax = subtotal * TAX_RATE

    return subtotal + tax


# no — return is packed against the preceding logic.
def total_price(items: list[Item]) -> float:
    """Compute the total price across all items."""

    subtotal = sum(item.price * item.quantity for item in items)
    tax = subtotal * TAX_RATE
    return subtotal + tax
```

When `return` is the only statement in the body, the blank line
already required after the docstring is enough — no second blank line:

```python
# yes.
def _normalize_rate(self, rate: float) -> float:
    """Clamp a discount rate to the valid 0-1 range."""

    return max(0.0, min(rate, 1.0))
```

## Exceptions

```python
# yes.
try:
    account = load_account(account_id)
except AccountNotFoundError:
    account = None

# no — swallows everything, including bugs and KeyboardInterrupt.
try:
    account = load_account(account_id)
except:
    account = None
```
