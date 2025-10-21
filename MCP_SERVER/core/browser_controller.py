from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from models import BrowserAction, ElementSelector, BrowserState


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


# Import the Playwright implementation if available
try:
    from .playwright_controller import PlaywrightBrowserController
except ImportError:
    # If Playwright is not available or fails to import, only use mock
    PlaywrightBrowserController = None