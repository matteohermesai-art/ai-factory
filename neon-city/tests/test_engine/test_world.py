"""Tests for world module."""

import pytest

from src.engine.world import World
from src.engine.grid import CellType
from src.economy.currency import CurrencyType


class TestWorldCreation:
    """Test World creation."""

    def test_world_creation_with_config(self):
        config = {
            "grid_width": 20,
            "grid_height": 20,
            "seed": 123,
            "enable_tick_logger": False,
        }
        world = World(config=config)
        assert world.grid.width == 20
        assert world.grid.height == 20
        assert world._seed == 123

    def test_world_creation_default_config(self):
        world = World(config={})
        assert world.grid.width == 50
        assert world.grid.height == 50
        assert world._seed == 42

    def test_world_has_event_bus(self):
        world = World(config={})
        assert world.event_bus is not None

    def test_world_has_market(self):
        world = World(config={})
        assert world.market is not None

    def test_world_has_analytics(self):
        world = World(config={})
        assert world.tick_analytics is not None
        assert world.sim_analytics is not None

    def test_world_has_transaction_log(self):
        world = World(config={})
        assert world.transaction_log is not None

    def test_world_initial_tick_is_zero(self):
        world = World(config={})
        assert world.tick_number == 0

    def test_world_running_initially_false(self):
        world = World(config={})
        assert world.running is False


class TestAgentManagement:
    """Test add_agent / remove_agent."""

    def test_add_agent(self, world):
        agent_id = world.add_agent("citizen", 5, 5, name="TestCitizen")
        assert agent_id is not None
        assert agent_id in world.agents
        assert world.agents[agent_id]["name"] == "TestCitizen"
        assert world.agents[agent_id]["x"] == 5
        assert world.agents[agent_id]["y"] == 5

    def test_add_agent_creates_wallet(self, world):
        agent_id = world.add_agent("citizen", 5, 5)
        assert agent_id in world.wallets

    def test_add_agent_places_on_grid(self, world):
        agent_id = world.add_agent("citizen", 5, 5)
        assert agent_id in world.grid.get_agents_at(5, 5)

    def test_add_hacker_agent(self, world):
        agent_id = world.add_agent("hacker", 3, 3, name="TestHacker")
        assert world.agents[agent_id]["agent_type"] == "hacker"

    def test_add_corporation_agent(self, world):
        agent_id = world.add_agent("corporation", 4, 4, name="MegaCorp")
        assert world.agents[agent_id]["agent_type"] == "corporation"

    def test_add_police_agent(self, world):
        agent_id = world.add_agent("police", 2, 2, name="Officer")
        assert world.agents[agent_id]["agent_type"] == "police"

    def test_remove_agent(self, world):
        agent_id = world.add_agent("citizen", 5, 5)
        result = world.remove_agent(agent_id)
        assert result is True
        assert agent_id not in world.agents

    def test_removes_agent_from_grid(self, world):
        agent_id = world.add_agent("citizen", 5, 5)
        world.remove_agent(agent_id)
        assert agent_id not in world.grid.get_agents_at(5, 5)

    def test_remove_agent_removes_wallet(self, world):
        agent_id = world.add_agent("citizen", 5, 5)
        world.remove_agent(agent_id)
        assert agent_id not in world.wallets

    def test_remove_nonexistent_agent(self, world):
        result = world.remove_agent("nonexistent")
        assert result is False

    def test_get_agent(self, world):
        agent_id = world.add_agent("citizen", 5, 5, name="Test")
        agent = world.get_agent(agent_id)
        assert agent is not None
        assert agent["name"] == "Test"

    def test_get_agent_not_found(self, world):
        assert world.get_agent("nonexistent") is None

    def test_get_agents_by_type(self, world):
        world.add_agent("citizen", 5, 5)
        world.add_agent("citizen", 3, 3)
        world.add_agent("hacker", 1, 1)
        citizens = world.get_agents_by_type("citizen")
        assert len(citizens) == 2
        hackers = world.get_agents_by_type("hacker")
        assert len(hackers) == 1

    def test_get_agents_by_type_empty(self, world):
        hackers = world.get_agents_by_type("hacker")
        assert len(hackers) == 0

    def test_get_all_agents(self, world):
        world.add_agent("citizen", 5, 5)
        world.add_agent("hacker", 1, 1)
        all_agents = world.get_all_agents()
        assert len(all_agents) == 2


class TestStateSerialization:
    """Test get_state serialization."""

    def test_get_state(self, world):
        state = world.get_state()
        assert "config" in state
        assert "seed" in state
        assert "tick_number" in state
        assert "running" in state
        assert "grid" in state
        assert "agents" in state
        assert "wallets" in state
        assert "market" in state

    def test_get_state_with_agents(self, world):
        world.add_agent("citizen", 5, 5, name="Test")
        state = world.get_state()
        assert len(state["agents"]) == 1
        assert len(state["wallets"]) == 1


class TestFromState:
    """Test from_state restoration."""

    def test_from_state(self, world):
        world.add_agent("citizen", 5, 5, name="Test")
        state = world.get_state()
        # Restore into a new world
        new_world = World(config={})
        new_world.from_state(state)
        assert new_world.tick_number == world.tick_number
        assert new_world._seed == world._seed
        assert len(new_world.agents) == 1

    def test_from_state_preserves_agent_data(self, world):
        world.add_agent("citizen", 5, 5, name="TestCitizen")
        state = world.get_state()
        new_world = World(config={})
        new_world.from_state(state)
        agent = list(new_world.agents.values())[0]
        assert agent["name"] == "TestCitizen"
        assert agent["x"] == 5
        assert agent["y"] == 5

    def test_from_state_preserves_wallets(self, world):
        agent_id = world.add_agent("citizen", 5, 5)
        world.wallets[agent_id].credit(CurrencyType.CREDITS, 500.0)
        state = world.get_state()
        new_world = World(config={})
        new_world.from_state(state)
        assert agent_id in new_world.wallets
        assert new_world.wallets[agent_id].balance(CurrencyType.CREDITS) == 500.0


class TestTickCounter:
    """Test tick counter."""

    def test_get_tick(self, world):
        assert world.get_tick() == 0

    def test_tick_number_increments(self, world):
        world.tick_number = 5
        assert world.get_tick() == 5


class TestSeedSetting:
    """Test seed setting."""

    def test_set_seed(self, world):
        world.set_seed(99)
        assert world._seed == 99

    def test_set_seed_affects_rng(self, world):
        world.set_seed(99)
        # After setting seed, RNG should be deterministic
        val1 = world._rng.random()
        world.set_seed(99)
        val2 = world._rng.random()
        assert val1 == val2
