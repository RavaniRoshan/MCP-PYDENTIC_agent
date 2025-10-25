from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from .browser_action import ExtractMethod, ExtractionFormat


class ExtractionRule(BaseModel):
    """
    Defines a rule for data extraction.

    Attributes:
        field_name (str): The name of the field to extract.
        selector (str): CSS or XPath selector for the element.
        attribute (Optional[str]): Attribute to extract instead of text content.
        transform (Optional[str]): Transformation function to apply to the extracted data.
        required (bool): Whether this field is required.
        default_value (Optional[str]): Default value if extraction fails.
    """
    field_name: str = Field(..., description="Name of the field to extract")
    selector: str = Field(..., description="CSS or XPath selector for the element")
    attribute: Optional[str] = Field(None, description="Attribute to extract instead of text content")
    transform: Optional[str] = Field(None, description="Transformation function to apply to the extracted data")
    required: bool = Field(True, description="Whether this field is required")
    default_value: Optional[str] = Field(None, description="Default value if extraction fails")


class ExtractionPattern(BaseModel):
    """
    Defines a pattern for structured data extraction.

    Attributes:
        name (str): Name of the extraction pattern.
        description (Optional[str]): Description of what this pattern extracts.
        rules (List[ExtractionRule]): List of extraction rules.
        method (ExtractMethod): Method to use for extraction.
        output_format (ExtractionFormat): Format for the extracted data.
        pagination_selector (Optional[str]): Selector for pagination elements.
    """
    name: str
    description: Optional[str] = Field(None, description="Description of what this pattern extracts")
    rules: List[ExtractionRule] = Field(default_factory=list)
    method: ExtractMethod
    output_format: ExtractionFormat = ExtractionFormat.JSON
    pagination_selector: Optional[str] = Field(None, description="Selector for pagination elements")


class ExtractedData(BaseModel):
    """
    Represents the result of a data extraction operation.

    Attributes:
        id (str): Unique identifier for the extraction result.
        extracted_content (Union[Dict[str, Any], List[Dict[str, Any]], str]): The extracted data.
        method_used (ExtractMethod): The method used for extraction.
        source_url (str): The URL from which data was extracted.
        extraction_time (datetime): The time when extraction was performed.
        success (bool): Whether the extraction was successful.
        error_message (Optional[str]): Error message if extraction failed.
        metadata (Optional[Dict[str, Any]]): Additional metadata about the extraction.
    """
    id: str
    extracted_content: Union[Dict[str, Any], List[Dict[str, Any]], str]
    method_used: ExtractMethod
    source_url: str
    extraction_time: datetime = Field(default_factory=datetime.utcnow)
    success: bool = True
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ScrapingTask(BaseModel):
    """
    Represents a web scraping task with multiple extraction steps.

    Attributes:
        id (str): Unique identifier for the scraping task.
        name (str): Name of the scraping task.
        start_urls (List[str]): URLs to start scraping from.
        extraction_patterns (List[ExtractionPattern]): Patterns to use for data extraction.
        output_format (ExtractionFormat): Format for the final output.
        max_pages (Optional[int]): Maximum number of pages to scrape.
        delay_between_requests (Optional[float]): Delay between requests in seconds.
        follow_links (bool): Whether to follow links found on pages.
        link_filter_pattern (Optional[str]): Pattern to filter which links to follow.
        headers (Optional[Dict[str, str]]): HTTP headers to use for requests.
        created_at (datetime): Timestamp when the task was created.
    """
    id: str
    name: str = Field(..., description="Name of the scraping task")
    start_urls: List[str] = Field(default_factory=list)
    extraction_patterns: List[ExtractionPattern] = Field(default_factory=list)
    output_format: ExtractionFormat = ExtractionFormat.JSON
    max_pages: Optional[int] = Field(None, description="Maximum number of pages to scrape")
    delay_between_requests: Optional[float] = Field(1.0, description="Delay between requests in seconds")
    follow_links: bool = Field(False, description="Whether to follow links found on pages")
    link_filter_pattern: Optional[str] = Field(None, description="Pattern to filter which links to follow")
    headers: Optional[Dict[str, str]] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ScrapingResult(BaseModel):
    """
    Represents the result of a scraping task.

    Attributes:
        task_id (str): ID of the scraping task.
        results (List[ExtractedData]): List of extracted data objects.
        total_items_extracted (int): Total number of items extracted.
        success_rate (float): Success rate of the extraction process.
        duration (float): Duration of the scraping task in seconds.
        completed_at (datetime): Timestamp when the task was completed.
        error_count (int): Number of errors encountered during scraping.
        errors (List[Dict[str, str]]): List of errors encountered.
    """
    task_id: str
    results: List[ExtractedData] = Field(default_factory=list)
    total_items_extracted: int = 0
    success_rate: float = 0.0
    duration: float
    completed_at: datetime = Field(default_factory=datetime.utcnow)
    error_count: int = 0
    errors: List[Dict[str, str]] = Field(default_factory=list)