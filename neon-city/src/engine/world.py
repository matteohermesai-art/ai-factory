"""World simulation module for the Neon City Simulation Engine.

The World class is the top-level container for all simulation state:
grid, agents, economy, events, and analytics.
"""

from __future__ import annotations

import random
import uuid
from typing import Any, Optional

from ..economy.currency import CurrencyType, Wallet
from ..economy.market import Market
from ..economy.transactions import TransactionLog
from ..events.bus import EventBus
from ..logging.analytics import SimulationAnalytics, TickAnalytics
from ..logging.structured import TickLogger, get_logger
from .grid import Grid

logger = get_logger("neon_city.world")


class World:
    """Top-level simulation state container."""

    def __init__(self, config: dict) -> None:
        """
        Initialize the world from a configuration dictionary.

        Expected config keys:
            - grid_width (int): Width of the city grid (default 50).
            - grid_height (int): Height of the city grid (default 50).
            - seed (int): Random seed for determinism (default 42).
            - log_level (str): Logging level (default "INFO").
            - enable_tick_logger (bool): Whether to use TickLogger (default True).
        """
        self._config: dict = dict(config)
        self._seed: int = config.get("seed", 42)
        self._rng: random.Random = random.Random(self._seed)

        # Grid
        grid_width = int(config.get("grid_width", 50))
        grid_height = int(config.get("grid_height", 50))
        self.grid: Grid = Grid(grid_width, grid_height, seed=self._seed)

        # Agents: agent_id -> agent state dict
        self.agents: dict[str, dict[str, Any]] = {}

        # Simulation tick
        self.tick_number: int = 0

        # Event system
        self.event_bus: EventBus = EventBus()

        # Economy
        self.market: Market = Market()
        self.transaction_log: TransactionLog = TransactionLog()
        self.wallets: dict[str, Wallet] = {}

        # Analytics
        self.tick_analytics: TickAnalytics = TickAnalytics()
        self.sim_analytics: SimulationAnalytics = SimulationAnalytics()

        # Logging
        enable_tick_logger = config.get("enable_tick_logger", True)
        self.tick_logger: Optional[TickLogger] = (
            TickLogger(self.tick_number) if enable_tick_logger else None
        )

        # State
        self.running: bool = False

    # ------------------------------------------------------------------
    # Agent management
    # ------------------------------------------------------------------

    def add_agent(
        self,
        agent_type: str,
        x: int,
        y: int,
        name: str | None = None,
        **kwargs,
    ) -> str:
        """
        Create a new agent and add it to the world.

        Args:
            agent_type: One of 'citizen', 'hacker', 'corporation', 'police'.
            x: Grid x-coordinate.
            y: Grid y-coordinate.
            name: Optional display name.
            **kwargs: Additional agent state fields.

        Returns:
            The new agent's unique ID.
        """
        agent_id = f"{agent_type}_{uuid.uuid4().hex[:8]}"
        display_name = name or agent_id

        agent_state: dict[str, Any] = {
            "agent_id": agent_id,
            "agent_type": agent_type,
            "name": display_name,
            "x": x,
            "y": y,
            "age": 0,
            "health": 100.0,
            "energy": 100.0,
            "alive": True,
            "mobile": True,
            "reputation": 50.0,
            "data_chips": 0,
            "inventory": {},
            **kwargs,
        }

        self.agents[agent_id] = agent_state
        self.grid.place_agent(agent_id, x, y)

        # Create a wallet for the agent
        self.wallets[agent_id] = Wallet(owner_id=agent_id)

        if self.tick_logger:
            self.tick_logger.log_agent_action(agent_id, "spawn", position=(x, y))

        return agent_id

    def remove_agent(self, agent_id: str) -> bool:
        """
        Remove an agent from the world.

        Returns True if the agent was found and removed.
        """
        agent = self.agents.get(agent_id)
        if agent is None:
            return False

        x, y = agent.get("x", 0), agent.get("y", 0)
        self.grid.remove_agent(agent_id, x, y)
        del self.agents[agent_id]

        if agent_id in self.wallets:
            del self.wallets[agent_id]

        if self.tick_logger:
            self.tick_logger.log_agent_action(agent_id, "removed")

        return True

    def get_agent(self, agent_id: str) -> dict | None:
        """Return the agent state dict, or None if not found."""
        return self.agents.get(agent_id)

    def get_agents_by_type(self, agent_type: str) -> list[dict]:
        """Return all agents of a given type."""
        return [a for a in self.agents.values() if a.get("agent_type") == agent_type]

    def get_all_agents(self) -> list[dict]:
        """Return all agents."""
        return list(self.agents.values())

    # ------------------------------------------------------------------
    # State serialization
    # ------------------------------------------------------------------

    def get_state(self) -> dict:
        """
        Return a fully serializable snapshot of the world state.
        """
        return {
            "config": dict(self._config),
            "seed": self._seed,
            "tick_number": self.tick_number,
            "running": self.running,
            "grid": self.grid.to_dict(),
            "agents": {
                aid: {
                    **agent,
                    "inventory": dict(agent.get("inventory", {})),
                }
                for aid, agent in self.agents.items()
            },
            "wallets": {wid: w.to_dict() for wid, w in self.wallets.items()},
            "market": self.market.to_dict(),
            "transaction_log": self.transaction_log.to_dict(),
            "event_bus_stats": self.event_bus.stats(),
        }

    def from_state(self, state: dict) -> None:
        """
        Restore the world from a previously saved state snapshot.

        Replaces all current state with the saved state.
        """
        self._config = dict(state.get("config", {}))
        self._seed = int(state.get("seed", 42))
        self._rng = random.Random(self._seed)
        self.tick_number = int(state.get("tick_number", 0))
        self.running = bool(state.get("running", False))

        self.grid = Grid.from_dict(state["grid"])

        self.agents = {}
        for aid, agent_data in state.get("agents", {}).items():
            agent = dict(agent_data)
            agent["inventory"] = dict(agent.get("inventory", {}))
            self.agents[aid] = agent

        self.wallets = {}
        for wid, wdata in state.get("wallets", {}).items():
            self.wallets[wid] = Wallet.from_dict(wdata)

        # Reconstruct market from dict
        self.market = Market()
        market_data = state.get("market", {})
        # Orders are not fully restored (Market doesn't have from_dict),
        # but the structure is preserved for future extension.

        self.transaction_log = TransactionLog()
        tx_data = state.get("transaction_log", {})
        # Transactions are not fully restored (TransactionLog doesn't have from_dict),
        # but the structure is preserved for future extension.

        self.tick_analytics = TickAnalytics()
        self.sim_analytics = SimulationAnalytics()

        self.event_bus = EventBus()

        enable_tick_logger = self._config.get("enable_tick_logger", True)
        self.tick_logger = (
            TickLogger(self.tick_number) if enable_tick_logger else None
        )

    # ------------------------------------------------------------------
    # Tick & seed
    # ------------------------------------------------------------------

    def get_tick(self) -> int:
        """Return the current tick number."""
        return self.tick_number

    def set_seed(self, seed: int) -> None:
        """Set the random seed for deterministic behavior."""
        self._seed = seed
        self._rng = random.Random(seed)
