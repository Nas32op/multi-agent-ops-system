"""Agent implementations for multi-agent-ops-system."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from .exceptions import AgentError, LLMError
from .llm import BaseLLM

logger = logging.getLogger(__name__)

__all__ = ["AgentResult", "BaseAgent", "PlannerAgent", "ExecutorAgent", "ReviewerAgent"]


@dataclass
class AgentResult:
    """Result from an agent execution."""

    name: str
    output: str
    meta: dict[str, Any] = field(default_factory=dict)


class BaseAgent:
    """Base class for all agents."""

    name: str = "base"
    system_prompt: str = ""

    def __init__(self, llm: BaseLLM) -> None:
        self.llm = llm
        self.logger = logging.getLogger(f"{__name__}.{self.name}")

    def run(self, task: str, context: str = "") -> AgentResult:
        """Execute the agent with the given task and context.

        Args:
            task: The task description
            context: Additional context from previous agents

        Returns:
            AgentResult containing the agent's output

        Raises:
            AgentError: If the agent fails to execute
        """
        self.logger.info("Agent %s starting execution", self.name)
        self.logger.debug("Task: %s, Context length: %d", task[:100], len(context))

        prompt = f"任务：{task}\n\n上下文：{context}\n\n请输出可直接使用的结果。"

        try:
            response = self.llm.generate(self.system_prompt, prompt)
            result = AgentResult(
                name=self.name,
                output=response.content,
                meta={"mock": getattr(response.raw, "mock", False)},
            )
            self.logger.info("Agent %s completed successfully", self.name)
            return result
        except LLMError as e:
            self.logger.error("Agent %s failed due to LLM error: %s", self.name, e)
            raise AgentError(
                f"Agent {self.name} failed to execute",
                details={"task": task[:100], "error": str(e)},
            ) from e
        except Exception as e:
            self.logger.error("Agent %s failed with unexpected error: %s", self.name, e)
            raise AgentError(
                f"Agent {self.name} failed with unexpected error",
                details={"task": task[:100], "error": str(e)},
            ) from e


class PlannerAgent(BaseAgent):
    """Agent responsible for planning and strategy."""

    name = "planner"
    system_prompt = (
        "你是运营规划 Agent。你的职责是拆解目标、定义内容节奏、确定渠道优先级、给出执行计划。"
        "输出时请使用简洁、可执行的要点格式。"
    )


class ExecutorAgent(BaseAgent):
    """Agent responsible for executing tasks and generating content."""

    name = "executor"
    system_prompt = (
        "你是执行 Agent。你的职责是根据计划产出具体运营内容、文案、动作清单与落地步骤。"
        "输出时请尽量具体，避免空话。"
    )


class ReviewerAgent(BaseAgent):
    """Agent responsible for reviewing and quality assurance."""

    name = "reviewer"
    system_prompt = (
        "你是审核 Agent。你的职责是检查方案是否完整、是否可落地、是否缺少 KPI 或风险控制。"
        "输出时请给出可操作的改进建议。"
    )
