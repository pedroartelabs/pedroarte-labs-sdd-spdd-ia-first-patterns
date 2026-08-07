"""PixKey invariants and log masking.

Educational only: these are format checks against fictional keys. No real PIX
key appears here, and a real implementation would additionally verify tax-id
check digits and normalise phone numbers.
"""

from __future__ import annotations

import pytest

from payment.domain.errors import InvalidPixKeyError
from payment.domain.pix_key import PixKey, PixKeyType


class TestValidation:
    @pytest.mark.parametrize(
        ("value", "key_type"),
        [
            ("alice@example.com", PixKeyType.EMAIL),
            ("a.b+tag@sub.example.co", PixKeyType.EMAIL),
            ("+5511999998888", PixKeyType.PHONE),
            ("12345678901", PixKeyType.TAX_ID),
            ("12345678000199", PixKeyType.TAX_ID),
            ("11111111-1111-4111-8111-111111111111", PixKeyType.RANDOM),
        ],
    )
    def test_accepts_well_formed_keys(self, value: str, key_type: PixKeyType) -> None:
        assert PixKey(value=value, key_type=key_type).value == value

    @pytest.mark.parametrize(
        ("value", "key_type"),
        [
            ("not-an-email", PixKeyType.EMAIL),
            ("alice@", PixKeyType.EMAIL),
            ("@example.com", PixKeyType.EMAIL),
            ("5511999998888", PixKeyType.PHONE),  # missing +
            ("+0511999998888", PixKeyType.PHONE),  # leading zero country code
            ("1234567890", PixKeyType.TAX_ID),  # 10 digits
            ("abcdefghijk", PixKeyType.TAX_ID),
            ("not-a-uuid", PixKeyType.RANDOM),
        ],
    )
    def test_rejects_malformed_keys(self, value: str, key_type: PixKeyType) -> None:
        with pytest.raises(InvalidPixKeyError, match="not a well-formed"):
            PixKey(value=value, key_type=key_type)

    @pytest.mark.parametrize("value", ["", "   ", "\t"])
    def test_rejects_blank_keys(self, value: str) -> None:
        with pytest.raises(InvalidPixKeyError, match="cannot be empty"):
            PixKey(value=value, key_type=PixKeyType.EMAIL)

    def test_rejects_an_over_long_key(self) -> None:
        too_long = "a" * 70 + "@example.com"

        with pytest.raises(InvalidPixKeyError, match="cannot exceed 77 characters"):
            PixKey(value=too_long, key_type=PixKeyType.EMAIL)

    def test_rejects_an_unknown_key_type(self) -> None:
        with pytest.raises(InvalidPixKeyError, match="unknown PIX key type"):
            PixKey(value="alice@example.com", key_type="EMAIL")  # type: ignore[arg-type]

    def test_a_valid_key_of_the_wrong_declared_type_is_rejected(self) -> None:
        # The value is a perfectly good email; it is simply not a phone number.
        # Validating against the *declared* type is what catches a client that
        # mixed up its fields.
        with pytest.raises(InvalidPixKeyError):
            PixKey(value="alice@example.com", key_type=PixKeyType.PHONE)


class TestMasking:
    """SEC-004: a key is a customer identifier and must not reach a log intact."""

    def test_masks_an_email_keeping_the_domain(self) -> None:
        key = PixKey(value="alice@example.com", key_type=PixKeyType.EMAIL)

        assert key.masked() == "al***@example.com"
        assert "alice" not in key.masked()

    def test_masks_a_very_short_email_local_part(self) -> None:
        key = PixKey(value="a@example.com", key_type=PixKeyType.EMAIL)

        assert key.masked() == "a*@example.com"

    def test_masks_a_phone_keeping_the_last_four_digits(self) -> None:
        key = PixKey(value="+5511999998888", key_type=PixKeyType.PHONE)

        assert key.masked() == "**********8888"

    def test_masks_a_tax_id(self) -> None:
        key = PixKey(value="12345678901", key_type=PixKeyType.TAX_ID)

        assert key.masked() == "*******8901"
        assert "12345678901" not in key.masked()

    def test_str_uses_the_masked_form(self) -> None:
        # The important property: an f-string in an adapter cannot accidentally
        # leak the raw key, because the default rendering is already redacted.
        key = PixKey(value="alice@example.com", key_type=PixKeyType.EMAIL)

        assert "alice@example.com" not in f"paying {key}"


class TestValueSemantics:
    def test_equal_by_value_and_type(self) -> None:
        left = PixKey(value="alice@example.com", key_type=PixKeyType.EMAIL)
        right = PixKey(value="alice@example.com", key_type=PixKeyType.EMAIL)

        assert left == right
        assert len({left, right}) == 1

    def test_is_immutable(self) -> None:
        key = PixKey(value="alice@example.com", key_type=PixKeyType.EMAIL)

        with pytest.raises(AttributeError):
            key.value = "mallory@example.com"  # type: ignore[misc]
