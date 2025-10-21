from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class TaskPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class UserPrompt(BaseModel):
    """
    Structured input from users
    """
    prompt: str = Field(..., description="The natural language instruction from the user")
    priority: TaskPriority = TaskPriority.NORMAL
    timeout: Optional[int] = Field(300, description="Maximum execution time in seconds")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    

class TaskRequest(BaseModel):
    """
    Detailed task specifications
    """
    id: str
    user_prompt: UserPrompt
    target_urls: List[str] = Field(default_factory=list)
    expected_outputs: List[str] = Field(default_factory=list)
    safety_preferences: Optional[Dict[str, Any]] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    

class SafetyPreferences(BaseModel):
    """
    User safety settings
    """
    require_confirmation: bool = True
    allowed_domains: List[str] = Field(default_factory=list)
    blocked_actions: List[str] = Field(default_factory=list)
    max_action_count: int = 100
    max_execution_time: int = 300  # 5 minutes