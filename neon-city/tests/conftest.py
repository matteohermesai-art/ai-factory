"""Test configuration and shared fixtures for Neon City Simulation Engine."""

import pytest
import pytest_asyncio

from src.engine.grid import Grid
from src.engine.world import World
from src.engine.tick import SimulationEngine
from src.economy.market import Market
from src.economy.currency import Wallet, CurrencyType
from src.economy.transactions import TransactionLog
from src.events.bus import EventBus
from src.logging.analytics import TickAnalytics, SimulationAnalytics


@pytest.fixture
def event_bus():
    """Fresh EventBus instance."""
    return EventBus()


@pytest.fixture
def market():
    """Fresh Market instance."""
    return Market()


@pytest.fixture
def wallet():
    """Wallet with 1000 CREDITS."""
    w = Wallet(owner_id="test_wallet")
    w.credit(CurrencyType.CREDITS, 1000.0)
    return w


@pytest.fixture
def grid():
    """10x10 Grid with seed=42."""
    return Grid(width=10, height=10, seed=42)


@pytest.fixture
def world():
    """World with small config (10x10, seed=42)."""
    config = {
        "grid_width": 10,
        "grid_height": 10,
        "seed": 42,
        "enable_tick_logger": False,
    }
    return World(config=config)


@pytest.fixture
def engine(world):
    """SimulationEngine with world."""
    return SimulationEngine(world=world)


@pytest.fixture
def tick_analytics():
    """Fresh TickAnalytics instance."""
    return TickAnalytics()


@pytest.fixture
def sim_analytics():
    """Fresh SimulationAnalytics instance."""
    return SimulationAnalytics()


@pytest.fixture
def transaction_log():
    """Fresh TransactionLog instance."""
    return TransactionLog()


@pytest.fixture
def anyio_backend():
    """Set anyio backend to asyncio."""
    return "asyncio"
