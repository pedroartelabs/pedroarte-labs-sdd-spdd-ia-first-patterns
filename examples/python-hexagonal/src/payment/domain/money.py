"""The Money value object.

Money is the canonical example of why primitives are not enough. A bare
``float`` for an amount loses cents to binary rounding; a bare ``Decimal``
still lets you add BRL to USD; a bare ``str`` currency lets you write "brl",
"BRL " and "Brl" and mean three different things.

The type carries the invariants so no caller has to remember them.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from payment.domain.errors import InvalidMoneyError

_MINOR_UNIT_EXPONENT = Decimal("0.01")
# Decimal exponents count digits after the point as negatives, so the minor unit
# (two decimal places) is -2. Anything smaller carries more precision than a
# currency has.
_MINOR_UNIT_DIGITS = -2
_SUPPORTED_CURRENCIES = frozenset({"BRL", "USD", "EUR"})


@dataclass(frozen=True, slots=True)
class Money:
    """An exact monetary amount in a specific currency.

    Immutable and compared by value, so two independently constructed instances
    of 10.00 BRL are the same money.
    """

    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            raise InvalidMoneyError(
                f"amount must be a Decimal, got {type(self.amount).__name__}; "
                "float cannot represent currency exactly"
            )
        if not self.amount.is_finite():
            # Catches NaN and Infinity in one check. Infinity is the one that
            # matters: it is greater than zero, so the positivity check below
            # would happily accept it, and the precision check would then blow
            # up with a TypeError instead of a domain error.
            raise InvalidMoneyError("amount must be a real, finite number")
        if self.amount <= 0:
            raise InvalidMoneyError(f"amount must be positive, got {self.amount}")
        # `exponent` is typed as `int | Literal['n', 'N', 'F']` because a
        # non-finite Decimal reports a marker instead of a number. is_finite()
        # above rules that out; the isinstance keeps the type checker informed.
        exponent = self.amount.as_tuple().exponent
        if isinstance(exponent, int) and exponent < _MINOR_UNIT_DIGITS:
            raise InvalidMoneyError(
                f"amount {self.amount} has more precision than the minor unit allows"
            )
        if self.currency not in _SUPPORTED_CURRENCIES:
            raise InvalidMoneyError(
                f"unsupported currency {self.currency!r}; "
                f"supported: {', '.join(sorted(_SUPPORTED_CURRENCIES))}"
            )

    @classmethod
    def of(cls, amount: str | int | Decimal, currency: str) -> Money:
        """Build Money from a string, int or Decimal.

        ``str`` is the safe way to write a literal amount: ``Money.of("10.50",
        "BRL")`` is exact, whereas ``Decimal(10.50)`` would already have lost
        precision before this method saw it. ``float`` is rejected on purpose.
        """
        # Widened to `object` so the isinstance check is a real runtime guard
        # rather than a branch the type checker proves unreachable. `float` is
        # deliberately absent from the signature — a typed caller is stopped by
        # mypy, and an untyped one is stopped here.
        raw: object = amount
        if isinstance(raw, float):
            raise InvalidMoneyError("refusing to build Money from float; pass a str or Decimal")
        try:
            value = Decimal(amount) if not isinstance(amount, Decimal) else amount
        except (InvalidOperation, ValueError) as exc:
            raise InvalidMoneyError(f"{amount!r} is not a valid amount") from exc
        return cls(amount=value.quantize(_MINOR_UNIT_EXPONENT), currency=currency)

    def add(self, other: Money) -> Money:
        """Add money of the same currency.

        Cross-currency arithmetic is a business decision requiring a rate and a
        rounding policy; silently allowing it here would hide that decision.
        """
        self._require_same_currency(other)
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def _require_same_currency(self, other: Money) -> None:
        if self.currency != other.currency:
            raise InvalidMoneyError(
                f"cannot combine {self.currency} with {other.currency}; "
                "conversion requires an explicit rate"
            )

    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"
