"""
Models package for AutomateAI
"""
from .user_input import UserPrompt, TaskRequest, SafetyPreferences
from .browser_action import (
    ActionType, 
    ElementSelector, 
    BrowserAction, 
    ClickAction, 
    TypeAction, 
    NavigateAction
)
from .state import BrowserState, TaskExecutionPlan, ActionResult
from .response import TaskResponse, ActionResponse, ErrorResponse

__all__ = [
    # User Input Models
    "UserPrompt",
    "TaskRequest", 
    "SafetyPreferences",
    
    # Browser Action Models
    "ActionType",
    "ElementSelector",
    "BrowserAction",
    "ClickAction", 
    "TypeAction",
    "NavigateAction",
    
    # State Models
    "BrowserState",
    "TaskExecutionPlan", 
    "ActionResult",
    
    # Response Models
    "TaskResponse",
    "ActionResponse",
    "ErrorResponse"
]