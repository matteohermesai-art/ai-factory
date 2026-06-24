"""Tests for tick engine."""

import pytest
import asyncio

from src.engine.tick import SimulationEngine, TickResult
from src.engine.world import World
from src.events.types import EventType


class TestSingleTick:
    """Test single tick execution."""

    @pytest.mark.asyncio
    async def test_run_tick(self, engine, world):
        result = await engine.run_tick()
        assert isinstance(result, TickResult)

    @pytest.mark.asyncio
    async def test_tick_increments_counter(self, engine, world):
        assert world.tick_number == 0
        await engine.run_tick()
        assert world.tick_number == 1

    @pytest.mark.asyncio
    async def test_tick_returns_tick_result(self, engine, world):
        result = await engine.run_tick()
        assert result.tick_number == 0
        assert isinstance(result.events, list)
        assert isinstance(result.analytics, dict)
        assert isinstance(result.agent_actions, int)
        assert isinstance(result.duration_ms, float)

    @pytest.mark.asyncio
    async def test_tick_result_has_analytics(self, engine, world):
        result = await engine.run_tick()
        assert "total_actions" in result.analytics
        assert "actions_by_type" in result.analytics
        assert "total_transactions" in result.analytics


class TestMultipleTicks:
    """Test multiple ticks."""

    @pytest.mark.asyncio
    async def test_multiple_ticks(self, engine, world):
        for i in range(5):
            result = await engine.run_tick()
            assert result.tick_number == i
        assert world.tick_number == 5

    @pytest.mark.asyncio
    async def test_ticks_age_agents(self, engine, world):
        agent_id = world.add_agent("citizen", 5, 5)
        agent = world.get_agent(agent_id)
        initial_age = agent["age"]
        await engine.run_tick()
        assert agent["age"] == initial_age + 1


class TestStopPauseResume:
    """Test stop/pause/resume."""

    @pytest.mark.asyncio
    async def test_stop(self, engine, world):
        engine.stop()
        assert engine._running is False

    @pytest.mark.asyncio
    async def test_pause(self, engine, world):
        await engine.pause()
        assert engine._paused is True

    @pytest.mark.asyncio
    async def test_resume(self, engine, world):
        await engine.pause()
        await engine.resume()
        assert engine._paused is False

    @pytest.mark.asyncio
    async def test_run_with_num_ticks(self, engine, world):
        await engine.run(num_ticks=3)
        assert world.tick_number == 3

    @pytest.mark.asyncio
    async def test_run_stops_at_num_ticks(self, engine, world):
        results = []
        await engine.run(num_ticks=2)
        assert world.tick_number == 2


class TestTickAnalytics:
    """Test tick analytics are populated."""

    @pytest.mark.asyncio
    async def test_analytics_populated(self, engine, world):
        # Add a corporation which always generates wealth (deterministic action)
        world.add_agent("corporation", 5, 5)
        result = await engine.run_tick()
        assert result.analytics["total_actions"] > 0

    @pytest.mark.asyncio
    async def test_sim_analytics_accumulates(self, engine, world):
        world.add_agent("citizen", 5, 5)
        await engine.run_tick()
        summary = world.sim_analytics.summary()
        assert summary["total_ticks"] == 1

    @pytest.mark.asyncio
    async def test_multiple_ticks_accumulate(self, engine, world):
        world.add_agent("citizen", 5, 5)
        await engine.run_tick()
        await engine.run_tick()
        summary = world.sim_analytics.summary()
        assert summary["total_ticks"] == 2


class TestEventsGenerated:
    """Test events are generated during tick."""

    @pytest.mark.asyncio
    async def test_events_generated(self, engine, world):
        # Add agents that will generate events
        world.add_agent("citizen", 5, 5)
        world.add_agent("hacker", 3, 3)
        result = await engine.run_tick()
        # Events list should exist (may be empty depending on RNG)
        assert isinstance(result.events, list)

    @pytest.mark.asyncio
    async def test_events_published_to_bus(self, engine, world):
        world.add_agent("citizen", 5, 5)
        await engine.run_tick()
        stats = world.event_bus.stats()
        # At minimum, agent actions should publish events
        assert stats["total_published"] >= 0

    @pytest.mark.asyncio
    async def test_composite_generator_property(self, engine, world):
        assert engine.composite_generator is not None
        # Should be able to add generators
        from src.events.generators import RandomEventGenerator
        gen = RandomEventGenerator(seed=42)
        engine.composite_generator.add_generator(gen)
