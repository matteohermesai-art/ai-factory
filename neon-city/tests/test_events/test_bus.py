"""Tests for event bus."""

import pytest

from src.events.bus import EventBus
from src.events.types import Event, EventType, EventSeverity


class TestSubscribePublish:
    """Test subscribe/publish."""

    def test_subscribe_and_publish(self, event_bus):
        received = []
        event_bus.subscribe(EventType.AGENT_SPAWN, received.append)

        event = Event(
            event_type=EventType.AGENT_SPAWN,
            severity=EventSeverity.LOW,
            tick=1,
            source_id="test",
        )
        event_bus.publish(event)

        assert len(received) == 1
        assert received[0].event_type == EventType.AGENT_SPAWN

    def test_subscribe_all_events(self, event_bus):
        received = []
        event_bus.subscribe(None, received.append)

        event = Event(
            event_type=EventType.TRANSACTION,
            severity=EventSeverity.LOW,
            tick=1,
            source_id="test",
        )
        event_bus.publish(event)

        assert len(received) == 1

    def test_multiple_subscribers(self, event_bus):
        received1 = []
        received2 = []
        event_bus.subscribe(EventType.AGENT_DEATH, received1.append)
        event_bus.subscribe(EventType.AGENT_DEATH, received2.append)

        event = Event(
            event_type=EventType.AGENT_DEATH,
            severity=EventSeverity.MEDIUM,
            tick=5,
            source_id="test",
        )
        event_bus.publish(event)

        assert len(received1) == 1
        assert len(received2) == 1

    def test_publish_increments_stats(self, event_bus):
        event = Event(
            event_type=EventType.POLICE_RAID,
            severity=EventSeverity.HIGH,
            tick=1,
            source_id="test",
        )
        event_bus.publish(event)

        stats = event_bus.stats()
        assert stats["total_published"] == 1
        assert stats["by_type"]["POLICE_RAID"] == 1


class TestUnsubscribe:
    """Test unsubscribe."""

    def test_unsubscribe(self, event_bus):
        received = []
        callback = received.append
        event_bus.subscribe(EventType.AGENT_SPAWN, callback)
        event_bus.unsubscribe(EventType.AGENT_SPAWN, callback)

        event = Event(
            event_type=EventType.AGENT_SPAWN,
            severity=EventSeverity.LOW,
            tick=1,
            source_id="test",
        )
        event_bus.publish(event)

        assert len(received) == 0

    def test_unsubscribe_nonexistent(self, event_bus):
        # Should not raise
        event_bus.subscribe(EventType.AGENT_SPAWN, lambda e: None)
        event_bus.unsubscribe(EventType.AGENT_SPAWN, lambda e: None)


class TestEventFilteringByType:
    """Test event filtering by type."""

    def test_get_history_all(self, event_bus):
        for i in range(3):
            event = Event(
                event_type=EventType.TRANSACTION,
                severity=EventSeverity.LOW,
                tick=i,
                source_id="test",
            )
            event_bus.publish(event)

        history = event_bus.get_history()
        assert len(history) == 3

    def test_get_history_filtered(self, event_bus):
        event1 = Event(
            event_type=EventType.TRANSACTION,
            severity=EventSeverity.LOW,
            tick=1,
            source_id="test",
        )
        event2 = Event(
            event_type=EventType.CYBER_ATTACK,
            severity=EventSeverity.HIGH,
            tick=2,
            source_id="test",
        )
        event_bus.publish(event1)
        event_bus.publish(event2)

        filtered = event_bus.get_history(event_type=EventType.CYBER_ATTACK)
        assert len(filtered) == 1
        assert filtered[0].event_type == EventType.CYBER_ATTACK

    def test_get_history_limit(self, event_bus):
        for i in range(10):
            event = Event(
                event_type=EventType.TRANSACTION,
                severity=EventSeverity.LOW,
                tick=i,
                source_id="test",
            )
            event_bus.publish(event)

        history = event_bus.get_history(limit=5)
        assert len(history) == 5


class TestEventHistory:
    """Test event history."""

    def test_history_order(self, event_bus):
        for i in range(5):
            event = Event(
                event_type=EventType.TRANSACTION,
                severity=EventSeverity.LOW,
                tick=i,
                source_id="test",
            )
            event_bus.publish(event)

        history = event_bus.get_history()
        # Most recent first
        assert history[0].tick == 4
        assert history[-1].tick == 0


class TestStats:
    """Test stats."""

    def test_initial_stats(self, event_bus):
        stats = event_bus.stats()
        assert stats["total_published"] == 0
        assert stats["by_type"] == {}

    def test_stats_multiple_types(self, event_bus):
        event_bus.publish(Event(
            event_type=EventType.TRANSACTION, severity=EventSeverity.LOW,
            tick=1, source_id="test",
        ))
        event_bus.publish(Event(
            event_type=EventType.TRANSACTION, severity=EventSeverity.LOW,
            tick=2, source_id="test",
        ))
        event_bus.publish(Event(
            event_type=EventType.CYBER_ATTACK, severity=EventSeverity.HIGH,
            tick=3, source_id="test",
        ))

        stats = event_bus.stats()
        assert stats["total_published"] == 3
        assert stats["by_type"]["TRANSACTION"] == 2
        assert stats["by_type"]["CYBER_ATTACK"] == 1


class TestClear:
    """Test clear."""

    def test_clear(self, event_bus):
        received = []
        event_bus.subscribe(EventType.TRANSACTION, received.append)
        event_bus.publish(Event(
            event_type=EventType.TRANSACTION, severity=EventSeverity.LOW,
            tick=1, source_id="test",
        ))

        event_bus.clear()

        # After clear, subscribers are gone
        event_bus.publish(Event(
            event_type=EventType.TRANSACTION, severity=EventSeverity.LOW,
            tick=2, source_id="test",
        ))
        assert len(received) == 1  # Only from before clear

    def test_clear_stats(self, event_bus):
        event_bus.publish(Event(
            event_type=EventType.TRANSACTION, severity=EventSeverity.LOW,
            tick=1, source_id="test",
        ))
        event_bus.clear()
        stats = event_bus.stats()
        assert stats["total_published"] == 0


class TestSubscriberCount:
    """Test subscriber_count property."""

    def test_subscriber_count(self, event_bus):
        assert event_bus.subscriber_count == 0

        event_bus.subscribe(EventType.TRANSACTION, lambda e: None)
        assert event_bus.subscriber_count == 1

        event_bus.subscribe(None, lambda e: None)
        assert event_bus.subscriber_count == 2


class TestPublishAsync:
    """Test async publish."""

    @pytest.mark.asyncio
    async def test_publish_async(self, event_bus):
        received = []
        event_bus.subscribe(EventType.TRANSACTION, received.append)

        event = Event(
            event_type=EventType.TRANSACTION,
            severity=EventSeverity.LOW,
            tick=1,
            source_id="test",
        )
        event_bus.publish_async(event)
        # Give it a chance to execute
        import asyncio
        await asyncio.sleep(0.01)

        assert len(received) == 1
