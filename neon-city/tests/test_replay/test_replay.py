"""Tests for replay system."""

import pytest
import json
import tempfile
import os

from src.engine.replay import ReplayManager
from src.engine.world import World
from src.engine.tick import SimulationEngine


class TestSnapshotSaveLoad:
    """Test snapshot save/load."""

    def test_save_snapshot(self):
        config = {"grid_width": 10, "grid_height": 10, "seed": 42, "enable_tick_logger": False}
        world = World(config=config)
        replay = ReplayManager(world)

        checksum = replay.save_snapshot(tick=0)
        assert checksum is not None
        assert isinstance(checksum, str)
        assert len(checksum) == 64  # SHA-256 hex digest

    def test_save_snapshot_default_tick(self):
        config = {"grid_width": 10, "grid_height": 10, "seed": 42, "enable_tick_logger": False}
        world = World(config=config)
        replay = ReplayManager(world)

        checksum = replay.save_snapshot()
        assert checksum is not None

    def test_load_snapshot(self):
        config = {"grid_width": 10, "grid_height": 10, "seed": 42, "enable_tick_logger": False}
        world = World(config=config)
        replay = ReplayManager(world)

        replay.save_snapshot(tick=0)
        result = replay.load_snapshot(tick=0)
        assert result is True

    def test_load_nonexistent_snapshot(self):
        config = {"grid_width": 10, "grid_height": 10, "seed": 42, "enable_tick_logger": False}
        world = World(config=config)
        replay = ReplayManager(world)

        result = replay.load_snapshot(tick=999)
        assert result is False

    def test_available_snapshots(self):
        config = {"grid_width": 10, "grid_height": 10, "seed": 42, "enable_tick_logger": False}
        world = World(config=config)
        replay = ReplayManager(world)

        replay.save_snapshot(tick=0)
        replay.save_snapshot(tick=5)
        replay.save_snapshot(tick=10)

        snapshots = replay.available_snapshots
        assert snapshots == [0, 5, 10]


class TestChecksumVerification:
    """Test checksum verification."""

    def test_verify_checksum_valid(self):
        config = {"grid_width": 10, "grid_height": 10, "seed": 42, "enable_tick_logger": False}
        world = World(config=config)
        replay = ReplayManager(world)

        replay.save_snapshot(tick=0)
        assert replay.verify_checksum(tick=0) is True

    def test_verify_checksum_nonexistent(self):
        config = {"grid_width": 10, "grid_height": 10, "seed": 42, "enable_tick_logger": False}
        world = World(config=config)
        replay = ReplayManager(world)

        assert replay.verify_checksum(tick=999) is False

    def test_load_verifies_checksum(self):
        config = {"grid_width": 10, "grid_height": 10, "seed": 42, "enable_tick_logger": False}
        world = World(config=config)
        replay = ReplayManager(world)

        replay.save_snapshot(tick=0)
        # Tamper with the snapshot
        state, _ = replay._snapshots[0]
        corrupted_state = state.copy()
        corrupted_state["tick_number"] = 99999
        replay._snapshots[0] = (corrupted_state, "invalid_checksum")

        result = replay.load_snapshot(tick=0)
        assert result is False


class TestReplayFromToTick:
    """Test replay from/to tick."""

    def test_replay_from_to(self):
        config = {"grid_width": 10, "grid_height": 10, "seed": 42, "enable_tick_logger": False}
        world = World(config=config)
        replay = ReplayManager(world)

        # Save snapshot at tick 0
        replay.save_snapshot(tick=0)

        # Replay 5 ticks
        results = replay.replay_from(from_tick=0, to_tick=5)
        assert len(results) == 5
        for i, result in enumerate(results):
            assert result.tick_number == i

    def test_replay_raises_without_snapshot(self):
        config = {"grid_width": 10, "grid_height": 10, "seed": 42, "enable_tick_logger": False}
        world = World(config=config)
        replay = ReplayManager(world)

        with pytest.raises(ValueError):
            replay.replay_from(from_tick=0, to_tick=5)

    def test_replay_preserves_original_state(self):
        config = {"grid_width": 10, "grid_height": 10, "seed": 42, "enable_tick_logger": False}
        world = World(config=config)
        world.tick_number = 10
        replay = ReplayManager(world)

        replay.save_snapshot(tick=0)
        replay.replay_from(from_tick=0, to_tick=3)

        # Original state should be restored
        assert world.tick_number == 10


class TestExportImport:
    """Test export/import."""

    def test_export_replay(self):
        config = {"grid_width": 10, "grid_height": 10, "seed": 42, "enable_tick_logger": False}
        world = World(config=config)
        replay = ReplayManager(world)

        replay.save_snapshot(tick=0)
        replay.save_snapshot(tick=5)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            path = f.name

        try:
            replay.export_replay(path)
            with open(path, 'r') as f:
                data = json.load(f)
            assert data["format"] == "neon_city_replay_v1"
            assert "0" in data["snapshots"]
            assert "5" in data["snapshots"]
        finally:
            os.unlink(path)

    def test_import_replay(self):
        config = {"grid_width": 10, "grid_height": 10, "seed": 42, "enable_tick_logger": False}
        world = World(config=config)
        replay = ReplayManager(world)

        # Export first
        replay.save_snapshot(tick=0)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            path = f.name

        try:
            replay.export_replay(path)

            # Create new replay manager and import
            replay2 = ReplayManager(world)
            result = replay2.import_replay(path)
            assert result is True
            assert 0 in replay2.available_snapshots
        finally:
            os.unlink(path)

    def test_import_invalid_format(self):
        config = {"grid_width": 10, "grid_height": 10, "seed": 42, "enable_tick_logger": False}
        world = World(config=config)
        replay = ReplayManager(world)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"format": "wrong_format"}, f)
            path = f.name

        try:
            result = replay.import_replay(path)
            assert result is False
        finally:
            os.unlink(path)

    def test_import_corrupted_json(self):
        config = {"grid_width": 10, "grid_height": 10, "seed": 42, "enable_tick_logger": False}
        world = World(config=config)
        replay = ReplayManager(world)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("not valid json{{{")
            path = f.name

        try:
            result = replay.import_replay(path)
            assert result is False
        finally:
            os.unlink(path)


class TestClearSnapshots:
    """Test clear snapshots."""

    def test_clear_snapshots(self):
        config = {"grid_width": 10, "grid_height": 10, "seed": 42, "enable_tick_logger": False}
        world = World(config=config)
        replay = ReplayManager(world)

        replay.save_snapshot(tick=0)
        replay.save_snapshot(tick=5)
        assert len(replay.available_snapshots) == 2

        replay.clear_snapshots()
        assert len(replay.available_snapshots) == 0
