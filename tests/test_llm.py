"""Tests for LLM implementations."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch

from multi_agent_ops.llm import BaseLLM, OpenAILLM, MockLLM, LLMResponse, make_llm
from multi_agent_ops.exceptions import LLMError, LLMRateLimitError, LLMTimeoutError


class TestLLMResponse:
    """Tests for LLMResponse dataclass."""

    def test_llm_response_creation(self) -> None:
        """Test creating an LLMResponse."""
        response = LLMResponse(content="test content")
        assert response.content == "test content"
        assert response.raw is None

    def test_llm_response_with_raw(self) -> None:
        """Test creating an LLMResponse with raw data."""
        raw_data = {"key": "value"}
        response = LLMResponse(content="test content", raw=raw_data)
        assert response.raw == raw_data


class TestMockLLM:
    """Tests for MockLLM class."""

    def test_mock_llm_plan_response(self) -> None:
        """Test MockLLM response for planning tasks."""
        llm = MockLLM()
        response = llm.generate("system", "请规划一下这个任务")

        assert "Day 1" in response.content
        assert response.raw == {"mock": True}

    def test_mock_llm_review_response(self) -> None:
        """Test MockLLM response for review tasks."""
        llm = MockLLM()
        response = llm.generate("system", "请审核这个方案")

        assert "KPI" in response.content
        assert response.raw == {"mock": True}

    def test_mock_llm_execution_response(self) -> None:
        """Test MockLLM response for execution tasks."""
        llm = MockLLM()
        response = llm.generate("system", "执行这个任务")

        assert "运营内容" in response.content
        assert response.raw == {"mock": True}


class TestMakeLLM:
    """Tests for make_llm function."""

    def test_make_llm_with_api_key(self) -> None:
        """Test creating LLM with API key."""
        with patch("multi_agent_ops.llm.OpenAI") as mock_openai:
            llm = make_llm("test-key", "gpt-4")
            assert isinstance(llm, OpenAILLM)
            mock_openai.assert_called_once_with(api_key="test-key")

    def test_make_llm_without_api_key(self) -> None:
        """Test creating LLM without API key (mock mode)."""
        llm = make_llm(None, "gpt-4")
        assert isinstance(llm, MockLLM)

    def test_make_llm_with_empty_api_key(self) -> None:
        """Test creating LLM with empty API key."""
        llm = make_llm("", "gpt-4")
        assert isinstance(llm, MockLLM)
