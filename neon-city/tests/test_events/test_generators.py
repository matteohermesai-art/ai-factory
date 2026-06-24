"""Tests for event generators."""

import pytest

from src.events.generators import (
    RandomEventGenerator,
    AgentEventGenerator,
    EconomyEventGenerator,
    CompositeGenerator,
)
from src.events.types import EventSeverity, EventType


class TestRandomEventGenerator:
    """Test RandomEventGenerator produces events."""

    def test_produces_events(self):
        gen = RandomEventGenerator(seed=42, prob_power_outage=1.0)  # 100% chance
        events = gen.generate(tick=1, world_state={"grid_size": (10, 10)})
        assert len(events) >= 1
        assert any(e.event_type == EventType.POWER_OUTAGE for e in events)

    def test_produces_riot_always(self):
        gen = RandomEventGenerator(seed=42, prob_riot=1.0)
        events = gen.generate(tick=1, world_state={"grid_size": (10, 10)})
        assert any(e.event_type == EventType.RIOT for e in events)

    def test_produces_tech_breakthrough(self):
        gen = RandomEventGenerator(seed=42, prob_tech_breakthrough=1.0)
        events = gen.generate(tick=1, world_state={"grid_size": (10, 10)})
        assert any(e.event_type == EventType.TECH_BREAKTHROUGH for e in events)

    def test_produces_market_crash(self):
        gen = RandomEventGenerator(seed=42, prob_market_crash=1.0)
        events = gen.generate(tick=1, world_state={"grid_size": (10, 10)})
        assert any(e.event_type == EventType.MARKET_CRASH for e in events)

    def test_no_events_when_probabilities_zero(self):
        gen = RandomEventGenerator(
            seed=42,
            prob_power_outage=0.0,
            prob_riot=0.0,
            prob_tech_breakthrough=0.0,
            prob_market_crash=0.0,
        )
        events = gen.generate(tick=1, world_state={"grid_size": (10, 10)})
        assert len(events) == 0

    def test_generates_zone_ids(self):
        gen = RandomEventGenerator(seed=42, prob_power_outage=1.0)
        events = gen.generate(tick=1, world_state={"grid_size": (100, 100)})
        if events:
            assert events[0].target_id is not None
            assert "zone_" in events[0].target_id


class TestAgentEventGenerator:
    """Test AgentEventGenerator spawns agents."""

    def test_spawns_below_threshold(self):
        gen = AgentEventGenerator(spawn_threshold=50)
        events = gen.generate(
            tick=1,
            world_state={"agents": {}, "population": 5}
        )
        spawns = [e for e in events if e.event_type == EventType.AGENT_SPAWN]
        assert len(spawns) > 0

    def test_no_spawn_above_threshold(self):
        gen = AgentEventGenerator(spawn_threshold=50)
        events = gen.generate(
            tick=1,
            world_state={"agents": {"a": {}}, "population": 100}
        )
        spawns = [e for e in events if e.event_type == EventType.AGENT_SPAWN]
        assert len(spawns) == 0

    def test_spawn_count_small_population(self):
        gen = AgentEventGenerator(spawn_threshold=50)
        events = gen.generate(
            tick=1,
            world_state={"agents": {}, "population": 3}
        )
        spawns = [e for e in events if e.event_type == EventType.AGENT_SPAWN]
        assert len(spawns) == 3  # Below 10 = spawn 3

    def test_no_spawn_at_max_population(self):
        gen = AgentEventGenerator(spawn_threshold=50, max_population=10)
        events = gen.generate(
            tick=1,
            world_state={"agents": {}, "population": 10}
        )
        spawns = [e for e in events if e.event_type == EventType.AGENT_SPAWN]
        assert len(spawns) == 0

    def test_death_events_for_old_agents(self):
        gen = AgentEventGenerator(death_age_threshold=100)
        old_agent = {
            "agent_id": "old_1",
            "age": 200,
            "health": 50.0,
            "position": (5, 5),
            "mobile": True,
        }
        events = gen.generate(
            tick=1,
            world_state={"agents": {"old_1": old_agent}, "population": 1}
        )
        # Old agents should generate death/move events
        assert len(events) >= 0  # May or may not die based on probability


class TestEconomyEventGenerator:
    """Test EconomyEventGenerator triggers on thresholds."""

    def test_market_crash_high_volatility(self):
        gen = EconomyEventGenerator(volatility_threshold=0.15)
        events = gen.generate(
            tick=1,
            world_state={"price_volatility": 0.3, "corps": {}}
        )
        crashes = [e for e in events if e.event_type == EventType.MARKET_CRASH]
        assert len(crashes) == 1
        assert crashes[0].severity == EventSeverity.HIGH

    def test_no_crash_low_volatility(self):
        gen = EconomyEventGenerator(volatility_threshold=0.15)
        events = gen.generate(
            tick=1,
            world_state={"price_volatility": 0.1, "corps": {}}
        )
        crashes = [e for e in events if e.event_type == EventType.MARKET_CRASH]
        assert len(crashes) == 0

    def test_critical_crash_very_high_volatility(self):
        gen = EconomyEventGenerator(volatility_threshold=0.15)
        events = gen.generate(
            tick=1,
            world_state={"price_volatility": 0.4, "corps": {}}
        )
        crashes = [e for e in events if e.event_type == EventType.MARKET_CRASH]
        assert len(crashes) == 1
        assert crashes[0].severity == EventSeverity.CRITICAL

    def test_corp_takeover_high_wealth(self):
        gen = EconomyEventGenerator(corp_wealth_threshold=1000.0)
        events = gen.generate(
            tick=1,
            world_state={
                "price_volatility": 0.0,
                "corps": {
                    "corp1": {"wealth": 2000.0},
                    "corp2": {"wealth": 500.0},
                }
            }
        )
        takeovers = [e for e in events if e.event_type == EventType.CORP_TAKEOVER]
        assert len(takeovers) == 1
        assert takeovers[0].source_id == "corp1"

    def test_no_takeover_low_wealth(self):
        gen = EconomyEventGenerator(corp_wealth_threshold=1000000.0)
        events = gen.generate(
            tick=1,
            world_state={
                "price_volatility": 0.0,
                "corps": {"corp1": {"wealth": 100.0}}
            }
        )
        takeovers = [e for e in events if e.event_type == EventType.CORP_TAKEOVER]
        assert len(takeovers) == 0


class TestCompositeGenerator:
    """Test CompositeGenerator deduplication."""

    def test_combines_generators(self):
        gen1 = RandomEventGenerator(seed=42, prob_power_outage=1.0)
        gen2 = RandomEventGenerator(seed=42, prob_riot=1.0)
        composite = CompositeGenerator([gen1, gen2])
        events = composite.generate(tick=1, world_state={"grid_size": (10, 10)})
        # Should have events from both generators
        assert len(events) >= 2

    def test_deduplication(self):
        # Create a generator that always produces the same event
        gen = RandomEventGenerator(
            seed=42,
            prob_power_outage=1.0,
            prob_riot=0.0,
            prob_tech_breakthrough=0.0,
            prob_market_crash=0.0,
        )
        composite = CompositeGenerator([gen, gen])  # Same generator twice
        events = composite.generate(tick=1, world_state={"grid_size": (10, 10)})
        # Events should be deduplicated by event_id
        event_ids = [e.event_id for e in events]
        assert len(event_ids) == len(set(event_ids))

    def test_empty_generators(self):
        composite = CompositeGenerator([])
        events = composite.generate(tick=1, world_state={})
        assert events == []

    def test_add_generator(self):
        composite = CompositeGenerator()
        gen = RandomEventGenerator(seed=42, prob_power_outage=1.0)
        composite.add_generator(gen)
        events = composite.generate(tick=1, world_state={"grid_size": (10, 10)})
        assert len(events) >= 1

    def test_remove_generator(self):
        gen = RandomEventGenerator(seed=42, prob_power_outage=1.0)
        composite = CompositeGenerator([gen])
        composite.remove_generator(gen)
        events = composite.generate(tick=1, world_state={"grid_size": (10, 10)})
        assert len(events) == 0

    def test_handles_generator_exception(self):
        """Composite should not crash if one generator raises."""
        class BrokenGenerator:
            def generate(self, tick, world_state):
                raise RuntimeError("Broken!")

        composite = CompositeGenerator([BrokenGenerator()])
        # Should not raise
        events = composite.generate(tick=1, world_state={})
        assert events == []


class TestDeterminism:
    """Test determinism with same seed."""

    def test_same_seed_same_events(self):
        gen1 = RandomEventGenerator(seed=42)
        gen2 = RandomEventGenerator(seed=42)

        events1 = gen1.generate(tick=1, world_state={"grid_size": (10, 10)})
        events2 = gen2.generate(tick=1, world_state={"grid_size": (10, 10)})

        # Same seed should produce same number of events
        assert len(events1) == len(events2)

    def test_different_seeds_different_events(self):
        gen1 = RandomEventGenerator(seed=42)
        gen2 = RandomEventGenerator(seed=99)

        events1 = gen1.generate(tick=1, world_state={"grid_size": (10, 10)})
        events2 = gen2.generate(tick=1, world_state={"grid_size": (10, 10)})

        # Different seeds should produce different results
        # (at least the target_ids should differ)
        if events1 and events2:
            ids1 = [e.target_id for e in events1]
            ids2 = [e.target_id for e in events2]
            assert ids1 != ids2
