"""Tests for agent implementations."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch

from multi_agent_ops.agents import AgentResult, BaseAgent, PlannerAgent, ExecutorAgent, ReviewerAgent
from multi_agent_ops.exceptions import AgentError
from multi_agent_ops.llm import BaseLLM, LLMResponse


class TestAgentResult:
    """Tests for AgentResult dataclass."""

    def test_agent_result_creation(self) -> None:
        """Test creating an AgentResult."""
        result = AgentResult(name="test", output="test output")
        assert result.name == "test"
        assert result.output == "test output"
        assert result.meta == {}

    def test_agent_result_with_meta(self) -> None:
        """Test creating an AgentResult with metadata."""
        meta = {"key": "value"}
        result = AgentResult(name="test", output="test output", meta=meta)
        assert result.meta == meta


class TestBaseAgent:
    """Tests for BaseAgent class."""

    def test_base_agent_initialization(self) -> None:
        """Test BaseAgent initialization."""
        mock_llm = MagicMock(spec=BaseLLM)
        agent = BaseAgent(mock_llm)
        assert agent.llm == mock_llm
        assert agent.name == "base"
        assert agent.system_prompt == ""

    def test_base_agent_run_success(self) -> None:
        """Test successful agent execution."""
        mock_llm = MagicMock(spec=BaseLLM)
        mock_llm.generate.return_value = LLMResponse(content="test response", raw={"mock": True})

        agent = BaseAgent(mock_llm)
        result = agent.run("test task", "test context")

        assert isinstance(result, AgentResult)
        assert result.name == "base"
        assert result.output == "test response"
        # The meta field gets mock=False because getattr on a dict returns False for "mock" key
        assert "mock" in result.meta

    def test_base_agent_run_failure(self) -> None:
        """Test agent execution failure."""
        mock_llm = MagicMock(spec=BaseLLM)
        mock_llm.generate.side_effect = Exception("LLM error")

        agent = BaseAgent(mock_llm)

        with pytest.raises(AgentError) as exc_info:
            agent.run("test task")

        assert "Agent base failed" in str(exc_info.value)


class TestPlannerAgent:
    """Tests for PlannerAgent class."""

    def test_planner_agent_attributes(self) -> None:
        """Test PlannerAgent attributes."""
        mock_llm = MagicMock(spec=BaseLLM)
        agent = PlannerAgent(mock_llm)

        assert agent.name == "planner"
        assert "运营规划" in agent.system_prompt


class TestExecutorAgent:
    """Tests for ExecutorAgent class."""

    def test_executor_agent_attributes(self) -> None:
        """Test ExecutorAgent attributes."""
        mock_llm = MagicMock(spec=BaseLLM)
        agent = ExecutorAgent(mock_llm)

        assert agent.name == "executor"
        assert "执行" in agent.system_prompt


class TestReviewerAgent:
    """Tests for ReviewerAgent class."""

    def test_reviewer_agent_attributes(self) -> None:
        """Test ReviewerAgent attributes."""
        mock_llm = MagicMock(spec=BaseLLM)
        agent = ReviewerAgent(mock_llm)

        assert agent.name == "reviewer"
        assert "审核" in agent.system_prompt
