"""Agent management routes."""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException

from src.api.schemas import (
    AgentCreate,
    AgentResponse,
)

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])

# In-memory agent store keyed by agent_id
_agents: dict[str, dict] = {}


def _agent_to_response(agent_id: str, data: dict) -> AgentResponse:
    return AgentResponse(
        agent_id=agent_id,
        agent_type=data.get("agent_type", ""),
        name=data.get("name", ""),
        x=data.get("x", 0),
        y=data.get("y", 0),
        health=data.get("health", 100.0),
        energy=data.get("energy", 100.0),
        status=data.get("status", "active"),
        wallet=data.get("wallet", {}),
    )


@router.get("/", response_model=list[AgentResponse])
async def list_agents(agent_type: Optional[str] = None) -> list[AgentResponse]:
    """List all agents, optionally filtered by agent_type."""
    results: list[AgentResponse] = []
    for agent_id, data in _agents.items():
        if agent_type is not None and data.get("agent_type") != agent_type:
            continue
        results.append(_agent_to_response(agent_id, data))
    return results


@router.post("/", response_model=AgentResponse, status_code=201)
async def spawn_agent(body: AgentCreate) -> AgentResponse:
    """Spawn a new agent into the simulation."""
    agent_id = str(uuid.uuid4())
    _agents[agent_id] = {
        "agent_type": body.agent_type,
        "name": body.name,
        "x": body.x,
        "y": body.y,
        "health": 100.0,
        "energy": 100.0,
        "status": "active",
        "wallet": {},
        "attributes": body.attributes,
    }
    return _agent_to_response(agent_id, _agents[agent_id])


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str) -> AgentResponse:
    """Get details for a specific agent."""
    data = _agents.get(agent_id)
    if data is None:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    return _agent_to_response(agent_id, data)


@router.delete("/{agent_id}", status_code=204)
async def remove_agent(agent_id: str) -> None:
    """Remove an agent from the simulation."""
    if agent_id not in _agents:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    del _agents[agent_id]


@router.get("/{agent_id}/history")
async def get_agent_history(agent_id: str) -> dict:
    """Get the history (positions, actions) for a specific agent."""
    data = _agents.get(agent_id)
    if data is None:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    return {
        "agent_id": agent_id,
        "agent_type": data.get("agent_type", ""),
        "name": data.get("name", ""),
        "current_position": {"x": data.get("x", 0), "y": data.get("y", 0)},
        "status": data.get("status", "active"),
        "positions_history": [],
        "actions_history": [],
    }
