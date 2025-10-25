from .browser_controller import BrowserControllerInterface
from models import ElementSelector, BrowserState, FormField
from core.config import settings
from typing import Optional, List, Dict, Any
import asyncio
import base64


class PlaywrightBrowserController(BrowserControllerInterface):
    """
    Playwright-based implementation of the browser controller.

    This class provides a concrete implementation of the BrowserControllerInterface
    using the Playwright library. It handles browser automation tasks such as
    navigation, clicking, typing, and extracting text.
    """
    
    def __init__(self):
        """
        Initializes the PlaywrightBrowserController.
        """
        self.browser = None
        self.page = None
        self.context = None
        self.tabs = {}  # Dictionary to store all pages with their IDs
        self.active_tab_id = None  # Track the currently active tab
        
    async def initialize(self):
        """
        Initializes the Playwright browser instance.

        This method starts the Playwright instance, launches a Chromium browser,
        creates a new browser context, and opens a new page.

        Raises:
            RuntimeError: If Playwright is not installed.
        """
        try:
            from playwright.async_api import async_playwright
            
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=settings.browser_headless
            )
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()
            
            # Initialize tab management
            tab_id = "default_tab"
            self.tabs[tab_id] = self.page
            self.active_tab_id = tab_id
        except ImportError:
            raise RuntimeError("Playwright is not installed. Please install it using 'pip install playwright' and run 'playwright install'")
    
    async def _ensure_initialized(self):
        """
        Ensures the browser is initialized before performing actions.

        If the browser has not been initialized, this method calls the
        `initialize` method to set it up.
        """
        if self.browser is None:
            await self.initialize()
    
    async def navigate(self, url: str, new_tab: bool = False) -> bool:
        """
        Navigates to a URL.

        Args:
            url: The URL to navigate to.
            new_tab: Whether to open the URL in a new tab.

        Returns:
            True if navigation is successful, False otherwise.
        """
        await self._ensure_initialized()
        
        try:
            if new_tab:
                # Create a new tab
                new_page = await self.context.new_page()
                tab_id = f"tab_{len(self.tabs) + 1}"
                self.tabs[tab_id] = new_page
                self.active_tab_id = tab_id
                self.page = new_page
            elif self.active_tab_id:
                # Use the currently active tab
                self.page = self.tabs[self.active_tab_id]
            
            await self.page.goto(url, timeout=settings.browser_timeout)
            return True
        except Exception as e:
            print(f"Navigation error: {e}")
            return False
    
    async def click(self, selector: ElementSelector, button: str = "left", click_count: int = 1) -> bool:
        """
        Clicks on an element.

        Args:
            selector: The element selector.
            button: The mouse button to use for the click.
            click_count: The number of times to click.

        Returns:
            True if the click is successful, False otherwise.
        """
        await self._ensure_initialized()
        
        try:
            # Use the currently active tab
            current_page = self.tabs[self.active_tab_id]
            
            # Convert the selector to Playwright format
            playwright_selector = await self._convert_selector(selector)
            
            # Wait for the element to be visible
            await current_page.wait_for_selector(playwright_selector, state="visible")
            
            # Perform the click action
            await current_page.click(playwright_selector, button=button, click_count=click_count)
            return True
        except Exception as e:
            print(f"Click error: {e}")
            return False
    
    async def type_text(self, selector: ElementSelector, text: str, clear: bool = True) -> bool:
        """
        Types text into an element.

        Args:
            selector: The element selector.
            text: The text to type.
            clear: Whether to clear the element before typing.

        Returns:
            True if typing is successful, False otherwise.
        """
        await self._ensure_initialized()
        
        try:
            # Use the currently active tab
            current_page = self.tabs[self.active_tab_id]
            
            # Convert the selector to Playwright format
            playwright_selector = await self._convert_selector(selector)
            
            # Wait for the element to be visible
            await current_page.wait_for_selector(playwright_selector, state="visible")
            
            if clear:
                await current_page.fill(playwright_selector, "")
            
            await current_page.type(playwright_selector, text, delay=settings.browser_timeout/1000)
            return True
        except Exception as e:
            print(f"Type text error: {e}")
            return False
    
    async def extract_text(self, selector: ElementSelector) -> Optional[str]:
        """
        Extracts text from an element.

        Args:
            selector: The element selector.

        Returns:
            The extracted text, or None if an error occurs.
        """
        await self._ensure_initialized()
        
        try:
            # Use the currently active tab
            current_page = self.tabs[self.active_tab_id]
            
            # Convert the selector to Playwright format
            playwright_selector = await self._convert_selector(selector)
            
            # Wait for the element to be visible
            await current_page.wait_for_selector(playwright_selector, state="visible")
            
            # Get the text content
            text = await current_page.text_content(playwright_selector)
            return text
        except Exception as e:
            print(f"Text extraction error: {e}")
            return None
    
    async def extract_multiple(self, selector: ElementSelector, method: str = "text_content") -> Optional[List[Dict[str, Any]]]:
        """
        Extracts multiple elements based on a selector.

        Args:
            selector: The element selector.
            method: The extraction method (text_content, html_content, attribute).

        Returns:
            A list of extracted elements, or None if an error occurs.
        """
        await self._ensure_initialized()
        
        try:
            # Use the currently active tab
            current_page = self.tabs[self.active_tab_id]
            
            # Convert the selector to Playwright format
            playwright_selector = await self._convert_selector(selector)
            
            # Find all matching elements
            elements = await current_page.query_selector_all(playwright_selector)
            
            results = []
            for i, element in enumerate(elements):
                if method == "text_content":
                    text = await element.text_content()
                    results.append({"text": text, "index": i})
                elif method == "html_content":
                    inner_html = await element.inner_html()
                    results.append({"html": inner_html, "index": i})
                elif method == "attribute":
                    attr_name = selector.metadata.get("attribute_name", "href") if hasattr(selector, 'metadata') and selector.metadata else "href"
                    attr_value = await element.get_attribute(attr_name)
                    results.append({"attribute": attr_value, "index": i})
                else:
                    text = await element.text_content()
                    results.append({"text": text, "index": i})
            
            return results
        except Exception as e:
            print(f"Multiple extraction error: {e}")
            return None
    
    async def extract_attribute(self, selector: ElementSelector, attr_name: str) -> Optional[str]:
        """
        Extracts a specific attribute from an element.

        Args:
            selector: The element selector.
            attr_name: The name of the attribute to extract.

        Returns:
            The extracted attribute value, or None if an error occurs.
        """
        await self._ensure_initialized()
        
        try:
            # Use the currently active tab
            current_page = self.tabs[self.active_tab_id]
            
            # Convert the selector to Playwright format
            playwright_selector = await self._convert_selector(selector)
            
            # Wait for the element to be visible
            await current_page.wait_for_selector(playwright_selector, state="visible")
            
            # Get the attribute value
            attr_value = await current_page.get_attribute(playwright_selector, attr_name)
            return attr_value
        except Exception as e:
            print(f"Attribute extraction error: {e}")
            return None
    
    async def extract_table(self, selector: ElementSelector) -> Optional[List[Dict[str, str]]]:
        """
        Extracts table data from an element.

        Args:
            selector: The element selector for the table.

        Returns:
            A list of dictionaries representing table rows, or None if an error occurs.
        """
        await self._ensure_initialized()
        
        try:
            # Use the currently active tab
            current_page = self.tabs[self.active_tab_id]
            
            # Convert the selector to Playwright format
            playwright_selector = await self._convert_selector(selector)
            
            # Wait for the table to be visible
            await current_page.wait_for_selector(playwright_selector, state="visible")
            
            # Get the table element
            table_element = await current_page.query_selector(playwright_selector)
            if not table_element:
                return None
            
            # Extract headers
            header_elements = await table_element.query_selector_all("thead th, tr:first-child th")
            headers = []
            for header_element in header_elements:
                header_text = await header_element.text_content()
                headers.append(header_text.strip())
            
            # If no headers found in thead, try first row of tbody
            if not headers:
                header_elements = await table_element.query_selector_all("tbody tr:first-child td, tbody tr:first-child th")
                for header_element in header_elements:
                    header_text = await header_element.text_content()
                    headers.append(header_text.strip())
            
            # Extract rows
            row_elements = await table_element.query_selector_all("tbody tr, tr")
            rows = []
            
            for i, row_element in enumerate(row_elements):
                # Skip header row if it's the first row and headers were already extracted from thead
                if i == 0 and len(headers) > 0 and len(row_elements) > 1:
                    continue
                    
                cell_elements = await row_element.query_selector_all("td, th")
                if cell_elements:
                    row_data = {}
                    for j, cell_element in enumerate(cell_elements):
                        cell_text = await cell_element.text_content()
                        header_key = headers[j] if j < len(headers) else f"column_{j}"
                        row_data[header_key] = cell_text.strip()
                    if row_data:  # Only add non-empty rows
                        rows.append(row_data)
            
            return rows
        except Exception as e:
            print(f"Table extraction error: {e}")
            return None
    
    async def extract_links(self, selector: ElementSelector = None) -> Optional[List[Dict[str, str]]]:
        """
        Extracts all links from the page or within a specific element.

        Args:
            selector: Optional element selector to limit extraction scope.

        Returns:
            A list of dictionaries containing link text and href, or None if an error occurs.
        """
        await self._ensure_initialized()
        
        try:
            # Use the currently active tab
            current_page = self.tabs[self.active_tab_id]
            
            if selector:
                # Extract links within a specific element
                playwright_selector = await self._convert_selector(selector)
                # Wait for the container element to be visible
                await current_page.wait_for_selector(playwright_selector, state="visible")
                
                # Get links within the specific element
                link_elements = await current_page.query_selector_all(f"{playwright_selector} a")
            else:
                # Extract all links from the page
                link_elements = await current_page.query_selector_all("a")
            
            links = []
            for link_element in link_elements:
                text = await link_element.text_content()
                href = await link_element.get_attribute("href")
                
                if href:  # Only add links that have an href attribute
                    links.append({
                        "text": text.strip(),
                        "href": href
                    })
            
            return links
        except Exception as e:
            print(f"Links extraction error: {e}")
            return None
    
    async def extract_images(self, selector: ElementSelector = None) -> Optional[List[Dict[str, str]]]:
        """
        Extracts all images from the page or within a specific element.

        Args:
            selector: Optional element selector to limit extraction scope.

        Returns:
            A list of dictionaries containing image alt text and src, or None if an error occurs.
        """
        await self._ensure_initialized()
        
        try:
            if selector:
                # Extract images within a specific element
                playwright_selector = await self._convert_selector(selector)
                # Wait for the container element to be visible
                await self.page.wait_for_selector(playwright_selector, state="visible")
                
                # Get images within the specific element
                img_elements = await self.page.query_selector_all(f"{playwright_selector} img")
            else:
                # Extract all images from the page
                img_elements = await self.page.query_selector_all("img")
            
            images = []
            for img_element in img_elements:
                alt = await img_element.get_attribute("alt")
                src = await img_element.get_attribute("src")
                
                if src:  # Only add images that have a src attribute
                    images.append({
                        "alt": alt or "",
                        "src": src
                    })
            
            return images
        except Exception as e:
            print(f"Images extraction error: {e}")
            return None
    
    async def extract_html(self, selector: ElementSelector) -> Optional[str]:
        """
        Extracts HTML content from an element.

        Args:
            selector: The element selector.

        Returns:
            The inner HTML content of the element, or None if an error occurs.
        """
        await self._ensure_initialized()
        
        try:
            # Convert the selector to Playwright format
            playwright_selector = await self._convert_selector(selector)
            
            # Wait for the element to be visible
            await self.page.wait_for_selector(playwright_selector, state="visible")
            
            # Get the inner HTML content
            inner_html = await self.page.inner_html(playwright_selector)
            return inner_html
        except Exception as e:
            print(f"HTML extraction error: {e}")
            return None
    
    async def detect_form_fields(self, form_selector: ElementSelector) -> Optional[List[FormField]]:
        """
        Detects and returns all fields in a form.

        Args:
            form_selector: The selector for the form element.

        Returns:
            A list of FormField objects representing the form fields.
        """
        await self._ensure_initialized()
        
        try:
            # Convert the selector to Playwright format
            playwright_selector = await self._convert_selector(form_selector)
            
            # Wait for the form to be visible
            await self.page.wait_for_selector(playwright_selector, state="visible")
            
            # Get the form element
            form_element = await self.page.query_selector(playwright_selector)
            if not form_element:
                return None
            
            # Query all input, textarea, and select elements within the form
            input_elements = await form_element.query_selector_all("input, textarea, select")
            fields = []
            
            for i, element in enumerate(input_elements):
                # Get attributes of the field
                name = await element.get_attribute("name") or f"field_{i}"
                field_type = await element.get_attribute("type") or "text"
                required = await element.get_attribute("required") is not None
                placeholder = await element.get_attribute("placeholder")
                label_elements = await self.page.query_selector_all(f"label[for='{await element.get_attribute('id')}']")
                
                # Try to find associated label
                label = ""
                if label_elements:
                    label = await label_elements[0].inner_text()
                else:
                    # Try to find if this input is inside a label
                    parent_label = await element.query_selector(".. >> label")
                    if parent_label:
                        label = await parent_label.inner_text()
                
                # Create field selector for this specific element
                element_id = await element.get_attribute("id")
                if element_id:
                    field_selector = ElementSelector(
                        type="id",
                        value=element_id,
                        description=f"Field {name}"
                    )
                else:
                    # Use a more specific CSS selector
                    field_selector = ElementSelector(
                        type="css",
                        value=f"{playwright_selector} [name='{name}']",
                        description=f"Field {name}"
                    )
                
                field = FormField(
                    name=name,
                    type=field_type,
                    selector=field_selector,
                    required=required,
                    label=label.strip() if label else None,
                    placeholder=placeholder
                )
                fields.append(field)
            
            return fields
        except Exception as e:
            print(f"Form field detection error: {e}")
            return None
    
    async def fill_form_field(self, field_selector: ElementSelector, value: str) -> bool:
        """
        Fills a single form field with a value.

        Args:
            field_selector: The selector for the form field.
            value: The value to fill into the field.

        Returns:
            True if the operation was successful, False otherwise.
        """
        await self._ensure_initialized()
        
        try:
            # Convert the selector to Playwright format
            playwright_selector = await self._convert_selector(field_selector)
            
            # Wait for the element to be visible and enabled
            await self.page.wait_for_selector(playwright_selector, state="visible")
            
            # Clear the field and type the new value
            await self.page.fill(playwright_selector, "")
            await self.page.type(playwright_selector, value)
            
            return True
        except Exception as e:
            print(f"Form field filling error: {e}")
            return False
    
    async def fill_form(self, form_selector: ElementSelector, field_values: Dict[str, str]) -> bool:
        """
        Fills all fields in a form with provided values.

        Args:
            form_selector: The selector for the form.
            field_values: A dictionary mapping field names to their values.

        Returns:
            True if the operation was successful, False otherwise.
        """
        await self._ensure_initialized()
        
        try:
            # First detect the form fields
            form_fields = await self.detect_form_fields(form_selector)
            if not form_fields:
                return False
            
            # Fill each field with its corresponding value
            success = True
            for field in form_fields:
                if field.name in field_values:
                    value = field_values[field.name]
                    field_success = await self.fill_form_field(field.selector, value)
                    if not field_success:
                        success = False
            
            return success
        except Exception as e:
            print(f"Form filling error: {e}")
            return False
    
    async def submit_form(self, form_selector: ElementSelector) -> bool:
        """
        Submits a form.

        Args:
            form_selector: The selector for the form to submit.

        Returns:
            True if the operation was successful, False otherwise.
        """
        await self._ensure_initialized()
        
        try:
            # Convert the selector to Playwright format
            playwright_selector = await self._convert_selector(form_selector)
            
            # Wait for the form to be visible
            await self.page.wait_for_selector(playwright_selector, state="visible")
            
            # Submit the form - find and click the submit button or use form submit
            submit_button = await self.page.query_selector(f"{playwright_selector} input[type='submit'], {playwright_selector} button[type='submit'], {playwright_selector} button[type='button'], {playwright_selector} button:not([type])")
            
            if submit_button:
                # Click the submit button
                await submit_button.click()
            else:
                # Fallback: submit the form directly using JavaScript
                await self.page.evaluate(f"document.querySelector('{playwright_selector}').submit()")
            
            return True
        except Exception as e:
            print(f"Form submission error: {e}")
            return False
    
    async def get_form_values(self, form_selector: ElementSelector) -> Optional[Dict[str, str]]:
        """
        Extracts all current values from form fields.

        Args:
            form_selector: The selector for the form.

        Returns:
            A dictionary mapping field names to their current values.
        """
        await self._ensure_initialized()
        
        try:
            # First detect the form fields
            form_fields = await self.detect_form_fields(form_selector)
            if not form_fields:
                return None
            
            # Get the values for each field
            values = {}
            for field in form_fields:
                playwright_selector = await self._convert_selector(field.selector)
                
                # Handle different field types
                if field.type in ["checkbox", "radio"]:
                    # For checkboxes and radios, we get the checked status
                    is_checked = await self.page.is_checked(playwright_selector)
                    values[field.name] = str(is_checked).lower()
                elif field.type == "select-one" or field.selector.value.startswith("select"):
                    # For select elements, get the selected value
                    selected_value = await self.page.input_value(playwright_selector)
                    values[field.name] = selected_value
                else:
                    # For text inputs, textareas, etc., get the value
                    field_value = await self.page.input_value(playwright_selector)
                    values[field.name] = field_value
            
            return values
        except Exception as e:
            print(f"Getting form values error: {e}")
            return None
    
    async def get_page_state(self) -> BrowserState:
        """
        Gets the current state of the browser.

        Returns:
            A BrowserState object representing the current state of the browser.
        """
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
        """
        Takes a screenshot of the current page.

        Args:
            path: The path to save the screenshot to.

        Returns:
            True if the screenshot is taken successfully, False otherwise.
        """
        await self._ensure_initialized()
        
        try:
            await self.page.screenshot(path=path)
            return True
        except Exception as e:
            print(f"Screenshot error: {e}")
            return False
    
    async def wait_for_element(self, selector: ElementSelector, timeout: int = 30000) -> bool:
        """
        Waits for an element to appear.

        Args:
            selector: The element selector.
            timeout: The maximum time to wait in milliseconds.

        Returns:
            True if the element appears within the timeout, False otherwise.
        """
        await self._ensure_initialized()
        
        try:
            playwright_selector = await self._convert_selector(selector)
            await self.page.wait_for_selector(playwright_selector, state="visible", timeout=timeout)
            return True
        except Exception:
            return False
    
    async def switch_to_tab(self, tab_id: str) -> bool:
        """
        Switches to a different tab by ID.

        Args:
            tab_id: The ID of the tab to switch to.

        Returns:
            True if the switch was successful, False otherwise.
        """
        if tab_id in self.tabs:
            self.active_tab_id = tab_id
            self.page = self.tabs[tab_id]
            return True
        return False

    async def get_current_tab_id(self) -> str:
        """
        Gets the ID of the current active tab.

        Returns:
            The ID of the current active tab.
        """
        return self.active_tab_id

    async def get_all_tab_ids(self) -> List[str]:
        """
        Gets all available tab IDs.

        Returns:
            A list of all tab IDs.
        """
        return list(self.tabs.keys())

    async def close_tab(self, tab_id: str = None) -> bool:
        """
        Closes a specific tab by ID.

        Args:
            tab_id: The ID of the tab to close. If None, closes the current tab.

        Returns:
            True if the tab was closed successfully, False otherwise.
        """
        tab_to_close = tab_id if tab_id else self.active_tab_id
        
        if tab_to_close and tab_to_close in self.tabs:
            # Close the page
            await self.tabs[tab_to_close].close()
            
            # Remove from tabs dictionary
            del self.tabs[tab_to_close]
            
            # If we closed the active tab, switch to another tab
            if tab_to_close == self.active_tab_id:
                if self.tabs:
                    # Switch to the first available tab
                    self.active_tab_id = next(iter(self.tabs))
                    self.page = self.tabs[self.active_tab_id]
                else:
                    # No more tabs
                    self.active_tab_id = None
                    self.page = None
            
            return True
        return False

    async def close(self):
        """
        Closes the browser.
        """
        try:
            # Close all tabs
            for page in self.tabs.values():
                await page.close()
        except:
            pass  # Continue with the rest even if closing pages fails
        
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    def get_raw_page(self):
        """
        Get the raw page object for direct access (e.g., Playwright page).
        This allows the compatibility layer to run JavaScript directly.
        """
        return self.page
    
    async def _convert_selector(self, element_selector: ElementSelector) -> str:
        """
        Converts an ElementSelector to a Playwright selector format.

        Args:
            element_selector: The ElementSelector to convert.

        Returns:
            The Playwright selector string.
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

    def get_page(self):
        """Method to access the Playwright page object"""
        return self.page