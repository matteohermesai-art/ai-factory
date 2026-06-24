"""Simulation tick engine for the Neon City Simulation Engine.

Provides TickResult dataclass and SimulationEngine class that runs the
core simulation loop: aging, event generation, agent actions, market matching.
"""

from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional

from ..economy.currency import CurrencyType
from ..economy.market import AVAILABLE_ITEMS, Order, OrderType
from ..events.generators import CompositeGenerator
from ..events.types import Event, EventSeverity, EventType
from ..logging.structured import get_logger

from .world import World

logger = get_logger("neon_city.tick_engine")


@dataclass
class TickResult:
    """Result of a single simulation tick."""
    tick_number: int
    events: list[Event] = field(default_factory=list)
    analytics: dict = field(default_factory=dict)
    agent_actions: int = 0
    duration_ms: float = 0.0

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "tick_number": self.tick_number,
            "events": [e.to_dict() for e in self.events],
            "analytics": self.analytics,
            "agent_actions": self.agent_actions,
            "duration_ms": self.duration_ms,
        }


class SimulationEngine:
    """Core simulation engine that drives the tick loop."""

    def __init__(self, world: World, event_bus: Optional[Any] = None) -> None:
        self._world: World = world
        self._event_bus = event_bus or world.event_bus
        self._running: bool = False
        self._paused: bool = False
        self._composite_generator: CompositeGenerator = CompositeGenerator()
        self._rng = world._rng

    @property
    def composite_generator(self) -> CompositeGenerator:
        """Access the composite event generator for adding sub-generators."""
        return self._composite_generator

    async def run_tick(self) -> TickResult:
        """Execute a single simulation tick."""
        start_time = time.monotonic()
        tick = self._world.tick_number
        agent_actions = 0

        # 1. Age all agents
        for agent in self._world.get_all_agents():
            if agent.get("alive", True):
                agent["age"] = agent.get("age", 0) + 1
                agent_actions += 1

        # 2. Reset tick analytics
        self._world.tick_analytics.reset()

        # 3. Generate events
        world_state = self._build_world_state()
        events = self._composite_generator.generate(tick, world_state)

        # 4. Process events on event bus
        for event in events:
            self._event_bus.publish(event)
            self._world.tick_analytics.record_event(event.event_type.value)

        # 5. Agent actions
        for agent in self._world.get_all_agents():
            if agent.get("alive", True):
                actions = self._process_agent_action(agent)
                agent_actions += actions

        # 6. Process market matching
        for item in AVAILABLE_ITEMS:
            matched = self._world.market.match_orders(item)
            for buy_order, sell_order in matched:
                trade_price = (buy_order.price + sell_order.price) / 2.0
                trade_qty = 1  # match_orders already decremented quantities
                self._execute_trade(buy_order, sell_order, trade_price, trade_qty)

        # 7. Finalize analytics
        analytics = self._world.tick_analytics.finalize()
        self._world.sim_analytics.add_tick(tick, analytics)

        # 8. Log tick summary
        if self._world.tick_logger:
            self._world.tick_logger.log_event(
                "tick_complete",
                tick_number=tick,
                event_count=len(events),
                agent_actions=agent_actions,
            )

        # 9. Increment tick counter
        self._world.tick_number += 1
        if self._world.tick_logger:
            self._world.tick_logger = type(self._world.tick_logger)(
                self._world.tick_number
            )

        # 10. Build result
        duration_ms = (time.monotonic() - start_time) * 1000.0
        result = TickResult(
            tick_number=tick,
            events=events,
            analytics=analytics,
            agent_actions=agent_actions,
            duration_ms=round(duration_ms, 3),
        )

        return result

    async def run(self, num_ticks: int | None = None) -> None:
        """Run the simulation continuously or for a fixed number of ticks."""
        self._running = True
        self._paused = False
        tick_count = 0

        logger.info("simulation_started", num_ticks=num_ticks)

        while self._running:
            if num_ticks is not None and tick_count >= num_ticks:
                break

            while self._paused:
                await asyncio.sleep(0.05)
                if not self._running:
                    return

            await self.run_tick()
            tick_count += 1
            await asyncio.sleep(0)

        logger.info("simulation_stopped", ticks_executed=tick_count)

    def stop(self) -> None:
        """Stop the simulation loop."""
        self._running = False
        logger.info("simulation_stop_requested")

    async def pause(self) -> None:
        """Pause the simulation loop."""
        self._paused = True
        logger.info("simulation_paused", tick=self._world.tick_number)

    async def resume(self) -> None:
        """Resume a paused simulation loop."""
        self._paused = False
        logger.info("simulation_resumed", tick=self._world.tick_number)

    # ------------------------------------------------------------------
    # World state for event generators
    # ------------------------------------------------------------------

    def _build_world_state(self) -> dict:
        """Build a world_state dict for event generators."""
        agents_state = {}
        for aid, agent in self._world.agents.items():
            agents_state[aid] = {
                "age": agent.get("age", 0),
                "health": agent.get("health", 100.0),
                "position": (agent.get("x", 0), agent.get("y", 0)),
                "mobile": agent.get("mobile", True),
                "agent_type": agent.get("agent_type", "citizen"),
            }

        corps = {}
        for aid, agent in self._world.agents.items():
            if agent.get("agent_type") == "corporation":
                wallet = self._world.wallets.get(aid)
                corps[aid] = {
                    "wealth": wallet.balance(CurrencyType.CREDITS) if wallet else 0.0,
                }

        return {
            "agents": agents_state,
            "population": len(self._world.agents),
            "grid_size": (self._world.grid.width, self._world.grid.height),
            "price_volatility": 0.05,  # placeholder
            "corps": corps,
        }

    # ------------------------------------------------------------------
    # Trade execution
    # ------------------------------------------------------------------

    def _execute_trade(
        self, buy_order: Order, sell_order: Order, price: float, quantity: int
    ) -> None:
        """Execute a matched trade between buyer and seller."""
        buyer_wallet = self._world.wallets.get(buy_order.agent_id)
        seller_wallet = self._world.wallets.get(sell_order.agent_id)

        if buyer_wallet and seller_wallet:
            total_cost = price * quantity
            if buyer_wallet.transfer_to(seller_wallet, sell_order.currency, total_cost):
                self._world.tick_analytics.record_transaction(
                    total_cost, sell_order.currency.value
                )

    # ------------------------------------------------------------------
    # Agent action delegation
    # ------------------------------------------------------------------

    def _process_agent_action(self, agent: dict[str, Any]) -> int:
        """Route an agent to the correct behavior based on agent_type."""
        agent_type = agent.get("agent_type", "citizen")

        if agent_type == "citizen":
            return self._action_citizen(agent)
        elif agent_type == "hacker":
            return self._action_hacker(agent)
        elif agent_type == "corporation":
            return self._action_corporation(agent)
        elif agent_type == "police":
            return self._action_police(agent)
        else:
            return self._action_citizen(agent)

    def _action_citizen(self, agent: dict[str, Any]) -> int:
        """Citizen behavior: move randomly, buy food/energy, rest to recover energy."""
        actions = 0
        x, y = agent.get("x", 0), agent.get("y", 0)
        energy = agent.get("energy", 100.0)
        wallet = self._world.wallets.get(agent["agent_id"])

        # Rest if low energy
        if energy < 20.0:
            agent["energy"] = min(100.0, energy + 10.0)
            self._world.tick_analytics.record_agent_action("citizen", "rest")
            return 1

        # Try to buy food
        if wallet and wallet.balance(CurrencyType.CREDITS) > 5.0:
            price = 5.0
            if wallet.debit(CurrencyType.CREDITS, price):
                agent["energy"] = min(100.0, energy + 15.0)
                inv = dict(agent.get("inventory", {}))
                inv["food"] = inv.get("food", 0) + 1
                agent["inventory"] = inv
                self._world.tick_analytics.record_agent_action("citizen", "buy_food")
                self._world.tick_analytics.record_transaction(price, "credits")
                actions += 1

        # Move randomly
        if self._rng.random() < 0.4:
            dx = self._rng.randint(-1, 1)
            dy = self._rng.randint(-1, 1)
            nx, ny = x + dx, y + dy
            if self._world.grid.get_walkable(nx, ny):
                if self._world.grid.move_agent(agent["agent_id"], x, y, nx, ny):
                    agent["x"] = nx
                    agent["y"] = ny
                    agent["energy"] = max(0.0, agent.get("energy", 100.0) - 1.0)
                    self._world.tick_analytics.record_agent_action("citizen", "move")
                    actions += 1

        return actions

    def _action_hacker(self, agent: dict[str, Any]) -> int:
        """Hacker behavior: cyber attacks, trade data chips, move toward data centers."""
        actions = 0
        x, y = agent.get("x", 0), agent.get("y", 0)
        wallet = self._world.wallets.get(agent["agent_id"])

        # Attempt cyber attack (30% chance)
        if self._rng.random() < 0.3:
            target_agents = [
                a for a in self._world.get_all_agents()
                if a["agent_id"] != agent["agent_id"] and a.get("alive", True)
            ]
            if target_agents:
                target = self._rng.choice(target_agents)
                success = self._rng.random() < 0.4
                steal_amount = 0.0
                if success:
                    target_wallet = self._world.wallets.get(target["agent_id"])
                    if target_wallet and target_wallet.balance(CurrencyType.CREDITS) > 10:
                        steal_amount = min(
                            50.0, target_wallet.balance(CurrencyType.CREDITS) * 0.1
                        )
                        target_wallet.transfer_to(
                            wallet, CurrencyType.CREDITS, steal_amount
                        )
                        agent["data_chips"] = agent.get("data_chips", 0) + 1
                        self._world.tick_analytics.record_transaction(
                            steal_amount, "credits"
                        )
                    event = Event(
                        event_type=EventType.CYBER_ATTACK,
                        severity=EventSeverity.HIGH,
                        tick=self._world.tick_number,
                        source_id=agent["agent_id"],
                        target_id=target["agent_id"],
                        data={"success": True, "amount": steal_amount},
                    )
                    self._event_bus.publish(event)
                else:
                    agent["reputation"] = max(
                        0.0, agent.get("reputation", 50.0) - 5.0
                    )
                self._world.tick_analytics.record_agent_action("hacker", "cyber_attack")
                actions += 1

        # Sell data chips at market
        if agent.get("data_chips", 0) > 0 and wallet:
            order = Order(
                order_id=f"order_{uuid.uuid4().hex[:8]}",
                agent_id=agent["agent_id"],
                order_type=OrderType.SELL,
                item="data_chip",
                quantity=agent["data_chips"],
                price=25.0,
                currency=CurrencyType.CREDITS,
                timestamp=float(self._world.tick_number),
            )
            self._world.market.place_order(order)
            agent["data_chips"] = 0
            self._world.tick_analytics.record_agent_action("hacker", "sell_data_chip")
            actions += 1

        # Move toward data center
        data_centers = [
            (cx, cy)
            for cx in range(self._world.grid.width)
            for cy in range(self._world.grid.height)
            if self._world.grid.get_cell(cx, cy).cell_type.value == "DATA_CENTER"
        ]
        if data_centers:
            nearest = min(data_centers, key=lambda p: abs(p[0] - x) + abs(p[1] - y))
            path = self._world.grid.find_path(x, y, nearest[0], nearest[1])
            if len(path) > 1:
                next_x, next_y = path[1]
                if self._world.grid.move_agent(agent["agent_id"], x, y, next_x, next_y):
                    agent["x"] = next_x
                    agent["y"] = next_y
                    self._world.tick_analytics.record_agent_action("hacker", "move")
                    actions += 1
            elif self._rng.random() < 0.3:
                dx = self._rng.randint(-1, 1)
                dy = self._rng.randint(-1, 1)
                nx, ny = x + dx, y + dy
                if self._world.grid.get_walkable(nx, ny):
                    if self._world.grid.move_agent(agent["agent_id"], x, y, nx, ny):
                        agent["x"] = nx
                        agent["y"] = ny
                        self._world.tick_analytics.record_agent_action("hacker", "move")
                        actions += 1

        return actions

    def _action_corporation(self, agent: dict[str, Any]) -> int:
        """Corporation behavior: generate wealth, acquire agents, issue orders."""
        actions = 0
        wallet = self._world.wallets.get(agent["agent_id"])

        # Generate wealth passively
        if wallet:
            income = 100.0 + self._rng.uniform(0, 50.0)
            wallet.credit(CurrencyType.CREDITS, income)
            self._world.tick_analytics.record_agent_action("corporation", "generate_wealth")
            self._world.tick_analytics.record_transaction(income, "credits")
            actions += 1

        # Try to acquire nearby agents (20% chance)
        if self._rng.random() < 0.2:
            x, y = agent.get("x", 0), agent.get("y", 0)
            nearby = []
            for ddx in range(-3, 4):
                for ddy in range(-3, 4):
                    nearby.extend(self._world.grid.get_agents_at(x + ddx, y + ddy))
            targets = [
                aid
                for aid in nearby
                if aid != agent["agent_id"]
                and aid in self._world.agents
                and self._world.agents[aid].get("agent_type") in ("citizen", "hacker")
            ]
            if targets:
                target_id = self._rng.choice(targets)
                event = Event(
                    event_type=EventType.CORP_TAKEOVER,
                    severity=EventSeverity.HIGH,
                    tick=self._world.tick_number,
                    source_id=agent["agent_id"],
                    target_id=target_id,
                    data={"takeover_type": "acquisition"},
                )
                self._event_bus.publish(event)
                self._world.tick_analytics.record_agent_action("corporation", "acquire")
                actions += 1

        return actions

    def _action_police(self, agent: dict[str, Any]) -> int:
        """Police behavior: patrol, raid black markets, arrest hackers."""
        actions = 0
        x, y = agent.get("x", 0), agent.get("y", 0)

        # Check for hackers at current position
        local_agents = self._world.grid.get_agents_at(x, y)
        hackers_here = [
            aid
            for aid in local_agents
            if aid in self._world.agents
            and self._world.agents[aid].get("agent_type") == "hacker"
        ]

        if hackers_here:
            # Arrest a hacker
            target_id = self._rng.choice(hackers_here)
            target_agent = self._world.agents[target_id]
            target_agent["alive"] = False
            self._world.grid.remove_agent(target_id, target_agent.get("x", 0), target_agent.get("y", 0))

            event = Event(
                event_type=EventType.POLICE_RAID,
                severity=EventSeverity.HIGH,
                tick=self._world.tick_number,
                source_id=agent["agent_id"],
                target_id=target_id,
                data={"action": "arrest"},
            )
            self._event_bus.publish(event)
            self._world.tick_analytics.record_agent_action("police", "arrest")
            actions += 1
            return actions

        # Move toward black market
        black_markets = [
            (cx, cy)
            for cx in range(self._world.grid.width)
            for cy in range(self._world.grid.height)
            if self._world.grid.get_cell(cx, cy).cell_type.value == "BLACK_MARKET"
        ]
        if black_markets and self._rng.random() < 0.5:
            nearest = min(
                black_markets, key=lambda p: abs(p[0] - x) + abs(p[1] - y)
            )
            path = self._world.grid.find_path(x, y, nearest[0], nearest[1])
            if len(path) > 1:
                next_x, next_y = path[1]
                if self._world.grid.move_agent(agent["agent_id"], x, y, next_x, next_y):
                    agent["x"] = next_x
                    agent["y"] = next_y
                    self._world.tick_analytics.record_agent_action("police", "patrol")
                    actions += 1
                return actions

        # Random patrol
        if self._rng.random() < 0.3:
            dx = self._rng.randint(-1, 1)
            dy = self._rng.randint(-1, 1)
            nx, ny = x + dx, y + dy
            if self._world.grid.get_walkable(nx, ny):
                if self._world.grid.move_agent(agent["agent_id"], x, y, nx, ny):
                    agent["x"] = nx
                    agent["y"] = ny
                    self._world.tick_analytics.record_agent_action("police", "patrol")
                    actions += 1

        return actions
