"""Bootstrap: the composition root.

The only package allowed to import every other package, and only in order to
wire them together: dependency injection, configuration, lifecycle and
technical observability.

Nothing may import *this* package. The Import Linter contract
`bootstrap-is-not-imported` enforces it (ARCH-007), because an adapter that
reaches back into the container has turned it into a service locator — at which
point the dependency graph is no longer visible in the code and no longer
checkable by any tool.
"""

from payment.bootstrap.app import create_app
from payment.bootstrap.container import PaymentComponents, build_payment_components

__all__ = ["PaymentComponents", "build_payment_components", "create_app"]
