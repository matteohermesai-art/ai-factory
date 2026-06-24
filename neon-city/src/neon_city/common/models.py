"""Base models and shared types for Neon City."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any
import orjson
import time


class AgentType(Enum):
    CITIZEN = "citizen"
    HACKER = "hacker"
    CORPORATION = "corporation"
    POLICE = "police"


class EventType(Enum):
    # Economy events
    MARKET_CRASH = "market_crash"
    MARKET_BOOM = "market_boom"
    RESOURCE_SHORTAGE = "resource_shortage"
    RESOURCE_SURPLUS = "resource_surplus"
    # Agent events
    HACK = "hack"
    ARREST = "arrest"
    TRADE = "trade"
    MOVE = "move"
    SPAWN = "spawn"
    DEATH = "death"
    # World events
    POWER_OUTAGE = "power_outage"
    NETWORK_BREACH = "network_breach"
    CORPORATE_TAKEOVER = "corporate_takeover"
    RIOT = "riot"
    WEATHER = "weather"
    # System events
    TICK = "tick"
    SAVE = "save"
    LOAD = "load"
    REPLAY = "replay"


class BuildingType(Enum):
    EMPTY = "empty"
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    CORPORATE_HQ = "corporate_hq"
    HACKER_DEN = "hacker_den"
    POLICE_STATION = "police_station"
    POWER_PLANT = "power_plant"
    NETWORK_HUB = "network_hub"


@dataclass(frozen=True)
class Position:
    x: int
    y: int

    def __add__(self, other: Position) -> Position:
        return Position(self.x + other.x, self.y + other.y)

    def distance_to(self, other: Position) -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def clamp(self, max_x: int, max_y: int) -> Position:
        return Position(max(0, min(self.x, max_x - 1)), max(0, min(self.y, max_y - 1)))


@dataclass
class GridCell:
    position: Position
    building: BuildingType = BuildingType.EMPTY
    owner_id: str | None = None
    power_level: float = 1.0
    network_level: float = 1.0
    security_level: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SimulationEvent:
    event_type: EventType
    tick: int
    timestamp: float
    source_id: str | None = None
    target_id: str | None = None
    position: Position | None = None
    payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type.value,
            "tick": self.tick,
            "timestamp": self.timestamp,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "position": {"x": self.position.x, "y": self.position.y} if self.position else None,
            "payload": self.payload,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SimulationEvent:
        pos = None
        if data.get("position"):
            pos = Position(data["position"]["x"], data["position"]["y"])
        return cls(
            event_type=EventType(data["event_type"]),
            tick=data["tick"],
            timestamp=data["timestamp"],
            source_id=data.get("source_id"),
            target_id=data.get("target_id"),
            position=pos,
            payload=data.get("payload", {}),
        )


@dataclass
class TickMetrics:
    tick: int
    timestamp: float
    agent_count: int = 0
    total_currency: float = 0.0
    market_price: float = 0.0
    event_count: int = 0
    avg_agent_health: float = 0.0
    avg_agent_wealth: float = 0.0
    hack_count: int = 0
    arrest_count: int = 0
    trade_volume: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "tick": self.tick,
            "timestamp": self.timestamp,
            "agent_count": self.agent_count,
            "total_currency": self.total_currency,
            "market_price": self.market_price,
            "event_count": self.event_count,
            "avg_agent_health": self.avg_agent_health,
            "avg_agent_wealth": self.avg_agent_wealth,
            "hack_count": self.hack_count,
            "arrest_count": self.arrest_count,
            "trade_volume": self.trade_volume,
        }


def now_ts() -> float:
    return time.time()


def serialize(data: Any) -> bytes:
    return orjson.dumps(data)


def deserialize(data: bytes) -> Any:
    return orjson.loads(data)
