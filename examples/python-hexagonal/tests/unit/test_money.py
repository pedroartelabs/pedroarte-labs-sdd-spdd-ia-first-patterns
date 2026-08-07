"""Money invariants.

Value-object tests are the cheapest tests in the suite and protect the rules
most likely to be violated by a well-meaning caller.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from payment.domain.errors import InvalidMoneyError
from payment.domain.money import Money


class TestConstruction:
    def test_builds_from_a_decimal_string(self) -> None:
        money = Money.of("10.50", "BRL")

        assert money.amount == Decimal("10.50")
        assert money.currency == "BRL"

    def test_builds_from_an_integer(self) -> None:
        assert Money.of(7, "USD").amount == Decimal("7.00")

    def test_rejects_float_outright(self) -> None:
        # The whole reason Money exists. 10.50 as a float is already
        # 10.5000000000000004..., so accepting it would silently lose money
        # before any validation could notice.
        with pytest.raises(InvalidMoneyError, match="refusing to build Money from float"):
            Money.of(10.50, "BRL")  # type: ignore[arg-type]

    def test_rejects_a_non_numeric_amount(self) -> None:
        with pytest.raises(InvalidMoneyError, match="not a valid amount"):
            Money.of("ten reais", "BRL")

    @pytest.mark.parametrize("amount", ["0", "0.00", "-1", "-0.01"])
    def test_rejects_non_positive_amounts(self, amount: str) -> None:
        with pytest.raises(InvalidMoneyError, match="must be positive"):
            Money.of(amount, "BRL")

    def test_rejects_an_unsupported_currency(self) -> None:
        with pytest.raises(InvalidMoneyError, match="unsupported currency"):
            Money.of("10.00", "XYZ")

    def test_rejects_a_lowercase_currency(self) -> None:
        # Normalising here would be a kindness that hides a bug: the caller
        # believes they sent a currency code and they did not.
        with pytest.raises(InvalidMoneyError, match="unsupported currency"):
            Money.of("10.00", "brl")

    def test_rejects_precision_finer_than_the_minor_unit(self) -> None:
        with pytest.raises(InvalidMoneyError, match="more precision"):
            Money(amount=Decimal("10.005"), currency="BRL")

    def test_rejects_a_non_decimal_amount_on_direct_construction(self) -> None:
        with pytest.raises(InvalidMoneyError, match="must be a Decimal"):
            Money(amount="10.00", currency="BRL")  # type: ignore[arg-type]

    def test_rejects_nan(self) -> None:
        with pytest.raises(InvalidMoneyError, match="finite"):
            Money(amount=Decimal("NaN"), currency="BRL")

    def test_rejects_infinity(self) -> None:
        # Infinity is the sneaky one: it passes `> 0`, so without an explicit
        # finiteness check it would reach the precision comparison and raise a
        # TypeError rather than a domain error.
        with pytest.raises(InvalidMoneyError, match="finite"):
            Money(amount=Decimal("Infinity"), currency="BRL")


class TestValueSemantics:
    def test_equal_when_amount_and_currency_match(self) -> None:
        assert Money.of("10.50", "BRL") == Money.of("10.50", "BRL")

    def test_differs_by_currency(self) -> None:
        assert Money.of("10.50", "BRL") != Money.of("10.50", "USD")

    def test_is_hashable_so_it_can_be_a_dict_key(self) -> None:
        assert len({Money.of("1.00", "BRL"), Money.of("1.00", "BRL")}) == 1

    def test_is_immutable(self) -> None:
        money = Money.of("10.00", "BRL")

        with pytest.raises(AttributeError):
            money.amount = Decimal("999.00")  # type: ignore[misc]


class TestArithmetic:
    def test_adds_same_currency(self) -> None:
        total = Money.of("10.50", "BRL").add(Money.of("0.50", "BRL"))

        assert total == Money.of("11.00", "BRL")

    def test_refuses_to_add_across_currencies(self) -> None:
        # Silently allowing this would invent an exchange rate of 1.0.
        with pytest.raises(InvalidMoneyError, match="conversion requires an explicit rate"):
            Money.of("10.00", "BRL").add(Money.of("10.00", "USD"))

    def test_addition_does_not_mutate_either_operand(self) -> None:
        left, right = Money.of("10.00", "BRL"), Money.of("5.00", "BRL")

        left.add(right)

        assert left == Money.of("10.00", "BRL")
        assert right == Money.of("5.00", "BRL")


class TestProperties:
    @given(
        cents=st.integers(min_value=1, max_value=10**12),
        other_cents=st.integers(min_value=1, max_value=10**12),
    )
    def test_addition_is_commutative(self, cents: int, other_cents: int) -> None:
        left = Money(amount=Decimal(cents) / 100, currency="BRL")
        right = Money(amount=Decimal(other_cents) / 100, currency="BRL")

        assert left.add(right) == right.add(left)

    @given(cents=st.integers(min_value=1, max_value=10**12))
    def test_any_positive_cent_amount_is_valid(self, cents: int) -> None:
        money = Money(amount=Decimal(cents) / 100, currency="BRL")

        assert money.amount > 0

    @given(cents=st.integers(min_value=1, max_value=10**9))
    def test_string_round_trip_preserves_the_exact_amount(self, cents: int) -> None:
        # Property worth stating explicitly: no amount survives a round trip
        # approximately. Either it is exact or Money is broken.
        original = Money(amount=Decimal(cents) / 100, currency="BRL")

        assert Money.of(str(original.amount), "BRL") == original
