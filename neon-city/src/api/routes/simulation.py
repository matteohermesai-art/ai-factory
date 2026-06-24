"""Simulation management routes."""

from __future__ import annotations

import time
import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException

from src.api.schemas import (
    SimulationCreate,
    SimulationStatus,
    TickResponse,
)

router = APIRouter(prefix="/api/v1/simulation", tags=["simulation"])

# In-memory registry of active simulations keyed by sim_id
_simulations: dict[str, "SimulationInstance"] = {}


class SimulationInstance:
    """Holds runtime state for a single simulation."""

    def __init__(self, sim_id: str, config: SimulationCreate) -> None:
        self.sim_id = sim_id
        self.config = config
        self.tick_number: int = 0
        self.running: bool = False
        self.paused: bool = False
        self.agent_count: int = 0
        self.last_analytics: dict = {}
        self._events_count: int = 0

    def status(self) -> SimulationStatus:
        return SimulationStatus(
            simulation_id=self.sim_id,
            tick_number=self.tick_number,
            running=self.running,
            agent_count=self.agent_count,
            last_analytics=self.last_analytics,
        )

    def run_tick(self) -> TickResponse:
        if self.paused:
            return TickResponse(
                tick_number=self.tick_number,
                events_count=0,
                analytics=self.last_analytics,
                duration_ms=0.0,
            )
        start = time.monotonic()
        self.tick_number += 1
        # Placeholder analytics; real engine integration would go here
        self.last_analytics = {
            "total_actions": 0,
            "actions_by_type": {},
            "actions_by_action": {},
            "total_transactions": 0,
            "transaction_volume": 0.0,
            "transaction_by_currency": {},
            "events_count": {},
            "gini_coefficient": None,
        }
        self._events_count = 0
        duration = (time.monotonic() - start) * 1000.0
        return TickResponse(
            tick_number=self.tick_number,
            events_count=self._events_count,
            analytics=self.last_analytics,
            duration_ms=round(duration, 2),
        )


@router.post("/", response_model=SimulationStatus, status_code=201)
async def create_simulation(body: SimulationCreate) -> SimulationStatus:
    """Create a new simulation and return its initial status."""
    sim_id = str(uuid.uuid4())
    instance = SimulationInstance(sim_id, config=body)
    _simulations[sim_id] = instance
    return instance.status()


@router.get("/{sim_id}", response_model=SimulationStatus)
async def get_simulation(sim_id: str) -> SimulationStatus:
    """Get the current status of a simulation."""
    instance = _simulations.get(sim_id)
    if instance is None:
        raise HTTPException(status_code=404, detail=f"Simulation {sim_id} not found")
    return instance.status()


@router.post("/{sim_id}/start", response_model=SimulationStatus)
async def start_simulation(sim_id: str) -> SimulationStatus:
    """Start (or resume) continuous tick execution."""
    instance = _simulations.get(sim_id)
    if instance is None:
        raise HTTPException(status_code=404, detail=f"Simulation {sim_id} not found")
    instance.running = True
    instance.paused = False
    return instance.status()


@router.post("/{sim_id}/stop", response_model=SimulationStatus)
async def stop_simulation(sim_id: str) -> SimulationStatus:
    """Stop the simulation (halts tick execution)."""
    instance = _simulations.get(sim_id)
    if instance is None:
        raise HTTPException(status_code=404, detail=f"Simulation {sim_id} not found")
    instance.running = False
    instance.paused = False
    return instance.status()


@router.post("/{sim_id}/pause", response_model=SimulationStatus)
async def pause_simulation(sim_id: str) -> SimulationStatus:
    """Pause the simulation (ticks are no-ops while paused)."""
    instance = _simulations.get(sim_id)
    if instance is None:
        raise HTTPException(status_code=404, detail=f"Simulation {sim_id} not found")
    instance.paused = True
    return instance.status()


@router.post("/{sim_id}/resume", response_model=SimulationStatus)
async def resume_simulation(sim_id: str) -> SimulationStatus:
    """Resume a paused simulation."""
    instance = _simulations.get(sim_id)
    if instance is None:
        raise HTTPException(status_code=404, detail=f"Simulation {sim_id} not found")
    instance.paused = False
    return instance.status()


@router.post("/{sim_id}/tick", response_model=TickResponse)
async def execute_tick(sim_id: str) -> TickResponse:
    """Execute a single tick and return the result."""
    instance = _simulations.get(sim_id)
    if instance is None:
        raise HTTPException(status_code=404, detail=f"Simulation {sim_id} not found")
    return instance.run_tick()


@router.get("/{sim_id}/state")
async def get_world_state(sim_id: str) -> dict:
    """Get the full world state for a simulation."""
    instance = _simulations.get(sim_id)
    if instance is None:
        raise HTTPException(status_code=404, detail=f"Simulation {sim_id} not found")
    return {
        "simulation_id": sim_id,
        "tick": instance.tick_number,
        "running": instance.running,
        "paused": instance.paused,
        "grid": {
            "width": instance.config.grid_width,
            "height": instance.config.grid_height,
        },
        "agent_count": instance.agent_count,
        "analytics": instance.last_analytics,
    }


@router.get("/{sim_id}/analytics")
async def get_analytics(sim_id: str, from_tick: Optional[int] = None) -> dict:
    """Get analytics history for a simulation."""
    instance = _simulations.get(sim_id)
    if instance is None:
        raise HTTPException(status_code=404, detail=f"Simulation {sim_id} not found")
    return {
        "simulation_id": sim_id,
        "current_tick": instance.tick_number,
        "last_analytics": instance.last_analytics,
        "from_tick": from_tick if from_tick is not None else 0,
    }


@router.delete("/{sim_id}", status_code=204)
async def delete_simulation(sim_id: str) -> None:
    """Delete a simulation and free its resources."""
    if sim_id not in _simulations:
        raise HTTPException(status_code=404, detail=f"Simulation {sim_id} not found")
    del _simulations[sim_id]
