"""
Event system for the Neon City Simulation Engine.

Provides event types, the central event bus, and various event generators
for creating simulation events based on world state.
"""

from .types import Event, EventSeverity, EventType
from .bus import EventBus
from .generators import (
    AgentEventGenerator,
    CompositeGenerator,
    EconomyEventGenerator,
    EventGenerator,
    RandomEventGenerator,
)

__all__ = [
    "EventType",
    "EventSeverity",
    "Event",
    "EventBus",
    "EventGenerator",
    "RandomEventGenerator",
    "AgentEventGenerator",
    "EconomyEventGenerator",
    "CompositeGenerator",
]
