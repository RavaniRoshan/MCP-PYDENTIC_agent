from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from datetime import datetime


class ActionType(str, Enum):
    """
    Enumeration of possible browser action types.
    """
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
    Defines how to identify an element in the browser.

    Attributes:
        type (str): The type of selector (e.g., css, xpath, text).
        value (str): The value of the selector.
        description (Optional[str]): A human-readable description of the element.
    """
    type: str = Field(..., description="Type of selector (css, xpath, text, etc.)")
    value: str = Field(..., description="The selector value")
    description: Optional[str] = Field(None, description="Human-readable description of the element")


class BrowserAction(BaseModel):
    """
    A base class for browser actions.

    Attributes:
        id (str): A unique identifier for the action.
        type (ActionType): The type of the action.
        element (Optional[ElementSelector]): The element to be acted upon.
        value (Optional[Union[str, int, float]]): The value associated with the action.
        description (Optional[str]): A human-readable description of the action.
        timeout (Optional[int]): The timeout for the action in milliseconds.
        created_at (datetime): The timestamp of when the action was created.
        metadata (Optional[Dict[str, Any]]): A dictionary of metadata for the action.
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
    Represents a click action with click-specific parameters.

    Attributes:
        type (ActionType): The type of the action, which is always CLICK.
        button (str): The mouse button to be used for the click (e.g., 'left', 'right', 'middle').
        click_count (int): The number of times to click.
        position (Optional[Dict[str, int]]): The x and y coordinates of the click.
    """
    type: ActionType = ActionType.CLICK
    button: str = "left"
    click_count: int = 1
    position: Optional[Dict[str, int]] = None


class TypeAction(BrowserAction):
    """
    Represents a text input action with type-specific parameters.

    Attributes:
        type (ActionType): The type of the action, which is always TYPE.
        delay (Optional[int]): The delay between keystrokes in milliseconds.
        clear (bool): A flag indicating whether to clear the input field before typing.
    """
    type: ActionType = ActionType.TYPE
    delay: Optional[int] = 10
    clear: bool = True


class NavigateAction(BrowserAction):
    """
    Represents a navigation action with navigation-specific parameters.

    Attributes:
        type (ActionType): The type of the action, which is always NAVIGATE.
        url (str): The URL to navigate to.
        new_tab (bool): A flag indicating whether to open the URL in a new tab.
    """
    type: ActionType = ActionType.NAVIGATE
    url: str
    new_tab: bool = False