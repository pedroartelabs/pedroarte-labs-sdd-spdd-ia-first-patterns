"""Inbound adapters: things that drive the application.

An inbound adapter validates the *shape* of a request, authenticates where
applicable, converts transport into an application command, calls an inbound
port, and maps the outcome back to the transport.

It contains no business rule. The test for whether a line belongs here is
simple: if adding a second transport would force you to copy it, it is in the
wrong layer.
"""

__all__: list[str] = []
