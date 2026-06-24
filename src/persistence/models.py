"""
Database models for AI Factory.
Stores worker state, task history, cron jobs, and agent memory.
"""
from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Worker(Base):
    """Configuration and state of an AI agent worker."""
    __tablename__ = "workers"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    role: Mapped[str] = mapped_column(String(64), nullable=False)
    model: Mapped[str] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(16), default="active")
    max_tasks: Mapped[int] = mapped_column(Integer, default=3)
    current_tasks: Mapped[int] = mapped_column(Integer, default=0)
    total_completed: Mapped[int] = mapped_column(Integer, default=0)
    last_active: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    config: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    tasks: Mapped[List["Task"]] = relationship(back_populates="worker")

    def __repr__(self):
        return f"<Worker(id={self.id}, name={self.name}, status={self.status})>"


class Task(Base):
    """A task assigned to a worker."""
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="pending")
    priority: Mapped[int] = mapped_column(Integer, default=5)
    worker_id: Mapped[Optional[str]] = mapped_column(
        String(64), ForeignKey("workers.id"), nullable=True
    )
    parent_task_id: Mapped[Optional[str]] = mapped_column(
        String(64), ForeignKey("tasks.id"), nullable=True
    )
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    result: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    worker: Mapped[Optional[Worker]] = relationship(back_populates="tasks")
    subtasks: Mapped[List["Task"]] = relationship(
        back_populates="parent_task", remote_side="Task.id"
    )
    parent_task: Mapped[Optional["Task"]] = relationship(
        back_populates="subtasks", remote_side="Task.id"
    )

    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, status={self.status})>"


class CronJob(Base):
    """A scheduled recurring job."""
    __tablename__ = "cron_jobs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    schedule: Mapped[str] = mapped_column(String(64), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    worker_id: Mapped[Optional[str]] = mapped_column(
        String(64), ForeignKey("workers.id"), nullable=True
    )
    last_run: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    next_run: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    run_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<CronJob(id={self.id}, name={self.name}, enabled={self.enabled})>"


class WorkspaceFile(Base):
    """Tracked files in agent workspaces."""
    __tablename__ = "workspace_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    worker_id: Mapped[str] = mapped_column(String(64), nullable=False)
    path: Mapped[str] = mapped_column(String(512), nullable=False)
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<WorkspaceFile(worker={self.worker_id}, path={self.path})>"


class Memory(Base):
    """Persistent memory entries for workers."""
    __tablename__ = "memory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    worker_id: Mapped[str] = mapped_column(String(64), nullable=False)
    key: Mapped[str] = mapped_column(String(128), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    importance: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Memory(worker={self.worker_id}, key={self.key})>"
