"""Tests for API routes."""

import pytest
from fastapi.testclient import TestClient

from src.api.app import create_app


class TestHealthCheck:
    """Test health endpoint."""

    def test_health_check(self):
        app = create_app()
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "service" in data


class TestSimulationCRUD:
    """Test simulation CRUD endpoints."""

    def test_create_simulation(self):
        app = create_app()
        client = TestClient(app)
        response = client.post("/api/v1/simulation/", json={
            "grid_width": 20,
            "grid_height": 20,
            "seed": 42,
        })
        assert response.status_code == 201
        data = response.json()
        assert data["tick_number"] == 0
        assert data["running"] is False
        assert data["simulation_id"] is not None

    def test_get_simulation(self):
        app = create_app()
        client = TestClient(app)
        # Create first
        create_resp = client.post("/api/v1/simulation/", json={
            "grid_width": 20, "grid_height": 20, "seed": 42,
        })
        sim_id = create_resp.json()["simulation_id"]

        # Get
        response = client.get(f"/api/v1/simulation/{sim_id}")
        assert response.status_code == 200
        assert response.json()["simulation_id"] == sim_id

    def test_get_simulation_not_found(self):
        app = create_app()
        client = TestClient(app)
        response = client.get("/api/v1/simulation/nonexistent-id")
        assert response.status_code == 404

    def test_start_simulation(self):
        app = create_app()
        client = TestClient(app)
        create_resp = client.post("/api/v1/simulation/", json={
            "grid_width": 20, "grid_height": 20, "seed": 42,
        })
        sim_id = create_resp.json()["simulation_id"]

        response = client.post(f"/api/v1/simulation/{sim_id}/start")
        assert response.status_code == 200
        assert response.json()["running"] is True

    def test_stop_simulation(self):
        app = create_app()
        client = TestClient(app)
        create_resp = client.post("/api/v1/simulation/", json={
            "grid_width": 20, "grid_height": 20, "seed": 42,
        })
        sim_id = create_resp.json()["simulation_id"]

        client.post(f"/api/v1/simulation/{sim_id}/start")
        response = client.post(f"/api/v1/simulation/{sim_id}/stop")
        assert response.status_code == 200
        assert response.json()["running"] is False

    def test_pause_simulation(self):
        app = create_app()
        client = TestClient(app)
        create_resp = client.post("/api/v1/simulation/", json={
            "grid_width": 20, "grid_height": 20, "seed": 42,
        })
        sim_id = create_resp.json()["simulation_id"]

        response = client.post(f"/api/v1/simulation/{sim_id}/pause")
        assert response.status_code == 200
        # SimulationStatus doesn't include paused field, just verify 200

    def test_resume_simulation(self):
        app = create_app()
        client = TestClient(app)
        create_resp = client.post("/api/v1/simulation/", json={
            "grid_width": 20, "grid_height": 20, "seed": 42,
        })
        sim_id = create_resp.json()["simulation_id"]

        client.post(f"/api/v1/simulation/{sim_id}/pause")
        response = client.post(f"/api/v1/simulation/{sim_id}/resume")
        assert response.status_code == 200

    def test_execute_tick(self):
        app = create_app()
        client = TestClient(app)
        create_resp = client.post("/api/v1/simulation/", json={
            "grid_width": 20, "grid_height": 20, "seed": 42,
        })
        sim_id = create_resp.json()["simulation_id"]

        response = client.post(f"/api/v1/simulation/{sim_id}/tick")
        assert response.status_code == 200
        data = response.json()
        assert data["tick_number"] == 1
        assert "analytics" in data

    def test_get_world_state(self):
        app = create_app()
        client = TestClient(app)
        create_resp = client.post("/api/v1/simulation/", json={
            "grid_width": 20, "grid_height": 20, "seed": 42,
        })
        sim_id = create_resp.json()["simulation_id"]

        response = client.get(f"/api/v1/simulation/{sim_id}/state")
        assert response.status_code == 200
        data = response.json()
        assert data["simulation_id"] == sim_id
        assert "grid" in data

    def test_get_analytics(self):
        app = create_app()
        client = TestClient(app)
        create_resp = client.post("/api/v1/simulation/", json={
            "grid_width": 20, "grid_height": 20, "seed": 42,
        })
        sim_id = create_resp.json()["simulation_id"]

        response = client.get(f"/api/v1/simulation/{sim_id}/analytics")
        assert response.status_code == 200
        data = response.json()
        assert "current_tick" in data

    def test_delete_simulation(self):
        app = create_app()
        client = TestClient(app)
        create_resp = client.post("/api/v1/simulation/", json={
            "grid_width": 20, "grid_height": 20, "seed": 42,
        })
        sim_id = create_resp.json()["simulation_id"]

        response = client.delete(f"/api/v1/simulation/{sim_id}")
        assert response.status_code == 204

        # Verify deleted
        get_response = client.get(f"/api/v1/simulation/{sim_id}")
        assert get_response.status_code == 404


class TestAgentEndpoints:
    """Test agent endpoints."""

    def setup_method(self):
        """Clear global agent store before each test."""
        from src.api.routes.agents import _agents
        _agents.clear()

    def test_spawn_agent(self):
        app = create_app()
        client = TestClient(app)
        response = client.post("/api/v1/agents/", json={
            "agent_type": "citizen",
            "x": 5,
            "y": 5,
            "name": "TestAgent",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["agent_type"] == "citizen"
        assert data["name"] == "TestAgent"
        assert data["x"] == 5
        assert data["y"] == 5

    def test_list_agents(self):
        app = create_app()
        client = TestClient(app)
        client.post("/api/v1/agents/", json={
            "agent_type": "citizen", "x": 1, "y": 1, "name": "A1",
        })
        client.post("/api/v1/agents/", json={
            "agent_type": "hacker", "x": 2, "y": 2, "name": "H1",
        })

        response = client.get("/api/v1/agents/")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_list_agents_filtered(self):
        app = create_app()
        client = TestClient(app)
        client.post("/api/v1/agents/", json={
            "agent_type": "citizen", "x": 1, "y": 1, "name": "A1",
        })
        client.post("/api/v1/agents/", json={
            "agent_type": "hacker", "x": 2, "y": 2, "name": "H1",
        })

        response = client.get("/api/v1/agents/?agent_type=hacker")
        assert response.status_code == 200
        agents = response.json()
        assert len(agents) == 1
        assert agents[0]["agent_type"] == "hacker"

    def test_get_agent(self):
        app = create_app()
        client = TestClient(app)
        create_resp = client.post("/api/v1/agents/", json={
            "agent_type": "citizen", "x": 1, "y": 1, "name": "TestAgent",
        })
        agent_id = create_resp.json()["agent_id"]

        response = client.get(f"/api/v1/agents/{agent_id}")
        assert response.status_code == 200
        assert response.json()["agent_id"] == agent_id

    def test_get_agent_not_found(self):
        app = create_app()
        client = TestClient(app)
        response = client.get("/api/v1/agents/nonexistent-id")
        assert response.status_code == 404

    def test_remove_agent(self):
        app = create_app()
        client = TestClient(app)
        create_resp = client.post("/api/v1/agents/", json={
            "agent_type": "citizen", "x": 1, "y": 1, "name": "TestAgent",
        })
        agent_id = create_resp.json()["agent_id"]

        response = client.delete(f"/api/v1/agents/{agent_id}")
        assert response.status_code == 204

        get_response = client.get(f"/api/v1/agents/{agent_id}")
        assert get_response.status_code == 404

    def test_get_agent_history(self):
        app = create_app()
        client = TestClient(app)
        create_resp = client.post("/api/v1/agents/", json={
            "agent_type": "citizen", "x": 1, "y": 1, "name": "TestAgent",
        })
        agent_id = create_resp.json()["agent_id"]

        response = client.get(f"/api/v1/agents/{agent_id}/history")
        assert response.status_code == 200
        data = response.json()
        assert data["agent_id"] == agent_id
        assert "current_position" in data


class TestEconomyEndpoints:
    """Test economy endpoints."""

    def test_get_wallets(self):
        app = create_app()
        client = TestClient(app)
        response = client.get("/api/v1/economy/wallets")
        assert response.status_code == 200
        data = response.json()
        assert "wallets" in data

    def test_get_wallet_not_found(self):
        app = create_app()
        client = TestClient(app)
        response = client.get("/api/v1/economy/wallets/nonexistent")
        assert response.status_code == 404

    def test_get_market(self):
        app = create_app()
        client = TestClient(app)
        response = client.get("/api/v1/economy/market")
        assert response.status_code == 200
        data = response.json()
        assert "order_books" in data
        assert "last_prices" in data

    def test_get_market_item(self):
        app = create_app()
        client = TestClient(app)
        response = client.get("/api/v1/economy/market/food")
        assert response.status_code == 200
        data = response.json()
        assert data["item"] == "food"

    def test_get_market_item_not_found(self):
        app = create_app()
        client = TestClient(app)
        response = client.get("/api/v1/economy/market/nonexistent")
        assert response.status_code == 404

    def test_place_order(self):
        app = create_app()
        client = TestClient(app)
        response = client.post("/api/v1/economy/market/order", json={
            "agent_id": "agent_001",
            "order_type": "buy",
            "item": "food",
            "quantity": 5,
            "price": 10.0,
            "currency": "credits",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "placed"
        assert "order_id" in data

    def test_place_order_invalid_item(self):
        app = create_app()
        client = TestClient(app)
        response = client.post("/api/v1/economy/market/order", json={
            "agent_id": "agent_001",
            "order_type": "buy",
            "item": "invalid_item",
            "quantity": 5,
            "price": 10.0,
        })
        assert response.status_code == 400

    def test_place_order_invalid_type(self):
        app = create_app()
        client = TestClient(app)
        response = client.post("/api/v1/economy/market/order", json={
            "agent_id": "agent_001",
            "order_type": "invalid",
            "item": "food",
            "quantity": 5,
            "price": 10.0,
        })
        assert response.status_code == 400

    def test_get_transactions(self):
        app = create_app()
        client = TestClient(app)
        response = client.get("/api/v1/economy/transactions")
        assert response.status_code == 200
        data = response.json()
        assert "transaction_count" in data

    def test_get_economy_stats(self):
        app = create_app()
        client = TestClient(app)
        response = client.get("/api/v1/economy/stats")
        assert response.status_code == 200
        data = response.json()
        assert "market_prices" in data
        assert "transaction_count" in data


class TestReplayEndpoints:
    """Test replay endpoints."""

    def test_start_replay(self):
        app = create_app()
        client = TestClient(app)
        response = client.post("/api/v1/replay/", json={
            "from_tick": 0,
            "to_tick": 10,
            "speed": 1.0,
        })
        assert response.status_code == 201
        data = response.json()
        assert "replay_id" in data
        assert len(data["ticks"]) == 11

    def test_get_replay(self):
        app = create_app()
        client = TestClient(app)
        create_resp = client.post("/api/v1/replay/", json={
            "from_tick": 0, "to_tick": 5,
        })
        replay_id = create_resp.json()["replay_id"]

        response = client.get(f"/api/v1/replay/{replay_id}")
        assert response.status_code == 200
        assert response.json()["replay_id"] == replay_id

    def test_get_replay_not_found(self):
        app = create_app()
        client = TestClient(app)
        response = client.get("/api/v1/replay/nonexistent-id")
        assert response.status_code == 404

    def test_stop_replay(self):
        app = create_app()
        client = TestClient(app)
        create_resp = client.post("/api/v1/replay/", json={
            "from_tick": 0, "to_tick": 5,
        })
        replay_id = create_resp.json()["replay_id"]

        response = client.post(f"/api/v1/replay/{replay_id}/stop")
        assert response.status_code == 200
        assert response.json()["status"] == "stopped"

    def test_export_replay(self):
        app = create_app()
        client = TestClient(app)
        response = client.get("/api/v1/replay/export/0/10")
        assert response.status_code == 200
        data = response.json()
        assert data["from_tick"] == 0
        assert data["to_tick"] == 10
        assert data["tick_count"] == 11

    def test_import_replay(self):
        app = create_app()
        client = TestClient(app)
        body = {
            "from_tick": 0,
            "to_tick": 5,
            "ticks": [
                {"tick_number": i, "events_count": 0, "analytics": {}, "duration_ms": 0.0}
                for i in range(6)
            ],
        }
        response = client.post("/api/v1/replay/import", json=body)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "imported"
        assert data["tick_count"] == 6


class TestErrorHandling:
    """Test error handling (404 for missing resources)."""

    def test_simulation_404(self):
        app = create_app()
        client = TestClient(app)
        response = client.get("/api/v1/simulation/nonexistent")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_agent_404(self):
        app = create_app()
        client = TestClient(app)
        response = client.get("/api/v1/agents/nonexistent")
        assert response.status_code == 404

    def test_wallet_404(self):
        app = create_app()
        client = TestClient(app)
        response = client.get("/api/v1/economy/wallets/nonexistent")
        assert response.status_code == 404

    def test_replay_404(self):
        app = create_app()
        client = TestClient(app)
        response = client.get("/api/v1/replay/nonexistent")
        assert response.status_code == 404

    def test_market_item_404(self):
        app = create_app()
        client = TestClient(app)
        response = client.get("/api/v1/economy/market/nonexistent")
        assert response.status_code == 404
