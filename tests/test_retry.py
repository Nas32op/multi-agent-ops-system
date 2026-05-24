"""Tests for retry mechanism."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch

from multi_agent_ops.retry import exponential_backoff, retry, retry_async
from multi_agent_ops.exceptions import RetryExhaustedError


class TestExponentialBackoff:
    """Tests for exponential_backoff function."""

    def test_exponential_backoff_first_attempt(self) -> None:
        """Test backoff calculation for first attempt."""
        delay = exponential_backoff(0, base_delay=1.0)
        assert delay == 1.0

    def test_exponential_backoff_second_attempt(self) -> None:
        """Test backoff calculation for second attempt."""
        delay = exponential_backoff(1, base_delay=1.0)
        assert delay == 2.0

    def test_exponential_backoff_third_attempt(self) -> None:
        """Test backoff calculation for third attempt."""
        delay = exponential_backoff(2, base_delay=1.0)
        assert delay == 4.0

    def test_exponential_backoff_max_delay(self) -> None:
        """Test backoff respects max delay."""
        delay = exponential_backoff(10, base_delay=1.0, max_delay=5.0)
        assert delay == 5.0


class TestRetryDecorator:
    """Tests for retry decorator."""

    @patch("multi_agent_ops.retry.time.sleep")
    def test_retry_success_on_first_attempt(self, mock_sleep: MagicMock) -> None:
        """Test function succeeds on first attempt."""
        @retry(max_attempts=3)
        def successful_func() -> str:
            return "success"

        result = successful_func()
        assert result == "success"
        mock_sleep.assert_not_called()

    @patch("multi_agent_ops.retry.time.sleep")
    def test_retry_success_on_second_attempt(self, mock_sleep: MagicMock) -> None:
        """Test function succeeds on second attempt."""
        call_count = 0

        @retry(max_attempts=3, exceptions=(ValueError,))
        def failing_then_succeeding() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("First attempt fails")
            return "success"

        result = failing_then_succeeding()
        assert result == "success"
        assert call_count == 2
        mock_sleep.assert_called_once()

    @patch("multi_agent_ops.retry.time.sleep")
    def test_retry_exhausted(self, mock_sleep: MagicMock) -> None:
        """Test function fails after all retries exhausted."""
        @retry(max_attempts=3, exceptions=(ValueError,))
        def always_failing() -> str:
            raise ValueError("Always fails")

        with pytest.raises(RetryExhaustedError) as exc_info:
            always_failing()

        assert exc_info.value.attempts == 3
        assert mock_sleep.call_count == 2  # Called between attempts


class TestRetryAsyncDecorator:
    """Tests for retry_async decorator."""

    @pytest.mark.asyncio
    @patch("multi_agent_ops.retry.asyncio.sleep")
    async def test_retry_async_success_on_first_attempt(self, mock_sleep: MagicMock) -> None:
        """Test async function succeeds on first attempt."""
        @retry_async(max_attempts=3)
        async def successful_func() -> str:
            return "success"

        result = await successful_func()
        assert result == "success"
        mock_sleep.assert_not_called()

    @pytest.mark.asyncio
    @patch("multi_agent_ops.retry.asyncio.sleep")
    async def test_retry_async_success_on_second_attempt(self, mock_sleep: MagicMock) -> None:
        """Test async function succeeds on second attempt."""
        call_count = 0

        @retry_async(max_attempts=3, exceptions=(ValueError,))
        async def failing_then_succeeding() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("First attempt fails")
            return "success"

        result = await failing_then_succeeding()
        assert result == "success"
        assert call_count == 2
        mock_sleep.assert_called_once()

    @pytest.mark.asyncio
    @patch("multi_agent_ops.retry.asyncio.sleep")
    async def test_retry_async_exhausted(self, mock_sleep: MagicMock) -> None:
        """Test async function fails after all retries exhausted."""
        @retry_async(max_attempts=3, exceptions=(ValueError,))
        async def always_failing() -> str:
            raise ValueError("Always fails")

        with pytest.raises(RetryExhaustedError) as exc_info:
            await always_failing()

        assert exc_info.value.attempts == 3
        assert mock_sleep.call_count == 2  # Called between attempts
