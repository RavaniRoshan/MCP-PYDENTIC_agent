from typing import Dict, List, Optional, Any
import asyncio
import logging
from datetime import datetime
from dataclasses import dataclass
from models import ElementSelector, BrowserState
from core.browser_controller import BrowserControllerInterface


@dataclass
class TabInfo:
    """
    Information about a browser tab.
    
    Attributes:
        tab_id: Unique identifier for the tab
        url: Current URL of the tab
        title: Title of the page in the tab
        created_at: When the tab was created
        last_accessed: When the tab was last accessed
        is_active: Whether this is the currently active tab
        page_reference: Reference to the actual page object (for Playwright)
    """
    tab_id: str
    url: str
    title: str
    created_at: datetime
    last_accessed: datetime
    is_active: bool = False
    page_reference: Optional[Any] = None  # For Playwright, this would be the page object


class TabManager:
    """
    Manages multiple browser tabs within a single browser session.
    For Playwright implementation, this uses separate page instances.
    For Mock implementation, this simulates tabs.
    """
    
    def __init__(self, browser_controller: BrowserControllerInterface):
        self.browser_controller = browser_controller
        self.tabs: Dict[str, TabInfo] = {}
        self.active_tab_id: Optional[str] = None
        self.logger = logging.getLogger(__name__)
    
    async def create_new_tab(self, url: str = "about:blank") -> str:
        """
        Creates a new browser tab and navigates to the specified URL.
        
        Args:
            url: URL to navigate to in the new tab (default: about:blank)
            
        Returns:
            The ID of the newly created tab
        """
        # Generate unique tab ID
        import uuid
        tab_id = f"tab_{uuid.uuid4().hex[:8]}"
        
        # For the mock controller, we'll simulate tabs by changing the current state
        # For Playwright, we'll create a new page
        if hasattr(self.browser_controller, 'context') and hasattr(self.browser_controller, 'page'):
            # This is likely a Playwright controller
            # Create new page in the existing context
            new_page = await self.browser_controller.context.new_page()
            await new_page.goto(url)
            page_reference = new_page
        else:
            # This is a mock controller, simulate tab behavior
            await self.browser_controller.navigate(url, new_tab=True)
            page_reference = None
        
        # Get the current state to populate tab info
        state = await self.browser_controller.get_page_state()
        
        tab_info = TabInfo(
            tab_id=tab_id,
            url=state.url,
            title=state.title,
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow(),
            is_active=True,
            page_reference=page_reference
        )
        
        self.tabs[tab_id] = tab_info
        self.active_tab_id = tab_id
        
        self.logger.info(f"Created new tab {tab_id} with URL: {url}")
        return tab_id
    
    async def switch_to_tab(self, tab_id: str) -> bool:
        """
        Switches to the specified tab.
        
        Args:
            tab_id: ID of the tab to switch to
            
        Returns:
            True if the switch was successful, False otherwise
        """
        if tab_id not in self.tabs:
            self.logger.warning(f"Tab {tab_id} does not exist")
            return False
        
        # Update active tab info
        if self.active_tab_id:
            self.tabs[self.active_tab_id].is_active = False
        
        self.tabs[tab_id].is_active = True
        self.active_tab_id = tab_id
        self.tabs[tab_id].last_accessed = datetime.utcnow()
        
        self.logger.info(f"Switched to tab {tab_id}")
        return True
    
    async def close_tab(self, tab_id: str) -> bool:
        """
        Closes the specified tab.
        
        Args:
            tab_id: ID of the tab to close
            
        Returns:
            True if the tab was closed successfully, False otherwise
        """
        if tab_id not in self.tabs:
            self.logger.warning(f"Tab {tab_id} does not exist")
            return False
        
        # If closing the active tab, switch to another tab if available
        if tab_id == self.active_tab_id:
            other_tabs = [tid for tid in self.tabs.keys() if tid != tab_id]
            if other_tabs:
                # Switch to the most recently accessed tab
                most_recent_tab = max(
                    other_tabs, 
                    key=lambda tid: self.tabs[tid].last_accessed
                )
                await self.switch_to_tab(most_recent_tab)
            else:
                self.active_tab_id = None
        
        # Remove the tab
        del self.tabs[tab_id]
        self.logger.info(f"Closed tab {tab_id}")
        return True
    
    def get_active_tab(self) -> Optional[TabInfo]:
        """
        Gets information about the currently active tab.
        
        Returns:
            TabInfo for the active tab, or None if no active tab
        """
        if self.active_tab_id and self.active_tab_id in self.tabs:
            return self.tabs[self.active_tab_id]
        return None
    
    def get_all_tabs(self) -> List[TabInfo]:
        """
        Gets information about all tabs.
        
        Returns:
            List of TabInfo for all tabs
        """
        return list(self.tabs.values())
    
    async def get_tab_state(self, tab_id: str) -> Optional[BrowserState]:
        """
        Gets the current state of the specified tab.
        
        Args:
            tab_id: ID of the tab to get state for
            
        Returns:
            BrowserState for the tab, or None if the tab doesn't exist
        """
        if tab_id not in self.tabs:
            return None
        
        # Switch to the tab first, get its state, then switch back
        original_active = self.active_tab_id
        await self.switch_to_tab(tab_id)
        
        try:
            state = await self.browser_controller.get_page_state()
            return state
        finally:
            # Switch back to the original active tab if it still exists
            if original_active and original_active in self.tabs:
                await self.switch_to_tab(original_active)
    
    async def navigate_in_tab(self, tab_id: str, url: str) -> bool:
        """
        Navigates to a URL in the specified tab.
        
        Args:
            tab_id: ID of the tab to navigate in
            url: URL to navigate to
            
        Returns:
            True if navigation was successful, False otherwise
        """
        original_active = self.active_tab_id
        success = await self.switch_to_tab(tab_id)
        if not success:
            return False
        
        try:
            navigation_result = await self.browser_controller.navigate(url)
            # Update tab info after navigation
            if tab_id in self.tabs:
                state = await self.browser_controller.get_page_state()
                self.tabs[tab_id].url = state.url
                self.tabs[tab_id].title = state.title
                self.tabs[tab_id].last_accessed = datetime.utcnow()
            return navigation_result
        finally:
            # Switch back to the original active tab if it still exists
            if original_active and original_active in self.tabs:
                await self.switch_to_tab(original_active)
    
    async def execute_action_in_tab(self, tab_id: str, action_callback) -> Any:
        """
        Executes an action in the specified tab.
        
        Args:
            tab_id: ID of the tab to execute the action in
            action_callback: Async function to execute in the tab
            
        Returns:
            Result of the action callback
        """
        original_active = self.active_tab_id
        success = await self.switch_to_tab(tab_id)
        if not success:
            return None
        
        try:
            result = await action_callback()
            if tab_id in self.tabs:
                # Update last accessed time
                self.tabs[tab_id].last_accessed = datetime.utcnow()
            return result
        finally:
            # Switch back to the original active tab if it still exists
            if original_active and original_active in self.tabs:
                await self.switch_to_tab(original_active)