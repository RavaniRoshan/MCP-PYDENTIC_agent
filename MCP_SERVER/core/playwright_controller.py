from .browser_controller import BrowserControllerInterface
from models import ElementSelector, BrowserState
from core.config import settings
from typing import Optional
import asyncio
import base64


class PlaywrightBrowserController(BrowserControllerInterface):
    """
    Playwright-based implementation of the browser controller
    """
    
    def __init__(self):
        self.browser = None
        self.page = None
        self.context = None
        
    async def initialize(self):
        """
        Initialize the Playwright browser instance
        """
        try:
            from playwright.async_api import async_playwright
            
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=settings.browser_headless
            )
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()
        except ImportError:
            raise RuntimeError("Playwright is not installed. Please install it using 'pip install playwright' and run 'playwright install'")
    
    async def _ensure_initialized(self):
        """
        Ensure the browser is initialized before performing actions
        """
        if self.browser is None:
            await self.initialize()
    
    async def navigate(self, url: str, new_tab: bool = False) -> bool:
        """Navigate to a URL"""
        await self._ensure_initialized()
        
        try:
            if new_tab:
                self.page = await self.context.new_page()
            
            await self.page.goto(url, timeout=settings.browser_timeout)
            return True
        except Exception as e:
            print(f"Navigation error: {e}")
            return False
    
    async def click(self, selector: ElementSelector, button: str = "left", click_count: int = 1) -> bool:
        """Click on an element"""
        await self._ensure_initialized()
        
        try:
            # Convert the selector to Playwright format
            playwright_selector = await self._convert_selector(selector)
            
            # Wait for the element to be visible
            await self.page.wait_for_selector(playwright_selector, state="visible")
            
            # Perform the click action
            await self.page.click(playwright_selector, button=button, click_count=click_count)
            return True
        except Exception as e:
            print(f"Click error: {e}")
            return False
    
    async def type_text(self, selector: ElementSelector, text: str, clear: bool = True) -> bool:
        """Type text into an element"""
        await self._ensure_initialized()
        
        try:
            # Convert the selector to Playwright format
            playwright_selector = await self._convert_selector(selector)
            
            # Wait for the element to be visible
            await self.page.wait_for_selector(playwright_selector, state="visible")
            
            if clear:
                await self.page.fill(playwright_selector, "")
            
            await self.page.type(playwright_selector, text, delay=settings.browser_timeout/1000)
            return True
        except Exception as e:
            print(f"Type text error: {e}")
            return False
    
    async def extract_text(self, selector: ElementSelector) -> Optional[str]:
        """Extract text from an element"""
        await self._ensure_initialized()
        
        try:
            # Convert the selector to Playwright format
            playwright_selector = await self._convert_selector(selector)
            
            # Wait for the element to be visible
            await self.page.wait_for_selector(playwright_selector, state="visible")
            
            # Get the text content
            text = await self.page.text_content(playwright_selector)
            return text
        except Exception as e:
            print(f"Text extraction error: {e}")
            return None
    
    async def get_page_state(self) -> BrowserState:
        """Get the current state of the browser"""
        await self._ensure_initialized()
        
        try:
            url = self.page.url
            title = await self.page.title()
            dom_content = await self.page.content()
            
            # Get viewport size
            viewport_size = {
                "width": self.page.viewport_size["width"],
                "height": self.page.viewport_size["height"]
            }
            
            return BrowserState(
                url=url,
                title=title,
                dom_content=dom_content,
                viewport_size=viewport_size
            )
        except Exception as e:
            print(f"Get page state error: {e}")
            return BrowserState(
                url="about:blank",
                title="Error",
                dom_content="<html><body>Error retrieving page state</body></html>"
            )
    
    async def take_screenshot(self, path: str) -> bool:
        """Take a screenshot of the current page"""
        await self._ensure_initialized()
        
        try:
            await self.page.screenshot(path=path)
            return True
        except Exception as e:
            print(f"Screenshot error: {e}")
            return False
    
    async def wait_for_element(self, selector: ElementSelector, timeout: int = 30000) -> bool:
        """Wait for an element to appear"""
        await self._ensure_initialized()
        
        try:
            playwright_selector = await self._convert_selector(selector)
            await self.page.wait_for_selector(playwright_selector, state="visible", timeout=timeout)
            return True
        except Exception:
            return False
    
    async def close(self):
        """Close the browser"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def _convert_selector(self, element_selector: ElementSelector) -> str:
        """
        Convert our ElementSelector to Playwright selector format
        """
        if element_selector.type == "css":
            return element_selector.value
        elif element_selector.type == "xpath":
            return f"xpath={element_selector.value}"
        elif element_selector.type == "text":
            return f"text={element_selector.value}"
        elif element_selector.type == "id":
            return f"id={element_selector.value}"
        else:
            # Default to CSS selector
            return element_selector.value