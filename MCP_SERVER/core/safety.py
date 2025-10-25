from typing import List, Dict, Any, Optional
from models import BrowserAction, TaskExecutionPlan, UserPrompt
from core.config import settings
import re
import logging

logger = logging.getLogger(__name__)


class SafetyValidator:
    """
    Validates actions and plans for safety compliance.

    This class provides methods to validate user prompts, browser actions, and
    task execution plans against a set of safety rules. It checks for
    disallowed actions, sensitive data, and potential security risks.
    """
    
    def __init__(self):
        """
        Initializes the SafetyValidator with settings from the configuration.
        """
        self.allowed_actions = settings.allowed_action_types
        self.max_execution_time = settings.max_execution_time
        self.blocked_domains = [
            "malware", "phishing", "scam", "hacking", "keylogger", 
            "trojan", "virus", "exploit", "spam", "botnet"
        ]
        self.sensitive_selectors = [
            "password", "ssn", "credit-card", "cvv", "pin", "social-security", 
            "bank-account", "routing-number", "api-key", "secret-key", "private-key"
        ]
        
    async def validate_plan(self, plan: TaskExecutionPlan) -> bool:
        """
        Validates an execution plan for safety.

        Args:
            plan: The TaskExecutionPlan to validate.

        Returns:
            True if the plan is safe, False otherwise.
        """
        # Check if all actions are allowed
        for action in plan.actions:
            if not await self.validate_action(action):
                logger.warning(f"Action {action.id} failed safety validation")
                return False
        
        # Check if estimated execution time is within limits
        if plan.estimated_duration and plan.estimated_duration > self.max_execution_time:
            logger.warning(f"Plan {plan.id} exceeds maximum execution time")
            return False
        
        # Check for potential security risks in the plan
        if await self._check_security_risks(plan):
            logger.warning(f"Plan {plan.id} contains potential security risks")
            return False
        
        return True
    
    async def validate_action(self, action: BrowserAction) -> bool:
        """
        Validates a single action for safety.

        Args:
            action: The BrowserAction to validate.

        Returns:
            True if the action is safe, False otherwise.
        """
        # Check if action type is allowed
        if action.type not in self.allowed_actions:
            logger.warning(f"Action type {action.type} is not allowed")
            return False
        
        # Check for sensitive element selectors
        if action.element:
            element_lower = action.element.value.lower() if action.element.value else ""
            for sensitive in self.sensitive_selectors:
                if sensitive in element_lower:
                    logger.warning(f"Action targets sensitive element: {action.element.value}")
                    return False
        
        # Check for potentially unsafe values (e.g., passwords in type actions)
        if action.type == "type" and action.value:
            value_str = str(action.value).lower()
            for sensitive in self.sensitive_selectors:
                if sensitive in value_str:
                    logger.warning(f"Action contains sensitive data in value: {action.value}")
                    return False
        
        return True
    
    async def validate_prompt(self, prompt: UserPrompt) -> bool:
        """
        Validates a user prompt for safety.

        Args:
            prompt: The UserPrompt to validate.

        Returns:
            True if the prompt is safe, False otherwise.
        """
        prompt_lower = prompt.prompt.lower()
        
        # Check for potentially malicious intent
        malicious_indicators = [
            "install malware", "steal", "hack", "crack", "keylogger", 
            "phishing", "spam", "botnet", "exploit", "virus", "trojan",
            "access private", "bypass security", "crack password", "brute force"
        ]
        
        for indicator in malicious_indicators:
            if indicator in prompt_lower:
                logger.warning(f"Prompt contains malicious intent: {indicator}")
                return False
        
        # Check for blocked domains in the prompt
        for domain in self.blocked_domains:
            if domain in prompt_lower:
                logger.warning(f"Prompt contains blocked domain reference: {domain}")
                return False
        
        return True
    
    async def _check_security_risks(self, plan: TaskExecutionPlan) -> bool:
        """
        Checks for potential security risks in a plan.

        Args:
            plan: The TaskExecutionPlan to check.

        Returns:
            True if a security risk is detected, False otherwise.
        """
        # Check for rapid-fire actions that might indicate abuse
        if len(plan.actions) > 50:  # arbitrary threshold
            logger.warning("Plan contains too many actions, potential abuse")
            return True
        
        # Check for patterns of actions that might indicate scraping or spam
        navigate_count = sum(1 for action in plan.actions if action.type == "navigate")
        click_count = sum(1 for action in plan.actions if action.type == "click")
        
        # If there are many navigates and clicks, it might be scraping
        if navigate_count > 10 and click_count > 20:
            logger.info("Plan may contain scraping pattern")
            # This may not be malicious, so we won't return True here
        
        return False

    async def _check_realtime_domain_risk(self, url: str) -> bool:
        """
        Checks a URL against real-time domain reputation services.
        In a real implementation, this would call external APIs like Google Safe Browsing API,
        PhishTank, or other domain reputation services.
        
        Args:
            url: The URL to check for safety
        
        Returns:
            True if the domain is flagged as risky, False otherwise.
        """
        # Placeholder for real-time domain checking
        # In a production implementation, you would integrate with a domain reputation API
        # For example, Google Safe Browsing API or similar service
        
        # For now, extract domain and check against local blocked list
        import re
        domain_pattern = r"https?://([a-zA-Z0-9\.-]+\.[a-zA-Z]{2,})"
        match = re.search(domain_pattern, url)
        
        if match:
            domain = match.group(1).lower()
            # Check against blocked domains list (could be expanded to call external API)
            for blocked in self.blocked_domains:
                if blocked in domain:
                    return True
        
        return False


class SafetyConfirmation:
    """
    Handles user confirmations for potentially risky actions.
    """
    
    def __init__(self):
        """
        Initializes the SafetyConfirmation handler.
        """
        self.pending_confirmations = {}
    
    async def request_confirmation(self, action: BrowserAction, user_id: str = "default_user") -> bool:
        """
        Requests user confirmation for a potentially risky action.

        Args:
            action: The BrowserAction requiring confirmation.
            user_id: The ID of the user.

        Returns:
            True if the action is confirmed, False otherwise. In this mock
            implementation, it always returns True.
        """
        # In a real implementation, this would send a notification to the user
        # For now, we'll implement a simple confirmation mechanism
        confirmation_id = f"{user_id}:{action.id}"
        
        # Store the pending confirmation
        self.pending_confirmations[confirmation_id] = {
            "action": action,
            "user_id": user_id,
            "confirmed": False
        }
        
        # Log the action requiring confirmation
        logger.info(f"Action {action.id} requires user confirmation: {action.description}")
        
        # In a real system, we would wait for user input here
        # For this implementation, we'll return True (assume user confirms)
        return True
    
    async def confirm_action(self, confirmation_id: str) -> bool:
        """
        Confirms a pending action.

        Args:
            confirmation_id: The ID of the confirmation to confirm.

        Returns:
            True if the confirmation is found and confirmed, False otherwise.
        """
        if confirmation_id in self.pending_confirmations:
            self.pending_confirmations[confirmation_id]["confirmed"] = True
            return True
        return False


class SafetyLogger:
    """
    Logs safety-related events for audit purposes.
    """
    
    def __init__(self):
        """
        Initializes the SafetyLogger.
        """
        self.logger = logging.getLogger("safety_audit")
        
        # Set up file handler for safety logs
        handler = logging.FileHandler("safety_audit.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    async def log_action(self, action: BrowserAction, user_id: str = "default_user", success: bool = True):
        """
        Logs an action for safety auditing.

        Args:
            action: The BrowserAction to log.
            user_id: The ID of the user who performed the action.
            success: Whether the action was successful.
        """
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"USER:{user_id} ACTION:{action.type} ID:{action.id} STATUS:{status}")
    
    async def log_safety_violation(self, message: str, user_id: str = "default_user"):
        """
        Logs a safety violation.

        Args:
            message: The safety violation message.
            user_id: The ID of the user associated with the violation.
        """
        self.logger.warning(f"SAFETY VIOLATION - USER:{user_id} - {message}")
    
    async def log_prompt(self, prompt: UserPrompt, user_id: str = "default_user"):
        """
        Logs a user prompt for review.

        Args:
            prompt: The UserPrompt to log.
            user_id: The ID of the user who submitted the prompt.
        """
        self.logger.info(f"USER:{user_id} PROMPT:{prompt.prompt[:100]}...")  # First 100 chars