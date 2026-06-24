"""Structured logging module for the Neon City Simulation Engine.

Uses structlog to provide JSON production logging and dev-friendly console output,
with context variables for request_id and tick_number.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

import structlog

# ---------------------------------------------------------------------------
# Context variable keys
# ---------------------------------------------------------------------------
_REQUEST_ID_KEY = "request_id"
_TICK_NUMBER_KEY = "tick_number"


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

def setup_logging(log_level: str = "INFO", json_format: bool = True) -> None:
    """Configure structlog for the simulation engine.

    Parameters
    ----------
    log_level:
        One of the standard logging level names (``"DEBUG"``, ``"INFO"``, etc.).
    json_format:
        When *True* (default) use ``JSONRenderer`` for production-friendly output.
        When *False* use the human-readable ``ConsoleRenderer`` for development.
    """
    level = getattr(logging, log_level.upper(), logging.INFO)

    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if json_format:
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[
            *shared_processors,
            renderer,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Also configure the root stdlib logger so that loggers created via
    # logging.getLogger(...) respect the requested level.
    logging.basicConfig(
        format="%(message)s",
        level=level,
    )


# ---------------------------------------------------------------------------
# Logger factory
# ---------------------------------------------------------------------------

def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Return a structlog logger bound with the given *name*."""
    return structlog.get_logger(name)


# ---------------------------------------------------------------------------
# Context helpers
# ---------------------------------------------------------------------------

def bind_request_id(request_id: str | None = None) -> str:
    """Bind a request_id to the current structlog context.

    Returns the id that was bound (a new UUID if none was supplied).
    """
    rid = request_id or uuid.uuid4().hex
    structlog.contextvars.bind_contextvars(**{_REQUEST_ID_KEY: rid})
    return rid


def bind_tick_number(tick_number: int) -> None:
    """Bind *tick_number* to the current structlog context."""
    structlog.contextvars.bind_contextvars(**{_TICK_NUMBER_KEY: tick_number})


def clear_context() -> None:
    """Clear all structlog context variables for the current execution unit."""
    structlog.contextvars.clear_contextvars()


# ---------------------------------------------------------------------------
# TickLogger
# ---------------------------------------------------------------------------

class TickLogger:
    """Convenience logger that automatically binds a tick number.

    Usage::

        tl = TickLogger(tick_number=42)
        tl.log_event("tick_start")
        tl.log_agent_action("agent-1", "move", destination="plaza")
        tl.log_economy("gdp", 1_250_000.0)
    """

    def __init__(self, tick_number: int) -> None:
        self._tick_number = tick_number
        self._logger = get_logger("neon_city.tick")
        # Bind tick_number into every log line produced by this instance.
        bind_tick_number(tick_number)

    # -- public API ---------------------------------------------------------

    def log_event(self, event_type: str, **kwargs: Any) -> None:
        """Log a simulation *event_type* with optional extra fields."""
        self._logger.info(
            "tick_event",
            event_type=event_type,
            **kwargs,
        )

    def log_agent_action(
        self, agent_id: str, action: str, **kwargs: Any
    ) -> None:
        """Log that *agent_id* performed *action*."""
        self._logger.info(
            "agent_action",
            agent_id=agent_id,
            action=action,
            **kwargs,
        )

    def log_economy(self, metric: str, value: float, **kwargs: Any) -> None:
        """Log an economy *metric* with its *value*."""
        self._logger.info(
            "economy_metric",
            metric=metric,
            value=value,
            **kwargs,
        )
