"""Citizen agent for the Neon City Simulation Engine."""

from __future__ import annotations

import random
import uuid
from typing import Dict, List, Optional

from src.agents.base import AgentStatus, AgentMemory, BaseAgent
from src.economy.currency import Wallet, CurrencyType
from src.events.bus import EventBus
from src.events.types import Event, EventType, EventSeverity
from src.engine.grid import Grid


class Citizen(BaseAgent):
    """A regular citizen agent that works, trades, and interacts."""

    def __init__(
        self,
        agent_id: Optional[str] = None,
        name: str = "Citizen",
        x: int = 0,
        y: int = 0,
        health: float = 100.0,
        energy: float = 100.0,
        wallet: Optional[Wallet] = None,
        job: str = "unemployed",
        happiness: float = 50.0,
        hunger: float = 0.0,
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
        self.agent_type = "citizen"
        self.job: str = job
        self.happiness: float = max(0.0, min(100.0, happiness))
        self.hunger: float = max(0.0, min(100.0, hunger))
        self._ticks_since_food: int = 0

    def tick(self, world_state: dict, event_bus: EventBus) -> List[Event]:
        """Execute one simulation tick for a citizen."""
        events: List[Event] = []
        if not self.is_alive:
            return events

        self.age += 1
        self.memory.tick = world_state.get("tick", self.age)
        self._ticks_since_food += 1
        self.hunger = min(100.0, self.hunger + 2.0)

        # Priority 1: Low energy -> rest
        if self.energy < 20:
            self.rest()
            self._generate_rest_event(event_bus)
            return events

        # Priority 2: Hunger -> try to buy food
        if self.hunger >= 50 or self._ticks_since_food >= 10:
            ate = self._try_buy_food(world_state, event_bus, events)
            if ate:
                self._ticks_since_food = 0
                self.hunger = max(0.0, self.hunger - 40.0)
            else:
                # Couldn't buy food, increase unhappiness
                self.happiness = max(0.0, self.happiness - 5.0)

        # Priority 3: Random interaction with nearby agent (5% chance)
        if random.random() < 0.05:
            self._try_random_interaction(world_state, event_bus, events)

        # Priority 4: Move and possibly work
        if self.energy >= 20 and self.hunger < 80:
            self._move_and_work(world_state, event_bus, events)

        # Decrease happiness slightly if hungry
        if self.hunger > 70:
            self.happiness = max(0.0, self.happiness - 2.0)

        # Recover a tiny bit of energy each tick
        self.energy = min(100.0, self.energy + 0.5)

        return events

    def _try_buy_food(
        self, world_state: dict, event_bus: EventBus, events: List[Event]
    ) -> bool:
        """Attempt to buy food from the market."""
        market = world_state.get("market")
        if market is None:
            return False

        # Check if we can afford food
        price = market.get_price("food") or 10.0
        if self.wallet.balance(CurrencyType.CREDITS) < price:
            return False

        from src.economy.market import Order, OrderType
        order = Order(
            order_id=str(uuid.uuid4()),
            agent_id=self.agent_id,
            order_type=OrderType.BUY,
            item="food",
            quantity=1,
            price=price + 5.0,  # willing to pay a bit more
            currency=CurrencyType.CREDITS,
        )
        market.place_order(order)

        # Check if we got matched (simplified: assume success if we had credits)
        if self.wallet.debit(CurrencyType.CREDITS, price):
            event = Event(
                event_type=EventType.TRANSACTION,
                severity=EventSeverity.LOW,
                tick=world_state.get("tick", 0),
                source_id=self.agent_id,
                data={"item": "food", "price": price, "action": "buy"},
            )
            event_bus.publish(event)
            events.append(event)
            return True
        return False

    def _try_random_interaction(
        self, world_state: dict, event_bus: EventBus, events: List[Event]
    ) -> None:
        """Attempt a random interaction with a nearby agent."""
        agents = world_state.get("agents", {})
        nearby = [
            a for a in agents.values()
            if a.agent_id != self.agent_id
            and a.is_alive
            and abs(a.x - self.x) <= 2
            and abs(a.y - self.y) <= 2
        ]
        if not nearby:
            return

        other = random.choice(nearby)
        success = self.interact(other)
        if success:
            self.happiness = min(100.0, self.happiness + 3.0)
            event = Event(
                event_type=EventType.AGENT_INTERACTION,
                severity=EventSeverity.LOW,
                tick=world_state.get("tick", 0),
                source_id=self.agent_id,
                target_id=other.agent_id,
                data={"interaction": "chat", "with": other.name},
            )
            event_bus.publish(event)
            events.append(event)

    def _move_and_work(
        self, world_state: dict, event_bus: EventBus, events: List[Event]
    ) -> None:
        """Move to adjacent cell and possibly work to earn credits."""
        grid = world_state.get("grid")
        if grid is None:
            return

        # Try random adjacent walkable cell
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
        random.shuffle(directions)
        moved = False
        for dx, dy in directions:
            nx, ny = self.x + dx, self.y + dy
            if self.move_to(nx, ny, grid):
                moved = True
                break

        if moved:
            # 60% chance to work and earn credits after moving
            if random.random() < 0.6:
                self.status = AgentStatus.WORKING
                earnings = random.uniform(5.0, 15.0)
                self.wallet.credit(CurrencyType.CREDITS, earnings)
                self.happiness = min(100.0, self.happiness + 1.0)
                event = Event(
                    event_type=EventType.TRANSACTION,
                    severity=EventSeverity.LOW,
                    tick=world_state.get("tick", 0),
                    source_id=self.agent_id,
                    data={"action": "work", "earnings": round(earnings, 2), "job": self.job},
                )
                event_bus.publish(event)
                events.append(event)
            else:
                self.status = AgentStatus.IDLE

    def _generate_rest_event(self, event_bus: EventBus) -> None:
        """Generate a rest event."""
        event = Event(
            event_type=EventType.AGENT_MOVE,
            severity=EventSeverity.LOW,
            tick=self.memory.tick,
            source_id=self.agent_id,
            data={"action": "rest", "energy": self.energy},
        )
        event_bus.publish(event)

    def to_dict(self) -> dict:
        """Serialize citizen to dictionary."""
        base = super().to_dict()
        base.update({
            "job": self.job,
            "happiness": self.happiness,
            "hunger": self.hunger,
            "ticks_since_food": self._ticks_since_food,
        })
        return base

    @classmethod
    def from_dict(cls, data: dict) -> Citizen:
        """Reconstruct a Citizen from a serialized dict."""
        agent = cls(
            agent_id=data["agent_id"],
            name=data["name"],
            x=data["x"],
            y=data["y"],
            health=data["health"],
            energy=data["energy"],
            wallet=Wallet.from_dict(data["wallet"]),
            job=data.get("job", "unemployed"),
            happiness=data.get("happiness", 50.0),
            hunger=data.get("hunger", 0.0),
            attributes=data.get("attributes", {}),
        )
        agent.agent_type = data.get("agent_type", "citizen")
        agent.age = data.get("age", 0)
        agent.status = AgentStatus(data.get("status", "IDLE"))
        agent.alive = data.get("alive", True)
        agent.memory = AgentMemory.from_dict(data.get("memory", {}))
        agent._ticks_since_food = data.get("ticks_since_food", 0)
        return agent

    def __repr__(self) -> str:
        return (
            f"Citizen(id={self.agent_id[:8]}, name={self.name!r}, "
            f"pos=({self.x},{self.y}), job={self.job!r}, "
            f"happiness={self.happiness:.1f}, hunger={self.hunger:.1f})"
        )
