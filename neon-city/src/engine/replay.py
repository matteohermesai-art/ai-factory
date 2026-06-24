"""Replay recording and playback module for the Neon City Simulation Engine.

Provides ReplayManager for saving/loading snapshots, deterministic replay,
checksum verification, and JSON export/import.
"""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Optional

from .tick import TickResult
from .world import World


class ReplayManager:
    """Manages simulation snapshots, replay, and state integrity verification."""

    def __init__(self, world: World) -> None:
        """
        Initialize the replay manager.

        Args:
            world: The World instance to snapshot and replay.
        """
        self._world: World = world
        # tick_number -> (state_dict, checksum)
        self._snapshots: dict[int, tuple[dict[str, Any], str]] = {}

    # ------------------------------------------------------------------
    # Snapshot management
    # ------------------------------------------------------------------

    def save_snapshot(self, tick: int | None = None) -> str:
        """
        Save a full state snapshot for a given tick.

        Args:
            tick: Tick number to snapshot. Defaults to current world tick.

        Returns:
            The SHA-256 checksum of the saved state.
        """
        if tick is None:
            tick = self._world.tick_number

        state = self._world.get_state()
        state_json = json.dumps(state, sort_keys=True, default=str)
        checksum = hashlib.sha256(state_json.encode("utf-8")).hexdigest()

        self._snapshots[tick] = (state, checksum)
        return checksum

    def load_snapshot(self, tick: int) -> bool:
        """
        Restore the world state from a saved snapshot.

        Args:
            tick: The tick number of the snapshot to load.

        Returns:
            True if the snapshot was found and loaded successfully.
        """
        if tick not in self._snapshots:
            return False

        state, expected_checksum = self._snapshots[tick]

        # Verify integrity before loading
        state_json = json.dumps(state, sort_keys=True, default=str)
        actual_checksum = hashlib.sha256(state_json.encode("utf-8")).hexdigest()
        if actual_checksum != expected_checksum:
            return False

        self._world.from_state(state)
        return True

    def verify_checksum(self, tick: int) -> bool:
        """
        Verify the integrity of a saved snapshot.

        Args:
            tick: The tick number to verify.

        Returns:
            True if the snapshot exists and its checksum matches.
        """
        if tick not in self._snapshots:
            return False

        state, expected_checksum = self._snapshots[tick]
        state_json = json.dumps(state, sort_keys=True, default=str)
        actual_checksum = hashlib.sha256(state_json.encode("utf-8")).hexdigest()
        return actual_checksum == expected_checksum

    # ------------------------------------------------------------------
    # Replay
    # ------------------------------------------------------------------

    def replay_from(
        self,
        from_tick: int,
        to_tick: int,
        speed: float = 1.0,
    ) -> list[TickResult]:
        """
        Deterministically replay ticks from a saved snapshot.

        Loads the snapshot at from_tick, then re-runs the simulation
        to to_tick, collecting TickResults.

        Args:
            from_tick: Tick number to start replay from (must have a snapshot).
            to_tick: Tick number to replay to (exclusive).
            speed: Replay speed multiplier (currently informational; actual
                   speed control is handled by the caller).

        Returns:
            List of TickResult objects for each replayed tick.

        Raises:
            ValueError: If from_tick snapshot doesn't exist.
        """
        if from_tick not in self._snapshots:
            raise ValueError(f"No snapshot found for tick {from_tick}")

        # Save current state so we can restore after replay
        original_state = self._world.get_state()

        # Load the from_tick snapshot
        self.load_snapshot(from_tick)

        # Build a temporary engine for replay
        from .tick import SimulationEngine

        engine = SimulationEngine(self._world, self._world.event_bus)

        results: list[TickResult] = []
        num_ticks = to_tick - from_tick

        # Synchronous replay (no async needed for deterministic replay)
        import asyncio

        loop = asyncio.new_event_loop()
        try:
            for i in range(num_ticks):
                result = loop.run_until_complete(engine.run_tick())
                results.append(result)
        finally:
            loop.close()

        # Restore original state
        self._world.from_state(original_state)

        return results

    # ------------------------------------------------------------------
    # Export / Import
    # ------------------------------------------------------------------

    def export_replay(self, path: str) -> None:
        """
        Export all snapshots to a JSON file.

        Args:
            path: File path to write the JSON replay data.
        """
        export_data: dict[str, Any] = {
            "format": "neon_city_replay_v1",
            "exported_at": time.time(),
            "snapshots": {},
        }

        for tick, (state, checksum) in self._snapshots.items():
            export_data["snapshots"][str(tick)] = {
                "state": state,
                "checksum": checksum,
            }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, default=str)

    def import_replay(self, path: str) -> bool:
        """
        Import snapshots from a JSON replay file.

        Args:
            path: File path to read the JSON replay data from.

        Returns:
            True if the import was successful.
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                import_data = json.load(f)

            if import_data.get("format") != "neon_city_replay_v1":
                return False

            snapshots = import_data.get("snapshots", {})
            for tick_str, snap_data in snapshots.items():
                tick = int(tick_str)
                state = snap_data["state"]
                checksum = snap_data["checksum"]

                # Verify checksum on import
                state_json = json.dumps(state, sort_keys=True, default=str)
                expected = hashlib.sha256(state_json.encode("utf-8")).hexdigest()
                if expected != checksum:
                    continue  # Skip corrupted snapshots

                self._snapshots[tick] = (state, checksum)

            return True

        except (json.JSONDecodeError, KeyError, ValueError, OSError):
            return False

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    @property
    def available_snapshots(self) -> list[int]:
        """Return a sorted list of tick numbers that have snapshots."""
        return sorted(self._snapshots.keys())

    def clear_snapshots(self) -> None:
        """Remove all saved snapshots."""
        self._snapshots.clear()
