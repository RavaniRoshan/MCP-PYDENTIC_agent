import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field
from bs4 import BeautifulSoup
import re
import google.generativeai as genai

from models import BrowserState, ElementSelector, ActionType
from core.browser_controller import BrowserControllerInterface
from core.config import settings


class ElementInfo(BaseModel):
    """
    Represents detailed information about a specific element on a web page.

    Attributes:
        selector (ElementSelector): The selector for the element.
        text (str): The text content of the element.
        attributes (Dict[str, Any]): A dictionary of the element's attributes.
        bounding_box (Optional[Dict[str, int]]): The bounding box of the element.
        visibility (bool): A flag indicating whether the element is visible.
        accessibility_info (Dict[str, Any]): A dictionary of accessibility information.
    """
    selector: ElementSelector
    text: str = ""
    attributes: Dict[str, Any] = Field(default_factory=dict)
    bounding_box: Optional[Dict[str, int]] = None
    visibility: bool = True
    accessibility_info: Dict[str, Any] = Field(default_factory=dict)


class StateObservationResult(BaseModel):
    """
    Represents the result of a browser state observation.

    Attributes:
        success (bool): A flag indicating whether the observation was successful.
        browser_state (Optional[BrowserState]): The current state of the browser.
        elements (List[ElementInfo]): A list of extracted elements from the page.
        summary (str): A summary of the page's content.
        error (Optional[str]): A description of the error if the observation failed.
    """
    success: bool
    browser_state: Optional[BrowserState] = None
    elements: List[ElementInfo] = Field(default_factory=list)
    summary: str = ""
    error: Optional[str] = None


class BrowserStateObserver:
    """
    Observes and analyzes the current state of the browser.

    This class provides methods to capture the browser's state, extract
    relevant elements, and generate a summary of the page's content.
    """
    
    def __init__(self, browser_controller: BrowserControllerInterface):
        """
        Initializes the BrowserStateObserver.

        Args:
            browser_controller (BrowserControllerInterface): An instance of a browser controller.
        """
        self.browser_controller = browser_controller
        self.logger = logging.getLogger(__name__)
    
    async def observe_state(self) -> StateObservationResult:
        """
        Observes the current state of the browser.

        Returns:
            StateObservationResult: The result of the state observation.
        """
        try:
            # Get the current browser state
            browser_state = await self.browser_controller.get_page_state()
            
            # Extract important elements from the page
            elements = await self._extract_elements(browser_state.dom_content)
            
            # Create a summary of the page
            page_summary = await self._summarize_page(browser_state, elements)
            
            return StateObservationResult(
                success=True,
                browser_state=browser_state,
                elements=elements,
                summary=page_summary
            )
        except Exception as e:
            self.logger.error(f"Error observing browser state: {e}")
            return StateObservationResult(
                success=False,
                error=str(e)
            )
    
    async def _extract_elements(self, dom_content: str) -> List[ElementInfo]:
        """
        Extracts important elements from the DOM content.

        Args:
            dom_content (str): The HTML content of the page.

        Returns:
            List[ElementInfo]: A list of extracted elements.
        """
        elements = []
        
        try:
            soup = BeautifulSoup(dom_content, 'html.parser')
            
            # Find interactive elements that might be relevant for automation
            interactive_selectors = [
                'button',  # All buttons
                'input[type="text"], input[type="email"], input[type="password"], input[type="search"], textarea',  # Input fields
                'a',  # Links
                'select',  # Dropdowns
                'input[type="submit"], input[type="button"]',  # Submit buttons
                '[role="button"]',  # ARIA buttons
                '[role="link"]',  # ARIA links
                '[role="textbox"]',  # ARIA textboxes
            ]
            
            for selector in interactive_selectors:
                found_elements = soup.select(selector)
                
                for element in found_elements[:20]:  # Limit to first 20 elements to avoid overload
                    # Create a CSS selector for this specific element
                    element_id = element.get('id')
                    element_class = element.get('class')
                    element_tag = element.name
                    
                    css_selector = ""
                    if element_id:
                        css_selector = f"#{element_id}"
                    elif element_class:
                        css_selector = f".{'.'.join(element_class)}"
                    else:
                        # Generate a more specific selector
                        css_selector = self._generate_css_selector(element, soup)
                    
                    # Get element text
                    element_text = element.get_text(strip=True)
                    if len(element_text) > 100:  # Truncate long text
                        element_text = element_text[:100] + "..."
                    
                    # Get element attributes
                    attributes = dict(element.attrs)
                    
                    element_info = ElementInfo(
                        selector=ElementSelector(
                            type="css",
                            value=css_selector,
                            description=element_text[:50] if element_text else element_tag
                        ),
                        text=element_text,
                        attributes=attributes
                    )
                    
                    elements.append(element_info)
        
        except Exception as e:
            self.logger.error(f"Error extracting elements: {e}")
        
        return elements
    
    def _generate_css_selector(self, element, soup) -> str:
        """
        Generates a unique CSS selector for an element.

        Args:
            element: The BeautifulSoup element.
            soup: The BeautifulSoup object for the entire page.

        Returns:
            str: A unique CSS selector for the element.
        """
        tag = element.name
        path = []
        
        while element:
            position = 1
            sibling = element.find_previous_sibling()
            
            while sibling:
                if sibling.name == element.name:
                    position += 1
                sibling = sibling.find_previous_sibling()
            
            if position > 1:
                path.insert(0, f"{tag}:nth-of-type({position})")
            else:
                path.insert(0, tag)
            
            element = element.parent
            if element == soup:
                break
        
        return " > ".join(path) if path else tag
    
    async def _summarize_page(self, browser_state: BrowserState, elements: List[ElementInfo]) -> str:
        """
        Creates a summary of the current page.

        Args:
            browser_state (BrowserState): The current state of the browser.
            elements (List[ElementInfo]): A list of extracted elements.

        Returns:
            str: A summary of the page's content.
        """
        title = browser_state.title
        url = browser_state.url
        
        # Count different types of elements
        buttons = [e for e in elements if 'button' in e.selector.value.lower() or e.attributes.get('type') == 'submit']
        input_fields = [e for e in elements if 'input' in e.selector.value or 'textarea' in e.selector.value]
        links = [e for e in elements if 'a' in e.selector.value]
        
        summary = f"Page: {title} at {url}\n"
        summary += f"Elements: {len(elements)} total, {len(buttons)} buttons, {len(input_fields)} input fields, {len(links)} links\n"
        
        # Add some example elements
        if input_fields:
            summary += f"Input fields: {[e.text[:20] for e in input_fields[:3]]}\n"
        if buttons:
            summary += f"Buttons: {[e.text[:20] for e in buttons[:3]]}\n"
        if links:
            summary += f"Example links: {[e.text[:20] for e in links[:3]]}\n"
        
        # Truncate if too long
        if len(summary) > 500:
            summary = summary[:500] + "..."
        
        return summary.strip()
    
    async def find_element_by_description(self, description: str) -> Optional[ElementInfo]:
        """
        Finds an element by its description or text content.

        Args:
            description (str): The description of the element to find.

        Returns:
            Optional[ElementInfo]: Information about the found element, or None if no element is found.
        """
        observation = await self.observe_state()
        
        if not observation.success:
            return None
        
        # Look for elements that match the description
        description_lower = description.lower()
        
        for element in observation.elements:
            element_text_lower = element.text.lower() if element.text else ""
            element_desc_lower = element.selector.description.lower() if element.selector.description else ""
            
            if (description_lower in element_text_lower or 
                description_lower in element_desc_lower or 
                description_lower in element.selector.value.lower()):
                return element
        
        # If no exact match found, try partial matches
        for element in observation.elements:
            element_text_lower = element.text.lower() if element.text else ""
            element_desc_lower = element.selector.description.lower() if element.selector.description else ""
            
            # Check if the element description or text starts with or contains the target description
            if (description_lower in element_text_lower or 
                description_lower in element_desc_lower):
                return element
        
        return None
    
    async def get_element_screenshot(self, selector: ElementSelector) -> Optional[str]:
        """
        Takes a screenshot of a specific element.

        Note: This is a placeholder implementation that takes a full-page screenshot.
        A real implementation would crop the screenshot to the element's bounding box.

        Args:
            selector (ElementSelector): The selector of the element.

        Returns:
            Optional[str]: The path to the screenshot, or None if an error occurs.
        """
        # This would take a screenshot of a specific element
        # For now, we'll just take a full page screenshot and return its path
        # In a real implementation, this would crop the screenshot to the element
        screenshot_path = f"screenshots/element_{selector.value.replace(' ', '_').replace('.', '_')}.png"
        
        try:
            success = await self.browser_controller.take_screenshot(screenshot_path)
            if success:
                return screenshot_path
        except Exception as e:
            self.logger.error(f"Error taking element screenshot: {e}")
        
        return None

    async def analyze_with_ai(self, user_query: str = "") -> Optional[Dict[str, Any]]:
        """
        Analyze the current browser state using AI.

        Args:
            user_query (str): An optional query from the user about the current page.

        Returns:
            Optional[Dict[str, Any]]: AI analysis of the browser state.
        """
        try:
            if not settings.gemini_api_key:
                self.logger.warning("No Gemini API key configured for AI analysis")
                return None
            
            # Get the current browser state
            observation = await self.observe_state()
            if not observation.success:
                self.logger.error("Failed to observe browser state for AI analysis")
                return None
            
            # Configure the API key
            genai.configure(api_key=settings.gemini_api_key)
            
            # Initialize the model
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            # Prepare the prompt for AI analysis
            if user_query:
                prompt = f"""
                A user has the following query: '{user_query}'
                
                Current page information:
                - URL: {observation.browser_state.url}
                - Title: {observation.browser_state.title}
                - Content: {observation.browser_state.dom_content[:3000]}...
                
                Please analyze the page content and provide a helpful response to the user's query.
                """
            else:
                prompt = f"""
                Analyze the following web page content:
                - URL: {observation.browser_state.url}
                - Title: {observation.browser_state.title}
                - Content: {observation.browser_state.dom_content[:3000]}...
                
                Please provide a summary of the page content, identify key elements,
                and suggest potential actions that could be taken on this page.
                """
            
            # Get AI response
            response = await model.generate_content_async(prompt)
            
            if response and response.text:
                return {
                    "analysis": response.text,
                    "url": observation.browser_state.url,
                    "title": observation.browser_state.title,
                    "element_count": len(observation.elements)
                }
        except Exception as e:
            self.logger.error(f"Error in AI analysis: {e}")
            return None