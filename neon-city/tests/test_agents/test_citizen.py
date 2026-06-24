"""Tests for citizen agent."""

import pytest

from src.agents.citizen import Citizen
from src.agents.base import AgentStatus
from src.events.bus import EventBus
from src.economy.currency import Wallet, CurrencyType
from src.engine.grid import Grid


class TestCitizenCreation:
    """Test citizen creation."""

    def test_citizen_creation(self):
        citizen = Citizen(agent_id="citizen_001", name="Alice")
        assert citizen.agent_id == "citizen_001"
        assert citizen.name == "Alice"
        assert citizen.agent_type == "citizen"
        assert citizen.alive is True

    def test_citizen_default_values(self):
        citizen = Citizen(agent_id="citizen_002")
        assert citizen.health == 100.0
        assert citizen.energy == 100.0
        assert citizen.job == "unemployed"
        assert citizen.happiness == 50.0
        assert citizen.hunger == 0.0

    def test_citizen_custom_values(self):
        citizen = Citizen(
            agent_id="citizen_003",
            name="Bob",
            health=80.0,
            energy=90.0,
            job="programmer",
            happiness=75.0,
            hunger=20.0,
        )
        assert citizen.health == 80.0
        assert citizen.energy == 90.0
        assert citizen.job == "programmer"
        assert citizen.happiness == 75.0
        assert citizen.hunger == 20.0

    def test_citizen_has_wallet(self):
        citizen = Citizen(agent_id="citizen_004")
        assert citizen.wallet is not None
        assert citizen.wallet.owner_id == "citizen_004"

    def test_citizen_position(self):
        citizen = Citizen(agent_id="citizen_005", x=5, y=10)
        assert citizen.x == 5
        assert citizen.y == 10
        assert citizen.position == (5, 10)


class TestCitizenTickBehavior:
    """Test citizen tick behavior (rest when tired, work when energized)."""

    def test_citizen_rests_when_tired(self):
        citizen = Citizen(agent_id="citizen_006", energy=10.0)
        assert citizen.energy < 20.0
        # Simulate the rest behavior
        citizen.rest()
        assert citizen.energy > 10.0
        assert citizen.energy == 20.0  # 10 + 10

    def test_citizen_does_not_exceed_max_energy(self):
        citizen = Citizen(agent_id="citizen_007", energy=95.0)
        citizen.rest()
        assert citizen.energy == 100.0

    def test_citizen_rest_only_when_alive(self):
        citizen = Citizen(agent_id="citizen_008", energy=10.0)
        citizen.alive = False
        citizen.rest()
        assert citizen.energy == 10.0  # Unchanged

    def test_citizen_take_damage(self):
        citizen = Citizen(agent_id="citizen_009", health=100.0)
        result = citizen.take_damage(30.0)
        assert result is True
        assert citizen.health == 70.0

    def test_citizen_damage_kills(self):
        citizen = Citizen(agent_id="citizen_010", health=10.0)
        result = citizen.take_damage(15.0)
        assert result is False
        assert citizen.health == 0.0
        assert citizen.alive is False
        assert citizen.status == AgentStatus.DEAD

    def test_citizen_heal(self):
        citizen = Citizen(agent_id="citizen_011", health=50.0)
        citizen.heal(20.0)
        assert citizen.health == 70.0

    def test_citizen_heal_capped_at_max(self):
        citizen = Citizen(agent_id="citizen_012", health=90.0)
        citizen.heal(20.0)
        assert citizen.health == 100.0

    def test_citizen_heal_only_when_alive(self):
        citizen = Citizen(agent_id="citizen_013", health=50.0)
        citizen.alive = False
        citizen.heal(20.0)
        assert citizen.health == 50.0  # Unchanged


class TestCitizenMovement:
    """Test citizen movement."""

    def test_citizen_is_alive_property(self):
        citizen = Citizen(agent_id="citizen_014")
        assert citizen.is_alive is True

    def test_citizen_is_alive_when_dead(self):
        citizen = Citizen(agent_id="citizen_015")
        citizen.alive = False
        assert citizen.is_alive is False

    def test_citizen_is_mobile(self):
        citizen = Citizen(agent_id="citizen_016")
        assert citizen.is_mobile is True

    def test_citizen_not_mobile_when_arrested(self):
        citizen = Citizen(agent_id="citizen_017")
        citizen.status = AgentStatus.ARRESTED
        assert citizen.is_mobile is False

    def test_citizen_not_mobile_when_dead(self):
        citizen = Citizen(agent_id="citizen_018")
        citizen.alive = False
        assert citizen.is_mobile is False


class TestCitizenSerialization:
    """Test citizen serialization."""

    def test_citizen_to_dict(self):
        citizen = Citizen(
            agent_id="citizen_019",
            name="TestCitizen",
            x=3,
            y=4,
            health=90.0,
            energy=80.0,
            job="engineer",
            happiness=60.0,
            hunger=30.0,
        )
        d = citizen.to_dict()
        assert d["agent_id"] == "citizen_019"
        assert d["name"] == "TestCitizen"
        assert d["x"] == 3
        assert d["y"] == 4
        assert d["health"] == 90.0
        assert d["energy"] == 80.0
        assert d["agent_type"] == "citizen"
        assert d["job"] == "engineer"
        assert d["happiness"] == 60.0
        assert d["hunger"] == 30.0

    def test_citizen_from_dict(self):
        citizen = Citizen(agent_id="citizen_020", name="Test")
        d = citizen.to_dict()
        restored = Citizen.from_dict(d)
        assert restored.agent_id == citizen.agent_id
        assert restored.name == citizen.name
        assert restored.agent_type == "citizen"

    def test_citizen_round_trip(self):
        citizen = Citizen(
            agent_id="citizen_021",
            name="Alice",
            x=7,
            y=8,
            health=85.0,
            energy=70.0,
            job="hacker",
            happiness=65.0,
            hunger=15.0,
        )
        d = citizen.to_dict()
        restored = Citizen.from_dict(d)
        assert restored.agent_id == citizen.agent_id
        assert restored.name == citizen.name
        assert restored.health == citizen.health
        assert restored.energy == citizen.energy
        assert restored.job == citizen.job
        assert restored.happiness == citizen.happiness
        assert restored.hunger == citizen.hunger
        assert restored.x == citizen.x
        assert restored.y == citizen.y
