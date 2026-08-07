"""Outbound port: the current time.

Reading the wall clock looks harmless and is not. A domain or use case that
calls ``datetime.now()`` directly becomes untestable at the exact points where
time matters — expiry, ordering, retention windows — and forces every test that
touches it to either freeze global state or accept flakiness.

Behind a port, "now" becomes an ordinary input. Tests pass a fixed instant; the
composition root passes the system clock (ARCH-012).
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol


class Clock(Protocol):
    """Supplies the current instant."""

    def now(self) -> datetime:
        """Return the current time as a timezone-aware datetime.

        Implementations must return an aware datetime. The ``Payment``
        aggregate rejects naive timestamps, because a bare local time is
        ambiguous the moment the system crosses a timezone or a DST boundary.
        """
        ...
