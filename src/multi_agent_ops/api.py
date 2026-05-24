"""FastAPI Web API for multi-agent-ops-system."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .config import AppConfig
from .exceptions import MultiAgentError
from .workflow import MultiAgentWorkflow

logger = logging.getLogger(__name__)

__all__ = ["app", "TaskRequest", "TaskResponse", "HealthResponse"]


class TaskRequest(BaseModel):
    """Request model for task execution."""

    task: str = Field(..., description="Task description", min_length=1)
    max_rounds: int = Field(default=1, ge=1, le=10, description="Maximum iteration rounds")


class TaskResponse(BaseModel):
    """Response model for task execution."""

    plan: str = Field(..., description="Planning output")
    execution: str = Field(..., description="Execution output")
    review: str = Field(..., description="Review output")
    final_output: str = Field(..., description="Combined final output")
    metadata: dict[str, Any] = Field(..., description="Execution metadata")


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Application version")
    mock_mode: bool = Field(..., description="Whether mock mode is enabled")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager.

    Args:
        app: FastAPI application instance

    Yields:
        None
    """
    logger.info("Starting Multi-Agent Ops API")
    yield
    logger.info("Shutting down Multi-Agent Ops API")


app = FastAPI(
    title="Multi-Agent Ops API",
    description="API for multi-agent operations automation system",
    version="0.2.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint.

    Returns:
        HealthResponse with service status
    """
    config = AppConfig.from_env()
    return HealthResponse(
        status="healthy",
        version="0.2.0",
        mock_mode=config.mock_mode,
    )


@app.post("/api/v1/tasks", response_model=TaskResponse)
async def execute_task(request: TaskRequest) -> TaskResponse:
    """Execute a task using the multi-agent workflow.

    Args:
        request: Task request containing task description and parameters

    Returns:
        TaskResponse with execution results

    Raises:
        HTTPException: If task execution fails
    """
    logger.info("Received task request: %s", request.task[:100])

    try:
        config = AppConfig.from_env()
        workflow = MultiAgentWorkflow(config)
        result = workflow.run(request.task, max_rounds=request.max_rounds)

        return TaskResponse(
            plan=result.plan,
            execution=result.execution,
            review=result.review,
            final_output=result.final_output,
            metadata=result.metadata,
        )
    except MultiAgentError as e:
        logger.error("Task execution failed: %s", e)
        raise HTTPException(
            status_code=400,
            detail={"error": e.message, "details": e.details},
        ) from e
    except Exception as e:
        logger.error("Unexpected error during task execution: %s", e)
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error", "details": str(e)},
        ) from e


@app.post("/api/v1/tasks/async")
async def execute_task_async(request: TaskRequest, background_tasks: BackgroundTasks) -> dict[str, str]:
    """Execute a task asynchronously.

    Args:
        request: Task request containing task description and parameters
        background_tasks: FastAPI background tasks

    Returns:
        Dictionary with task ID for status checking
    """
    import uuid

    task_id = str(uuid.uuid4())
    logger.info("Starting async task execution: %s", task_id)

    # In a real implementation, you would store the task status in a database
    # and use a task queue like Celery or RQ
    background_tasks.add_task(_execute_background_task, task_id, request)

    return {
        "task_id": task_id,
        "status": "accepted",
        "message": "Task accepted for background execution",
    }


async def _execute_background_task(task_id: str, request: TaskRequest) -> None:
    """Execute a task in the background.

    Args:
        task_id: Unique task identifier
        request: Task request
    """
    try:
        logger.info("Background task %s started", task_id)
        config = AppConfig.from_env()
        workflow = MultiAgentWorkflow(config)
        result = workflow.run(request.task, max_rounds=request.max_rounds)
        logger.info("Background task %s completed successfully", task_id)

        # In a real implementation, you would store the result in a database
        # and notify the client via WebSocket or polling

    except Exception as e:
        logger.error("Background task %s failed: %s", task_id, e)


@app.get("/api/v1/tasks/{task_id}")
async def get_task_status(task_id: str) -> dict[str, Any]:
    """Get the status of an async task.

    Args:
        task_id: Unique task identifier

    Returns:
        Dictionary with task status

    Raises:
        HTTPException: If task not found
    """
    # In a real implementation, you would look up the task status in a database
    # This is a placeholder implementation
    return {
        "task_id": task_id,
        "status": "not_implemented",
        "message": "Task status checking not implemented in this version",
    }


def start_api(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Start the API server.

    Args:
        host: Host to bind to
        port: Port to bind to
    """
    import uvicorn

    logger.info("Starting API server on %s:%d", host, port)
    uvicorn.run(app, host=host, port=port)
