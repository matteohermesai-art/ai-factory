"""Tests for repository."""

import pytest

from src.persistence.repository import AgentRepository, WorldStateRepository


class TestAgentRepository:
    """Test AgentRepository interface."""

    def test_agent_repository_has_save(self):
        assert hasattr(AgentRepository, 'save')

    def test_agent_repository_has_get(self):
        assert hasattr(AgentRepository, 'get')

    def test_agent_repository_has_get_all(self):
        assert hasattr(AgentRepository, 'get_all')

    def test_agent_repository_has_delete(self):
        assert hasattr(AgentRepository, 'delete')

    def test_agent_repository_has_count(self):
        assert hasattr(AgentRepository, 'count')


class TestWorldStateRepository:
    """Test WorldStateRepository interface."""

    def test_world_state_repository_has_save(self):
        assert hasattr(WorldStateRepository, 'save')

    def test_world_state_repository_has_get(self):
        assert hasattr(WorldStateRepository, 'get')

    def test_world_state_repository_has_get_latest(self):
        assert hasattr(WorldStateRepository, 'get_latest')

    def test_world_state_repository_has_get_range(self):
        assert hasattr(WorldStateRepository, 'get_range')
