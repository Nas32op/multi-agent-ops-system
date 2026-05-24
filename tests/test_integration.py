"""Integration tests for multi-agent-ops-system."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch

from multi_agent_ops.config import AppConfig
from multi_agent_ops.workflow import MultiAgentWorkflow
from multi_agent_ops.llm import LLMResponse


class TestWorkflowIntegration:
    """Integration tests for MultiAgentWorkflow."""

    def test_workflow_with_mock_llm(self) -> None:
        """Test complete workflow execution with mock LLM."""
        config = AppConfig(mock_mode=True)
        workflow = MultiAgentWorkflow(config)

        result = workflow.run("制定7天运营方案")

        assert result.plan
        assert result.execution
        assert result.review
        assert "PLAN" in result.final_output
        assert "EXECUTION" in result.final_output
        assert "REVIEW" in result.final_output
        assert result.metadata["mock_mode"] is True
        assert result.metadata["model"] == "gpt-4o-mini"

    def test_workflow_memory_tracking(self) -> None:
        """Test that workflow properly tracks memory."""
        config = AppConfig(mock_mode=True)
        workflow = MultiAgentWorkflow(config)

        result = workflow.run("测试任务")

        memory = result.metadata["memory"]
        assert len(memory) == 4  # user, planner, executor, reviewer
        assert memory[0]["role"] == "user"
        assert memory[1]["role"] == "planner"
        assert memory[2]["role"] == "executor"
        assert memory[3]["role"] == "reviewer"

    def test_workflow_metadata_structure(self) -> None:
        """Test workflow metadata structure."""
        config = AppConfig(mock_mode=True)
        workflow = MultiAgentWorkflow(config)

        result = workflow.run("测试任务")

        metadata = result.metadata
        assert "model" in metadata
        assert "mock_mode" in metadata
        assert "rounds" in metadata
        assert "timestamp" in metadata
        assert "memory" in metadata
        assert "agent_results" in metadata


class TestAPIIntegration:
    """Integration tests for API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        from multi_agent_ops.api import app

        return TestClient(app)

    def test_health_endpoint(self, client) -> None:
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "0.2.0"
        assert "mock_mode" in data

    def test_execute_task_endpoint(self, client) -> None:
        """Test task execution endpoint."""
        with patch("multi_agent_ops.api.AppConfig.from_env") as mock_config:
            mock_config.return_value = AppConfig(mock_mode=True)

            response = client.post(
                "/api/v1/tasks",
                json={"task": "测试任务", "max_rounds": 1},
            )

            assert response.status_code == 200
            data = response.json()
            assert "plan" in data
            assert "execution" in data
            assert "review" in data
            assert "final_output" in data
            assert "metadata" in data

    def test_execute_task_validation(self, client) -> None:
        """Test task execution validation."""
        response = client.post(
            "/api/v1/tasks",
            json={"task": "", "max_rounds": 1},
        )
        assert response.status_code == 422  # Validation error

    def test_async_task_endpoint(self, client) -> None:
        """Test async task execution endpoint."""
        with patch("multi_agent_ops.api.AppConfig.from_env") as mock_config:
            mock_config.return_value = AppConfig(mock_mode=True)

            response = client.post(
                "/api/v1/tasks/async",
                json={"task": "测试任务", "max_rounds": 1},
            )

            assert response.status_code == 200
            data = response.json()
            assert "task_id" in data
            assert data["status"] == "accepted"
