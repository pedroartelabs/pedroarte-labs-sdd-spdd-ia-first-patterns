"""Outbound adapters: infrastructure the application drives.

    memory/       in-memory storage — a real adapter, not a test double
    persistence/  SQLAlchemy storage
    system/       clock, identifier generation, event publication

Each implements a port declared by the application layer and translates its
technology's failures into ``OutboundPortError`` before they cross the boundary
(ARCH-011).

`memory/` and `persistence/` are both subject to the same contract suite in
`tests/contract/`, which is what stops the fast implementation used by every
unit test from quietly disagreeing with the one that runs in production.
"""

__all__: list[str] = []
