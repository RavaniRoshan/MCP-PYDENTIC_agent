from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from datetime import datetime


class ExtractMethod(str, Enum):
    """
    Enumeration of possible extraction methods.
    """
    TEXT_CONTENT = "text_content"
    HTML_CONTENT = "html_content"
    ATTRIBUTE = "attribute"
    TABLE = "table"
    LIST = "list"
    FORM_DATA = "form_data"
    LINKS = "links"
    IMAGES = "images"
    CUSTOM_SELECTOR = "custom_selector"


class ExtractionFormat(str, Enum):
    """
    Enumeration of possible extraction formats.
    """
    JSON = "json"
    CSV = "csv"
    TEXT = "text"
    XML = "xml"


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
    FILL_FORM = "fill_form"
    SUBMIT_FORM = "submit_form"
    DETECT_FORM = "detect_form"
    VALIDATE_FORM = "validate_form"


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


class ExtractAction(BrowserAction):
    """
    Represents a data extraction action with extraction-specific parameters.

    Attributes:
        type (ActionType): The type of the action, which is always EXTRACT.
        method (ExtractMethod): The method to use for extraction.
        selector (Optional[ElementSelector]): The element selector for targeted extraction.
        attribute_name (Optional[str]): The name of the attribute to extract (for attribute extraction).
        output_format (ExtractionFormat): The format in which to return the extracted data.
        multiple (bool): Whether to extract multiple elements or just the first match.
        filters (Optional[List[Dict[str, str]]]): Additional filters for the extraction.
        validation_rules (Optional[List[Dict[str, Any]]]): Rules to validate the extracted data.
    """
    type: ActionType = ActionType.EXTRACT
    method: ExtractMethod
    selector: Optional[ElementSelector] = None
    attribute_name: Optional[str] = None
    output_format: ExtractionFormat = ExtractionFormat.JSON
    multiple: bool = False
    filters: Optional[List[Dict[str, str]]] = Field(default_factory=list)
    validation_rules: Optional[List[Dict[str, Any]]] = Field(default_factory=list)


class FormActionModel(BrowserAction):
    """
    Represents a form automation action with form-specific parameters.

    Attributes:
        type (ActionType): The type of the form action.
        form_selector (ElementSelector): Selector for the form to act on.
        field_data (Optional[Dict[str, Any]]): Data to fill into form fields.
        field_selector (Optional[ElementSelector]): Specific field selector for single-field actions.
        submit_after_fill (bool): Whether to submit the form after filling.
    """
    type: ActionType  # Can be FILL_FORM, SUBMIT_FORM, DETECT_FORM, or VALIDATE_FORM
    form_selector: ElementSelector
    field_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    field_selector: Optional[ElementSelector] = None
    submit_after_fill: bool = False


class FormField(BaseModel):
    """
    Represents a form field with its properties.

    Attributes:
        name (str): The name of the form field.
        type (str): The type of the field (text, email, password, checkbox, etc.).
        selector (ElementSelector): Selector to identify the field in the DOM.
        required (bool): Whether this field is required.
        label (Optional[str]): The label associated with this field.
        placeholder (Optional[str]): The placeholder text for this field.
        value (Optional[str]): The current value of the field.
    """
    name: str
    type: str
    selector: ElementSelector
    required: bool = False
    label: Optional[str] = None
    placeholder: Optional[str] = None
    value: Optional[str] = None


class FormDefinition(BaseModel):
    """
    Represents the structure of a form with all its fields.

    Attributes:
        name (str): Name of the form.
        selector (ElementSelector): Selector to identify the form in the DOM.
        fields (List[FormField]): List of fields in the form.
        action (Optional[str]): The form's action attribute (destination URL).
        method (Optional[str]): The form's method (GET, POST).
        validation_rules (Optional[List[Dict[str, Any]]]): Validation rules for the form.
    """
    name: str
    selector: ElementSelector
    fields: List[FormField] = Field(default_factory=list)
    action: Optional[str] = None
    method: Optional[str] = "POST"
    validation_rules: Optional[List[Dict[str, Any]]] = Field(default_factory=list)


class FormData(BaseModel):
    """
    Represents data to be filled into a form.

    Attributes:
        form_id (str): ID of the form to fill.
        field_values (Dict[str, Any]): Values to fill into the form fields.
        submit (bool): Whether to submit the form after filling.
        validation_errors (Optional[List[str]]): Validation errors if any.
    """
    form_id: str
    field_values: Dict[str, Any] = Field(default_factory=dict)
    submit: bool = True
    validation_errors: Optional[List[str]] = Field(default_factory=list)


class FormActionType(str, Enum):
    """
    Enumeration of possible form actions.
    """
    FILL = "fill"
    SUBMIT = "submit"
    VALIDATE = "validate"
    RESET = "reset"
    EXTRACT_VALUES = "extract_values"


class FormAction(BaseModel):
    """
    Represents a form automation action.

    Attributes:
        id (str): A unique identifier for the action.
        type (FormActionType): The type of the form action.
        form_selector (ElementSelector): Selector for the form to act on.
        field_data (Optional[Dict[str, Any]]): Data for form fields (for fill actions).
        field_selector (Optional[ElementSelector]): Specific field selector for single-field actions.
        validate_before_submit (bool): Whether to validate before submitting.
    """
    id: str
    type: FormActionType
    form_selector: ElementSelector
    field_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    field_selector: Optional[ElementSelector] = None
    validate_before_submit: bool = True