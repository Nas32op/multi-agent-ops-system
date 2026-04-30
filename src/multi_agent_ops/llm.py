from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from openai import OpenAI


@dataclass
class LLMResponse:
    content: str
    raw: Any | None = None


class BaseLLM:
    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.4) -> LLMResponse:
        raise NotImplementedError


class OpenAILLM(BaseLLM):
    def __init__(self, api_key: str, model: str):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.4) -> LLMResponse:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )
        content = resp.choices[0].message.content or ""
        return LLMResponse(content=content, raw=resp)


class MockLLM(BaseLLM):
    """Offline fallback so the repo can run without an API key."""

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.4) -> LLMResponse:
        lower = user_prompt.lower()
        if "plan" in lower or "规划" in user_prompt:
            content = "- Day 1: 发布入门内容\n- Day 2: 发布案例拆解\n- Day 3: 发布教程\n- Day 4: 做用户互动\n- Day 5: 推出复盘\n- Day 6: 发布对比内容\n- Day 7: 总结增长建议"
        elif "review" in lower or "审核" in user_prompt or "quality" in lower:
            content = "方案结构完整，但建议补充明确 KPI、每日报告模板和 A/B 测试指标。"
        else:
            content = "根据计划生成了可执行的运营内容，包括选题、节奏、渠道和增长动作。"
        return LLMResponse(content=content, raw={"mock": True})


def make_llm(api_key: str | None, model: str) -> BaseLLM:
    if api_key:
        return OpenAILLM(api_key=api_key, model=model)
    return MockLLM()
