"""Async workflow orchestration for multi-agent-ops-system."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any

from .agents import ExecutorAgent, PlannerAgent, ReviewerAgent
from .config import AppConfig
from .exceptions import WorkflowError
from .llm import BaseLLM, make_llm
from .tools import MemoryStore, now_iso

logger = logging.getLogger(__name__)

__all__ = ["AsyncWorkflowResult", "AsyncMultiAgentWorkflow"]


@dataclass
class AsyncWorkflowResult:
    """Result from an async workflow execution."""

    plan: str
    execution: str
    review: str
    final_output: str
    metadata: dict[str, Any]


class AsyncMultiAgentWorkflow:
    """Async orchestrator for multiple agents."""

    def __init__(self, config: AppConfig) -> None:
        """Initialize the async workflow with configuration.

        Args:
            config: Application configuration
        """
        self.config = config
        self.llm = make_llm(config.openai_api_key, config.openai_model, config.max_retries)
        self.memory = MemoryStore()
        logger.info("AsyncMultiAgentWorkflow initialized")

    async def _run_agent(self, agent_name: str, system_prompt: str, task: str, context: str = "") -> str:
        """Run a single agent asynchronously.

        Args:
            agent_name: Name of the agent
            system_prompt: System prompt for the agent
            task: Task description
            context: Additional context

        Returns:
            Agent output string
        """
        logger.info("Starting async agent: %s", agent_name)

        # Run LLM generation in a thread pool since it's synchronous
        loop = asyncio.get_event_loop()
        prompt = f"任务：{task}\n\n上下文：{context}\n\n请输出可直接使用的结果。"

        try:
            response = await loop.run_in_executor(
                None,
                lambda: self.llm.generate(system_prompt, prompt),
            )
            logger.info("Async agent %s completed", agent_name)
            return response.content
        except Exception as e:
            logger.error("Async agent %s failed: %s", agent_name, e)
            raise WorkflowError(
                f"Agent {agent_name} failed",
                details={"error": str(e)},
            ) from e

    async def run(self, task: str, max_rounds: int = 1) -> AsyncWorkflowResult:
        """Execute the workflow asynchronously.

        Args:
            task: The task description
            max_rounds: Maximum number of iteration rounds

        Returns:
            AsyncWorkflowResult containing all outputs

        Raises:
            WorkflowError: If workflow execution fails
        """
        logger.info("Starting async workflow execution for task: %s", task[:100])
        self.memory.add("user", task)

        try:
            # Define agent prompts
            planner_prompt = (
                "你是运营规划 Agent。你的职责是拆解目标、定义内容节奏、确定渠道优先级、给出执行计划。"
                "输出时请使用简洁、可执行的要点格式。"
            )
            executor_prompt = (
                "你是执行 Agent。你的职责是根据计划产出具体运营内容、文案、动作清单与落地步骤。"
                "输出时请尽量具体，避免空话。"
            )
            reviewer_prompt = (
                "你是审核 Agent。你的职责是检查方案是否完整、是否可落地、是否缺少 KPI 或风险控制。"
                "输出时请给出可操作的改进建议。"
            )

            # Execute agents sequentially (can be parallelized if needed)
            logger.info("Starting planning phase")
            plan_output = await self._run_agent("planner", planner_prompt, task)
            self.memory.add("planner", plan_output)

            logger.info("Starting execution phase")
            execution_output = await self._run_agent("executor", executor_prompt, task, context=plan_output)
            self.memory.add("executor", execution_output)

            logger.info("Starting review phase")
            review_output = await self._run_agent("reviewer", reviewer_prompt, task, context=execution_output)
            self.memory.add("reviewer", review_output)

            # Compile final output
            final_output = (
                "=== PLAN ===\n"
                f"{plan_output}\n\n"
                "=== EXECUTION ===\n"
                f"{execution_output}\n\n"
                "=== REVIEW ===\n"
                f"{review_output}"
            )

            metadata = {
                "model": self.config.openai_model,
                "mock_mode": self.config.mock_mode,
                "rounds": max_rounds,
                "timestamp": now_iso(),
                "memory": self.memory.export(),
                "async": True,
            }

            logger.info("Async workflow execution completed successfully")
            return AsyncWorkflowResult(
                plan=plan_output,
                execution=execution_output,
                review=review_output,
                final_output=final_output,
                metadata=metadata,
            )
        except Exception as e:
            logger.error("Async workflow execution failed: %s", e)
            raise WorkflowError(
                "Async workflow execution failed",
                details={"task": task[:100], "error": str(e)},
            ) from e

    async def run_parallel(self, task: str, max_rounds: int = 1) -> AsyncWorkflowResult:
        """Execute planning and execution in parallel.

        Args:
            task: The task description
            max_rounds: Maximum number of iteration rounds

        Returns:
            AsyncWorkflowResult containing all outputs

        Raises:
            WorkflowError: If workflow execution fails
        """
        logger.info("Starting parallel async workflow execution for task: %s", task[:100])
        self.memory.add("user", task)

        try:
            # Define agent prompts
            planner_prompt = (
                "你是运营规划 Agent。你的职责是拆解目标、定义内容节奏、确定渠道优先级、给出执行计划。"
                "输出时请使用简洁、可执行的要点格式。"
            )
            executor_prompt = (
                "你是执行 Agent。你的职责是根据计划产出具体运营内容、文案、动作清单与落地步骤。"
                "输出时请尽量具体，避免空话。"
            )
            reviewer_prompt = (
                "你是审核 Agent。你的职责是检查方案是否完整、是否可落地、是否缺少 KPI 或风险控制。"
                "输出时请给出可操作的改进建议。"
            )

            # Run planner and executor in parallel
            logger.info("Starting parallel planning and execution phases")
            plan_task = asyncio.create_task(self._run_agent("planner", planner_prompt, task))
            execution_task = asyncio.create_task(self._run_agent("executor", executor_prompt, task))

            # Wait for both to complete
            plan_output, execution_output = await asyncio.gather(plan_task, execution_task)

            self.memory.add("planner", plan_output)
            self.memory.add("executor", execution_output)

            # Run reviewer with execution context
            logger.info("Starting review phase")
            review_output = await self._run_agent("reviewer", reviewer_prompt, task, context=execution_output)
            self.memory.add("reviewer", review_output)

            # Compile final output
            final_output = (
                "=== PLAN ===\n"
                f"{plan_output}\n\n"
                "=== EXECUTION ===\n"
                f"{execution_output}\n\n"
                "=== REVIEW ===\n"
                f"{review_output}"
            )

            metadata = {
                "model": self.config.openai_model,
                "mock_mode": self.config.mock_mode,
                "rounds": max_rounds,
                "timestamp": now_iso(),
                "memory": self.memory.export(),
                "async": True,
                "parallel": True,
            }

            logger.info("Parallel async workflow execution completed successfully")
            return AsyncWorkflowResult(
                plan=plan_output,
                execution=execution_output,
                review=review_output,
                final_output=final_output,
                metadata=metadata,
            )
        except Exception as e:
            logger.error("Parallel async workflow execution failed: %s", e)
            raise WorkflowError(
                "Parallel async workflow execution failed",
                details={"task": task[:100], "error": str(e)},
            ) from e
