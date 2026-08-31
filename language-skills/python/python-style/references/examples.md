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
