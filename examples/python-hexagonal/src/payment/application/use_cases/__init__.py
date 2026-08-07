"""Use cases: implementations of the inbound ports.

A use case orchestrates. It converts input into domain types, calls the ports it
was given, lets the aggregate decide, and reports the outcome.

If a use case starts containing branching business rules, that logic belongs in
the domain — an anaemic domain with a fat service layer is the most common way
hexagonal architecture is adopted in form while being abandoned in substance.
"""

from payment.application.use_cases.create_pix_payment import CreatePixPaymentService

__all__ = ["CreatePixPaymentService"]
