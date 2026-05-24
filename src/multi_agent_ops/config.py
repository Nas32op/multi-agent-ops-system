"""Configuration management for multi-agent-ops-system."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

from .exceptions import ConfigurationError, TaskValidationError

logger = logging.getLogger(__name__)

__all__ = ["AppConfig", "load_task_file"]


class AppConfig(BaseModel):
    """Application configuration with validation."""

    openai_api_key: str | None = Field(default=None, description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o-mini", description="OpenAI model name")
    mock_mode: bool = Field(default=False, description="Whether to use mock mode")
    max_retries: int = Field(default=3, ge=0, le=10, description="Maximum retry attempts")
    retry_delay: float = Field(default=1.0, ge=0, description="Delay between retries in seconds")
    log_level: str = Field(default="INFO", description="Logging level")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v.upper()

    @classmethod
    def from_env(cls) -> AppConfig:
        """Create configuration from environment variables.

        Returns:
            AppConfig instance loaded from environment

        Raises:
            ConfigurationError: If configuration is invalid
        """
        try:
            load_dotenv()
            import os

            api_key = os.getenv("OPENAI_API_KEY")
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            mock_mode = not bool(api_key)
            max_retries = int(os.getenv("MAX_RETRIES", "3"))
            retry_delay = float(os.getenv("RETRY_DELAY", "1.0"))
            log_level = os.getenv("LOG_LEVEL", "INFO")

            config = cls(
                openai_api_key=api_key,
                openai_model=model,
                mock_mode=mock_mode,
                max_retries=max_retries,
                retry_delay=retry_delay,
                log_level=log_level,
            )
            logger.info("Configuration loaded: mock_mode=%s, model=%s", config.mock_mode, config.openai_model)
            return config
        except Exception as e:
            raise ConfigurationError(
                "Failed to load configuration from environment",
                details={"error": str(e)},
            ) from e


def load_task_file(path: str | Path) -> dict[str, Any]:
    """Load and validate a task file.

    Args:
        path: Path to the YAML task file

    Returns:
        Dictionary containing task data

    Raises:
        TaskValidationError: If task file is invalid
        FileNotFoundError: If task file not found
    """
    p = Path(path)
    logger.info("Loading task file: %s", p)

    if not p.exists():
        raise FileNotFoundError(f"Task file not found: {p}")

    try:
        with p.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        if not isinstance(data, dict):
            raise TaskValidationError(
                "Task file must be a YAML mapping/object",
                details={"path": str(p)},
            )

        logger.info("Task file loaded successfully: %d keys", len(data))
        return data
    except yaml.YAMLError as e:
        raise TaskValidationError(
            "Invalid YAML in task file",
            details={"path": str(p), "error": str(e)},
        ) from e
    except Exception as e:
        raise TaskValidationError(
            "Failed to load task file",
            details={"path": str(p), "error": str(e)},
        ) from e
