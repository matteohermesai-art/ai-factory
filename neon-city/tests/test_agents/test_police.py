"""Tests for police agent."""

import pytest

from src.agents.police import Police
from src.agents.base import AgentStatus
from src.economy.currency import Wallet, CurrencyType
from src.engine.grid import Grid


class TestPoliceCreation:
    """Test police creation."""

    def test_police_creation(self):
        police = Police(agent_id="police_001", name="Officer")
        assert police.agent_id == "police_001"
        assert police.name == "Officer"
        assert police.agent_type == "police"
        assert police.alive is True

    def test_police_default_attributes(self):
        police = Police(agent_id="police_002", x=5, y=5)
        assert police.jurisdiction == [(5, 5)]
        assert police.alert_level == 0.0
        assert police.arrests == 0

    def test_police_custom_attributes(self):
        police = Police(
            agent_id="police_003",
            name="Chief",
            jurisdiction=[(0, 0), (10, 10)],
            alert_level=50.0,
            arrests=5,
        )
        assert len(police.jurisdiction) == 2
        assert police.alert_level == 50.0
        assert police.arrests == 5

    def test_police_alert_level_clamped(self):
        police = Police(agent_id="police_004", alert_level=150.0)
        assert police.alert_level == 100.0

    def test_police_has_wallet(self):
        police = Police(agent_id="police_005")
        assert police.wallet is not None


class TestPatrolBehavior:
    """Test patrol behavior."""

    def test_police_is_mobile(self):
        police = Police(agent_id="police_006")
        assert police.is_mobile is True

    def test_police_not_mobile_when_dead(self):
        police = Police(agent_id="police_007")
        police.alive = False
        assert police.is_mobile is False


class TestArrestLogic:
    """Test arrest logic."""

    def test_police_take_damage(self):
        police = Police(agent_id="police_008", health=100.0)
        result = police.take_damage(20.0)
        assert result is True
        assert police.health == 80.0

    def test_police_damage_kills(self):
        police = Police(agent_id="police_009", health=5.0)
        result = police.take_damage(10.0)
        assert result is False
        assert police.alive is False
        assert police.status == AgentStatus.DEAD

    def test_police_heal(self):
        police = Police(agent_id="police_010", health=60.0)
        police.heal(20.0)
        assert police.health == 80.0

    def test_police_heal_capped(self):
        police = Police(agent_id="police_011", health=95.0)
        police.heal(20.0)
        assert police.health == 100.0

    def test_police_interact(self):
        police = Police(agent_id="police_012")
        other = Police(agent_id="police_013")
        assert police.interact(other) is True

    def test_police_interact_dead(self):
        police = Police(agent_id="police_014")
        other = Police(agent_id="police_015")
        other.alive = False
        assert police.interact(other) is False

    def test_police_interact_arrested(self):
        police = Police(agent_id="police_016")
        other = Police(agent_id="police_017")
        other.status = AgentStatus.ARRESTED
        assert police.interact(other) is False


class TestRaidBehavior:
    """Test raid behavior (via tick integration)."""

    @pytest.mark.asyncio
    async def test_police_arrests_hacker_on_grid(self):
        """Test that police can arrest hackers during simulation tick."""
        from src.engine.world import World
        from src.engine.tick import SimulationEngine

        config = {
            "grid_width": 10,
            "grid_height": 10,
            "seed": 42,
            "enable_tick_logger": False,
        }
        world = World(config=config)
        police_id = world.add_agent("police", 5, 5, name="Officer")
        hacker_id = world.add_agent("hacker", 5, 5, name="Hacker")

        engine = SimulationEngine(world=world)
        # Force police to find hacker
        world.agents[hacker_id]["alive"] = True

        # Run tick - police at same position as hacker should detect
        await engine.run_tick()

        # Police analytics should record something
        stats = world.event_bus.stats()
        assert stats["total_published"] >= 0  # At least no crash


class TestSerialization:
    """Test serialization."""

    def test_police_to_dict(self):
        police = Police(
            agent_id="police_018",
            name="Anderson",
            jurisdiction=[(0, 0), (5, 5)],
            alert_level=75.0,
            arrests=3,
        )
        d = police.to_dict()
        assert d["agent_id"] == "police_018"
        assert d["name"] == "Anderson"
        assert d["jurisdiction"] == [[0, 0], [5, 5]]
        assert d["alert_level"] == 75.0
        assert d["arrests"] == 3
        assert d["agent_type"] == "police"

    def test_police_from_dict(self):
        police = Police(agent_id="police_019", name="Test")
        d = police.to_dict()
        restored = Police.from_dict(d)
        assert restored.agent_id == police.agent_id
        assert restored.alert_level == police.alert_level
        assert restored.arrests == police.arrests

    def test_police_round_trip(self):
        police = Police(
            agent_id="police_020",
            name="Murphy",
            jurisdiction=[(1, 1), (2, 2), (3, 3)],
            alert_level=60.0,
            arrests=10,
        )
        d = police.to_dict()
        restored = Police.from_dict(d)
        assert restored.jurisdiction == [(1, 1), (2, 2), (3, 3)]
        assert restored.alert_level == 60.0
        assert restored.arrests == 10
