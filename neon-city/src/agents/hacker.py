"""Hacker agent for the Neon City Simulation Engine."""

from __future__ import annotations

import random
import uuid
from typing import Dict, List, Optional

from src.agents.base import AgentStatus, AgentMemory, BaseAgent
from src.economy.currency import Wallet, CurrencyType
from src.events.bus import EventBus
from src.events.types import Event, EventType, EventSeverity
from src.engine.grid import Grid


class Hacker(BaseAgent):
    """A hacker agent that performs cyber attacks and trades data."""

    def __init__(
        self,
        agent_id: Optional[str] = None,
        name: str = "Hacker",
        x: int = 0,
        y: int = 0,
        health: float = 100.0,
        energy: float = 100.0,
        wallet: Optional[Wallet] = None,
        skill_level: int = 5,
        reputation: float = 0.0,
        stealth: float = 70.0,
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
        self.agent_type = "hacker"
        self.skill_level: int = max(1, min(10, skill_level))
        self.reputation: float = max(0.0, min(100.0, reputation))
        self.stealth: float = max(0.0, min(100.0, stealth))
        self._data_chips: int = 0

    def tick(self, world_state: dict, event_bus: EventBus) -> List[Event]:
        """Execute one simulation tick for a hacker."""
        events: List[Event] = []
        if not self.is_alive:
            return events

        self.age += 1
        self.memory.tick = world_state.get("tick", self.age)

        # Regenerate stealth each tick
        self.stealth = min(100.0, self.stealth + 2.0)

        # Risk police raid if stealth is low
        if self.stealth < 30:
            self._risk_police_raid(world_state, event_bus, events)

        # Move toward data center or random location
        self._move_toward_target(world_state)

        # 15% chance: attempt cyber attack
        if random.random() < 0.15:
            self._attempt_cyber_attack(world_state, event_bus, events)

        # Trade data chips if we have any
        if self._data_chips > 0:
            self._trade_data_chips(world_state, event_bus, events)

        # Consume energy
        self.energy = max(0.0, self.energy - 1.5)

        return events

    def _move_toward_target(self, world_state: dict) -> None:
        """Move toward a data center or random location."""
        grid = world_state.get("grid")
        if grid is None or not self.is_mobile:
            return

        # Find data centers in memory or world state
        data_centers = [
            pos for name, pos in self.memory.known_locations.items()
            if "data" in name.lower() or "center" in name.lower()
        ]
        # Also check world state for data center locations
        dc_locations = world_state.get("data_centers", [])
        for dc in dc_locations:
            if isinstance(dc, (list, tuple)) and len(dc) == 2:
                data_centers.append(tuple(dc))

        target = None
        if data_centers:
            # Move toward nearest data center
            data_centers.sort(key=lambda p: abs(p[0] - self.x) + abs(p[1] - self.y))
            target = data_centers[0]

        if target:
            dx = target[0] - self.x
            dy = target[1] - self.y
            # Normalize to single step
            step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
            step_y = 0 if dy == 0 else (1 if dy > 0 else -1)
            # Prefer axis with larger distance
            if abs(dx) >= abs(dy):
                self.move_to(self.x + step_x, self.y, grid)
            else:
                self.move_to(self.x, self.y + step_y, grid)
        else:
            # Random movement
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            random.shuffle(directions)
            for d_x, d_y in directions:
                if self.move_to(self.x + d_x, self.y + d_y, grid):
                    break

    def _attempt_cyber_attack(
        self, world_state: dict, event_bus: EventBus, events: List[Event]
    ) -> None:
        """Attempt a cyber attack on a nearby agent."""
        self.status = AgentStatus.ATTACKING
        agents = world_state.get("agents", {})
        targets = [
            a for a in agents.values()
            if a.agent_id != self.agent_id
            and a.is_alive
            and abs(a.x - self.x) <= 3
            and abs(a.y - self.y) <= 3
        ]
        if not targets:
            return

        target = random.choice(targets)
        # Success chance based on skill_level (10% per level = max 100%)
        success_chance = self.skill_level * 0.10
        if random.random() < success_chance:
            # Attack succeeded
            steal_amount = random.uniform(5.0, 25.0)
            stolen = target.wallet.transfer_to(self.wallet, CurrencyType.CREDITS, steal_amount)

            # Gain data currency
            data_gain = random.uniform(1.0, 5.0)
            self.wallet.credit(CurrencyType.DATA, data_gain)
            self._data_chips += random.randint(0, 2)

            # Increase reputation
            self.reputation = min(100.0, self.reputation + 5.0)

            # Reduce stealth
            self.stealth = max(0.0, self.stealth - 10.0)

            event = Event(
                event_type=EventType.CYBER_ATTACK,
                severity=EventSeverity.HIGH,
                tick=world_state.get("tick", 0),
                source_id=self.agent_id,
                target_id=target.agent_id,
                data={
                    "success": True,
                    "stolen_amount": round(steal_amount, 2) if stolen else 0,
                    "data_gained": round(data_gain, 2),
                    "skill_level": self.skill_level,
                },
            )
            event_bus.publish(event)
            events.append(event)

            # Update memory
            self.memory.known_agents[target.agent_id] = "enemy"
        else:
            # Failed attack
            self.stealth = max(0.0, self.stealth - 15.0)
            event = Event(
                event_type=EventType.CYBER_ATTACK,
                severity=EventSeverity.MEDIUM,
                tick=world_state.get("tick", 0),
                source_id=self.agent_id,
                target_id=target.agent_id,
                data={"success": False, "skill_level": self.skill_level},
            )
            event_bus.publish(event)
            events.append(event)

    def _risk_police_raid(
        self, world_state: dict, event_bus: EventBus, events: List[Event]
    ) -> None:
        """Generate a police raid event if stealth is low."""
        if random.random() < 0.2:  # 20% chance of raid when stealth < 30
            event = Event(
                event_type=EventType.POLICE_RAID,
                severity=EventSeverity.HIGH,
                tick=world_state.get("tick", 0),
                source_id="system",
                target_id=self.agent_id,
                data={"reason": "low_stealth", "stealth": self.stealth},
            )
            event_bus.publish(event)
            events.append(event)

    def _trade_data_chips(
        self, world_state: dict, event_bus: EventBus, events: List[Event]
    ) -> None:
        """Trade data chips on the market."""
        market = world_state.get("market")
        if market is None:
            return

        from src.economy.market import Order, OrderType

        chips_to_sell = self._data_chips
        price_per_chip = random.uniform(8.0, 20.0)

        order = Order(
            order_id=str(uuid.uuid4()),
            agent_id=self.agent_id,
            order_type=OrderType.SELL,
            item="data_chip",
            quantity=chips_to_sell,
            price=price_per_chip,
            currency=CurrencyType.CREDITS,
        )
        market.place_order(order)
        self._data_chips = 0

        event = Event(
            event_type=EventType.TRANSACTION,
            severity=EventSeverity.LOW,
            tick=world_state.get("tick", 0),
            source_id=self.agent_id,
            data={
                "action": "sell_data_chips",
                "quantity": chips_to_sell,
                "price_per_chip": round(price_per_chip, 2),
            },
        )
        event_bus.publish(event)
        events.append(event)

    def to_dict(self) -> dict:
        """Serialize hacker to dictionary."""
        base = super().to_dict()
        base.update({
            "skill_level": self.skill_level,
            "reputation": self.reputation,
            "stealth": self.stealth,
            "data_chips": self._data_chips,
        })
        return base

    @classmethod
    def from_dict(cls, data: dict) -> Hacker:
        """Reconstruct a Hacker from a serialized dict."""
        agent = cls(
            agent_id=data["agent_id"],
            name=data["name"],
            x=data["x"],
            y=data["y"],
            health=data["health"],
            energy=data["energy"],
            wallet=Wallet.from_dict(data["wallet"]),
            skill_level=data.get("skill_level", 5),
            reputation=data.get("reputation", 0.0),
            stealth=data.get("stealth", 70.0),
            attributes=data.get("attributes", {}),
        )
        agent.agent_type = data.get("agent_type", "hacker")
        agent.age = data.get("age", 0)
        agent.status = AgentStatus(data.get("status", "IDLE"))
        agent.alive = data.get("alive", True)
        agent.memory = AgentMemory.from_dict(data.get("memory", {}))
        agent._data_chips = data.get("data_chips", 0)
        return agent

    def __repr__(self) -> str:
        return (
            f"Hacker(id={self.agent_id[:8]}, name={self.name!r}, "
            f"pos=({self.x},{self.y}), skill={self.skill_level}, "
            f"stealth={self.stealth:.1f}, rep={self.reputation:.1f})"
        )
