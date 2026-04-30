from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


@dataclass
class AppConfig:
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    mock_mode: bool = False

    @classmethod
    def from_env(cls) -> "AppConfig":
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        mock_mode = not bool(api_key)
        return cls(openai_api_key=api_key, openai_model=model, mock_mode=mock_mode)


def load_task_file(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Task file not found: {p}")
    with p.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError("Task file must be a YAML mapping/object.")
    return data
