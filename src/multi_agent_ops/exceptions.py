"""Custom exceptions for multi-agent-ops-system."""

from __future__ import annotations


class MultiAgentError(Exception):
    """Base exception for multi-agent-ops-system."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message


class ConfigurationError(MultiAgentError):
    """Raised when there's a configuration issue."""
    pass


class LLMError(MultiAgentError):
    """Raised when LLM API call fails."""
    pass


class LLMRateLimitError(LLMError):
    """Raised when LLM API rate limit is exceeded."""
    pass


class LLMTimeoutError(LLMError):
    """Raised when LLM API call times out."""
    pass


class AgentError(MultiAgentError):
    """Raised when an agent encounters an error."""
    pass


class WorkflowError(MultiAgentError):
    """Raised when workflow execution fails."""
    pass


class TaskValidationError(MultiAgentError):
    """Raised when task validation fails."""
    pass


class ToolError(MultiAgentError):
    """Raised when a tool execution fails."""
    pass


class RetryExhaustedError(MultiAgentError):
    """Raised when all retry attempts are exhausted."""

    def __init__(self, message: str, attempts: int, last_error: Exception | None = None) -> None:
        super().__init__(message, {"attempts": attempts, "last_error": str(last_error) if last_error else None})
        self.attempts = attempts
        self.last_error = last_error


__all__ = [
    "MultiAgentError",
    "ConfigurationError",
    "LLMError",
    "LLMRateLimitError",
    "LLMTimeoutError",
    "AgentError",
    "WorkflowError",
    "TaskValidationError",
    "ToolError",
    "RetryExhaustedError",
]
