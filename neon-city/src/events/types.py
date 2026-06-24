"""
Event type definitions for the Neon City Simulation Engine.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class EventType(Enum):
    """Types of events that can occur in the simulation."""
    AGENT_SPAWN = "AGENT_SPAWN"
    AGENT_DEATH = "AGENT_DEATH"
    TRANSACTION = "TRANSACTION"
    MARKET_CRASH = "MARKET_CRASH"
    CYBER_ATTACK = "CYBER_ATTACK"
    POLICE_RAID = "POLICE_RAID"
    CORP_TAKEOVER = "CORP_TAKEOVER"
    DATA_BREACH = "DATA_BREACH"
    POWER_OUTAGE = "POWER_OUTAGE"
    RIOT = "RIOT"
    TECH_BREAKTHROUGH = "TECH_BREAKTHROUGH"
    AGENT_MOVE = "AGENT_MOVE"
    AGENT_INTERACTION = "AGENT_INTERACTION"


class EventSeverity(Enum):
    """Severity levels for events."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class Event:
    """Represents a simulation event."""
    event_type: EventType
    severity: EventSeverity
    tick: int
    source_id: str
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    target_id: Optional[str] = None
    data: dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        """Serialize event to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "severity": self.severity.value,
            "tick": self.tick,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "data": self.data,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Event:
        """Deserialize event from dictionary."""
        return cls(
            event_id=data["event_id"],
            event_type=EventType(data["event_type"]),
            severity=EventSeverity(data["severity"]),
            tick=data["tick"],
            source_id=data["source_id"],
            target_id=data.get("target_id"),
            data=data.get("data", {}),
            timestamp=data.get("timestamp", time.time()),
        )

    def __repr__(self) -> str:
        return (
            f"Event(id={self.event_id[:8]}, type={self.event_type.value}, "
            f"severity={self.severity.value}, tick={self.tick}, "
            f"source={self.source_id}, target={self.target_id})"
        )
