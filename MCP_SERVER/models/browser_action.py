from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from datetime import datetime


class ActionType(str, Enum):
    CLICK = "click"
    TYPE = "type"
    NAVIGATE = "navigate"
    EXTRACT = "extract"
    WAIT = "wait"
    SCREENSHOT = "screenshot"
    HOVER = "hover"
    SCROLL = "scroll"


class ElementSelector(BaseModel):
    """
    Defines how to identify an element in the browser
    """
    type: str = Field(..., description="Type of selector (css, xpath, text, etc.)")
    value: str = Field(..., description="The selector value")
    description: Optional[str] = Field(None, description="Human-readable description of the element")


class BrowserAction(BaseModel):
    """
    Base class for browser actions
    """
    id: str
    type: ActionType
    element: Optional[ElementSelector] = None
    value: Optional[Union[str, int, float]] = None
    description: Optional[str] = Field(None, description="Human-readable description of the action")
    timeout: Optional[int] = 30000  # 30 seconds
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ClickAction(BrowserAction):
    """
    Click-specific parameters
    """
    type: ActionType = ActionType.CLICK
    button: str = "left"  # left, right, middle
    click_count: int = 1
    position: Optional[Dict[str, int]] = None  # x, y coordinates


class TypeAction(BrowserAction):
    """
    Text input parameters
    """
    type: ActionType = ActionType.TYPE
    delay: Optional[int] = 10  # milliseconds between keystrokes
    clear: bool = True


class NavigateAction(BrowserAction):
    """
    Navigation commands
    """
    type: ActionType = ActionType.NAVIGATE
    url: str
    new_tab: bool = False