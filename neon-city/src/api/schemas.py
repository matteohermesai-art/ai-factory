"""Pydantic request/response schemas for the Neon City Simulation Engine API."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class SimulationCreate(BaseModel):
    """Request body for creating a new simulation."""

    grid_width: int = Field(default=100, ge=1, le=1000, description="Width of the city grid")
    grid_height: int = Field(default=100, ge=1, le=1000, description="Height of the city grid")
    seed: int = Field(default=42, description="Random seed for reproducibility")
    agent_counts: dict = Field(
        default_factory=dict,
        description="Mapping of agent_type to count, e.g. {\"citizen\": 50, \"hacker\": 10}",
    )


class SimulationStatus(BaseModel):
    """Response body for simulation status."""

    simulation_id: str
    tick_number: int = 0
    running: bool = False
    agent_count: int = 0
    last_analytics: dict = Field(default_factory=dict)


class AgentCreate(BaseModel):
    """Request body for spawning a new agent."""

    agent_type: str = Field(..., description="Type of agent: citizen, hacker, corporation, police")
    x: int = Field(..., ge=0, description="X position on the grid")
    y: int = Field(..., ge=0, description="Y position on the grid")
    name: str = Field(default="", display="Agent name")
    attributes: dict = Field(default_factory=dict, description="Additional agent attributes")


class AgentResponse(BaseModel):
    """Response body for agent details."""

    agent_id: str
    agent_type: str
    name: str
    x: int
    y: int
    health: float
    energy: float
    status: str
    wallet: dict = Field(default_factory=dict)


class TickResponse(BaseModel):
    """Response body for a single tick execution."""

    tick_number: int
    events_count: int = 0
    analytics: dict = Field(default_factory=dict)
    duration_ms: float = 0.0


class EconomyStats(BaseModel):
    """Response body for economy statistics."""

    wallets_total: dict = Field(default_factory=dict)
    market_prices: dict = Field(default_factory=dict)
    transaction_count: int = 0


class ReplayRequest(BaseModel):
    """Request body for starting a replay."""

    from_tick: int = Field(default=0, ge=0)
    to_tick: int = Field(default=100, ge=0)
    speed: float = Field(default=1.0, ge=0.1, le=100.0)


class ReplayResponse(BaseModel):
    """Response body for replay status/data."""

    replay_id: str
    ticks: list[TickResponse] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    """Standard error response body."""

    error: str
    detail: Optional[str] = None
