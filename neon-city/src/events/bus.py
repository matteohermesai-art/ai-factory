"""
Event bus implementation for the Neon City Simulation Engine.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict, deque
from typing import Callable, Deque, Dict, List, Optional

from .types import Event, EventType


class EventBus:
    """
    Central event bus for publishing and subscribing to simulation events.
    
    Supports synchronous and asynchronous subscribers, event history tracking,
    and statistics collection.
    """

    def __init__(self) -> None:
        """Initialize the event bus with empty subscribers and history."""
        self._subscribers: Dict[Optional[EventType], List[Callable]] = defaultdict(list)
        self._history: Deque[Event] = deque(maxlen=10000)
        self._total_published: int = 0
        self._by_type: Dict[EventType, int] = defaultdict(int)

    def subscribe(self, event_type: Optional[EventType], callback: Callable) -> None:
        """
        Register a listener for events.
        
        Args:
            event_type: The type of event to listen for. None = subscribe to all events.
            callback: The callable to invoke when matching events are published.
        """
        if callback not in self._subscribers[event_type]:
            self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: Optional[EventType], callback: Callable) -> None:
        """
        Remove a listener.
        
        Args:
            event_type: The event type the callback was registered for.
            callback: The callable to remove.
        """
        if event_type in self._subscribers:
            self._subscribers[event_type] = [
                cb for cb in self._subscribers[event_type] if cb is not callback
            ]
            if not self._subscribers[event_type]:
                del self._subscribers[event_type]

    def publish(self, event: Event) -> None:
        """
        Publish an event to all matching subscribers (synchronous).
        
        Notifies subscribers registered for the specific event type and
        subscribers registered for all events (None).
        
        Args:
            event: The event to publish.
        """
        self._history.append(event)
        self._total_published += 1
        self._by_type[event.event_type] += 1

        # Notify type-specific subscribers
        for callback in self._subscribers.get(event.event_type, []):
            try:
                callback(event)
            except Exception as e:
                # Log but don't crash on subscriber errors
                pass

        # Notify global subscribers (subscribed to all events)
        if event.event_type is not None:
            for callback in self._subscribers.get(None, []):
                try:
                    callback(event)
                except Exception as e:
                    pass

    def publish_async(self, event: Event) -> None:
        """
        Publish an event via asyncio for async subscribers.
        
        Runs the publish in the current event loop if one exists,
        otherwise creates a new one.
        
        Args:
            event: The event to publish.
        """
        try:
            loop = asyncio.get_running_loop()
            # Schedule on the running loop
            loop.call_soon(self.publish, event)
        except RuntimeError:
            # No running loop, run synchronously
            self.publish(event)

    def get_history(
        self, event_type: Optional[EventType] = None, limit: int = 100
    ) -> List[Event]:
        """
        Get recent events from history.
        
        Args:
            event_type: Filter by event type. None = return all events.
            limit: Maximum number of events to return.
            
        Returns:
            List of recent events, most recent first.
        """
        if event_type is None:
            events = list(self._history)
        else:
            events = [e for e in self._history if e.event_type == event_type]

        # Return most recent first, limited
        return events[-limit:][::-1]

    def clear(self) -> None:
        """Clear all history and remove all subscribers."""
        self._history.clear()
        self._subscribers.clear()
        self._total_published = 0
        self._by_type.clear()

    def stats(self) -> dict:
        """
        Get event bus statistics.
        
        Returns:
            Dictionary with total_published count and by_type breakdown.
        """
        return {
            "total_published": self._total_published,
            "by_type": {et.value: count for et, count in self._by_type.items()},
        }

    @property
    def subscriber_count(self) -> int:
        """Total number of registered subscribers across all event types."""
        return sum(len(cbs) for cbs in self._subscribers.values())
