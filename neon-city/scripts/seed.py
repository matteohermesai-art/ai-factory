"""Database seeding script for the Neon City Simulation Engine.

Creates a World with initial agents at random positions and saves a snapshot.
"""

from __future__ import annotations

import argparse
import asyncio
import random
import time
import uuid
from typing import Any


def create_world(width: int, height: int, seed: int) -> dict[str, Any]:
    """Create a world configuration dict with the given dimensions."""
    random.seed(seed)
    return {
        "grid_width": width,
        "grid_height": height,
        "seed": seed,
        "agents": [],
    }


def spawn_agents(
    world: dict[str, Any],
    citizens: int = 10,
    hackers: int = 5,
    corporations: int = 3,
    police: int = 5,
) -> list[dict[str, Any]]:
    """Generate agents at random positions within the world grid."""
    agents: list[dict[str, Any]] = []
    grid_width = world["grid_width"]
    grid_height = world["grid_height"]

    agent_specs = [
        ("citizen", citizens),
        ("hacker", hackers),
        ("corporation", corporations),
        ("police", police),
    ]

    for agent_type, count in agent_specs:
        for i in range(count):
            agent = {
                "id": str(uuid.uuid4()),
                "agent_type": agent_type,
                "name": f"{agent_type}_{i:04d}",
                "pos_x": random.randint(0, grid_width - 1),
                "pos_y": random.randint(0, grid_height - 1),
                "health": 100.0,
                "energy": 100.0,
                "age": 0,
                "alive": True,
                "wallet_data": {"credits": random.uniform(100, 10000)},
                "attributes": {},
                "created_at": time.time(),
                "updated_at": time.time(),
            }
            agents.append(agent)

    return agents


def save_snapshot(agents: list[dict[str, Any]], output: str = "seed_snapshot.json") -> None:
    """Save the seeded agents as a JSON snapshot file."""
    import json

    snapshot = {
        "timestamp": time.time(),
        "agent_count": len(agents),
        "agents": agents,
    }
    with open(output, "w") as f:
        json.dump(snapshot, f, indent=2)
    print(f"Snapshot saved to {output}")


async def main() -> None:
    """CLI entrypoint: parse args, create world, spawn agents, save snapshot."""
    parser = argparse.ArgumentParser(
        description="Seed the Neon City simulation with initial agents"
    )
    parser.add_argument("--citizens", type=int, default=10, help="Number of citizen agents")
    parser.add_argument("--hackers", type=int, default=5, help="Number of hacker agents")
    parser.add_argument("--corporations", type=int, default=3, help="Number of corporation agents")
    parser.add_argument("--police", type=int, default=5, help="Number of police agents")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--grid-width", type=int, default=100, help="Grid width")
    parser.add_argument("--grid-height", type=int, default=100, help="Grid height")
    parser.add_argument("--output", type=str, default="seed_snapshot.json", help="Output snapshot file")
    args = parser.parse_args()

    print(f"Seeding Neon City simulation (seed={args.seed})...")
    print(f"Grid: {args.grid_width}x{args.grid_height}")
    print(f"Agents: {args.citizens} citizens, {args.hackers} hackers, "
          f"{args.corporations} corporations, {args.police} police")

    # Create world
    world = create_world(args.grid_width, args.grid_height, args.seed)

    # Spawn agents
    agents = spawn_agents(
        world,
        citizens=args.citizens,
        hackers=args.hackers,
        corporations=args.corporations,
        police=args.police,
    )

    total = len(agents)
    print(f"Spawned {total} agents")

    # Save snapshot
    save_snapshot(agents, args.output)
    print("Seeding complete.")


if __name__ == "__main__":
    asyncio.run(main())
