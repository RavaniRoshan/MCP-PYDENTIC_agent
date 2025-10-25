from typing import Dict, List, Optional, Any
import asyncio
import logging
from datetime import datetime
import uuid
from dataclasses import dataclass
from core.browser_controller import BrowserControllerInterface, MockBrowserController
try:
    from core.playwright_controller import PlaywrightBrowserController
except ImportError:
    PlaywrightBrowserController = None

from core.tab_manager import TabManager


@dataclass
class SessionInfo:
    """
    Information about a browser session.
    
    Attributes:
        session_id: Unique identifier for the session
        user_id: ID of the user associated with this session
        browser_type: Type of browser used in the session
        created_at: When the session was created
        last_accessed: When the session was last accessed
        is_active: Whether the session is currently active
        tab_count: Number of tabs in the session
    """
    session_id: str
    user_id: str
    browser_type: str
    created_at: datetime
    last_accessed: datetime
    is_active: bool = True
    tab_count: int = 0


class SessionManager:
    """
    Manages multiple browser sessions for different users or tasks.
    """
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}  # session_id -> {controller, tab_manager, info}
        self.logger = logging.getLogger(__name__)
    
    async def create_session(self, user_id: str, browser_type: str = "chromium") -> str:
        """
        Creates a new browser session.
        
        Args:
            user_id: ID of the user requesting the session
            browser_type: Type of browser to use (chromium, firefox, webkit)
            
        Returns:
            The ID of the newly created session
        """
        # Generate unique session ID
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        
        # Create the appropriate browser controller
        if browser_type == "chromium" and PlaywrightBrowserController:
            controller = PlaywrightBrowserController()
            await controller.initialize()
        else:
            # Use mock controller for testing or if Playwright is not available
            controller = MockBrowserController()
        
        # Create tab manager for this session
        tab_manager = TabManager(controller)
        
        # Create new tab in the session
        await tab_manager.create_new_tab()
        
        # Create session info
        session_info = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            browser_type=browser_type,
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow(),
            tab_count=1
        )
        
        # Store the session
        self.sessions[session_id] = {
            'controller': controller,
            'tab_manager': tab_manager,
            'info': session_info
        }
        
        self.logger.info(f"Created new session {session_id} for user {user_id} using {browser_type}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Gets the session data for the specified session ID.
        
        Args:
            session_id: ID of the session to retrieve
            
        Returns:
            Session data dict or None if session doesn't exist
        """
        if session_id in self.sessions:
            # Update last accessed time
            self.sessions[session_id]['info'].last_accessed = datetime.utcnow()
            return self.sessions[session_id]
        return None
    
    def get_session_info(self, session_id: str) -> Optional[SessionInfo]:
        """
        Gets information about the specified session.
        
        Args:
            session_id: ID of the session to retrieve info for
            
        Returns:
            SessionInfo or None if session doesn't exist
        """
        session_data = self.get_session(session_id)
        if session_data:
            return session_data['info']
        return None
    
    async def delete_session(self, session_id: str) -> bool:
        """
        Deletes the specified session and closes all its tabs/resources.
        
        Args:
            session_id: ID of the session to delete
            
        Returns:
            True if the session was deleted successfully, False otherwise
        """
        if session_id not in self.sessions:
            self.logger.warning(f"Session {session_id} does not exist")
            return False
        
        # Close the browser controller
        controller = self.sessions[session_id]['controller']
        await controller.close()
        
        # Remove the session
        del self.sessions[session_id]
        
        self.logger.info(f"Deleted session {session_id}")
        return True
    
    def get_all_sessions(self) -> List[SessionInfo]:
        """
        Gets information about all active sessions.
        
        Returns:
            List of SessionInfo for all active sessions
        """
        return [data['info'] for data in self.sessions.values()]
    
    def get_user_sessions(self, user_id: str) -> List[SessionInfo]:
        """
        Gets information about all sessions for a specific user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of SessionInfo for the user's sessions
        """
        user_sessions = []
        for data in self.sessions.values():
            if data['info'].user_id == user_id:
                user_sessions.append(data['info'])
        return user_sessions
    
    async def close_inactive_sessions(self, max_age_minutes: int = 30) -> int:
        """
        Closes sessions that have been inactive for more than the specified time.
        
        Args:
            max_age_minutes: Maximum age in minutes before a session is considered inactive
            
        Returns:
            Number of sessions closed
        """
        closed_count = 0
        current_time = datetime.utcnow()
        cutoff_time = current_time - timedelta(minutes=max_age_minutes)
        
        sessions_to_close = []
        for session_id, data in self.sessions.items():
            if data['info'].last_accessed < cutoff_time:
                sessions_to_close.append(session_id)
        
        for session_id in sessions_to_close:
            await self.delete_session(session_id)
            closed_count += 1
        
        self.logger.info(f"Closed {closed_count} inactive sessions")
        return closed_count


# For compatibility with Python < 3.7, add timedelta import
from datetime import timedelta