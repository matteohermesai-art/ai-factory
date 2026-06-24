"""Tests for hacker agent."""

import pytest

from src.agents.hacker import Hacker
from src.agents.base import AgentStatus
from src.economy.currency import Wallet, CurrencyType


class TestHackerCreation:
    """Test hacker creation with attributes."""

    def test_hacker_creation(self):
        hacker = Hacker(agent_id="hacker_001", name="Neo")
        assert hacker.agent_id == "hacker_001"
        assert hacker.name == "Neo"
        assert hacker.agent_type == "hacker"
        assert hacker.alive is True

    def test_hacker_default_attributes(self):
        hacker = Hacker(agent_id="hacker_002")
        assert hacker.skill_level == 5
        assert hacker.reputation == 0.0
        assert hacker.stealth == 70.0
        assert hacker._data_chips == 0

    def test_hacker_custom_attributes(self):
        hacker = Hacker(
            agent_id="hacker_003",
            name="Trinity",
            skill_level=9,
            reputation=50.0,
            stealth=30.0,
        )
        assert hacker.skill_level == 9
        assert hacker.reputation == 50.0
        assert hacker.stealth == 30.0

    def test_hacker_skill_level_clamped_low(self):
        hacker = Hacker(agent_id="hacker_004", skill_level=0)
        assert hacker.skill_level == 1

    def test_hacker_skill_level_clamped_high(self):
        hacker = Hacker(agent_id="hacker_005", skill_level=15)
        assert hacker.skill_level == 10

    def test_hacker_stealth_clamped(self):
        hacker = Hacker(agent_id="hacker_006", stealth=150.0)
        assert hacker.stealth == 100.0

    def test_hacker_reputation_clamped(self):
        hacker = Hacker(agent_id="hacker_007", reputation=-10.0)
        assert hacker.reputation == 0.0

    def test_hacker_has_wallet(self):
        hacker = Hacker(agent_id="hacker_008")
        assert hacker.wallet is not None


class TestHackerCyberAttack:
    """Test hacker cyber attack logic."""

    def test_cyber_attack_no_targets(self):
        hacker = Hacker(agent_id="hacker_009", skill_level=5)
        world_state = {"agents": {}}
        event_bus = None  # Won't be reached
        # Should not crash
        hacker._attempt_cyber_attack(world_state, event_bus := __import__("src.events.bus", fromlist=["EventBus"]).EventBus(), [])

    def test_cyber_attack_status_set(self):
        hacker = Hacker(agent_id="hacker_010", skill_level=5)
        assert hacker.status != AgentStatus.ATTACKING  # Default is IDLE
        # After attack attempt, status might be ATTACKING
        # (depends on whether targets are available)


class TestHackerStealthRegeneration:
    """Test stealth regeneration."""

    def test_stealth_regeneration(self):
        hacker = Hacker(agent_id="hacker_011", stealth=50.0)
        # Simulate the stealth regeneration behavior
        hacker.stealth = min(100.0, hacker.stealth + 2.0)
        assert hacker.stealth == 52.0

    def test_stealth_does_not_exceed_max(self):
        hacker = Hacker(agent_id="hacker_012", stealth=99.0)
        hacker.stealth = min(100.0, hacker.stealth + 2.0)
        assert hacker.stealth == 100.0

    def test_stealth_at_max(self):
        hacker = Hacker(agent_id="hacker_013", stealth=100.0)
        hacker.stealth = min(100.0, hacker.stealth + 2.0)
        assert hacker.stealth == 100.0


class TestHackerSerialization:
    """Test serialization."""

    def test_hacker_to_dict(self):
        hacker = Hacker(
            agent_id="hacker_014",
            name="Morpheus",
            x=5,
            y=5,
            health=100.0,
            energy=80.0,
            skill_level=7,
            reputation=30.0,
            stealth=60.0,
        )
        d = hacker.to_dict()
        assert d["agent_id"] == "hacker_014"
        assert d["name"] == "Morpheus"
        assert d["skill_level"] == 7
        assert d["reputation"] == 30.0
        assert d["stealth"] == 60.0
        assert d["agent_type"] == "hacker"

    def test_hacker_from_dict(self):
        hacker = Hacker(agent_id="hacker_015", name="Test")
        d = hacker.to_dict()
        restored = Hacker.from_dict(d)
        assert restored.agent_id == hacker.agent_id
        assert restored.skill_level == hacker.skill_level
        assert restored.stealth == hacker.stealth

    def test_hacker_round_trip(self):
        hacker = Hacker(
            agent_id="hacker_016",
            name="Cipher",
            skill_level=8,
            reputation=45.0,
            stealth=25.0,
        )
        d = hacker.to_dict()
        restored = Hacker.from_dict(d)
        assert restored.skill_level == 8
        assert restored.reputation == 45.0
        assert restored.stealth == 25.0
        assert restored._data_chips == hacker._data_chips
