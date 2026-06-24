"""Corporation agent for the Neon City Simulation Engine."""

from __future__ import annotations

import random
import uuid
from typing import Dict, List, Optional

from src.agents.base import AgentStatus, AgentMemory, BaseAgent
from src.economy.currency import Wallet, CurrencyType
from src.events.bus import EventBus
from src.events.types import Event, EventType, EventSeverity
from src.engine.grid import Grid


class Corporation(BaseAgent):
    """A corporation agent that controls resources and influences markets."""

    def __init__(
        self,
        agent_id: Optional[str] = None,
        name: str = "Corporation",
        x: int = 0,
        y: int = 0,
        health: float = 100.0,
        energy: float = 100.0,
        wallet: Optional[Wallet] = None,
        market_share: float = 10.0,
        influence: float = 10.0,
        employees: Optional[List[str]] = None,
        tech_level: int = 5,
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
        self.agent_type = "corporation"
        self.market_share: float = max(0.0, min(100.0, market_share))
        self.influence: float = max(0.0, min(100.0, influence))
        self.employees: List[str] = employees or []
        self.tech_level: int = max(1, min(10, tech_level))

    def tick(self, world_state: dict, event_bus: EventBus) -> List[Event]:
        """Execute one simulation tick for a corporation."""
        events: List[Event] = []
        if not self.is_alive:
            return events

        self.age += 1
        self.memory.tick = world_state.get("tick", self.age)
        self.status = AgentStatus.IDLE  # Corps don't move

        # Generate income based on market_share and tech_level
        self._generate_income(world_state, event_bus, events)

        # 10% chance: issue market order to manipulate prices
        if random.random() < 0.10:
            self._issue_market_order(world_state, event_bus, events)

        # 5% chance: attempt corp takeover
        if random.random() < 0.05:
            self._attempt_takeover(world_state, event_bus, events)

        # 3% chance: hire nearby citizen
        if random.random() < 0.03:
            self._try_hire(world_state, event_bus, events)

        # If wealth > threshold: expand
        wealth = self.wallet.balance(CurrencyType.CREDITS)
        if wealth > 500.0:
            self._expand(world_state, event_bus, events)

        return events

    def _generate_income(
        self, world_state: dict, event_bus: EventBus, events: List[Event]
    ) -> None:
        """Generate income based on market share and tech level."""
        income = self.market_share * self.tech_level * 0.5
        if income > 0:
            self.wallet.credit(CurrencyType.CREDITS, income)

            # Pay employee salaries
            salary_per_employee = 2.0
            total_salaries = len(self.employees) * salary_per_employee
            if total_salaries > 0:
                self.wallet.debit(CurrencyType.CREDITS, total_salaries)

            event = Event(
                event_type=EventType.TRANSACTION,
                severity=EventSeverity.LOW,
                tick=world_state.get("tick", 0),
                source_id=self.agent_id,
                data={
                    "action": "income",
                    "amount": round(income, 2),
                    "salaries_paid": round(total_salaries, 2),
                    "employees": len(self.employees),
                },
            )
            event_bus.publish(event)
            events.append(event)

    def _issue_market_order(
        self, world_state: dict, event_bus: EventBus, events: List[Event]
    ) -> None:
        """Issue a market order to manipulate prices."""
        market = world_state.get("market")
        if market is None:
            return

        from src.economy.market import Order, OrderType

        items = ["food", "energy", "data_chip"]
        item = random.choice(items)
        order_type = random.choice([OrderType.BUY, OrderType.SELL])
        price = random.uniform(5.0, 50.0)
        quantity = random.randint(5, 20)

        order = Order(
            order_id=str(uuid.uuid4()),
            agent_id=self.agent_id,
            order_type=order_type,
            item=item,
            quantity=quantity,
            price=price,
            currency=CurrencyType.CREDITS,
        )
        market.place_order(order)

        event = Event(
            event_type=EventType.TRANSACTION,
            severity=EventSeverity.MEDIUM,
            tick=world_state.get("tick", 0),
            source_id=self.agent_id,
            data={
                "action": "market_order",
                "order_type": order_type.value,
                "item": item,
                "quantity": quantity,
                "price": round(price, 2),
            },
        )
        event_bus.publish(event)
        events.append(event)

    def _attempt_takeover(
        self, world_state: dict, event_bus: EventBus, events: List[Event]
    ) -> None:
        """Attempt to take over a weaker corporation."""
        agents = world_state.get("agents", {})
        targets = [
            a for a in agents.values()
            if a.agent_id != self.agent_id
            and isinstance(a, Corporation)
            and a.is_alive
            and a.market_share < self.market_share * 0.5
        ]
        if not targets:
            return

        target = random.choice(targets)

        # Takeover success based on relative market share and influence
        power_ratio = self.market_share / max(target.market_share, 1.0)
        success_chance = min(0.8, power_ratio * 0.1 + self.influence * 0.005)

        if random.random() < success_chance:
            # Takeover successful
            stolen_share = target.market_share * 0.3
            target.market_share -= stolen_share
            self.market_share = min(100.0, self.market_share + stolen_share)
            self.influence = min(100.0, self.influence + 5.0)

            # Transfer some employees
            hired = target.employees[:3]
            self.employees.extend(hired)
            for emp in hired:
                target.employees.remove(emp)

            event = Event(
                event_type=EventType.CORP_TAKEOVER,
                severity=EventSeverity.CRITICAL,
                tick=world_state.get("tick", 0),
                source_id=self.agent_id,
                target_id=target.agent_id,
                data={
                    "success": True,
                    "stolen_share": round(stolen_share, 2),
                    "hired_employees": len(hired),
                },
            )
            event_bus.publish(event)
            events.append(event)
        else:
            event = Event(
                event_type=EventType.CORP_TAKEOVER,
                severity=EventSeverity.HIGH,
                tick=world_state.get("tick", 0),
                source_id=self.agent_id,
                target_id=target.agent_id,
                data={"success": False},
            )
            event_bus.publish(event)
            events.append(event)

    def _try_hire(
        self, world_state: dict, event_bus: EventBus, events: List[Event]
    ) -> None:
        """Attempt to hire a nearby citizen."""
        agents = world_state.get("agents", {})
        candidates = [
            a for a in agents.values()
            if a.agent_id != self.agent_id
            and isinstance(a, "Citizen")
            and a.is_alive
            and a.agent_id not in self.employees
            and abs(a.x - self.x) <= 5
            and abs(a.y - self.y) <= 5
        ]
        if not candidates:
            return

        candidate = random.choice(candidates)
        self.employees.append(candidate.agent_id)

        event = Event(
            event_type=EventType.AGENT_INTERACTION,
            severity=EventSeverity.LOW,
            tick=world_state.get("tick", 0),
            source_id=self.agent_id,
            target_id=candidate.agent_id,
            data={"action": "hired", "employee": candidate.name},
        )
        event_bus.publish(event)
        events.append(event)

    def _expand(
        self, world_state: dict, event_bus: EventBus, events: List[Event]
    ) -> None:
        """Expand market share when wealthy."""
        expansion_cost = 200.0
        if self.wallet.balance(CurrencyType.CREDITS) >= expansion_cost:
            self.wallet.debit(CurrencyType.CREDITS, expansion_cost)
            self.market_share = min(100.0, self.market_share + 2.0)
            self.tech_level = min(10, self.tech_level + 1)

            event = Event(
                event_type=EventType.TRANSACTION,
                severity=EventSeverity.MEDIUM,
                tick=world_state.get("tick", 0),
                source_id=self.agent_id,
                data={
                    "action": "expand",
                    "cost": expansion_cost,
                    "new_market_share": round(self.market_share, 2),
                    "new_tech_level": self.tech_level,
                },
            )
            event_bus.publish(event)
            events.append(event)

    def to_dict(self) -> dict:
        """Serialize corporation to dictionary."""
        base = super().to_dict()
        base.update({
            "market_share": self.market_share,
            "influence": self.influence,
            "employees": list(self.employees),
            "tech_level": self.tech_level,
        })
        return base

    @classmethod
    def from_dict(cls, data: dict) -> Corporation:
        """Reconstruct a Corporation from a serialized dict."""
        agent = cls(
            agent_id=data["agent_id"],
            name=data["name"],
            x=data["x"],
            y=data["y"],
            health=data["health"],
            energy=data["energy"],
            wallet=Wallet.from_dict(data["wallet"]),
            market_share=data.get("market_share", 10.0),
            influence=data.get("influence", 10.0),
            employees=data.get("employees", []),
            tech_level=data.get("tech_level", 5),
            attributes=data.get("attributes", {}),
        )
        agent.agent_type = data.get("agent_type", "corporation")
        agent.age = data.get("age", 0)
        agent.status = AgentStatus(data.get("status", "IDLE"))
        agent.alive = data.get("alive", True)
        agent.memory = AgentMemory.from_dict(data.get("memory", {}))
        return agent

    def __repr__(self) -> str:
        return (
            f"Corporation(id={self.agent_id[:8]}, name={self.name!r}, "
            f"market_share={self.market_share:.1f}, employees={len(self.employees)}, "
            f"tech={self.tech_level})"
        )
