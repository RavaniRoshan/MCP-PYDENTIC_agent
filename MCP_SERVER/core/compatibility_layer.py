from typing import Dict, List, Optional, Any, Callable
from abc import ABC, abstractmethod
import asyncio
import logging
from enum import Enum
from dataclasses import dataclass
from models import ElementSelector
from core.browser_controller import BrowserControllerInterface


class BrowserType(str, Enum):
    """
    Enumeration of supported browser types.
    """
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"


@dataclass
class CompatibilityRule:
    """
    A rule for handling compatibility issues with specific websites or technologies.
    
    Attributes:
        id: Unique identifier for the rule
        description: Human-readable description of what the rule handles
        selector: CSS/XPath selector to identify problematic elements
        action: Action to take when the element is encountered
        parameters: Additional parameters for the action
        priority: Priority of the rule (higher numbers are applied first)
        applies_to: List of URLs or domains where the rule applies
    """
    id: str
    description: str
    selector: str
    action: str  # e.g., "wait_and_click", "scroll_into_view", "use_alternative_selector"
    parameters: Optional[Dict[str, Any]] = None
    priority: int = 0
    applies_to: Optional[List[str]] = None


class CompatibilityHandlerInterface(ABC):
    """
    Abstract interface for compatibility handlers.
    """
    
    @abstractmethod
    async def detect_compatibility_issues(self, page_content: str, url: str) -> List[CompatibilityRule]:
        """
        Detects potential compatibility issues on a web page.
        
        Args:
            page_content: The HTML content of the page
            url: The URL of the page
            
        Returns:
            List of compatibility rules that apply to the page
        """
        pass
    
    @abstractmethod
    async def apply_compatibility_rule(self, rule: CompatibilityRule, controller: BrowserControllerInterface) -> bool:
        """
        Applies a compatibility rule using the browser controller.
        
        Args:
            rule: The compatibility rule to apply
            controller: The browser controller to use
            
        Returns:
            True if the rule was applied successfully, False otherwise
        """
        pass


class UniversalCompatibilityHandler(CompatibilityHandlerInterface):
    """
    A universal compatibility handler that manages compatibility rules for different websites.
    """
    
    def __init__(self):
        self.rules: List[CompatibilityRule] = []
        self.logger = logging.getLogger(__name__)
        self._load_default_rules()
    
    def _load_default_rules(self):
        """
        Loads default compatibility rules for common web issues.
        """
        self.rules = [
            # Rule for sites with overlays that block clicks
            CompatibilityRule(
                id="overlay_blocking_element",
                description="Handle click-blocking overlays",
                selector=".modal-overlay, .modal-backdrop, .cookie-notice, .banner",
                action="click_close_button",
                parameters={"close_button_selector": ".close, .btn-close, .modal-close"},
                priority=10,
                applies_to=[]
            ),
            # Rule for single-page applications that need time to load
            CompatibilityRule(
                id="spa_loading_delay",
                description="Handle Single Page Applications that need time to load",
                selector="body[data-spa='true'], [id*='app'], [class*='app']",
                action="wait_additional_time",
                parameters={"wait_time": 2000},
                priority=5,
                applies_to=[]
            ),
            # Rule for sites that require scrolling to load content
            CompatibilityRule(
                id="infinite_scroll",
                description="Handle infinite scroll pages",
                selector="[data-infinite-scroll], .infinite-scroll",
                action="scroll_to_bottom",
                priority=5,
                applies_to=[]
            ),
            # Rule for sites with dynamic content loading
            CompatibilityRule(
                id="dynamic_load",
                description="Wait for dynamic content to load",
                selector=".loading, [class*='spinner'], [class*='loading']",
                action="wait_for_element_absence",
                parameters={"timeout": 10000},
                priority=8,
                applies_to=[]
            ),
            # Rule for sites with shadow DOM elements
            CompatibilityRule(
                id="shadow_dom",
                description="Handle shadow DOM elements",
                selector="*",
                action="shadow_dom_fallback",
                priority=3,
                applies_to=[]
            ),
            # Rule for sites with aggressive ad blockers
            CompatibilityRule(
                id="adblock_detection",
                description="Handle ad blocker detection pages",
                selector=".adblock-message, .adblock-notice",
                action="bypass_adblock_detection",
                priority=7,
                applies_to=[]
            )
        ]
    
    def add_rule(self, rule: CompatibilityRule):
        """
        Adds a new compatibility rule.
        
        Args:
            rule: The rule to add
        """
        self.rules.append(rule)
        # Sort rules by priority (highest first)
        self.rules.sort(key=lambda r: r.priority, reverse=True)
    
    async def detect_compatibility_issues(self, page_content: str, url: str) -> List[CompatibilityRule]:
        """
        Detects potential compatibility issues on a web page.
        
        Args:
            page_content: The HTML content of the page
            url: The URL of the page
            
        Returns:
            List of compatibility rules that apply to the page
        """
        applicable_rules = []
        
        # Check each rule to see if it applies to the current page
        for rule in self.rules:
            # Check if rule applies to specific URLs/domains
            if rule.applies_to:
                url_applies = any(domain in url for domain in rule.applies_to)
                if not url_applies:
                    continue
            
            # Check if the selector exists in the page content
            # In a real implementation, we'd use more sophisticated DOM checking
            # For now, we'll do simple string matching as a basic check
            if rule.selector in page_content or rule.selector.replace('*', '') in page_content:
                applicable_rules.append(rule)
        
        # Sort by priority
        applicable_rules.sort(key=lambda r: r.priority, reverse=True)
        return applicable_rules
    
    async def apply_compatibility_rule(self, rule: CompatibilityRule, controller: BrowserControllerInterface) -> bool:
        """
        Applies a compatibility rule using the browser controller.
        
        Args:
            rule: The compatibility rule to apply
            controller: The browser controller to use
            
        Returns:
            True if the rule was applied successfully, False otherwise
        """
        self.logger.info(f"Applying compatibility rule: {rule.id} - {rule.description}")
        
        try:
            if rule.action == "click_close_button":
                return await self._handle_click_close_button(rule, controller)
            elif rule.action == "wait_additional_time":
                return await self._handle_wait_additional_time(rule, controller)
            elif rule.action == "scroll_to_bottom":
                return await self._handle_scroll_to_bottom(rule, controller)
            elif rule.action == "wait_for_element_absence":
                return await self._handle_wait_for_element_absence(rule, controller)
            elif rule.action == "shadow_dom_fallback":
                return await self._handle_shadow_dom_fallback(rule, controller)
            elif rule.action == "bypass_adblock_detection":
                return await self._handle_bypass_adblock_detection(rule, controller)
            else:
                self.logger.warning(f"Unknown compatibility action: {rule.action}")
                return False
        except Exception as e:
            self.logger.error(f"Error applying compatibility rule {rule.id}: {e}")
            return False
    
    async def _handle_click_close_button(self, rule: CompatibilityRule, controller: BrowserControllerInterface) -> bool:
        """
        Handles clicking close buttons for overlays.
        """
        close_selector = rule.parameters.get("close_button_selector", ".close")
        
        # Create a selector for the close button
        close_element = ElementSelector(type="css", value=close_selector)
        
        # Click the close button
        success = await controller.click(close_element)
        return success
    
    async def _handle_wait_additional_time(self, rule: CompatibilityRule, controller: BrowserControllerInterface) -> bool:
        """
        Handles waiting for additional time for SPA content to load.
        """
        wait_time = rule.parameters.get("wait_time", 2000) / 1000.0  # convert to seconds
        await asyncio.sleep(wait_time)
        return True
    
    async def _handle_scroll_to_bottom(self, rule: CompatibilityRule, controller: BrowserControllerInterface) -> bool:
        """
        Handles scrolling to the bottom of infinite scroll pages.
        """
        # In a real implementation, we'd scroll in steps and check for content
        # Access the raw page object to scroll
        page = controller.get_raw_page()
        if hasattr(page, 'evaluate'):  # Check if it's a Playwright page
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        return True
    
    async def _handle_wait_for_element_absence(self, rule: CompatibilityRule, controller: BrowserControllerInterface) -> bool:
        """
        Handles waiting for elements to disappear (like loading indicators).
        """
        timeout = rule.parameters.get("timeout", 10000)
        
        # For now, we'll just wait for the specified time
        # In a real implementation, we would monitor for the absence of elements
        await asyncio.sleep(timeout / 1000.0)  # convert to seconds
        return True
    
    async def _handle_shadow_dom_fallback(self, rule: CompatibilityRule, controller: BrowserControllerInterface) -> bool:
        """
        Handles shadow DOM elements by using alternative selectors.
        """
        # This is a placeholder implementation
        # In a real implementation, we would need to handle shadow DOM traversal
        self.logger.info("Handling shadow DOM elements")
        return True
    
    async def _handle_bypass_adblock_detection(self, rule: CompatibilityRule, controller: BrowserControllerInterface) -> bool:
        """
        Handles ad blocker detection by modifying page behavior.
        """
        # Execute JavaScript to disable ad blocker detection
        try:
            page = controller.get_raw_page()
            if hasattr(page, 'evaluate'):  # Check if it's a Playwright page
                await page.evaluate("""
                    // Disable common ad blocker detection techniques
                    window.adsbygoogle = window.adsbygoogle || [];
                    window.google_ad_status = 1;
                    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                """)
            return True
        except:
            return False


class BrowserCompatibilityLayer:
    """
    A compatibility layer that wraps browser controllers and applies compatibility rules.
    """
    
    def __init__(self, controller: BrowserControllerInterface):
        self.controller = controller
        self.compatibility_handler = UniversalCompatibilityHandler()
        self.logger = logging.getLogger(__name__)
    
    async def get_page_content(self) -> str:
        """
        Gets the current page content from the controller.
        
        Returns:
            The HTML content of the current page
        """
        state = await self.controller.get_page_state()
        return state.dom_content
    
    async def prepare_page_for_automation(self, url: str) -> List[CompatibilityRule]:
        """
        Prepares the current page for automation by detecting and handling compatibility issues.
        
        Args:
            url: The URL of the current page
            
        Returns:
            List of rules that were applied to handle compatibility issues
        """
        page_content = await self.get_page_content()
        
        # Detect compatibility issues
        issues = await self.compatibility_handler.detect_compatibility_issues(page_content, url)
        
        # Apply rules to handle issues
        applied_rules = []
        for issue in issues:
            success = await self.compatibility_handler.apply_compatibility_rule(issue, self.controller)
            if success:
                applied_rules.append(issue)
                self.logger.info(f"Applied compatibility rule: {issue.id}")
        
        return applied_rules
    
    async def navigate(self, url: str, new_tab: bool = False) -> bool:
        """
        Navigates to a URL with compatibility handling.
        
        Args:
            url: The URL to navigate to
            new_tab: Whether to open in a new tab
            
        Returns:
            True if navigation was successful, False otherwise
        """
        # First navigate to the page
        success = await self.controller.navigate(url, new_tab)
        if not success:
            return False
        
        # Then prepare the page for automation by handling compatibility issues
        await self.prepare_page_for_automation(url)
        return True
    
    async def click(self, selector: ElementSelector, button: str = "left", click_count: int = 1) -> bool:
        """
        Clicks an element with compatibility handling.
        
        Args:
            selector: The element selector
            button: The mouse button to use
            click_count: Number of clicks
            
        Returns:
            True if click was successful, False otherwise
        """
        # Try clicking directly first
        success = await self.controller.click(selector, button, click_count)
        
        if not success:
            # If direct click fails, handle potential compatibility issues
            url = (await self.controller.get_page_state()).url
            page_content = await self.get_page_content()
            
            issues = await self.compatibility_handler.detect_compatibility_issues(page_content, url)
            for issue in issues:
                if issue.selector in f"{selector.type}:{selector.value}":  # Basic matching
                    await self.compatibility_handler.apply_compatibility_rule(issue, self.controller)
                    # Try clicking again after applying compatibility rule
                    success = await self.controller.click(selector, button, click_count)
                    if success:
                        break
        
        return success
    
    async def type_text(self, selector: ElementSelector, text: str, clear: bool = True) -> bool:
        """
        Types text into an element with compatibility handling.
        
        Args:
            selector: The element selector
            text: Text to type
            clear: Whether to clear the field first
            
        Returns:
            True if typing was successful, False otherwise
        """
        return await self.controller.type_text(selector, text, clear)
    
    async def extract_text(self, selector: ElementSelector) -> Optional[str]:
        """
        Extracts text from an element with compatibility handling.
        
        Args:
            selector: The element selector
            
        Returns:
            Extracted text or None if extraction failed
        """
        return await self.controller.extract_text(selector)
    
    async def get_page_state(self):
        """
        Gets the current page state with compatibility handling.
        
        Returns:
            BrowserState object with current page information
        """
        return await self.controller.get_page_state()
    
    async def take_screenshot(self, path: str) -> bool:
        """
        Takes a screenshot with compatibility handling.
        
        Args:
            path: Path to save the screenshot
            
        Returns:
            True if screenshot was successful, False otherwise
        """
        return await self.controller.take_screenshot(path)
    
    async def wait_for_element(self, selector: ElementSelector, timeout: int = 30000) -> bool:
        """
        Waits for an element with compatibility handling.
        
        Args:
            selector: The element selector
            timeout: Timeout in milliseconds
            
        Returns:
            True if element was found within timeout, False otherwise
        """
        return await self.controller.wait_for_element(selector, timeout)
    
    async def close(self):
        """
        Closes the browser.
        """
        await self.controller.close()