"""Replay management routes."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException

from src.api.schemas import (
    ReplayRequest,
    ReplayResponse,
    TickResponse,
)

router = APIRouter(prefix="/api/v1/replay", tags=["replay"])

# In-memory replay store
_replays: dict[str, dict] = {}


@router.post("/", response_model=ReplayResponse, status_code=201)
async def start_replay(body: ReplayRequest) -> ReplayResponse:
    """Start a replay from stored snapshots within the given tick range."""
    replay_id = str(uuid.uuid4())
    ticks: list[TickResponse] = []
    for t in range(body.from_tick, body.to_tick + 1):
        ticks.append(
            TickResponse(
                tick_number=t,
                events_count=0,
                analytics={},
                duration_ms=0.0,
            )
        )
    _replays[replay_id] = {
        "replay_id": replay_id,
        "from_tick": body.from_tick,
        "to_tick": body.to_tick,
        "speed": body.speed,
        "status": "playing",
        "ticks": [t.model_dump() for t in ticks],
    }
    return ReplayResponse(replay_id=replay_id, ticks=ticks)


@router.get("/{replay_id}", response_model=ReplayResponse)
async def get_replay(replay_id: str) -> ReplayResponse:
    """Get the status and data for a specific replay."""
    replay = _replays.get(replay_id)
    if replay is None:
        raise HTTPException(status_code=404, detail=f"Replay {replay_id} not found")
    tick_responses = [TickResponse(**t) for t in replay["ticks"]]
    return ReplayResponse(replay_id=replay_id, ticks=tick_responses)


@router.post("/{replay_id}/stop")
async def stop_replay(replay_id: str) -> dict:
    """Stop an active replay."""
    replay = _replays.get(replay_id)
    if replay is None:
        raise HTTPException(status_code=404, detail=f"Replay {replay_id} not found")
    replay["status"] = "stopped"
    return {"replay_id": replay_id, "status": "stopped"}


@router.get("/export/{from_tick}/{to_tick}")
async def export_replay(from_tick: int, to_tick: int) -> dict:
    """Export replay data as JSON for the given tick range."""
    ticks = []
    for t in range(from_tick, to_tick + 1):
        ticks.append({
            "tick_number": t,
            "events_count": 0,
            "analytics": {},
            "duration_ms": 0.0,
        })
    return {
        "from_tick": from_tick,
        "to_tick": to_tick,
        "tick_count": len(ticks),
        "ticks": ticks,
    }


@router.post("/import")
async def import_replay(body: dict) -> dict:
    """Import a replay from uploaded JSON data.

    Expected body: {"from_tick": int, "to_tick": int, "ticks": [...]}
    """
    replay_id = str(uuid.uuid4())
    from_tick = body.get("from_tick", 0)
    to_tick = body.get("to_tick", 0)
    raw_ticks = body.get("ticks", [])

    tick_responses = []
    for t in raw_ticks:
        tick_responses.append(TickResponse(**t))

    _replays[replay_id] = {
        "replay_id": replay_id,
        "from_tick": from_tick,
        "to_tick": to_tick,
        "speed": body.get("speed", 1.0),
        "status": "imported",
        "ticks": [t.model_dump() for t in tick_responses],
    }
    return {
        "replay_id": replay_id,
        "status": "imported",
        "tick_count": len(tick_responses),
    }
