"""Tests for corporation agent."""

import pytest

from src.agents.corporation import Corporation
from src.agents.base import AgentStatus
from src.economy.currency import Wallet, CurrencyType


class TestCorporationCreation:
    """Test corporation creation."""

    def test_corporation_creation(self):
        corp = Corporation(agent_id="corp_001", name="MegaCorp")
        assert corp.agent_id == "corp_001"
        assert corp.name == "MegaCorp"
        assert corp.agent_type == "corporation"
        assert corp.alive is True

    def test_corporation_default_attributes(self):
        corp = Corporation(agent_id="corp_002")
        assert corp.market_share == 10.0
        assert corp.influence == 10.0
        assert corp.employees == []
        assert corp.tech_level == 5

    def test_corporation_custom_attributes(self):
        corp = Corporation(
            agent_id="corp_003",
            name="NeoCorp",
            market_share=25.0,
            influence=50.0,
            tech_level=8,
            employees=["emp1", "emp2"],
        )
        assert corp.market_share == 25.0
        assert corp.influence == 50.0
        assert corp.tech_level == 8
        assert len(corp.employees) == 2

    def test_corporation_market_share_clamped(self):
        corp = Corporation(agent_id="corp_004", market_share=150.0)
        assert corp.market_share == 100.0

    def test_corporation_tech_level_clamped(self):
        corp = Corporation(agent_id="corp_005", tech_level=15)
        assert corp.tech_level == 10

    def test_corporation_has_wallet(self):
        corp = Corporation(agent_id="corp_006")
        assert corp.wallet is not None


class TestIncomeGeneration:
    """Test income generation."""

    def test_generate_income(self):
        corp = Corporation(
            agent_id="corp_007",
            market_share=20.0,
            tech_level=5,
        )
        initial_balance = corp.wallet.balance(CurrencyType.CREDITS)
        assert initial_balance == 0.0
        # Manually trigger income
        events = []
        corp._generate_income(
            {"tick": 1, "market": None},
            __import__("src.events.bus", fromlist=["EventBus"]).EventBus(),
            events,
        )
        # Income = market_share * tech_level * 0.5 = 20 * 5 * 0.5 = 50.0
        expected_income = 20.0 * 5.0 * 0.5
        assert corp.wallet.balance(CurrencyType.CREDITS) == expected_income

    def test_income_with_employees(self):
        corp = Corporation(
            agent_id="corp_008",
            market_share=10.0,
            tech_level=5,
            employees=["emp1", "emp2", "emp3"],
        )
        events = []
        corp._generate_income(
            {"tick": 1, "market": None},
            __import__("src.events.bus", fromlist=["EventBus"]).EventBus(),
            events,
        )
        # Income = 10 * 5 * 0.5 = 25.0
        # Salaries = 3 * 2.0 = 6.0
        expected = 25.0 - 6.0
        assert corp.wallet.balance(CurrencyType.CREDITS) == expected

    def test_income_issues_event(self):
        corp = Corporation(agent_id="corp_009", market_share=10.0, tech_level=5)
        events = []
        bus = __import__("src.events.bus", fromlist=["EventBus"]).EventBus()
        corp._generate_income({"tick": 1, "market": None}, bus, events)
        assert len(events) == 1
        assert events[0].event_type.value == "TRANSACTION"


class TestMarketManipulation:
    """Test market manipulation."""

    def test_issue_market_order(self):
        from src.economy.market import Market
        corp = Corporation(agent_id="corp_010")
        market = Market()
        events = []
        bus = __import__("src.events.bus", fromlist=["EventBus"]).EventBus()
        corp._issue_market_order({"tick": 1, "market": market}, bus, events)
        assert len(events) == 1
        # Check that order was placed in market
        from src.economy.market import AVAILABLE_ITEMS
        total_orders = sum(len(orders) for orders in market._order_books.values())
        assert total_orders == 1

    def test_market_order_no_market(self):
        corp = Corporation(agent_id="corp_011")
        events = []
        bus = __import__("src.events.bus", fromlist=["EventBus"]).EventBus()
        result = corp._issue_market_order({"tick": 1, "market": None}, bus, events)
        assert result is None
        assert len(events) == 0


class TestSerialization:
    """Test serialization."""

    def test_corporation_to_dict(self):
        corp = Corporation(
            agent_id="corp_012",
            name="AcmeCorp",
            market_share=30.0,
            influence=40.0,
            tech_level=7,
            employees=["emp1"],
        )
        d = corp.to_dict()
        assert d["agent_id"] == "corp_012"
        assert d["name"] == "AcmeCorp"
        assert d["market_share"] == 30.0
        assert d["influence"] == 40.0
        assert d["tech_level"] == 7
        assert d["employees"] == ["emp1"]
        assert d["agent_type"] == "corporation"

    def test_corporation_from_dict(self):
        corp = Corporation(agent_id="corp_013", name="Test")
        d = corp.to_dict()
        restored = Corporation.from_dict(d)
        assert restored.agent_id == corp.agent_id
        assert restored.market_share == corp.market_share

    def test_corporation_round_trip(self):
        corp = Corporation(
            agent_id="corp_014",
            name="CyberDyne",
            market_share=45.0,
            influence=60.0,
            tech_level=9,
            employees=["e1", "e2", "e3"],
        )
        d = corp.to_dict()
        restored = Corporation.from_dict(d)
        assert restored.market_share == 45.0
        assert restored.influence == 60.0
        assert restored.tech_level == 9
        assert len(restored.employees) == 3
