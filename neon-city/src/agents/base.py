"""Base agent class for the Neon City Simulation Engine."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

from src.economy.currency import Wallet, CurrencyType
from src.events.bus import EventBus
from src.events.types import Event, EventType, EventSeverity
from src.engine.grid import Grid


class AgentStatus(Enum):
    """Possible states an agent can be in."""
    IDLE = "IDLE"
    MOVING = "MOVING"
    WORKING = "WORKING"
    ATTACKING = "ATTACKING"
    TRADING = "TRADING"
    RESTING = "RESTING"
    ARRESTED = "ARRESTED"
    DEAD = "DEAD"


@dataclass
class AgentMemory:
    """Memory storage for an agent's learned information."""
    known_locations: Dict[str, Tuple[int, int]] = field(default_factory=dict)
    known_agents: Dict[str, str] = field(default_factory=dict)  # agent_id -> "friend"/"enemy"/"neutral"
    last_events: List[str] = field(default_factory=list)
    tick: int = 0

    def to_dict(self) -> dict:
        return {
            "known_locations": {k: list(v) for k, v in self.known_locations.items()},
            "known_agents": dict(self.known_agents),
            "last_events": list(self.last_events),
            "tick": self.tick,
        }

    @classmethod
    def from_dict(cls, data: dict) -> AgentMemory:
        known_locations = {k: tuple(v) for k, v in data.get("known_locations", {}).items()}
        return cls(
            known_locations=known_locations,
            known_agents=data.get("known_agents", {}),
            last_events=data.get("last_events", []),
            tick=data.get("tick", 0),
        )


class BaseAgent(ABC):
    """Abstract base class for all simulation agents."""

    def __init__(
        self,
        agent_id: Optional[str] = None,
        name: str = "Agent",
        x: int = 0,
        y: int = 0,
        health: float = 100.0,
        energy: float = 100.0,
        wallet: Optional[Wallet] = None,
        attributes: Optional[Dict] = None,
    ):
        self.agent_id: str = agent_id or str(uuid.uuid4())
        self.agent_type: str = "base"
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.health: float = max(0.0, min(100.0, health))
        self.energy: float = max(0.0, min(100.0, energy))
        self.age: int = 0
        self.status: AgentStatus = AgentStatus.IDLE
        self.alive: bool = True
        self.wallet: Wallet = wallet or Wallet(owner_id=self.agent_id)
        self.memory: AgentMemory = AgentMemory()
        self.attributes: Dict = attributes or {}

    @abstractmethod
    def tick(self, world_state: dict, event_bus: EventBus) -> List[Event]:
        """Execute one simulation tick. Returns list of events generated."""
        ...

    def move_to(self, x: int, y: int, grid: Grid) -> bool:
        """Attempt to move to a position on the grid. Returns success."""
        if not self.alive or self.status == AgentStatus.ARRESTED:
            return False
        if 0 <= x < grid.width and 0 <= y < grid.height:
            old_x, old_y = self.x, self.y
            self.x = x
            self.y = y
            self.status = AgentStatus.MOVING
            self.energy = max(0.0, self.energy - 1.0)
            return True
        return False

    def interact(self, other: BaseAgent) -> bool:
        """Interact with another agent. Returns success."""
        if not self.alive or not other.alive:
            return False
        if self.status == AgentStatus.ARRESTED or other.status == AgentStatus.ARRESTED:
            return False
        return True

    def take_damage(self, amount: float) -> bool:
        """Apply damage. Returns False if agent is killed."""
        if not self.alive:
            return False
        self.health = max(0.0, self.health - amount)
        if self.health <= 0:
            self.alive = False
            self.status = AgentStatus.DEAD
            return False
        return True

    def heal(self, amount: float) -> None:
        """Restore health."""
        if self.alive:
            self.health = min(100.0, self.health + amount)

    def rest(self) -> None:
        """Recover energy."""
        if self.alive:
            self.energy = min(100.0, self.energy + 10.0)
            self.status = AgentStatus.RESTING

    def to_dict(self) -> dict:
        """Serialize agent to dictionary."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "health": self.health,
            "energy": self.energy,
            "age": self.age,
            "status": self.status.value,
            "alive": self.alive,
            "wallet": self.wallet.to_dict(),
            "memory": self.memory.to_dict(),
            "attributes": dict(self.attributes),
        }

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict) -> BaseAgent:
        """Reconstruct agent from serialized dict. Implemented by subclasses."""
        ...

    @property
    def is_alive(self) -> bool:
        """Whether the agent is alive."""
        return self.alive and self.health > 0

    @property
    def position(self) -> Tuple[int, int]:
        """Current grid position."""
        return (self.x, self.y)

    @property
    def is_mobile(self) -> bool:
        """Whether the agent can move."""
        return self.alive and self.status != AgentStatus.ARRESTED and self.status != AgentStatus.DEAD

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(id={self.agent_id[:8]}, name={self.name!r}, "
            f"pos=({self.x},{self.y}), hp={self.health:.1f}, energy={self.energy:.1f}, "
            f"status={self.status.value})"
        )
