"""The `payment` bounded context.

Layout is *package by bounded context first, hexagonal layers inside*:

    payment/
    ├── domain/        the centre — pure business behaviour
    ├── application/   use cases and the ports they depend on
    ├── adapters/      inbound (transport) and outbound (infrastructure)
    └── bootstrap/     the only place allowed to wire the above together

A system with several contexts gets several packages shaped like this one,
rather than one global `domain/`, `application/` and `adapters/` tree holding
everything. The difference matters at scale: global layering makes every team
share three enormous packages, whereas context-first keeps a team's blast
radius inside its own directory.

Educational only. There is no real bank integration behind any of this.
"""

__all__: list[str] = []
