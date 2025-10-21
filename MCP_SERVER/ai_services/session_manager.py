import asyncio
import logging
import secrets
import time
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel
from uuid import uuid4

from core.browser_controller import BrowserControllerInterface, MockBrowserController
from core.config import settings


class SessionInfo(BaseModel):
    """
    Information about a browser session
    """
    session_id: str
    user_id: str
    created_at: datetime
    last_activity: datetime
    is_active: bool
    browser_type: str  # 'mock' or 'playwright'
    permission_level: str  # 'read', 'write', 'full'
    allowed_domains: List[str] = []


class SessionManager:
    """
    Manages secure browser sessions for different users
    """
    
    def __init__(self):
        self.sessions: Dict[str, SessionInfo] = {}
        self.browser_instances: Dict[str, BrowserControllerInterface] = {}
        self.user_sessions: Dict[str, List[str]] = {}  # user_id -> [session_ids...]
        self.max_sessions_per_user = 5
        self.session_timeout = timedelta(minutes=settings.browser_timeout//60000 if settings.browser_timeout >= 60000 else 30)  # 30 min default
        self.logger = logging.getLogger(__name__)
        
        # Start the cleanup task
        self._cleanup_task = None
        self._stop_cleanup = asyncio.Event()
    
    async def start(self):
        """
        Start the session manager
        """
        self._cleanup_task = asyncio.create_task(self._cleanup_expired_sessions())
        self.logger.info("Session manager started")
    
    async def stop(self):
        """
        Stop the session manager
        """
        self._stop_cleanup.set()
        if self._cleanup_task:
            await self._cleanup_task
        
        # Close all browser instances
        for session_id, browser in self.browser_instances.items():
            try:
                await browser.close()
            except Exception as e:
                self.logger.error(f"Error closing browser instance for session {session_id}: {e}")
        
        self.logger.info("Session manager stopped")
    
    async def create_session(self, user_id: str, permission_level: str = "write", allowed_domains: List[str] = None) -> Optional[SessionInfo]:
        """
        Create a new browser session for a user
        """
        # Check if user has reached maximum sessions
        user_session_ids = self.user_sessions.get(user_id, [])
        if len(user_session_ids) >= self.max_sessions_per_user:
            self.logger.warning(f"User {user_id} has reached maximum session limit")
            return None
        
        # Generate a unique session ID
        session_id = secrets.token_urlsafe(32)
        
        # Create a browser controller instance
        # In a real implementation, this would create a new isolated browser instance
        # For now, we'll use the mock controller as a placeholder
        try:
            from utils.browser_init import get_browser_controller
            browser_controller = await get_browser_controller()
        except:
            # Fallback to mock controller
            browser_controller = MockBrowserController()
        
        self.browser_instances[session_id] = browser_controller
        
        # Create session info
        session_info = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            is_active=True,
            browser_type="mock" if isinstance(browser_controller, MockBrowserController) else "playwright",
            permission_level=permission_level,
            allowed_domains=allowed_domains or []
        )
        
        # Store session info
        self.sessions[session_id] = session_info
        
        # Track user's sessions
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = []
        self.user_sessions[user_id].append(session_id)
        
        self.logger.info(f"Created session {session_id} for user {user_id}")
        
        return session_info
    
    async def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """
        Get session information by session ID
        """
        session_info = self.sessions.get(session_id)
        if session_info and session_info.is_active:
            # Update last activity
            session_info.last_activity = datetime.utcnow()
            return session_info
        return None
    
    async def get_browser_controller(self, session_id: str) -> Optional[BrowserControllerInterface]:
        """
        Get the browser controller for a specific session
        """
        if session_id in self.browser_instances:
            return self.browser_instances[session_id]
        return None
    
    async def validate_session_access(self, session_id: str, url: str) -> bool:
        """
        Validate if a session has permission to access a specific URL
        """
        session_info = await self.get_session(session_id)
        if not session_info:
            return False
        
        # Check permission level
        if session_info.permission_level not in ["write", "full"]:
            return False  # read-only sessions can't access most URLs
        
        # Check allowed domains if specified
        if session_info.allowed_domains:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc.lower()
            if domain not in [d.lower() for d in session_info.allowed_domains]:
                return False
        
        return True
    
    async def close_session(self, session_id: str) -> bool:
        """
        Close and remove a session
        """
        if session_id not in self.sessions:
            return False
        
        session_info = self.sessions[session_id]
        
        # Remove from user's session list
        if session_info.user_id in self.user_sessions:
            if session_id in self.user_sessions[session_info.user_id]:
                self.user_sessions[session_info.user_id].remove(session_id)
        
        # Close browser instance
        if session_id in self.browser_instances:
            try:
                await self.browser_instances[session_id].close()
            except Exception as e:
                self.logger.error(f"Error closing browser instance for session {session_id}: {e}")
            finally:
                del self.browser_instances[session_id]
        
        # Remove session info
        del self.sessions[session_id]
        
        self.logger.info(f"Closed session {session_id} for user {session_info.user_id}")
        return True
    
    async def _cleanup_expired_sessions(self):
        """
        Periodically clean up expired sessions
        """
        while not self._stop_cleanup.is_set():
            try:
                current_time = datetime.utcnow()
                expired_sessions = []
                
                for session_id, session_info in self.sessions.items():
                    if (current_time - session_info.last_activity) > self.session_timeout:
                        expired_sessions.append(session_id)
                
                for session_id in expired_sessions:
                    self.logger.info(f"Cleaning up expired session {session_id}")
                    await self.close_session(session_id)
                
                # Check every 5 minutes
                try:
                    await asyncio.wait_for(self._stop_cleanup.wait(), timeout=300)
                except asyncio.TimeoutError:
                    continue  # Normal timeout, continue the loop
                
            except Exception as e:
                self.logger.error(f"Error in session cleanup: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying
    
    async def get_user_sessions(self, user_id: str) -> List[SessionInfo]:
        """
        Get all sessions for a specific user
        """
        session_ids = self.user_sessions.get(user_id, [])
        return [self.sessions[sid] for sid in session_ids if sid in self.sessions]
    
    async def get_active_session_count(self) -> int:
        """
        Get the number of active sessions
        """
        count = 0
        current_time = datetime.utcnow()
        for session_info in self.sessions.values():
            if session_info.is_active and (current_time - session_info.last_activity) <= self.session_timeout:
                count += 1
        return count


class SessionMiddleware:
    """
    Middleware to handle session management in API requests
    """
    
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
        self.logger = logging.getLogger(__name__)
    
    async def authenticate_session(self, session_id: str) -> Optional[SessionInfo]:
        """
        Authenticate a session ID
        """
        session_info = await self.session_manager.get_session(session_id)
        if not session_info:
            self.logger.warning(f"Authentication failed for session ID: {session_id}")
            return None
        return session_info
    
    async def validate_and_get_controller(self, session_id: str) -> Optional[BrowserControllerInterface]:
        """
        Validate a session and get its browser controller
        """
        session_info = await self.authenticate_session(session_id)
        if not session_info:
            return None
        
        return await self.session_manager.get_browser_controller(session_id)