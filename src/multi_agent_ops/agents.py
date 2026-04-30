from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .llm import BaseLLM


@dataclass
class AgentResult:
    name: str
    output: str
    meta: dict[str, Any] | None = None


class BaseAgent:
    name: str = "base"
    system_prompt: str = ""

    def __init__(self, llm: BaseLLM):
        self.llm = llm

    def run(self, task: str, context: str = "") -> AgentResult:
        prompt = f"任务：{task}\n\n上下文：{context}\n\n请输出可直接使用的结果。"
        response = self.llm.generate(self.system_prompt, prompt)
        return AgentResult(name=self.name, output=response.content, meta={"mock": getattr(response.raw, "mock", False)})


class PlannerAgent(BaseAgent):
    name = "planner"
    system_prompt = (
        "你是运营规划 Agent。你的职责是拆解目标、定义内容节奏、确定渠道优先级、给出执行计划。"
        "输出时请使用简洁、可执行的要点格式。"
    )


class ExecutorAgent(BaseAgent):
    name = "executor"
    system_prompt = (
        "你是执行 Agent。你的职责是根据计划产出具体运营内容、文案、动作清单与落地步骤。"
        "输出时请尽量具体，避免空话。"
    )


class ReviewerAgent(BaseAgent):
    name = "reviewer"
    system_prompt = (
        "你是审核 Agent。你的职责是检查方案是否完整、是否可落地、是否缺少 KPI 或风险控制。"
        "输出时请给出可操作的改进建议。"
    )
