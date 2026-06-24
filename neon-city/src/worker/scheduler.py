"""Background simulation worker for the Neon City Simulation Engine."""

from __future__ import annotations

import asyncio
import logging
import os
import signal
from typing import Any, Optional

logger = logging.getLogger(__name__)


class SimulationEngine:
    """Minimal simulation engine interface for the worker.

    This wraps the core simulation components (World, TickEngine, etc.)
    and exposes a simple ``run_tick()`` method.
    """

    def __init__(
        self,
        grid_width: int = 100,
        grid_height: int = 100,
        seed: int = 42,
    ) -> None:
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.seed = seed
        self.tick_number: int = 0
        self.running: bool = False

    def run_tick(self) -> dict[str, Any]:
        """Execute a single simulation tick and return analytics."""
        self.tick_number += 1
        return {
            "tick": self.tick_number,
            "actions": 0,
            "events": 0,
            "transactions": 0,
        }


class SimulationWorker:
    """Background worker that continuously runs simulation ticks.

    Takes a simulation engine and runs it as a background async loop,
    persisting each tick to the database via the persistence layer.
    """

    def __init__(
        self,
        engine: SimulationEngine,
        interval_seconds: float = 1.0,
        persist: bool = True,
    ) -> None:
        self.engine = engine
        self.interval_seconds = interval_seconds
        self.persist = persist
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._session_factory: Any = None

    async def start(self) -> None:
        """Start the continuous tick loop."""
        if self._running:
            logger.warning("Worker is already running")
            return

        self._running = True
        self.engine.running = True

        # Initialize persistence if needed
        if self.persist:
            try:
                from src.persistence import get_engine, get_session_factory, init_db
                from src.config import settings

                db_url = settings.DATABASE_URL
                engine = get_engine(db_url)
                self._session_factory = get_session_factory(engine)
                await init_db(engine)
                logger.info("Database initialized for worker persistence")
            except Exception as e:
                logger.warning(f"Persistence initialization failed (continuing without DB): {e}")
                self._session_factory = None

        self._task = asyncio.create_task(self._tick_loop())
        logger.info(
            "SimulationWorker started (interval=%.2fs, persist=%s)",
            self.interval_seconds,
            self.persist,
        )

    async def stop(self) -> None:
        """Gracefully stop the tick loop."""
        if not self._running:
            return

        self._running = False
        self.engine.running = False

        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

        logger.info("SimulationWorker stopped at tick %d", self.engine.tick_number)

    async def _tick_loop(self) -> None:
        """Main tick loop: calls run_tick at the configured interval."""
        while self._running:
            try:
                result = await asyncio.to_thread(self.engine.run_tick)
                tick_number = result.get("tick", self.engine.tick_number)

                # Persist tick if session factory is available
                if self.persist and self._session_factory is not None:
                    await self._persist_tick(tick_number, result)

                if tick_number % 100 == 0:
                    logger.info("Tick %d completed", tick_number)

            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.error("Error in tick loop: %s", e, exc_info=True)
                # Continue running despite errors

            await asyncio.sleep(self.interval_seconds)

    async def _persist_tick(self, tick_number: int, result: dict[str, Any]) -> None:
        """Persist a tick result to the database."""
        try:
            from src.persistence import WorldStateRepository, get_session

            async with get_session(self._session_factory) as session:
                await WorldStateRepository.save(
                    session=tick_number,
                    grid_data={"width": self.engine.grid_width, "height": self.engine.grid_height},
                    agent_count=0,
                    analytics=result,
                )
        except Exception as e:
            logger.warning("Failed to persist tick %d: %s", tick_number, e)


async def main() -> None:
    """Entry point for the background worker.

    Reads configuration from environment, initializes the world/engine,
    starts the worker, and runs until SIGTERM.
    """
    import structlog

    from src.config import settings

    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(settings.LOG_LEVEL.upper())
        ),
    )

    log = structlog.get_logger()

    # Read config from environment
    grid_width = settings.GRID_WIDTH
    grid_height = settings.GRID_HEIGHT
    tick_interval = settings.TICK_INTERVAL_SECONDS
    seed = settings.SEED

    log.info(
        "Initializing simulation: grid=%dx%d, seed=%d, interval=%.2fs",
        grid_width, grid_height, seed, tick_interval,
    )

    # Initialize world and engine
    engine = SimulationEngine(
        grid_width=grid_width,
        grid_height=grid_height,
        seed=seed,
    )

    # Create and start worker
    worker = SimulationWorker(
        engine=engine,
        interval_seconds=tick_interval,
        persist=True,
    )

    # Handle shutdown signals
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def _signal_handler() -> None:
        log.info("Received shutdown signal")
        stop_event.set()

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, _signal_handler)

    await worker.start()
    log.info("Worker running. Send SIGTERM or SIGINT to stop.")

    await stop_event.wait()

    await worker.stop()
    log.info("Worker shut down cleanly.")


if __name__ == "__main__":
    asyncio.run(main())
