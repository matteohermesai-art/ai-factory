"""SQLAlchemy ORM models for the Neon City Simulation Engine."""

from __future__ import annotations

from sqlalchemy import Boolean, Float, Integer, String, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


class AgentModel(Base):
    """Model representing an agent in the simulation."""

    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    agent_type: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    pos_x: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pos_y: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    health: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    energy: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    age: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    alive: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    wallet_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    attributes: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[float] = mapped_column(Float, nullable=False)
    updated_at: Mapped[float] = mapped_column(Float, nullable=False)


class WorldStateModel(Base):
    """Model representing the world state at a given tick."""

    __tablename__ = "world_states"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tick: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    grid_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    agent_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    timestamp: Mapped[float] = mapped_column(Float, nullable=False)
    analytics_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class EventRecordModel(Base):
    """Model representing an event record in the simulation."""

    __tablename__ = "event_records"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    severity: Mapped[str] = mapped_column(String, nullable=False)
    tick: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    source_id: Mapped[str] = mapped_column(String, nullable=False)
    target_id: Mapped[str | None] = mapped_column(String, nullable=True)
    data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    timestamp: Mapped[float] = mapped_column(Float, nullable=False)


class TransactionRecordModel(Base):
    """Model representing a transaction record in the simulation."""

    __tablename__ = "transaction_records"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    from_id: Mapped[str] = mapped_column(String, nullable=False)
    to_id: Mapped[str] = mapped_column(String, nullable=False)
    currency: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    tick: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    timestamp: Mapped[float] = mapped_column(Float, nullable=False)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)


class ReplaySnapshotModel(Base):
    """Model representing a replay snapshot at a given tick."""

    __tablename__ = "replay_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tick: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    full_state: Mapped[dict] = mapped_column(JSON, nullable=False)
    checksum: Mapped[str] = mapped_column(String, nullable=False)
    timestamp: Mapped[float] = mapped_column(Float, nullable=False)
