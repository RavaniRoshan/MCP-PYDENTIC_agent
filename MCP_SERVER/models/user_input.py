from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class TaskPriority(str, Enum):
    """
    Enumeration of task priorities.
    """
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class UserPrompt(BaseModel):
    """
    Represents structured input from users.

    Attributes:
        prompt (str): The natural language instruction from the user.
        priority (TaskPriority): The priority of the task.
        timeout (Optional[int]): The maximum execution time in seconds.
        metadata (Optional[Dict[str, Any]]): A dictionary of metadata for the prompt.
    """
    prompt: str = Field(..., description="The natural language instruction from the user")
    priority: TaskPriority = TaskPriority.NORMAL
    timeout: Optional[int] = Field(300, description="Maximum execution time in seconds")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    

class TaskRequest(BaseModel):
    """
    Represents detailed task specifications.

    Attributes:
        id (str): A unique identifier for the task request.
        user_prompt (UserPrompt): The user's prompt.
        target_urls (List[str]): A list of target URLs for the task.
        expected_outputs (List[str]): A list of expected outputs from the task.
        safety_preferences (Optional[Dict[str, Any]]): A dictionary of safety preferences for the task.
        created_at (datetime): The timestamp of when the task request was created.
    """
    id: str
    user_prompt: UserPrompt
    target_urls: List[str] = Field(default_factory=list)
    expected_outputs: List[str] = Field(default_factory=list)
    safety_preferences: Optional[Dict[str, Any]] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    

class SafetyPreferences(BaseModel):
    """
    Represents user safety settings.

    Attributes:
        require_confirmation (bool): A flag indicating whether to require confirmation for risky actions.
        allowed_domains (List[str]): A list of allowed domains.
        blocked_actions (List[str]): A list of blocked actions.
        max_action_count (int): The maximum number of actions allowed in a task.
        max_execution_time (int): The maximum execution time for a task in seconds.
    """
    require_confirmation: bool = True
    allowed_domains: List[str] = Field(default_factory=list)
    blocked_actions: List[str] = Field(default_factory=list)
    max_action_count: int = 100
    max_execution_time: int = 300