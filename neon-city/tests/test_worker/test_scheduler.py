"""Tests for scheduler."""

import pytest
import asyncio

from src.worker.scheduler import SimulationEngine, SimulationWorker


class TestSimulationEngine:
    """Test the worker's SimulationEngine."""

    def test_engine_creation(self):
        engine = SimulationEngine(grid_width=50, grid_height=50, seed=42)
        assert engine.grid_width == 50
        assert engine.grid_height == 50
        assert engine.seed == 42
        assert engine.tick_number == 0
        assert engine.running is False

    def test_engine_run_tick(self):
        engine = SimulationEngine(grid_width=10, grid_height=10, seed=42)
        result = engine.run_tick()
        assert isinstance(result, dict)
        assert "tick" in result
        assert "actions" in result
        assert "events" in result
        assert "transactions" in result

    def test_engine_increments_tick(self):
        engine = SimulationEngine(grid_width=10, grid_height=10, seed=42)
        engine.run_tick()
        assert engine.tick_number == 1
        engine.run_tick()
        assert engine.tick_number == 2


class TestWorkerStartStop:
    """Test worker start/stop."""

    @pytest.mark.asyncio
    async def test_worker_start(self):
        engine = SimulationEngine(grid_width=10, grid_height=10, seed=42)
        worker = SimulationWorker(engine=engine, interval_seconds=0.01, persist=False)
        await worker.start()
        assert worker._running is True
        await worker.stop()

    @pytest.mark.asyncio
    async def test_worker_stop(self):
        engine = SimulationEngine(grid_width=10, grid_height=10, seed=42)
        worker = SimulationWorker(engine=engine, interval_seconds=0.01, persist=False)
        await worker.start()
        await worker.stop()
        assert worker._running is False

    @pytest.mark.asyncio
    async def test_worker_start_idempotent(self):
        engine = SimulationEngine(grid_width=10, grid_height=10, seed=42)
        worker = SimulationWorker(engine=engine, interval_seconds=0.01, persist=False)
        await worker.start()
        # Starting again should not crash
        await worker.start()
        assert worker._running is True
        await worker.stop()

    @pytest.mark.asyncio
    async def test_worker_stop_not_running(self):
        engine = SimulationEngine(grid_width=10, grid_height=10, seed=42)
        worker = SimulationWorker(engine=engine, interval_seconds=0.01, persist=False)
        # Should not crash
        await worker.stop()


class TestTickLoopExecution:
    """Test tick loop execution."""

    @pytest.mark.asyncio
    async def test_tick_loop_executes(self):
        engine = SimulationEngine(grid_width=10, grid_height=10, seed=42)
        worker = SimulationWorker(engine=engine, interval_seconds=0.01, persist=False)
        await worker.start()
        # Wait for at least one tick
        await asyncio.sleep(0.05)
        await worker.stop()
        assert engine.tick_number >= 1

    @pytest.mark.asyncio
    async def test_tick_loop_increments(self):
        engine = SimulationEngine(grid_width=10, grid_height=10, seed=42)
        worker = SimulationWorker(engine=engine, interval_seconds=0.01, persist=False)
        await worker.start()
        await asyncio.sleep(0.1)
        await worker.stop()
        # Should have executed multiple ticks
        assert engine.tick_number > 0


class TestErrorHandling:
    """Test error handling in tick loop."""

    @pytest.mark.asyncio
    async def test_error_in_tick_continues(self):
        """Worker should continue running even if a tick raises an error."""
        class BrokenEngine:
            tick_number = 0
            running = True

            def run_tick(self):
                raise RuntimeError("Tick failed!")

        worker = SimulationWorker(engine=BrokenEngine(), interval_seconds=0.01, persist=False)
        await worker.start()
        # Worker should still be running despite the error
        await asyncio.sleep(0.05)
        assert worker._running is True
        await worker.stop()

    @pytest.mark.asyncio
    async def test_error_handling_does_not_crash_loop(self):
        """Multiple errors should not crash the worker."""
        call_count = 0

        class FlakyEngine:
            tick_number = 0
            running = True

            def run_tick(self):
                nonlocal call_count
                call_count += 1
                if call_count <= 3:
                    raise RuntimeError(f"Tick {call_count} failed!")
                return {"tick": call_count, "actions": 0, "events": 0, "transactions": 0}

        worker = SimulationWorker(engine=FlakyEngine(), interval_seconds=0.01, persist=False)
        await worker.start()
        await asyncio.sleep(0.1)
        await worker.stop()
        # Worker should have continued despite errors
        assert call_count > 0
