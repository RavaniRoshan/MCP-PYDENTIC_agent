from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from models import BrowserAction, ElementSelector, BrowserState, FormField


class BrowserControllerInterface(ABC):
    """
    Abstract interface for browser controllers
    """
    
    @abstractmethod
    async def navigate(self, url: str, new_tab: bool = False) -> bool:
        """Navigate to a URL"""
        pass
    
    @abstractmethod
    async def click(self, selector: ElementSelector, button: str = "left", click_count: int = 1) -> bool:
        """Click on an element"""
        pass
    
    @abstractmethod
    async def type_text(self, selector: ElementSelector, text: str, clear: bool = True) -> bool:
        """Type text into an element"""
        pass
    
    @abstractmethod
    async def extract_text(self, selector: ElementSelector) -> Optional[str]:
        """Extract text from an element"""
        pass
    
    @abstractmethod
    async def extract_multiple(self, selector: ElementSelector, method: str = "text_content") -> Optional[List[Dict[str, Any]]]:
        """Extract multiple elements based on a selector"""
        pass
    
    @abstractmethod
    async def extract_attribute(self, selector: ElementSelector, attr_name: str) -> Optional[str]:
        """Extract a specific attribute from an element"""
        pass
    
    @abstractmethod
    async def extract_table(self, selector: ElementSelector) -> Optional[List[Dict[str, str]]]:
        """Extract table data from an element"""
        pass
    
    @abstractmethod
    async def extract_links(self, selector: ElementSelector = None) -> Optional[List[Dict[str, str]]]:
        """Extract all links from the page or within a specific element"""
        pass
    
    @abstractmethod
    async def extract_images(self, selector: ElementSelector = None) -> Optional[List[Dict[str, str]]]:
        """Extract all images from the page or within a specific element"""
        pass
    
    @abstractmethod
    async def extract_html(self, selector: ElementSelector) -> Optional[str]:
        """Extract HTML content from an element"""
        pass
    
    @abstractmethod
    async def detect_form_fields(self, form_selector: ElementSelector) -> Optional[List[FormField]]:
        """Detect and return all fields in a form"""
        pass
    
    @abstractmethod
    async def fill_form_field(self, field_selector: ElementSelector, value: str) -> bool:
        """Fill a single form field with a value"""
        pass
    
    @abstractmethod
    async def fill_form(self, form_selector: ElementSelector, field_values: Dict[str, str]) -> bool:
        """Fill all fields in a form with provided values"""
        pass
    
    @abstractmethod
    async def submit_form(self, form_selector: ElementSelector) -> bool:
        """Submit a form"""
        pass
    
    @abstractmethod
    async def get_form_values(self, form_selector: ElementSelector) -> Optional[Dict[str, str]]:
        """Extract all current values from form fields"""
        pass
    
    @abstractmethod
    async def get_page_state(self) -> BrowserState:
        """Get the current state of the browser"""
        pass
    
    @abstractmethod
    async def take_screenshot(self, path: str) -> bool:
        """Take a screenshot of the current page"""
        pass
    
    @abstractmethod
    async def wait_for_element(self, selector: ElementSelector, timeout: int = 30000) -> bool:
        """Wait for an element to appear"""
        pass
    
    @abstractmethod
    async def close(self):
        """Close the browser"""
        pass
    
    def get_raw_page(self):
        """
        Get the raw page object for direct access (e.g., Playwright page).
        This allows the compatibility layer to run JavaScript directly.
        """
        pass


class MockBrowserController(BrowserControllerInterface):
    """
    Mock implementation of the browser controller for testing
    """
    
    def __init__(self):
        self.current_url = "about:blank"
        self.current_title = "New Tab"
        self.dom_content = "<html><head></head><body></body></html>"
    
    async def navigate(self, url: str, new_tab: bool = False) -> bool:
        """Navigate to a URL"""
        print(f"Mock navigation to {url}")
        self.current_url = url
        return True
    
    async def click(self, selector: ElementSelector, button: str = "left", click_count: int = 1) -> bool:
        """Click on an element"""
        print(f"Mock click on {selector.value} with {button} button, {click_count} times")
        return True
    
    async def type_text(self, selector: ElementSelector, text: str, clear: bool = True) -> bool:
        """Type text into an element"""
        print(f"Mock typing '{text}' into {selector.value}")
        return True
    
    async def extract_text(self, selector: ElementSelector) -> Optional[str]:
        """Extract text from an element"""
        print(f"Mock text extraction from {selector.value}")
        return "Mock extracted text"
    
    async def extract_multiple(self, selector: ElementSelector, method: str = "text_content") -> Optional[List[Dict[str, Any]]]:
        """Extract multiple elements based on a selector"""
        print(f"Mock multiple extraction from {selector.value} using method {method}")
        return [{"text": "Mock item 1"}, {"text": "Mock item 2"}]
    
    async def extract_attribute(self, selector: ElementSelector, attr_name: str) -> Optional[str]:
        """Extract a specific attribute from an element"""
        print(f"Mock attribute '{attr_name}' extraction from {selector.value}")
        return f"Mock {attr_name} value"
    
    async def extract_table(self, selector: ElementSelector) -> Optional[List[Dict[str, str]]]:
        """Extract table data from an element"""
        print(f"Mock table extraction from {selector.value}")
        return [{"header1": "value1", "header2": "value2"}, {"header1": "value3", "header2": "value4"}]
    
    async def extract_links(self, selector: ElementSelector = None) -> Optional[List[Dict[str, str]]]:
        """Extract all links from the page or within a specific element"""
        print(f"Mock links extraction")
        return [{"text": "Link 1", "href": "https://example.com/1"}, {"text": "Link 2", "href": "https://example.com/2"}]
    
    async def extract_images(self, selector: ElementSelector = None) -> Optional[List[Dict[str, str]]]:
        """Extract all images from the page or within a specific element"""
        print(f"Mock images extraction")
        return [{"alt": "Image 1", "src": "https://example.com/image1.jpg"}, {"alt": "Image 2", "src": "https://example.com/image2.jpg"}]
    
    async def extract_html(self, selector: ElementSelector) -> Optional[str]:
        """Extract HTML content from an element"""
        print(f"Mock HTML extraction from {selector.value}")
        return f"<div>{selector.value}</div>"
    
    async def detect_form_fields(self, form_selector: ElementSelector) -> Optional[List[FormField]]:
        """Detect and return all fields in a form"""
        print(f"Mock detecting form fields in {form_selector.value}")
        return [
            FormField(
                name="name",
                type="text",
                selector=ElementSelector(type="css", value="input[name='name']"),
                required=True,
                label="Name",
                placeholder="Enter your name"
            ),
            FormField(
                name="email",
                type="email",
                selector=ElementSelector(type="css", value="input[name='email']"),
                required=True,
                label="Email",
                placeholder="Enter your email"
            )
        ]
    
    async def fill_form_field(self, field_selector: ElementSelector, value: str) -> bool:
        """Fill a single form field with a value"""
        print(f"Mock filling form field {field_selector.value} with '{value}'")
        return True
    
    async def fill_form(self, form_selector: ElementSelector, field_values: Dict[str, str]) -> bool:
        """Fill all fields in a form with provided values"""
        print(f"Mock filling form {form_selector.value} with values: {field_values}")
        return True
    
    async def submit_form(self, form_selector: ElementSelector) -> bool:
        """Submit a form"""
        print(f"Mock submitting form {form_selector.value}")
        return True
    
    async def get_form_values(self, form_selector: ElementSelector) -> Optional[Dict[str, str]]:
        """Extract all current values from form fields"""
        print(f"Mock getting form values from {form_selector.value}")
        return {"name": "Test Name", "email": "test@example.com"}
    
    async def get_page_state(self) -> BrowserState:
        """Get the current state of the browser"""
        return BrowserState(
            url=self.current_url,
            title=self.current_title,
            dom_content=self.dom_content
        )
    
    async def take_screenshot(self, path: str) -> bool:
        """Take a screenshot of the current page"""
        print(f"Mock screenshot saved to {path}")
        return True
    
    async def wait_for_element(self, selector: ElementSelector, timeout: int = 30000) -> bool:
        """Wait for an element to appear"""
        print(f"Mock waiting for element {selector.value}")
        return True
    
    async def close(self):
        """Close the browser"""
        print("Mock browser closed")
    
    def get_raw_page(self):
        """
        Get the raw page object for direct access (e.g., Playwright page).
        This allows the compatibility layer to run JavaScript directly.
        """
        # For mock, return a mock page object
        class MockPage:
            async def evaluate(self, js_code):
                print(f"Mock evaluating JS: {js_code}")
                return "mock_result"
        
        return MockPage()


# Import the Playwright implementation if available
try:
    from .playwright_controller import PlaywrightBrowserController
except ImportError:
    # If Playwright is not available or fails to import, only use mock
    PlaywrightBrowserController = None