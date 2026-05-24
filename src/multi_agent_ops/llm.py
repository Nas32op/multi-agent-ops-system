"""LLM implementations for multi-agent-ops-system."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from openai import OpenAI, APIError, RateLimitError, APITimeoutError

from .exceptions import LLMError, LLMRateLimitError, LLMTimeoutError
from .retry import retry

logger = logging.getLogger(__name__)

__all__ = ["LLMResponse", "BaseLLM", "OpenAILLM", "MockLLM", "make_llm"]


@dataclass
class LLMResponse:
    """Response from an LLM call."""

    content: str
    raw: Any | None = None


class BaseLLM:
    """Base class for LLM implementations."""

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.4) -> LLMResponse:
        """Generate a response from the LLM.

        Args:
            system_prompt: The system prompt
            user_prompt: The user prompt
            temperature: Sampling temperature

        Returns:
            LLMResponse containing the generated content

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError


class OpenAILLM(BaseLLM):
    """OpenAI API LLM implementation."""

    def __init__(self, api_key: str, model: str, max_retries: int = 3) -> None:
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.max_retries = max_retries
        self.logger = logging.getLogger(f"{__name__}.OpenAI")

    @retry(max_attempts=3, exceptions=(LLMRateLimitError, LLMTimeoutError, LLMError))
    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.4) -> LLMResponse:
        """Generate a response using OpenAI API.

        Args:
            system_prompt: The system prompt
            user_prompt: The user prompt
            temperature: Sampling temperature

        Returns:
            LLMResponse containing the generated content

        Raises:
            LLMRateLimitError: If rate limit is exceeded
            LLMTimeoutError: If the request times out
            LLMError: If the API call fails
        """
        self.logger.info("Calling OpenAI API with model %s", self.model)
        self.logger.debug("System prompt length: %d, User prompt length: %d", len(system_prompt), len(user_prompt))

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
            )
            content = resp.choices[0].message.content or ""
            self.logger.info("OpenAI API call successful, response length: %d", len(content))
            return LLMResponse(content=content, raw=resp)
        except RateLimitError as e:
            self.logger.warning("OpenAI API rate limit exceeded: %s", e)
            raise LLMRateLimitError(
                "OpenAI API rate limit exceeded",
                details={"model": self.model, "error": str(e)},
            ) from e
        except APITimeoutError as e:
            self.logger.warning("OpenAI API timeout: %s", e)
            raise LLMTimeoutError(
                "OpenAI API request timed out",
                details={"model": self.model, "error": str(e)},
            ) from e
        except APIError as e:
            self.logger.error("OpenAI API error: %s", e)
            raise LLMError(
                "OpenAI API call failed",
                details={"model": self.model, "error": str(e)},
            ) from e
        except Exception as e:
            self.logger.error("Unexpected error calling OpenAI API: %s", e)
            raise LLMError(
                "Unexpected error calling OpenAI API",
                details={"model": self.model, "error": str(e)},
            ) from e


class MockLLM(BaseLLM):
    """Offline fallback so the repo can run without an API key."""

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.4) -> LLMResponse:
        """Generate a mock response for testing.

        Args:
            system_prompt: The system prompt
            user_prompt: The user prompt
            temperature: Sampling temperature (ignored)

        Returns:
            LLMResponse containing mock content
        """
        logger.info("Using MockLLM for response generation")
        lower = user_prompt.lower()

        if "plan" in lower or "规划" in user_prompt:
            content = "- Day 1: 发布入门内容\n- Day 2: 发布案例拆解\n- Day 3: 发布教程\n- Day 4: 做用户互动\n- Day 5: 推出复盘\n- Day 6: 发布对比内容\n- Day 7: 总结增长建议"
        elif "review" in lower or "审核" in user_prompt or "quality" in lower:
            content = "方案结构完整，但建议补充明确 KPI、每日报告模板和 A/B 测试指标。"
        else:
            content = "根据计划生成了可执行的运营内容，包括选题、节奏、渠道和增长动作。"

        logger.debug("MockLLM generated content length: %d", len(content))
        return LLMResponse(content=content, raw={"mock": True})


def make_llm(api_key: str | None, model: str, max_retries: int = 3) -> BaseLLM:
    """Create an LLM instance based on the provided API key.

    Args:
        api_key: OpenAI API key (None for mock mode)
        model: Model name to use
        max_retries: Maximum number of retry attempts

    Returns:
        BaseLLM instance (OpenAILLM or MockLLM)
    """
    if api_key:
        logger.info("Creating OpenAILLM with model %s", model)
        return OpenAILLM(api_key=api_key, model=model, max_retries=max_retries)
    logger.info("No API key provided, using MockLLM")
    return MockLLM()
