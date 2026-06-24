"""Per-tick and aggregate analytics for the Neon City Simulation Engine.

``TickAnalytics`` accumulates data for a single tick and produces a summary
dict via ``finalize()``.  ``SimulationAnalytics`` stores the per-tick summaries
and can produce an aggregate view across the entire simulation run.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any


class TickAnalytics:
    """Accumulate analytics data for a single simulation tick.

    Usage::

        ta = TickAnalytics()
        ta.record_agent_action("citizen", "move")
        ta.record_transaction(50.0, "credits")
        ta.record_event("collision")
        summary = ta.finalize()
        ta.reset()  # ready for the next tick
    """

    def __init__(self) -> None:
        self.reset()

    # -- recording API ------------------------------------------------------

    def record_agent_action(self, agent_type: str, action: str) -> None:
        """Record that an agent of *agent_type* performed *action*."""
        self._total_actions += 1
        self._actions_by_type[agent_type] += 1
        self._actions_by_action[action] += 1

    def record_transaction(self, amount: float, currency_type: str) -> None:
        """Record a monetary transaction."""
        self._total_transactions += 1
        self._transaction_volume += amount
        self._transaction_by_currency[currency_type] += amount

    def record_event(self, event_type: str) -> None:
        """Count an event of the given *event_type*."""
        self._events_count[event_type] += 1

    # -- output -------------------------------------------------------------

    def finalize(self) -> dict[str, Any]:
        """Return a summary dict for the current tick.

        The returned dict contains:
        - ``total_actions`` – total agent actions this tick
        - ``actions_by_type`` – ``{agent_type: count}``
        - ``actions_by_action`` – ``{action: count}``
        - ``total_transactions`` – number of transactions
        - ``transaction_volume`` – sum of all transaction amounts
        - ``transaction_by_currency`` – ``{currency_type: total}``
        - ``events_count`` – ``{event_type: count}``
        - ``gini_coefficient`` – placeholder (``None``) for future computation
        """
        return {
            "total_actions": self._total_actions,
            "actions_by_type": dict(self._actions_by_type),
            "actions_by_action": dict(self._actions_by_action),
            "total_transactions": self._total_transactions,
            "transaction_volume": self._transaction_volume,
            "transaction_by_currency": dict(self._transaction_by_currency),
            "events_count": dict(self._events_count),
            "gini_coefficient": None,  # placeholder for future implementation
        }

    # -- lifecycle ----------------------------------------------------------

    def reset(self) -> None:
        """Clear all counters so the instance can be reused for the next tick."""
        self._total_actions: int = 0
        self._actions_by_type: defaultdict[str, int] = defaultdict(int)
        self._actions_by_action: defaultdict[str, int] = defaultdict(int)
        self._total_transactions: int = 0
        self._transaction_volume: float = 0.0
        self._transaction_by_currency: defaultdict[str, float] = defaultdict(float)
        self._events_count: defaultdict[str, int] = defaultdict(int)


class SimulationAnalytics:
    """Collects and aggregates ``TickAnalytics`` summaries across the run."""

    def __init__(self) -> None:
        self._history: list[dict[str, Any]] = []

    # -- recording ---------------------------------------------------------

    def add_tick(self, tick_number: int, analytics: dict[str, Any]) -> None:
        """Store the analytics *dict* produced by ``TickAnalytics.finalize()``.

        The *tick_number* is injected into the stored record so that history
        queries can filter by tick.
        """
        record = {"tick_number": tick_number, **analytics}
        self._history.append(record)

    # -- queries ------------------------------------------------------------

    def get_history(self, from_tick: int = 0) -> list[dict[str, Any]]:
        """Return all stored tick summaries starting at *from_tick* (inclusive)."""
        return [r for r in self._history if r["tick_number"] >= from_tick]

    def summary(self) -> dict[str, Any]:
        """Return an aggregate summary across all stored ticks.

        Fields:
        - ``total_ticks`` – number of ticks recorded
        - ``avg_actions_per_tick`` – mean total_actions across ticks
        - ``peak_activity_tick`` – tick number with the most total_actions
        - ``total_transactions`` – sum of all transactions across ticks
        - ``total_transaction_volume`` – sum of all transaction volumes
        """
        if not self._history:
            return {
                "total_ticks": 0,
                "avg_actions_per_tick": 0.0,
                "peak_activity_tick": None,
                "total_transactions": 0,
                "total_transaction_volume": 0.0,
            }

        total_ticks = len(self._history)
        total_actions = sum(r["total_actions"] for r in self._history)
        total_transactions = sum(r["total_transactions"] for r in self._history)
        total_volume = sum(r["transaction_volume"] for r in self._history)

        peak_tick = max(self._history, key=lambda r: r["total_actions"])

        return {
            "total_ticks": total_ticks,
            "avg_actions_per_tick": total_actions / total_ticks,
            "peak_activity_tick": peak_tick["tick_number"],
            "total_transactions": total_transactions,
            "total_transaction_volume": total_volume,
        }
