"""
Social media platform controller for AutomateAI
"""
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from datetime import datetime
import asyncio
import logging

from models import BrowserAction, ElementSelector, UserPrompt, TaskRequest
from .models import (
    SocialPlatform, SocialMediaAccount, SocialMediaCredentials, 
    PostContent, ScheduledPost, PostResult, SocialMediaTaskRequest
)
from agents.automateai_agent import AutomateAIAgent


logger = logging.getLogger(__name__)


class SocialMediaControllerInterface(ABC):
    """Abstract interface for social media platform controllers"""
    
    @abstractmethod
    async def login(self, credentials: SocialMediaCredentials) -> bool:
        """Login to the social media platform"""
        pass
    
    @abstractmethod
    async def post_content(self, content: PostContent) -> PostResult:
        """Post content to the social media platform"""
        pass
    
    @abstractmethod
    async def schedule_post(self, content: PostContent, scheduled_time: datetime) -> str:
        """Schedule a post for later publication"""
        pass
    
    @abstractmethod
    async def get_account_info(self) -> SocialMediaAccount:
        """Get current account information"""
        pass


class LinkedInController(SocialMediaControllerInterface):
    """Controller for LinkedIn operations"""
    
    def __init__(self, agent: AutomateAIAgent):
        self.agent = agent
        self.is_logged_in = False
        self.current_account: Optional[SocialMediaAccount] = None
    
    async def _ensure_browser_ready(self):
        """Ensure the browser controller is ready"""
        # Initialize browser controller if not already done
        if not hasattr(self.agent, '_browser_controller') or self.agent._browser_controller is None:
            from utils.browser_init import get_browser_controller
            self.agent._browser_controller = await get_browser_controller()
    
    async def login(self, credentials: SocialMediaCredentials) -> bool:
        """Login to LinkedIn using browser automation"""
        try:
            # Ensure browser is ready
            await self._ensure_browser_ready()
            
            # Navigate to LinkedIn login page
            navigate_action = BrowserAction(
                id=f"linkedin_login_nav_{int(datetime.utcnow().timestamp())}",
                type="navigate",
                value="https://www.linkedin.com/login",
                description="Navigate to LinkedIn login page"
            )
            
            # Execute navigation
            nav_result = await self.agent.execute_action(navigate_action)
            if not nav_result.success:
                logger.error("Failed to navigate to LinkedIn login page")
                return False
            
            # Fill email
            email_selector = ElementSelector(type="id", value="username", description="Email input field")
            email_action = BrowserAction(
                id=f"linkedin_email_{int(datetime.utcnow().timestamp())}",
                type="type",
                element=email_selector,
                value=credentials.username,
                description="Fill LinkedIn email field"
            )
            
            email_result = await self.agent.execute_action(email_action)
            if not email_result.success:
                logger.error("Failed to fill LinkedIn email field")
                return False
            
            # Fill password
            password_selector = ElementSelector(type="id", value="password", description="Password input field")
            password_action = BrowserAction(
                id=f"linkedin_password_{int(datetime.utcnow().timestamp())}",
                type="type",
                element=password_selector,
                value=credentials.password,
                description="Fill LinkedIn password field"
            )
            
            password_result = await self.agent.execute_action(password_action)
            if not password_result.success:
                logger.error("Failed to fill LinkedIn password field")
                return False
            
            # Click login button
            login_selector = ElementSelector(type="css", value="button[type='submit']", description="Login button")
            login_action = BrowserAction(
                id=f"linkedin_login_click_{int(datetime.utcnow().timestamp())}",
                type="click",
                element=login_selector,
                description="Click LinkedIn login button"
            )
            
            login_result = await self.agent.execute_action(login_action)
            success = login_result.success
            
            if success:
                self.is_logged_in = True
                logger.info("Successfully logged into LinkedIn")
            else:
                logger.error("Failed to login to LinkedIn")
            
            return success
        
        except Exception as e:
            logger.error(f"Error during LinkedIn login: {str(e)}")
            return False
    
    async def post_content(self, content: PostContent) -> PostResult:
        """Post content to LinkedIn"""
        try:
            if not self.is_logged_in:
                return PostResult(
                    post_id="", 
                    success=False, 
                    platform=SocialPlatform.LINKEDIN,
                    error_message="Not logged in"
                )
            
            # Navigate to home page
            navigate_action = BrowserAction(
                id=f"linkedin_home_nav_{int(datetime.utcnow().timestamp())}",
                type="navigate",
                value="https://www.linkedin.com/feed/",
                description="Navigate to LinkedIn home page"
            )
            
            nav_result = await self.agent.execute_action(navigate_action)
            if not nav_result.success:
                return PostResult(
                    post_id="", 
                    success=False, 
                    platform=SocialPlatform.LINKEDIN,
                    error_message="Failed to navigate to home page"
                )
            
            # Click on the post creation button
            post_selector = ElementSelector(
                type="css", 
                value="[data-test-id='profile-nav-item'] [data-test-id='share-box-button']",
                description="Create post button"
            )
            
            # If the above selector doesn't work, try common LinkedIn post selectors
            possible_selectors = [
                "[data-test-id='profile-nav-item'] [data-test-id='share-box-button']",
                "button[aria-label='Start a post']",
                "button.artdeco-button--primary",
                "div[contenteditable='true']"  # For the text area
            ]
            
            post_action = None
            for selector in possible_selectors:
                post_selector = ElementSelector(type="css", value=selector, description="Create post button")
                post_action = BrowserAction(
                    id=f"linkedin_post_click_{int(datetime.utcnow().timestamp())}",
                    type="click",
                    element=post_selector,
                    description="Click create post button"
                )
                
                result = await self.agent.execute_action(post_action)
                if result.success:
                    break
            
            if not result.success:
                return PostResult(
                    post_id="", 
                    success=False, 
                    platform=SocialPlatform.LINKEDIN,
                    error_message="Failed to find and click post creation button"
                )
            
            # Wait a bit for the post box to appear
            await asyncio.sleep(2)
            
            # Fill the post content
            post_text_selector = ElementSelector(
                type="css", 
                value="div[contenteditable='true']", 
                description="Post text area"
            )
            
            text_action = BrowserAction(
                id=f"linkedin_post_text_{int(datetime.utcnow().timestamp())}",
                type="type",
                element=post_text_selector,
                value=content.text,
                description="Fill post content"
            )
            
            text_result = await self.agent.execute_action(text_action)
            if not text_result.success:
                return PostResult(
                    post_id="", 
                    success=False, 
                    platform=SocialPlatform.LINKEDIN,
                    error_message="Failed to fill post content"
                )
            
            # Add hashtags if any
            if content.hashtags:
                hashtag_text = " " + " ".join([f"#{tag}" for tag in content.hashtags])
                hashtag_action = BrowserAction(
                    id=f"linkedin_hashtags_{int(datetime.utcnow().timestamp())}",
                    type="type",
                    element=post_text_selector,
                    value=hashtag_text,
                    description="Add hashtags to post"
                )
                
                await self.agent.execute_action(hashtag_action)
            
            # Upload images if any
            for img_url in content.images:
                # For now, we'll just add a note that images need to be uploaded
                # Actual image upload would require more complex automation
                logger.info(f"Image upload for LinkedIn post would use: {img_url}")
            
            # Click the post button
            post_button_selector = ElementSelector(
                type="css", 
                value="button[aria-label='Post']",
                description="Post button"
            )
            
            post_button_action = BrowserAction(
                id=f"linkedin_post_submit_{int(datetime.utcnow().timestamp())}",
                type="click",
                element=post_button_selector,
                description="Click post button"
            )
            
            submit_result = await self.agent.execute_action(post_button_action)
            
            post_result = PostResult(
                post_id=f"linkedin_{int(datetime.utcnow().timestamp())}",
                success=submit_result.success,
                platform=SocialPlatform.LINKEDIN,
                timestamp=datetime.utcnow()
            )
            
            if submit_result.success:
                logger.info("Successfully posted to LinkedIn")
            else:
                post_result.error_message = "Failed to submit post to LinkedIn"
            
            return post_result
        
        except Exception as e:
            logger.error(f"Error posting to LinkedIn: {str(e)}")
            return PostResult(
                post_id="", 
                success=False, 
                platform=SocialPlatform.LINKEDIN,
                error_message=str(e),
                timestamp=datetime.utcnow()
            )
    
    async def schedule_post(self, content: PostContent, scheduled_time: datetime) -> str:
        """Schedule a post for later publication on LinkedIn"""
        # For now, return a simple ID - actual scheduling would require
        # more complex browser automation or LinkedIn API usage
        logger.info(f"Scheduling LinkedIn post for {scheduled_time}")
        return f"linkedin_scheduled_{int(scheduled_time.timestamp())}"
    
    async def get_account_info(self) -> SocialMediaAccount:
        """Get current LinkedIn account information"""
        # In a real implementation, this would extract account info from the page
        return SocialMediaAccount(
            id="linkedin_demo_account",
            platform=SocialPlatform.LINKEDIN,
            username="demo_user",
            display_name="Demo User",
            profile_url="https://www.linkedin.com/in/demo",
            is_active=True
        )


class TwitterController(SocialMediaControllerInterface):
    """Controller for Twitter/X operations"""
    
    def __init__(self, agent: AutomateAIAgent):
        self.agent = agent
        self.is_logged_in = False
        self.current_account: Optional[SocialMediaAccount] = None
    
    async def _ensure_browser_ready(self):
        """Ensure the browser controller is ready"""
        # Initialize browser controller if not already done
        if not hasattr(self.agent, '_browser_controller') or self.agent._browser_controller is None:
            from utils.browser_init import get_browser_controller
            self.agent._browser_controller = await get_browser_controller()
    
    async def login(self, credentials: SocialMediaCredentials) -> bool:
        """Login to Twitter/X using browser automation"""
        try:
            # Ensure browser is ready
            await self._ensure_browser_ready()
            
            # Navigate to Twitter login page
            navigate_action = BrowserAction(
                id=f"twitter_login_nav_{int(datetime.utcnow().timestamp())}",
                type="navigate",
                value="https://twitter.com/login",
                description="Navigate to Twitter login page"
            )
            
            nav_result = await self.agent.execute_action(navigate_action)
            if not nav_result.success:
                logger.error("Failed to navigate to Twitter login page")
                return False
            
            # Fill username/email
            username_selector = ElementSelector(type="css", value="input[name='text']", description="Username field")
            username_action = BrowserAction(
                id=f"twitter_username_{int(datetime.utcnow().timestamp())}",
                type="type",
                element=username_selector,
                value=credentials.username,
                description="Fill Twitter username field"
            )
            
            username_result = await self.agent.execute_action(username_action)
            if not username_result.success:
                logger.error("Failed to fill Twitter username field")
                return False
            
            # Click next button
            next_selector = ElementSelector(type="css", value="div[role='button']:nth-child(6)",
                                          description="Next button")
            next_action = BrowserAction(
                id=f"twitter_next_{int(datetime.utcnow().timestamp())}",
                type="click",
                element=next_selector,
                description="Click next button"
            )
            
            await self.agent.execute_action(next_action)
            await asyncio.sleep(1)  # Wait for possible additional fields
            
            # Fill password
            password_selector = ElementSelector(type="css", value="input[name='password']", description="Password field")
            password_action = BrowserAction(
                id=f"twitter_password_{int(datetime.utcnow().timestamp())}",
                type="type",
                element=password_selector,
                value=credentials.password,
                description="Fill Twitter password field"
            )
            
            password_result = await self.agent.execute_action(password_action)
            if not password_result.success:
                logger.error("Failed to fill Twitter password field")
                return False
            
            # Click login button
            login_selector = ElementSelector(type="css", value="div[role='button'][data-testid='LoginForm_Login_Button']",
                                           description="Login button")
            login_action = BrowserAction(
                id=f"twitter_login_submit_{int(datetime.utcnow().timestamp())}",
                type="click",
                element=login_selector,
                description="Click Twitter login button"
            )
            
            login_result = await self.agent.execute_action(login_action)
            success = login_result.success
            
            if success:
                self.is_logged_in = True
                logger.info("Successfully logged into Twitter")
            else:
                logger.error("Failed to login to Twitter")
            
            return success
        
        except Exception as e:
            logger.error(f"Error during Twitter login: {str(e)}")
            return False
    
    async def post_content(self, content: PostContent) -> PostResult:
        """Post content to Twitter/X"""
        try:
            if not self.is_logged_in:
                return PostResult(
                    post_id="", 
                    success=False, 
                    platform=SocialPlatform.TWITTER,
                    error_message="Not logged in"
                )
            
            # Navigate to home page
            navigate_action = BrowserAction(
                id=f"twitter_home_nav_{int(datetime.utcnow().timestamp())}",
                type="navigate",
                value="https://twitter.com/home",
                description="Navigate to Twitter home page"
            )
            
            nav_result = await self.agent.execute_action(navigate_action)
            if not nav_result.success:
                return PostResult(
                    post_id="", 
                    success=False, 
                    platform=SocialPlatform.TWITTER,
                    error_message="Failed to navigate to home page"
                )
            
            # Click on the post button
            post_selector = ElementSelector(
                type="css", 
                value="a[href='/compose/post']",
                description="Post button"
            )
            
            post_action = BrowserAction(
                id=f"twitter_post_click_{int(datetime.utcnow().timestamp())}",
                type="click",
                element=post_selector,
                description="Click compose post button"
            )
            
            result = await self.agent.execute_action(post_action)
            if not result.success:
                return PostResult(
                    post_id="", 
                    success=False, 
                    platform=SocialPlatform.TWITTER,
                    error_message="Failed to find and click post button"
                )
            
            # Wait for the post composer to appear
            await asyncio.sleep(1)
            
            # Fill the tweet content
            post_text_selector = ElementSelector(
                type="css", 
                value="div[data-testid='tweetTextarea_0']",
                description="Tweet text area"
            )
            
            text_action = BrowserAction(
                id=f"twitter_post_text_{int(datetime.utcnow().timestamp())}",
                type="type",
                element=post_text_selector,
                value=content.text,
                description="Fill tweet content"
            )
            
            text_result = await self.agent.execute_action(text_action)
            if not text_result.success:
                return PostResult(
                    post_id="", 
                    success=False, 
                    platform=SocialPlatform.TWITTER,
                    error_message="Failed to fill tweet content"
                )
            
            # Add hashtags
            if content.hashtags:
                hashtag_text = " " + " ".join([f"#{tag}" for tag in content.hashtags])
                hashtag_action = BrowserAction(
                    id=f"twitter_hashtags_{int(datetime.utcnow().timestamp())}",
                    type="type",
                    element=post_text_selector,
                    value=hashtag_text,
                    description="Add hashtags to tweet"
                )
                
                await self.agent.execute_action(hashtag_action)
            
            # Add mentions
            if content.mentions:
                mention_text = " " + " ".join([f"@{mention}" for mention in content.mentions])
                mention_action = BrowserAction(
                    id=f"twitter_mentions_{int(datetime.utcnow().timestamp())}",
                    type="type",
                    element=post_text_selector,
                    value=mention_text,
                    description="Add mentions to tweet"
                )
                
                await self.agent.execute_action(mention_action)
            
            # Upload images if any
            for img_url in content.images:
                logger.info(f"Image upload for Twitter post would use: {img_url}")
            
            # Click the post button
            post_button_selector = ElementSelector(
                type="css", 
                value="div[data-testid='tweetButtonInline']",
                description="Post button"
            )
            
            post_button_action = BrowserAction(
                id=f"twitter_post_submit_{int(datetime.utcnow().timestamp())}",
                type="click",
                element=post_button_selector,
                description="Click post button"
            )
            
            submit_result = await self.agent.execute_action(post_button_action)
            
            post_result = PostResult(
                post_id=f"twitter_{int(datetime.utcnow().timestamp())}",
                success=submit_result.success,
                platform=SocialPlatform.TWITTER,
                timestamp=datetime.utcnow()
            )
            
            if submit_result.success:
                logger.info("Successfully posted to Twitter")
            else:
                post_result.error_message = "Failed to submit post to Twitter"
            
            return post_result
        
        except Exception as e:
            logger.error(f"Error posting to Twitter: {str(e)}")
            return PostResult(
                post_id="", 
                success=False, 
                platform=SocialPlatform.TWITTER,
                error_message=str(e),
                timestamp=datetime.utcnow()
            )
    
    async def schedule_post(self, content: PostContent, scheduled_time: datetime) -> str:
        """Schedule a post for later publication on Twitter"""
        logger.info(f"Scheduling Twitter post for {scheduled_time}")
        return f"twitter_scheduled_{int(scheduled_time.timestamp())}"
    
    async def get_account_info(self) -> SocialMediaAccount:
        """Get current Twitter account information"""
        return SocialMediaAccount(
            id="twitter_demo_account",
            platform=SocialPlatform.TWITTER,
            username="demo_user",
            display_name="Demo User",
            profile_url="https://twitter.com/demo",
            is_active=True
        )


class SocialMediaScheduler:
    """Main scheduler for social media posts"""
    
    def __init__(self, agent: AutomateAIAgent):
        self.agent = agent
        self.platform_controllers: Dict[SocialPlatform, SocialMediaControllerInterface] = {}
        self._initialize_controllers()
    
    def _initialize_controllers(self):
        """Initialize platform-specific controllers"""
        self.platform_controllers[SocialPlatform.LINKEDIN] = LinkedInController(self.agent)
        self.platform_controllers[SocialPlatform.TWITTER] = TwitterController(self.agent)
    
    async def authenticate_account(self, credentials: SocialMediaCredentials) -> bool:
        """Authenticate a social media account"""
        platform = credentials.platform
        if platform in self.platform_controllers:
            controller = self.platform_controllers[platform]
            return await controller.login(credentials)
        else:
            logger.error(f"Unsupported platform: {platform}")
            return False
    
    async def post_to_platforms(self, 
                               content: PostContent, 
                               platforms: List[SocialPlatform],
                               accounts: List[str] = None) -> List[PostResult]:
        """Post content to specified platforms"""
        results = []
        
        for platform in platforms:
            if platform in self.platform_controllers:
                controller = self.platform_controllers[platform]
                result = await controller.post_content(content)
                results.append(result)
            else:
                logger.error(f"Unsupported platform: {platform}")
                results.append(PostResult(
                    post_id="", 
                    success=False, 
                    platform=platform,
                    error_message="Platform not supported"
                ))
        
        return results
    
    async def schedule_post(self, 
                           content: PostContent, 
                           platforms: List[SocialPlatform], 
                           scheduled_time: datetime) -> Dict[SocialPlatform, str]:
        """Schedule a post across multiple platforms"""
        scheduled_post_ids = {}
        
        for platform in platforms:
            if platform in self.platform_controllers:
                controller = self.platform_controllers[platform]
                post_id = await controller.schedule_post(content, scheduled_time)
                scheduled_post_ids[platform] = post_id
            else:
                logger.error(f"Unsupported platform for scheduling: {platform}")
                scheduled_post_ids[platform] = None
        
        return scheduled_post_ids
    
    async def execute_social_media_task(self, task_request: SocialMediaTaskRequest) -> List[PostResult]:
        """Execute a social media task request"""
        if task_request.scheduling_time:
            # Schedule the post for later
            scheduled_ids = await self.schedule_post(
                task_request.content,
                task_request.target_platforms,
                task_request.scheduling_time
            )
            
            # Return results indicating scheduled status
            results = []
            for platform, post_id in scheduled_ids.items():
                results.append(PostResult(
                    post_id=post_id or "",
                    success=True,
                    platform=platform,
                    timestamp=task_request.scheduling_time
                ))
            return results
        else:
            # Post immediately
            return await self.post_to_platforms(
                task_request.content,
                task_request.target_platforms
            )