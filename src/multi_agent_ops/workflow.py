from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .agents import ExecutorAgent, PlannerAgent, ReviewerAgent
from .config import AppConfig
from .llm import make_llm
from .tools import MemoryStore, now_iso


@dataclass
class WorkflowResult:
    plan: str
    execution: str
    review: str
    final_output: str
    metadata: dict[str, Any]


class MultiAgentWorkflow:
    def __init__(self, config: AppConfig):
        llm = make_llm(config.openai_api_key, config.openai_model)
        self.planner = PlannerAgent(llm)
        self.executor = ExecutorAgent(llm)
        self.reviewer = ReviewerAgent(llm)
        self.memory = MemoryStore()
        self.config = config

    def run(self, task: str, max_rounds: int = 1) -> WorkflowResult:
        self.memory.add("user", task)

        plan_result = self.planner.run(task)
        self.memory.add("planner", plan_result.output)

        execution_result = self.executor.run(task, context=plan_result.output)
        self.memory.add("executor", execution_result.output)

        review_result = self.reviewer.run(task, context=execution_result.output)
        self.memory.add("reviewer", review_result.output)

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
        }

        return WorkflowResult(
            plan=plan_result.output,
            execution=execution_result.output,
            review=review_result.output,
            final_output=final_output,
            metadata=metadata,
        )
