"""Workflow orchestration for multi-agent-ops-system."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from .agents import ExecutorAgent, PlannerAgent, ReviewerAgent
from .config import AppConfig
from .exceptions import WorkflowError
from .llm import make_llm
from .tools import MemoryStore, now_iso

logger = logging.getLogger(__name__)

__all__ = ["WorkflowResult", "MultiAgentWorkflow"]


@dataclass
class WorkflowResult:
    """Result from a workflow execution."""

    plan: str
    execution: str
    review: str
    final_output: str
    metadata: dict[str, Any]


class MultiAgentWorkflow:
    """Orchestrates multiple agents to complete a task."""

    def __init__(self, config: AppConfig) -> None:
        """Initialize the workflow with configuration.

        Args:
            config: Application configuration
        """
        self.config = config
        llm = make_llm(config.openai_api_key, config.openai_model, config.max_retries)
        self.planner = PlannerAgent(llm)
        self.executor = ExecutorAgent(llm)
        self.reviewer = ReviewerAgent(llm)
        self.memory = MemoryStore()
        logger.info("MultiAgentWorkflow initialized")

    def run(self, task: str, max_rounds: int = 1) -> WorkflowResult:
        """Execute the workflow for the given task.

        Args:
            task: The task description
            max_rounds: Maximum number of iteration rounds

        Returns:
            WorkflowResult containing all outputs

        Raises:
            WorkflowError: If workflow execution fails
        """
        logger.info("Starting workflow execution for task: %s", task[:100])
        self.memory.add("user", task)

        try:
            # Planning phase
            logger.info("Starting planning phase")
            plan_result = self.planner.run(task)
            self.memory.add("planner", plan_result.output)
            logger.info("Planning phase completed")

            # Execution phase
            logger.info("Starting execution phase")
            execution_result = self.executor.run(task, context=plan_result.output)
            self.memory.add("executor", execution_result.output)
            logger.info("Execution phase completed")

            # Review phase
            logger.info("Starting review phase")
            review_result = self.reviewer.run(task, context=execution_result.output)
            self.memory.add("reviewer", review_result.output)
            logger.info("Review phase completed")

            # Compile final output
            final_output = (
                "=== PLAN ===\n"
                f"{plan_result.output}\n\n"
                "=== EXECUTION ===\n"
                f"{execution_result.output}\n\n"
                "=== REVIEW ===\n"
                f"{review_result.output}"
            )

            metadata = {
                "model": self.config.openai_model,
                "mock_mode": self.config.mock_mode,
                "rounds": max_rounds,
                "timestamp": now_iso(),
                "memory": self.memory.export(),
                "agent_results": {
                    "planner": plan_result.meta,
                    "executor": execution_result.meta,
                    "reviewer": review_result.meta,
                },
            }

            logger.info("Workflow execution completed successfully")
            return WorkflowResult(
                plan=plan_result.output,
                execution=execution_result.output,
                review=review_result.output,
                final_output=final_output,
                metadata=metadata,
            )
        except Exception as e:
            logger.error("Workflow execution failed: %s", e)
            raise WorkflowError(
                "Workflow execution failed",
                details={"task": task[:100], "error": str(e)},
            ) from e
