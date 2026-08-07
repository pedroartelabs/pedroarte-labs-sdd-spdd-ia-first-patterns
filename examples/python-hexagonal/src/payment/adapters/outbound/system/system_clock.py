"""System implementation of the ``Clock`` port.

A three-line adapter that exists so that ``datetime.now()`` appears exactly once
in the codebase, at the outermost edge, where it can be swapped for a fixed
instant in every test.

UTC is not a preference here. A naive local timestamp is ambiguous twice a year
under DST and meaningless once a second machine in another region writes to the
same store, so ``Payment`` rejects one outright.
"""

from __future__ import annotations

from datetime import UTC, datetime


class SystemClock:
    """Reads the real wall clock, in UTC."""

    def now(self) -> datetime:
        return datetime.now(tz=UTC)
