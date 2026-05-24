"""Retry mechanism for multi-agent-ops-system."""

from __future__ import annotations

import asyncio
import functools
import logging
import time
from typing import Any, Callable, TypeVar

from .exceptions import RetryExhaustedError

logger = logging.getLogger(__name__)

__all__ = ["retry", "retry_async", "exponential_backoff"]

F = TypeVar("F", bound=Callable[..., Any])


def exponential_backoff(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
    """Calculate exponential backoff delay.

    Args:
        attempt: Current attempt number (0-based)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds

    Returns:
        Delay in seconds
    """
    delay = min(base_delay * (2 ** attempt), max_delay)
    return delay


def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[F], F]:
    """Decorator to retry a function on failure.

    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Base delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exceptions: Tuple of exception types to catch

    Returns:
        Decorated function
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        delay = exponential_backoff(attempt, base_delay, max_delay)
                        logger.warning(
                            "Attempt %d/%d failed: %s. Retrying in %.2f seconds...",
                            attempt + 1,
                            max_attempts,
                            str(e),
                            delay,
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            "All %d attempts failed. Last error: %s",
                            max_attempts,
                            str(e),
                        )

            raise RetryExhaustedError(
                f"All {max_attempts} retry attempts exhausted",
                attempts=max_attempts,
                last_error=last_exception,
            )

        return wrapper  # type: ignore

    return decorator


def retry_async(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[F], F]:
    """Decorator to retry an async function on failure.

    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Base delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exceptions: Tuple of exception types to catch

    Returns:
        Decorated async function
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        delay = exponential_backoff(attempt, base_delay, max_delay)
                        logger.warning(
                            "Attempt %d/%d failed: %s. Retrying in %.2f seconds...",
                            attempt + 1,
                            max_attempts,
                            str(e),
                            delay,
                        )
                        await asyncio.sleep(delay)
                    else:
                        logger.error(
                            "All %d attempts failed. Last error: %s",
                            max_attempts,
                            str(e),
                        )

            raise RetryExhaustedError(
                f"All {max_attempts} retry attempts exhausted",
                attempts=max_attempts,
                last_error=last_exception,
            )

        return wrapper  # type: ignore

    return decorator
