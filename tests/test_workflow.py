"""Tests for workflow execution."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch

from multi_agent_ops.config import AppConfig
from multi_agent_ops.workflow import MultiAgentWorkflow, WorkflowResult
from multi_agent_ops.exceptions import WorkflowError


class TestWorkflowResult:
    """Tests for WorkflowResult dataclass."""

    def test_workflow_result_creation(self) -> None:
        """Test creating a WorkflowResult."""
        result = WorkflowResult(
            plan="test plan",
            execution="test execution",
            review="test review",
            final_output="test final output",
            metadata={"key": "value"},
        )
        assert result.plan == "test plan"
        assert result.execution == "test execution"
        assert result.review == "test review"
        assert result.final_output == "test final output"
        assert result.metadata == {"key": "value"}


class TestMultiAgentWorkflow:
    """Tests for MultiAgentWorkflow class."""

    def test_workflow_initialization(self) -> None:
        """Test workflow initialization."""
        config = AppConfig(mock_mode=True)
        workflow = MultiAgentWorkflow(config)

        assert workflow.config == config
        assert workflow.planner is not None
        assert workflow.executor is not None
        assert workflow.reviewer is not None
        assert workflow.memory is not None

    def test_workflow_run_success(self) -> None:
        """Test successful workflow execution."""
        config = AppConfig(mock_mode=True)
        workflow = MultiAgentWorkflow(config)

        result = workflow.run("测试任务")

        assert isinstance(result, WorkflowResult)
        assert result.plan
        assert result.execution
        assert result.review
        assert "PLAN" in result.final_output
        assert "EXECUTION" in result.final_output
        assert "REVIEW" in result.final_output

    def test_workflow_run_with_context(self) -> None:
        """Test workflow execution with context."""
        config = AppConfig(mock_mode=True)
        workflow = MultiAgentWorkflow(config)

        result = workflow.run("测试任务", max_rounds=2)

        assert result.metadata["rounds"] == 2

    def test_workflow_run_failure(self) -> None:
        """Test workflow execution failure."""
        config = AppConfig(mock_mode=True)
        workflow = MultiAgentWorkflow(config)

        with patch.object(workflow.planner, "run", side_effect=Exception("Test error")):
            with pytest.raises(WorkflowError):
                workflow.run("测试任务")

    def test_workflow_metadata_structure(self) -> None:
        """Test workflow metadata structure."""
        config = AppConfig(mock_mode=True)
        workflow = MultiAgentWorkflow(config)

        result = workflow.run("测试任务")

        metadata = result.metadata
        assert metadata["model"] == "gpt-4o-mini"
        assert metadata["mock_mode"] is True
        assert metadata["rounds"] == 1
        assert "timestamp" in metadata
        assert "memory" in metadata
        assert "agent_results" in metadata


class TestWorkflowEdgeCases:
    """Tests for workflow edge cases."""

    def test_workflow_empty_task(self) -> None:
        """Test workflow with empty task."""
        config = AppConfig(mock_mode=True)
        workflow = MultiAgentWorkflow(config)

        # Should still work with empty task
        result = workflow.run("")
        assert result.plan
        assert result.execution
        assert result.review

    def test_workflow_long_task(self) -> None:
        """Test workflow with long task."""
        config = AppConfig(mock_mode=True)
        workflow = MultiAgentWorkflow(config)

        long_task = "这" * 1000
        result = workflow.run(long_task)
        assert result.plan
        assert result.execution
        assert result.review

    def test_workflow_special_characters(self) -> None:
        """Test workflow with special characters in task."""
        config = AppConfig(mock_mode=True)
        workflow = MultiAgentWorkflow(config)

        task_with_special_chars = "任务包含特殊字符：!@#$%^&*()_+{}|:<>?"
        result = workflow.run(task_with_special_chars)
        assert result.plan
        assert result.execution
        assert result.review
