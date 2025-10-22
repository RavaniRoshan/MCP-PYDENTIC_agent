from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from .user_input import TaskRequest
from .state import BrowserState, TaskExecutionPlan, ActionResult


class TaskResponse(BaseModel):
    """
    Represents the complete response for a task execution.

    Attributes:
        task_id (str): The unique identifier for the task.
        status (str): The current status of the task (e.g., pending, executing, completed).
        request (TaskRequest): The original task request.
        plan (Optional[TaskExecutionPlan]): The execution plan for the task.
        results (List[ActionResult]): A list of results for each action in the plan.
        final_state (Optional[BrowserState]): The final state of the browser after the task is completed.
        error (Optional[str]): A description of the error if the task failed.
        started_at (Optional[datetime]): The timestamp of when the task started.
        completed_at (Optional[datetime]): The timestamp of when the task was completed.
        execution_time (Optional[float]): The execution time of the task in seconds.
    """
    task_id: str
    status: str
    request: TaskRequest
    plan: Optional[TaskExecutionPlan] = None
    results: List[ActionResult] = Field(default_factory=list)
    final_state: Optional[BrowserState] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time: Optional[float] = None


class ActionResponse(BaseModel):
    """
    Represents the result of an individual action.

    Attributes:
        action_id (str): The unique identifier for the action.
        status (str): The status of the action (e.g., pending, executing, completed).
        result (Optional[ActionResult]): The result of the action.
        next_action (Optional[str]): The ID of the next action in the sequence.
        timestamp (datetime): The timestamp of when the response was generated.
    """
    action_id: str
    status: str
    result: Optional[ActionResult] = None
    next_action: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """
    Represents an error response.

    Attributes:
        error_code (str): The error code.
        message (str): The error message.
        details (Optional[Dict[str, Any]]): A dictionary of additional error details.
        timestamp (datetime): The timestamp of when the error occurred.
        request_id (Optional[str]): The ID of the request that caused the error.
    """
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None