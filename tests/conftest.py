"""Pytest configuration for multi-agent-ops-system tests."""

from __future__ import annotations

import pytest
from pathlib import Path

from multi_agent_ops.config import AppConfig


@pytest.fixture
def mock_config() -> AppConfig:
    """Create a mock configuration for testing."""
    return AppConfig(
        openai_api_key=None,
        openai_model="gpt-4o-mini",
        mock_mode=True,
        max_retries=1,
        retry_delay=0.0,
        log_level="DEBUG",
    )


@pytest.fixture
def sample_task_file(tmp_path: Path) -> Path:
    """Create a sample task file for testing."""
    task_file = tmp_path / "test_task.yaml"
    task_file.write_text(
        """
title: "测试任务"
objective: "测试目标"
task: "执行测试任务"
""",
        encoding="utf-8",
    )
    return task_file


@pytest.fixture
def complex_task_file(tmp_path: Path) -> Path:
    """Create a complex task file for testing."""
    task_file = tmp_path / "complex_task.yaml"
    task_file.write_text(
        """
title: "AI 学习产品周运营"
objective: "提升新用户激活率与内容转化"
audience: "学生与初级开发者"
constraints:
  tone: "专业、简洁、可执行"
  output_length: "medium"
task: "为一款 AI 学习产品制定 7 天内容运营方案，包含选题、发布节奏、增长策略、复盘指标。"
""",
        encoding="utf-8",
    )
    return task_file
