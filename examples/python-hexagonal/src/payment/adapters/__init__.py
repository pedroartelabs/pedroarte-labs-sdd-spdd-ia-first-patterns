"""Adapters: where technology is allowed to live.

    inbound/   transport driving the application (REST, CLI, consumers)
    outbound/  infrastructure the application drives (storage, messaging, time)

The two are siblings and must never import each other (ARCH-004/005). A
controller that calls a repository directly has skipped the use case, which
means the rule it was about to apply now exists only on the HTTP path — invisible
to the CLI, the consumer and the scheduler.

This module deliberately re-exports nothing. Importing it must not pull both
sides of the boundary into the same import graph.
"""

__all__: list[str] = []
