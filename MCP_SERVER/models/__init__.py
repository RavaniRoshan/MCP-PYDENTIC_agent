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
    NavigateAction,
    ExtractAction,
    ExtractMethod,
    ExtractionFormat,
    FormActionModel
)
from .state import BrowserState, TaskExecutionPlan, ActionResult
from .response import TaskResponse, ActionResponse, ErrorResponse
from .extraction import (
    ExtractionRule,
    ExtractionPattern,
    ExtractedData,
    ScrapingTask,
    ScrapingResult
)
from .browser_action import (
    FormField,
    FormDefinition,
    FormData,
    FormActionType,
    FormAction
)

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
    "ExtractAction",
    "ExtractMethod",
    "ExtractionFormat",
    "FormActionModel",
    
    # State Models
    "BrowserState",
    "TaskExecutionPlan", 
    "ActionResult",
    
    # Response Models
    "TaskResponse",
    "ActionResponse",
    "ErrorResponse",
    
    # Extraction Models
    "ExtractionRule",
    "ExtractionPattern",
    "ExtractedData",
    "ScrapingTask",
    "ScrapingResult",
    "FormField",
    "FormDefinition",
    "FormData",
    "FormActionType",
    "FormAction"
]