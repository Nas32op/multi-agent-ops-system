from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import AppConfig, load_task_file
from .workflow import MultiAgentWorkflow


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Multi-Agent Ops Automation System")
    parser.add_argument("--task", type=str, help="Direct task description")
    parser.add_argument("--task-file", type=str, help="YAML task file path")
    parser.add_argument("--output", type=str, help="Write result JSON to file", default=None)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.task and not args.task_file:
        parser.error("Please provide --task or --task-file")

    if args.task_file:
        task_data = load_task_file(args.task_file)
        task = task_data.get("task") or task_data.get("objective") or json.dumps(task_data, ensure_ascii=False)
    else:
        task = args.task

    cfg = AppConfig.from_env()
    workflow = MultiAgentWorkflow(cfg)
    result = workflow.run(task)

    payload = {
        "plan": result.plan,
        "execution": result.execution,
        "review": result.review,
        "final_output": result.final_output,
        "metadata": result.metadata,
    }

    text = json.dumps(payload, ensure_ascii=False, indent=2)
    print(text)

    if args.output:
        out = Path(args.output)
        out.write_text(text, encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
