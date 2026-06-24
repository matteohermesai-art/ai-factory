"""Replay CLI tool for the Neon City Simulation Engine.

Loads snapshots from the database and replays them with configurable speed.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from typing import Any


def load_snapshots_from_db(
    database_url: str,
    from_tick: int,
    to_tick: int,
) -> list[dict[str, Any]]:
    """Load replay snapshots from the database within the given tick range.

    Falls back to generating placeholder data if DB is unavailable.
    """
    try:
        import asyncio as _asyncio
        import sys, os
        # Ensure project root is on path when run as a script
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from src.persistence import (
            ReplayRepository,
            get_engine,
            get_session_factory,
            init_db,
            get_session,
        )

        async def _load() -> list[dict[str, Any]]:
            engine = get_engine(database_url)
            session_factory = get_session_factory(engine)
            await init_db(engine)
            result = []
            async with get_session(session_factory) as session:
                for tick in range(from_tick, to_tick + 1):
                    snap = await ReplayRepository.get_snapshot(session, tick)
                    if snap is not None:
                        result.append(snap)
            await engine.dispose()
            return result

        return _asyncio.run(_load())
    except Exception as e:
        print(f"Warning: Could not load from DB ({e}). Using placeholder data.", file=sys.stderr)
        return [
            {
                "tick": t,
                "full_state": {"tick": t, "agents": [], "events": []},
                "checksum": "placeholder",
                "timestamp": time.time(),
            }
            for t in range(from_tick, to_tick + 1)
        ]


def replay_snapshots(
    snapshots: list[dict[str, Any]],
    speed: float = 1.0,
) -> list[dict[str, Any]]:
    """Replay loaded snapshots at the given speed.

    Returns a list of tick results.
    """
    results: list[dict[str, Any]] = []
    interval = 1.0 / speed if speed > 0 else 0.0

    for snapshot in snapshots:
        tick_start = time.monotonic()
        tick_number = snapshot.get("tick", 0)
        full_state = snapshot.get("full_state", {})

        result = {
            "tick": tick_number,
            "agent_count": len(full_state.get("agents", [])),
            "event_count": len(full_state.get("events", [])),
            "checksum": snapshot.get("checksum", ""),
        }
        results.append(result)

        # Print progress
        print(f"Tick {tick_number}: {result['agent_count']} agents, {result['event_count']} events")

        # Simulate replay speed
        elapsed = time.monotonic() - tick_start
        sleep_time = max(0.0, interval - elapsed)
        if sleep_time > 0:
            time.sleep(sleep_time)

    return results


def export_results(results: list[dict[str, Any]], output: str | None = None) -> None:
    """Export replay results to a file or stdout."""
    data = {
        "timestamp": time.time(),
        "tick_count": len(results),
        "results": results,
    }
    output_str = json.dumps(data, indent=2)

    if output:
        with open(output, "w") as f:
            f.write(output_str)
        print(f"Results exported to {output}")
    else:
        print(output_str)


async def async_main() -> None:
    """Async entrypoint for replay CLI."""
    parser = argparse.ArgumentParser(
        description="Neon City Replay CLI — replay simulation from DB snapshots"
    )
    parser.add_argument("--from-tick", type=int, default=0, help="Starting tick (inclusive)")
    parser.add_argument("--to-tick", type=int, default=10, help="Ending tick (inclusive)")
    parser.add_argument("--speed", type=float, default=1.0, help="Replay speed multiplier (0.1-100)")
    parser.add_argument(
        "--database-url",
        type=str,
        default=os.environ.get(
            "DATABASE_URL", "postgresql+asyncpg://neon:neon@db:5432/neoncity"
        ),
        help="Database connection URL",
    )
    parser.add_argument("--output", type=str, default=None, help="Output file (JSON)")
    args = parser.parse_args()

    print(f"Replaying ticks {args.from_tick} to {args.to_tick} at {args.speed}x speed...")

    # Load snapshots
    snapshots = load_snapshots_from_db(args.database_url, args.from_tick, args.to_tick)
    print(f"Loaded {len(snapshots)} snapshots")

    if not snapshots:
        print("No snapshots found for the given range.")
        return

    # Run replay
    results = replay_snapshots(snapshots, args.speed)
    print(f"Replay complete: {len(results)} ticks processed")

    # Export
    export_results(results, args.output)


def main() -> None:
    """CLI entrypoint."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
