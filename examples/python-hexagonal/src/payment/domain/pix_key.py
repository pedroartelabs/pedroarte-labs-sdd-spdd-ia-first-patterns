"""The PixKey value object.

Educational only. This models the *shape* of a PIX key so the example has a
realistic invariant to enforce; it is not, and must not be used as, a real PIX
integration. There is no lookup against any directory, no real key is valid
here, and no real key should ever be placed in this repository.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum

from payment.domain.errors import InvalidPixKeyError


class PixKeyType(StrEnum):
    """The kinds of PIX key this example understands."""

    EMAIL = "EMAIL"
    PHONE = "PHONE"
    TAX_ID = "TAX_ID"
    RANDOM = "RANDOM"


# Format checks only. Deliberately simple: a real implementation would validate
# tax-id check digits and normalise phone numbers, and doing that here would
# add noise without teaching anything about hexagonal boundaries.
_PATTERNS: dict[PixKeyType, re.Pattern[str]] = {
    PixKeyType.EMAIL: re.compile(r"^[^@\s]+@[^@\s]+\.[a-z]{2,}$", re.IGNORECASE),
    PixKeyType.PHONE: re.compile(r"^\+[1-9][0-9]{7,14}$"),
    PixKeyType.TAX_ID: re.compile(r"^[0-9]{11}$|^[0-9]{14}$"),
    PixKeyType.RANDOM: re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        re.IGNORECASE,
    ),
}

_MAX_KEY_LENGTH = 77


@dataclass(frozen=True, slots=True)
class PixKey:
    """A destination key for a PIX transfer, validated against its declared type."""

    value: str
    key_type: PixKeyType

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise InvalidPixKeyError("a PIX key cannot be empty")
        if len(self.value) > _MAX_KEY_LENGTH:
            raise InvalidPixKeyError(f"a PIX key cannot exceed {_MAX_KEY_LENGTH} characters")
        if not isinstance(self.key_type, PixKeyType):
            raise InvalidPixKeyError(f"unknown PIX key type: {self.key_type!r}")
        if not _PATTERNS[self.key_type].match(self.value):
            raise InvalidPixKeyError(f"{self.value!r} is not a well-formed {self.key_type} key")

    def masked(self) -> str:
        """A form safe to write to a log.

        SEC-004 forbids logging a full payment identifier. A key is a customer
        identifier, so the adapter that logs it needs a redacted rendering, and
        the domain is the right place to define what "redacted" means for this
        type rather than leaving each adapter to improvise.
        """
        if self.key_type is PixKeyType.EMAIL:
            local, _, domain = self.value.partition("@")
            head = local[:2] if len(local) > 2 else local[:1]
            return f"{head}{'*' * max(len(local) - len(head), 1)}@{domain}"
        visible = 4
        if len(self.value) <= visible:
            return "*" * len(self.value)
        return f"{'*' * (len(self.value) - visible)}{self.value[-visible:]}"

    def __str__(self) -> str:
        return self.masked()
