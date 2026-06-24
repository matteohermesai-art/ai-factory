"""Repository pattern for data access in the Neon City Simulation Engine."""

from __future__ import annotations

from typing import Any

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import (
    AgentModel,
    EventRecordModel,
    ReplaySnapshotModel,
    TransactionRecordModel,
    WorldStateModel,
)


def _agent_to_dict(agent: AgentModel) -> dict[str, Any]:
    """Convert an AgentModel instance to a dictionary."""
    return {
        "id": agent.id,
        "agent_type": agent.agent_type,
        "name": agent.name,
        "pos_x": agent.pos_x,
        "pos_y": agent.pos_y,
        "health": agent.health,
        "energy": agent.energy,
        "age": agent.age,
        "alive": agent.alive,
        "wallet_data": agent.wallet_data,
        "attributes": agent.attributes,
        "created_at": agent.created_at,
        "updated_at": agent.updated_at,
    }


def _world_state_to_dict(ws: WorldStateModel) -> dict[str, Any]:
    """Convert a WorldStateModel instance to a dictionary."""
    return {
        "id": ws.id,
        "tick": ws.tick,
        "grid_data": ws.grid_data,
        "agent_count": ws.agent_count,
        "timestamp": ws.timestamp,
        "analytics_data": ws.analytics_data,
    }


def _event_to_dict(event: EventRecordModel) -> dict[str, Any]:
    """Convert an EventRecordModel instance to a dictionary."""
    return {
        "id": event.id,
        "event_type": event.event_type,
        "severity": event.severity,
        "tick": event.tick,
        "source_id": event.source_id,
        "target_id": event.target_id,
        "data": event.data,
        "timestamp": event.timestamp,
    }


def _tx_to_dict(tx: TransactionRecordModel) -> dict[str, Any]:
    """Convert a TransactionRecordModel instance to a dictionary."""
    return {
        "id": tx.id,
        "from_id": tx.from_id,
        "to_id": tx.to_id,
        "currency": tx.currency,
        "amount": tx.amount,
        "tick": tx.tick,
        "timestamp": tx.timestamp,
        "metadata": tx.metadata_,
    }


def _snapshot_to_dict(snapshot: ReplaySnapshotModel) -> dict[str, Any]:
    """Convert a ReplaySnapshotModel instance to a dictionary."""
    return {
        "id": snapshot.id,
        "tick": snapshot.tick,
        "full_state": snapshot.full_state,
        "checksum": snapshot.checksum,
        "timestamp": snapshot.timestamp,
    }


class AgentRepository:
    """Repository for agent data access."""

    @staticmethod
    async def save(session: AsyncSession, agent_data: dict[str, Any]) -> None:
        """Upsert an agent record.

        If an agent with the same id exists, update it; otherwise insert a new one.
        """
        existing = await session.get(AgentModel, agent_data["id"])
        if existing is not None:
            for key, value in agent_data.items():
                if key != "id":
                    setattr(existing, key, value)
        else:
            agent = AgentModel(**agent_data)
            session.add(agent)

    @staticmethod
    async def get(session: AsyncSession, agent_id: str) -> dict[str, Any] | None:
        """Get an agent by its id.

        Returns None if not found.
        """
        agent = await session.get(AgentModel, agent_id)
        if agent is None:
            return None
        return _agent_to_dict(agent)

    @staticmethod
    async def get_all(
        session: AsyncSession, agent_type: str | None = None
    ) -> list[dict[str, Any]]:
        """Get all agents, optionally filtered by agent_type."""
        stmt = select(AgentModel)
        if agent_type is not None:
            stmt = stmt.where(AgentModel.agent_type == agent_type)
        result = await session.execute(stmt)
        agents = result.scalars().all()
        return [_agent_to_dict(a) for a in agents]

    @staticmethod
    async def delete(session: AsyncSession, agent_id: str) -> bool:
        """Delete an agent by its id.

        Returns True if the agent was deleted, False if not found.
        """
        agent = await session.get(AgentModel, agent_id)
        if agent is None:
            return False
        await session.delete(agent)
        return True

    @staticmethod
    async def count(
        session: AsyncSession, agent_type: str | None = None
    ) -> int:
        """Count agents, optionally filtered by agent_type."""
        stmt = select(func.count()).select_from(AgentModel)
        if agent_type is not None:
            stmt = stmt.where(AgentModel.agent_type == agent_type)
        result = await session.execute(stmt)
        return result.scalar_one()

    @staticmethod
    async def bulk_save(
        session: AsyncSession, agents_data: list[dict[str, Any]]
    ) -> None:
        """Bulk upsert multiple agent records."""
        for agent_data in agents_data:
            existing = await session.get(AgentModel, agent_data["id"])
            if existing is not None:
                for key, value in agent_data.items():
                    if key != "id":
                        setattr(existing, key, value)
            else:
                agent = AgentModel(**agent_data)
                session.add(agent)


class WorldStateRepository:
    """Repository for world state data access."""

    @staticmethod
    async def save(
        session: AsyncSession,
        tick: int,
        grid_data: dict[str, Any],
        agent_count: int,
        analytics: dict[str, Any],
    ) -> None:
        """Save a world state record for the given tick.

        If a record for the tick already exists, update it.
        """
        existing = await session.get(WorldStateModel, tick)
        if existing is not None:
            existing.grid_data = grid_data
            existing.agent_count = agent_count
            existing.analytics_data = analytics
        else:
            world_state = WorldStateModel(
                tick=tick,
                grid_data=grid_data,
                agent_count=agent_count,
                analytics_data=analytics,
                timestamp=__import__("time").time(),
            )
            session.add(world_state)

    @staticmethod
    async def get(session: AsyncSession, tick: int) -> dict[str, Any] | None:
        """Get the world state for a specific tick.

        Returns None if not found.
        """
        ws = await session.get(WorldStateModel, tick)
        if ws is None:
            return None
        return _world_state_to_dict(ws)

    @staticmethod
    async def get_latest(session: AsyncSession) -> dict[str, Any] | None:
        """Get the world state for the most recent tick.

        Returns None if no records exist.
        """
        stmt = select(WorldStateModel).order_by(WorldStateModel.tick.desc()).limit(1)
        result = await session.execute(stmt)
        ws = result.scalar_one_or_none()
        if ws is None:
            return None
        return _world_state_to_dict(ws)

    @staticmethod
    async def get_range(
        session: AsyncSession, from_tick: int, to_tick: int
    ) -> list[dict[str, Any]]:
        """Get world states for a range of ticks (inclusive)."""
        stmt = (
            select(WorldStateModel)
            .where(WorldStateModel.tick >= from_tick, WorldStateModel.tick <= to_tick)
            .order_by(WorldStateModel.tick)
        )
        result = await session.execute(stmt)
        records = result.scalars().all()
        return [_world_state_to_dict(ws) for ws in records]


class EventRepository:
    """Repository for event record data access."""

    @staticmethod
    async def save(session: AsyncSession, event_data: dict[str, Any]) -> None:
        """Save an event record."""
        event = EventRecordModel(**event_data)
        session.add(event)

    @staticmethod
    async def get_by_tick(
        session: AsyncSession, tick: int
    ) -> list[dict[str, Any]]:
        """Get all event records for a specific tick."""
        stmt = select(EventRecordModel).where(EventRecordModel.tick == tick)
        result = await session.execute(stmt)
        events = result.scalars().all()
        return [_event_to_dict(e) for e in events]

    @staticmethod
    async def get_by_type(
        session: AsyncSession, event_type: str, limit: int = 100
    ) -> list[dict[str, Any]]:
        """Get event records filtered by type, limited to `limit` results."""
        stmt = (
            select(EventRecordModel)
            .where(EventRecordModel.event_type == event_type)
            .limit(limit)
        )
        result = await session.execute(stmt)
        events = result.scalars().all()
        return [_event_to_dict(e) for e in events]


class TransactionRepository:
    """Repository for transaction record data access."""

    @staticmethod
    async def save(session: AsyncSession, tx_data: dict[str, Any]) -> None:
        """Save a transaction record."""
        # Handle the metadata -> metadata_ mapping
        data = dict(tx_data)
        if "metadata" in data and "metadata_" not in data:
            data["metadata_"] = data.pop("metadata")
        tx = TransactionRecordModel(**data)
        session.add(tx)

    @staticmethod
    async def get_by_agent(
        session: AsyncSession, agent_id: str
    ) -> list[dict[str, Any]]:
        """Get all transaction records involving a specific agent (as sender or receiver)."""
        stmt = select(TransactionRecordModel).where(
            (TransactionRecordModel.from_id == agent_id)
            | (TransactionRecordModel.to_id == agent_id)
        )
        result = await session.execute(stmt)
        txs = result.scalars().all()
        return [_tx_to_dict(t) for t in txs]

    @staticmethod
    async def get_by_tick(
        session: AsyncSession, tick: int
    ) -> list[dict[str, Any]]:
        """Get all transaction records for a specific tick."""
        stmt = select(TransactionRecordModel).where(
            TransactionRecordModel.tick == tick
        )
        result = await session.execute(stmt)
        txs = result.scalars().all()
        return [_tx_to_dict(t) for t in txs]


class ReplayRepository:
    """Repository for replay snapshot data access."""

    @staticmethod
    async def save_snapshot(
        session: AsyncSession,
        tick: int,
        full_state: dict[str, Any],
        checksum: str,
    ) -> None:
        """Save a replay snapshot for the given tick.

        If a snapshot for the tick already exists, update it.
        """
        existing = await session.get(ReplaySnapshotModel, tick)
        if existing is not None:
            existing.full_state = full_state
            existing.checksum = checksum
            existing.timestamp = __import__("time").time()
        else:
            snapshot = ReplaySnapshotModel(
                tick=tick,
                full_state=full_state,
                checksum=checksum,
                timestamp=__import__("time").time(),
            )
            session.add(snapshot)

    @staticmethod
    async def get_snapshot(
        session: AsyncSession, tick: int
    ) -> dict[str, Any] | None:
        """Get the replay snapshot for a specific tick.

        Returns None if not found.
        """
        snapshot = await session.get(ReplaySnapshotModel, tick)
        if snapshot is None:
            return None
        return _snapshot_to_dict(snapshot)

    @staticmethod
    async def get_latest_snapshot(session: AsyncSession) -> dict[str, Any] | None:
        """Get the most recent replay snapshot.

        Returns None if no snapshots exist.
        """
        stmt = (
            select(ReplaySnapshotModel)
            .order_by(ReplaySnapshotModel.tick.desc())
            .limit(1)
        )
        result = await session.execute(stmt)
        snapshot = result.scalar_one_or_none()
        if snapshot is None:
            return None
        return _snapshot_to_dict(snapshot)
