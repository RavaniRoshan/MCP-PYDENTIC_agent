from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from .user_input import TaskRequest
from .state import BrowserState, TaskExecutionPlan, ActionResult


class TaskResponse(BaseModel):
    """
    Complete task execution response
    """
    task_id: str
    status: str  # pending, executing, completed, failed, cancelled
    request: TaskRequest
    plan: Optional[TaskExecutionPlan] = None
    results: List[ActionResult] = Field(default_factory=list)
    final_state: Optional[BrowserState] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time: Optional[float] = None  # in seconds


class ActionResponse(BaseModel):
    """
    Individual action results
    """
    action_id: str
    status: str  # pending, executing, completed, failed
    result: Optional[ActionResult] = None
    next_action: Optional[str] = None  # ID of next action in sequence
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """
    Error handling structure
    """
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None