"""Tests for configuration management."""

from __future__ import annotations

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from multi_agent_ops.config import AppConfig, load_task_file
from multi_agent_ops.exceptions import ConfigurationError, TaskValidationError


class TestAppConfig:
    """Tests for AppConfig class."""

    def test_app_config_defaults(self) -> None:
        """Test AppConfig default values."""
        config = AppConfig()
        assert config.openai_api_key is None
        assert config.openai_model == "gpt-4o-mini"
        assert config.mock_mode is False
        assert config.max_retries == 3
        assert config.retry_delay == 1.0
        assert config.log_level == "INFO"

    def test_app_config_custom_values(self) -> None:
        """Test AppConfig with custom values."""
        config = AppConfig(
            openai_api_key="test-key",
            openai_model="gpt-4",
            mock_mode=True,
            max_retries=5,
            retry_delay=2.0,
            log_level="DEBUG",
        )
        assert config.openai_api_key == "test-key"
        assert config.openai_model == "gpt-4"
        assert config.mock_mode is True
        assert config.max_retries == 5
        assert config.retry_delay == 2.0
        assert config.log_level == "DEBUG"

    def test_app_config_validation_log_level(self) -> None:
        """Test log level validation."""
        with pytest.raises(ValueError):
            AppConfig(log_level="INVALID")

    def test_app_config_from_env(self) -> None:
        """Test loading config from environment variables."""
        with patch("multi_agent_ops.config.load_dotenv") as mock_load_dotenv:
            with patch("os.getenv") as mock_getenv:
                mock_getenv.side_effect = lambda key, default=None: {
                    "OPENAI_API_KEY": "test-key",
                    "OPENAI_MODEL": "gpt-4",
                    "MAX_RETRIES": "5",
                    "RETRY_DELAY": "2.0",
                    "LOG_LEVEL": "DEBUG",
                }.get(key, default)

                config = AppConfig.from_env()
                assert config.openai_api_key == "test-key"
                assert config.openai_model == "gpt-4"
                assert config.mock_mode is False
                assert config.max_retries == 5
                assert config.retry_delay == 2.0
                assert config.log_level == "DEBUG"


class TestLoadTaskFile:
    """Tests for load_task_file function."""

    def test_load_task_file_success(self, tmp_path: Path) -> None:
        """Test loading a valid task file."""
        task_file = tmp_path / "test_task.yaml"
        task_file.write_text("task: Test task\ntitle: Test", encoding="utf-8")

        result = load_task_file(task_file)
        assert result["task"] == "Test task"
        assert result["title"] == "Test"

    def test_load_task_file_not_found(self) -> None:
        """Test loading a non-existent task file."""
        with pytest.raises(FileNotFoundError):
            load_task_file("nonexistent.yaml")

    def test_load_task_file_invalid_yaml(self, tmp_path: Path) -> None:
        """Test loading an invalid YAML file."""
        task_file = tmp_path / "invalid.yaml"
        task_file.write_text("invalid: yaml: content: [", encoding="utf-8")

        with pytest.raises(TaskValidationError):
            load_task_file(task_file)

    def test_load_task_file_not_mapping(self, tmp_path: Path) -> None:
        """Test loading a YAML file that's not a mapping."""
        task_file = tmp_path / "list.yaml"
        task_file.write_text("- item1\n- item2", encoding="utf-8")

        with pytest.raises(TaskValidationError):
            load_task_file(task_file)
