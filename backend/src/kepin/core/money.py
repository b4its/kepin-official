from __future__ import annotations
from decimal import Decimal, ROUND_HALF_UP


ZERO = Decimal("0.00")
TWO_PLACES = Decimal("0.01")
FOUR_PLACES = Decimal("0.0001")


def to_money(value: str | int | float | Decimal) -> Decimal:
    """Convert any numeric input to Decimal(20,2)."""
    return Decimal(str(value)).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def to_quantity(value: str | int | float | Decimal) -> Decimal:
    """Convert to Decimal(20,4) for quantities."""
    return Decimal(str(value)).quantize(FOUR_PLACES, rounding=ROUND_HALF_UP)


def money_str(value: Decimal) -> str:
    return str(value.quantize(TWO_PLACES))
