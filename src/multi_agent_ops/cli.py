"""Command-line interface for multi-agent-ops-system."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

from .config import AppConfig, load_task_file
from .exceptions import MultiAgentError
from .workflow import MultiAgentWorkflow

logger = logging.getLogger(__name__)

__all__ = ["build_parser", "main"]


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser.

    Returns:
        Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description="Multi-Agent Ops Automation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m multi_agent_ops.cli --task "制定运营方案"
  python -m multi_agent_ops.cli --task-file examples/example_task.yaml
  python -m multi_agent_ops.cli --task "任务" --output result.json
        """,
    )
    parser.add_argument(
        "--task",
        type=str,
        help="Direct task description",
    )
    parser.add_argument(
        "--task-file",
        type=str,
        help="YAML task file path",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Write result JSON to file",
        default=None,
    )
    parser.add_argument(
        "--max-rounds",
        type=int,
        help="Maximum number of iteration rounds",
        default=1,
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set logging level",
        default="INFO",
    )
    return parser


def setup_logging(level: str) -> None:
    """Setup logging configuration.

    Args:
        level: Logging level
    """
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main() -> int:
    """Main entry point for the CLI.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = build_parser()
    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level)
    logger.info("Starting Multi-Agent Ops System")

    # Validate arguments
    if not args.task and not args.task_file:
        parser.error("Please provide --task or --task-file")

    try:
        # Load task
        if args.task_file:
            logger.info("Loading task from file: %s", args.task_file)
            task_data = load_task_file(args.task_file)
            task = task_data.get("task") or task_data.get("objective") or json.dumps(task_data, ensure_ascii=False)
        else:
            task = args.task

        # Load configuration
        logger.info("Loading configuration")
        cfg = AppConfig.from_env()

        # Execute workflow
        logger.info("Executing workflow with max_rounds=%d", args.max_rounds)
        workflow = MultiAgentWorkflow(cfg)
        result = workflow.run(task, max_rounds=args.max_rounds)

        # Prepare output
        payload = {
            "plan": result.plan,
            "execution": result.execution,
            "review": result.review,
            "final_output": result.final_output,
            "metadata": result.metadata,
        }

        text = json.dumps(payload, ensure_ascii=False, indent=2)
        print(text)

        # Save to file if requested
        if args.output:
            out = Path(args.output)
            out.write_text(text, encoding="utf-8")
            logger.info("Result saved to: %s", out)

        logger.info("Workflow completed successfully")
        return 0

    except MultiAgentError as e:
        logger.error("Application error: %s", e)
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
