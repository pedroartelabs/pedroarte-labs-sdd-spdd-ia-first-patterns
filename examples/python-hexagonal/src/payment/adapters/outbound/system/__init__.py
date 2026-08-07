"""System adapters: time, identity and event publication.

Three tiny classes that exist so that `datetime.now()`, `uuid4()` and a logging
call each appear exactly once, at the edge, where a test can replace them
(ARCH-012). Their smallness is the point — the cost of the abstraction is three
files, and the benefit is that nothing inward is non-deterministic.
"""

from payment.adapters.outbound.system.logging_event_publisher import LoggingEventPublisher
from payment.adapters.outbound.system.system_clock import SystemClock
from payment.adapters.outbound.system.uuid_id_generator import UuidIdGenerator

__all__ = ["LoggingEventPublisher", "SystemClock", "UuidIdGenerator"]
