"""Police agent for the Neon City Simulation Engine."""

from __future__ import annotations

import random
import uuid
from typing import Dict, List, Optional, Tuple

from src.agents.base import AgentStatus, AgentMemory, BaseAgent
from src.economy.currency import Wallet, CurrencyType
from src.events.bus import EventBus
from src.events.types import Event, EventType, EventSeverity
from src.engine.grid import Grid


class Police(BaseAgent):
    """A police agent that patrols, enforces laws, and arrests criminals."""

    def __init__(
        self,
        agent_id: Optional[str] = None,
        name: str = "Officer",
        x: int = 0,
        y: int = 0,
        health: float = 100.0,
        energy: float = 100.0,
        wallet: Optional[Wallet] = None,
        jurisdiction: Optional[List[Tuple[int, int]]] = None,
        alert_level: float = 0.0,
        arrests: int = 0,
        attributes: Optional[Dict] = None,
    ):
        super().__init__(
            agent_id=agent_id,
            name=name,
            x=x,
            y=y,
            health=health,
            energy=energy,
            wallet=wallet,
            attributes=attributes,
        )
        self.agent_type = "police"
        self.jurisdiction: List[Tuple[int, int]] = jurisdiction or [(x, y)]
        self.alert_level: float = max(0.0, min(100.0, alert_level))
        self.arrests: int = arrests
        self._patrol_index: int = 0
        self._arrest_cooldown: Dict[str, int] = {}  # agent_id -> ticks until release

    def tick(self, world_state: dict, event_bus: EventBus) -> List[Event]:
        """Execute one simulation tick for a police agent."""
        events: List[Event] = []
        if not self.is_alive:
            return events

        self.age += 1
        self.memory.tick = world_state.get("tick", self.age)

        # Decay alert level over time
        self.alert_level = max(0.0, self.alert_level - 1.0)

        # Check for nearby crimes (hackers with low stealth)
        self._detect_crimes(world_state, event_bus, events)

        # Check for black market activity
        self._check_black_market(world_state, event_bus, events)

        # Update arrest cooldowns
        self._update_arrests(world_state, event_bus, events)

        # Patrol movement
        self._patrol(world_state)

        # Recover energy
        self.energy = min(100.0, self.energy + 0.5)

        return events

    def _detect_crimes(
        self, world_state: dict, event_bus: EventBus, events: List[Event]
    ) -> None:
        """Detect and respond to crimes (hackers with low stealth)."""
        agents = world_state.get("agents", {})
        detection_range = 4

        for agent in agents.values():
            if agent.agent_id == self.agent_id or not agent.is_alive:
                continue

            # Check if it's a hacker with low stealth
            if hasattr(agent, 'stealth') and agent.stealth < 40:
                dist = abs(agent.x - self.x) + abs(agent.y - self.y)
                if dist <= detection_range:
                    # Increase alert level
                    self.alert_level = min(100.0, self.alert_level + 15.0)

                    # Attempt arrest
                    if dist <= 2 and agent.agent_id not in self._arrest_cooldown:
                        self._attempt_arrest(agent, world_state, event_bus, events)

    def _attempt_arrest(
        self,
        target: BaseAgent,
        world_state: dict,
        event_bus: EventBus,
        events: List[Event],
    ) -> None:
        """Attempt to arrest a criminal agent."""
        # Arrest success based on alert level and distance
        success_chance = 0.3 + (self.alert_level * 0.005)

        # If target has low stealth, higher chance
        if hasattr(target, 'stealth'):
            success_chance += (100 - target.stealth) * 0.002

        if random.random() < success_chance:
            # Arrest successful
            target.status = AgentStatus.ARRESTED
            self.arrests += 1
            self._arrest_cooldown[target.agent_id] = 20  # 20 ticks in jail

            # Damage the target slightly
            target.take_damage(5.0)

            event = Event(
                event_type=EventType.POLICE_RAID,
                severity=EventSeverity.HIGH,
                tick=world_state.get("tick", 0),
                source_id=self.agent_id,
                target_id=target.agent_id,
                data={
                    "action": "arrest",
                    "success": True,
                    "crime": "hacking",
                    "sentence": 20,
                },
            )
            event_bus.publish(event)
            events.append(event)

            # Update memory
            self.memory.known_agents[target.agent_id] = "enemy"
        else:
            event = Event(
                event_type=EventType.POLICE_RAID,
                severity=EventSeverity.MEDIUM,
                tick=world_state.get("tick", 0),
                source_id=self.agent_id,
                target_id=target.agent_id,
                data={"action": "arrest_attempt", "success": False},
            )
            event_bus.publish(event)
            events.append(event)

    def _check_black_market(
        self, world_state: dict, event_bus: EventBus, events: List[Event]
    ) -> None:
        """Check for black market activity in range and conduct raids."""
        market = world_state.get("market")
        if market is None:
            return

        # Check if there are black market trades nearby
        black_market_balance = 0
        for agent in world_state.get("agents", {}).values():
            if agent.is_alive and hasattr(agent, 'wallet'):
                black_market_balance += agent.wallet.balance(CurrencyType.BLACK_MARKET)

        if black_market_balance > 0:
            # Check for nearby illegal agents
            agents = world_state.get("agents", {})
            raid_targets = [
                a for a in agents.values()
                if a.is_alive
                and a.agent_id != self.agent_id
                and hasattr(a, 'stealth')
                and a.stealth < 50
                and abs(a.x - self.x) <= 3
                and abs(a.y - self.y) <= 3
            ]

            if raid_targets and random.random() < 0.3:
                # Conduct raid
                for target in raid_targets:
                    target.take_damage(10.0)
                    self.alert_level = min(100.0, self.alert_level + 10.0)

                event = Event(
                    event_type=EventType.POLICE_RAID,
                    severity=EventSeverity.CRITICAL,
                    tick=world_state.get("tick", 0),
                    source_id=self.agent_id,
                    data={
                        "action": "black_market_raid",
                        "targets": [t.agent_id for t in raid_targets],
                    },
                )
                event_bus.publish(event)
                events.append(event)

    def _update_arrests(
        self, world_state: dict, event_bus: EventBus, events: List[Event]
    ) -> None:
        """Update arrest timers and release agents when their sentence is done."""
        released = []
        for agent_id, ticks_left in list(self._arrest_cooldown.items()):
            ticks_left -= 1
            if ticks_left <= 0:
                released.append(agent_id)
            else:
                self._arrest_cooldown[agent_id] = ticks_left

        for agent_id in released:
            del self._arrest_cooldown[agent_id]
            agents = world_state.get("agents", {})
            if agent_id in agents:
                agent = agents[agent_id]
                agent.status = AgentStatus.IDLE
                event = Event(
                    event_type=EventType.AGENT_INTERACTION,
                    severity=EventSeverity.MEDIUM,
                    tick=world_state.get("tick", 0),
                    source_id=self.agent_id,
                    target_id=agent_id,
                    data={"action": "released", "after_ticks": 20},
                )
                event_bus.publish(event)
                events.append(event)

    def _patrol(self, world_state: dict) -> None:
        """Move along patrol route."""
        grid = world_state.get("grid")
        if grid is None or not self.is_mobile:
            return

        if not self.jurisdiction:
            return

        # Move to next patrol point
        target = self.jurisdiction[self._patrol_index % len(self.jurisdiction)]
        dx = target[0] - self.x
        dy = target[1] - self.y

        if dx == 0 and dy == 0:
            # Reached patrol point, move to next
            self._patrol_index += 1
            return

        # Step toward target
        step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
        step_y = 0 if dy == 0 else (1 if dy > 0 else -1)
        self.move_to(self.x + step_x, self.y + step_y, grid)
        self.status = AgentStatus.MOVING

    def to_dict(self) -> dict:
        """Serialize police to dictionary."""
        base = super().to_dict()
        base.update({
            "jurisdiction": [list(p) for p in self.jurisdiction],
            "alert_level": self.alert_level,
            "arrests": self.arrests,
            "patrol_index": self._patrol_index,
            "arrest_cooldown": dict(self._arrest_cooldown),
        })
        return base

    @classmethod
    def from_dict(cls, data: dict) -> Police:
        """Reconstruct a Police agent from a serialized dict."""
        jurisdiction = [tuple(p) for p in data.get("jurisdiction", [])]
        agent = cls(
            agent_id=data["agent_id"],
            name=data["name"],
            x=data["x"],
            y=data["y"],
            health=data["health"],
            energy=data["energy"],
            wallet=Wallet.from_dict(data["wallet"]),
            jurisdiction=jurisdiction,
            alert_level=data.get("alert_level", 0.0),
            arrests=data.get("arrests", 0),
            attributes=data.get("attributes", {}),
        )
        agent.agent_type = data.get("agent_type", "police")
        agent.age = data.get("age", 0)
        agent.status = AgentStatus(data.get("status", "IDLE"))
        agent.alive = data.get("alive", True)
        agent.memory = AgentMemory.from_dict(data.get("memory", {}))
        agent._patrol_index = data.get("patrol_index", 0)
        agent._arrest_cooldown = data.get("arrest_cooldown", {})
        return agent

    def __repr__(self) -> str:
        return (
            f"Police(id={self.agent_id[:8]}, name={self.name!r}, "
            f"pos=({self.x},{self.y}), alert={self.alert_level:.1f}, "
            f"arrests={self.arrests})"
        )
