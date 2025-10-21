import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from models import (
    UserPrompt, TaskRequest, TaskResponse, TaskExecutionPlan, 
    BrowserAction, ActionResult, BrowserState
)
from ai_services.vision_language import VisionLanguageProcessor
from ai_services.natural_language import NaturalLanguageProcessor
from ai_services.state_observer import BrowserStateObserver
from core.browser_controller import BrowserControllerInterface
from core.config import settings
from core.safety import SafetyValidator, SafetyConfirmation


class ActionExecutionResult:
    """
    Result of executing an action or plan
    """
    def __init__(self, success: bool, action_results: List[ActionResult] = None, error: str = None):
        self.success = success
        self.action_results = action_results or []
        self.error = error
        self.completed_at = datetime.utcnow()


class ActionExecutionFramework:
    """
    Framework for executing browser automation actions
    Integrates vision-language processing, NLP, state observation, and safety checks
    """
    
    def __init__(self, browser_controller: BrowserControllerInterface):
        self.browser_controller = browser_controller
        self.vision_language_processor = VisionLanguageProcessor()
        self.nlp_processor = NaturalLanguageProcessor()
        self.state_observer = BrowserStateObserver(browser_controller)
        self.safety_validator = SafetyValidator()
        self.safety_confirmation = SafetyConfirmation()
        
        self.logger = logging.getLogger(__name__)
        self.active_tasks: Dict[str, TaskResponse] = {}
    
    async def process_user_request(self, user_prompt: UserPrompt) -> TaskResponse:
        """
        Process a user request end-to-end
        """
        task_id = str(uuid.uuid4())
        
        # Create initial task response
        task_request = TaskRequest(
            id=task_id,
            user_prompt=user_prompt,
            target_urls=[],
            expected_outputs=[]
        )
        
        task_response = TaskResponse(
            task_id=task_id,
            status="processing",
            request=task_request,
            started_at=datetime.utcnow()
        )
        
        self.active_tasks[task_id] = task_response
        
        try:
            # Step 1: Observe current browser state
            self.logger.info(f"Observing browser state for task {task_id}")
            state_result = await self.state_observer.observe_state()
            
            if not state_result.success:
                raise Exception(f"Failed to observe browser state: {state_result.error}")
            
            # Step 2: Generate execution plan using vision-language model
            self.logger.info(f"Generating execution plan for task {task_id}")
            
            # First try with NLP to see if it's a simple request
            nlp_result = await self.nlp_processor.process_prompt(user_prompt)
            
            if nlp_result.intent == "unknown":
                # Use vision-language model for complex understanding
                plan = await self.vision_language_processor.process_user_request(
                    user_prompt, state_result.browser_state
                )
            else:
                # For simple requests, we can potentially create plan directly from NLP
                # For now, let's use vision-language for all requests
                plan = await self.vision_language_processor.process_user_request(
                    user_prompt, state_result.browser_state
                )
            
            task_response.plan = plan
            
            # Step 3: Validate the plan for safety
            self.logger.info(f"Validating plan safety for task {task_id}")
            if not await self.safety_validator.validate_plan(plan):
                task_response.status = "failed"
                task_response.error = "Task plan failed safety validation"
                return task_response
            
            # Step 4: Execute the plan
            self.logger.info(f"Executing plan for task {task_id}")
            execution_result = await self.execute_plan(plan)
            
            task_response.results = execution_result.action_results
            task_response.final_state = await self.browser_controller.get_page_state()
            
            # Step 5: Determine final status
            if execution_result.success:
                task_response.status = "completed"
            else:
                task_response.status = "failed"
                if execution_result.error:
                    task_response.error = execution_result.error
            
            task_response.completed_at = execution_result.completed_at
            
        except Exception as e:
            self.logger.error(f"Error processing task {task_id}: {e}")
            task_response.status = "failed"
            task_response.error = str(e)
        
        return task_response
    
    async def execute_plan(self, plan: TaskExecutionPlan) -> ActionExecutionResult:
        """
        Execute a complete action plan
        """
        results = []
        success = True
        error = None
        
        try:
            for action in plan.actions:
                # Validate each action before execution
                if not await self.safety_validator.validate_action(action):
                    result = ActionResult(
                        action_id=action.id,
                        success=False,
                        error="Action failed safety validation",
                        timestamp=action.created_at
                    )
                    results.append(result)
                    success = False
                    error = f"Action {action.id} failed safety validation"
                    break
                
                # For high-risk actions, request confirmation
                if await self._is_high_risk_action(action):
                    confirmed = await self.safety_confirmation.request_confirmation(action)
                    if not confirmed:
                        result = ActionResult(
                            action_id=action.id,
                            success=False,
                            error="User did not confirm high-risk action",
                            timestamp=action.created_at
                        )
                        results.append(result)
                        success = False
                        error = "User did not confirm high-risk action"
                        break
                
                # Execute the action
                result = await self.execute_action(action)
                results.append(result)
                
                # If an action fails, stop execution
                if not result.success:
                    success = False
                    error = f"Action {action.id} failed: {result.error}"
                    break
        
        except Exception as e:
            success = False
            error = f"Unexpected error during plan execution: {str(e)}"
        
        return ActionExecutionResult(success, results, error)
    
    async def execute_action(self, action: BrowserAction) -> ActionResult:
        """
        Execute a single browser action
        """
        try:
            # Wait for the element if needed
            if action.element:
                element_exists = await self.browser_controller.wait_for_element(
                    action.element, timeout=action.timeout or settings.browser_timeout
                )
                if not element_exists:
                    return ActionResult(
                        action_id=action.id,
                        success=False,
                        error=f"Element not found: {action.element.value}",
                        timestamp=datetime.utcnow()
                    )
            
            # Execute the action based on its type
            if action.type == "navigate":
                success = await self.browser_controller.navigate(
                    action.value or "", 
                    action.metadata.get("new_tab", False)
                )
                result = f"Navigated to {action.value}" if success else "Navigation failed"
                
            elif action.type == "click":
                if not action.element:
                    return ActionResult(
                        action_id=action.id,
                        success=False,
                        error="Click action requires an element selector",
                        timestamp=datetime.utcnow()
                    )
                
                success = await self.browser_controller.click(
                    action.element,
                    action.metadata.get("button", "left"),
                    action.metadata.get("click_count", 1)
                )
                result = f"Clicked on {action.element.value}" if success else "Click failed"
                
            elif action.type == "type":
                if not (action.element and action.value is not None):
                    return ActionResult(
                        action_id=action.id,
                        success=False,
                        error="Type action requires both an element selector and a value",
                        timestamp=datetime.utcnow()
                    )
                
                success = await self.browser_controller.type_text(
                    action.element,
                    str(action.value),
                    action.metadata.get("clear", True)
                )
                result = f"Typed text into {action.element.value}" if success else "Type action failed"
                
            elif action.type == "extract":
                if not action.element:
                    return ActionResult(
                        action_id=action.id,
                        success=False,
                        error="Extract action requires an element selector",
                        timestamp=datetime.utcnow()
                    )
                
                extracted_text = await self.browser_controller.extract_text(action.element)
                success = extracted_text is not None
                result = extracted_text or "Extraction failed"
                
            elif action.type == "screenshot":
                screenshot_path = action.value or f"screenshots/action_{action.id}.png"
                success = await self.browser_controller.take_screenshot(screenshot_path)
                result = f"Screenshot saved to {screenshot_path}" if success else "Screenshot failed"
                
            else:
                return ActionResult(
                    action_id=action.id,
                    success=False,
                    error=f"Unsupported action type: {action.type}",
                    timestamp=datetime.utcnow()
                )
            
            return ActionResult(
                action_id=action.id,
                success=success,
                result=result,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            return ActionResult(
                action_id=action.id,
                success=False,
                error=str(e),
                timestamp=datetime.utcnow()
            )
    
    async def _is_high_risk_action(self, action: BrowserAction) -> bool:
        """
        Determine if an action is high-risk and requires user confirmation
        """
        # Actions that might be high-risk:
        # - Actions targeting sensitive elements (password, SSN, etc.)
        # - Actions that change system settings
        # - Actions that might trigger financial transactions
        
        if not action.element or not action.element.value:
            return False
        
        sensitive_keywords = [
            "password", "ssn", "credit-card", "cvv", "pin", "social-security",
            "bank-account", "routing-number", "api-key", "secret", "private",
            "payment", "checkout", "purchase", "delete", "remove", "cancel"
        ]
        
        element_lower = action.element.value.lower()
        for keyword in sensitive_keywords:
            if keyword in element_lower:
                return True
        
        return False
    
    async def get_task_status(self, task_id: str) -> Optional[TaskResponse]:
        """
        Get the status of a specific task
        """
        return self.active_tasks.get(task_id)
    
    async def get_all_tasks(self) -> Dict[str, TaskResponse]:
        """
        Get all active tasks
        """
        return self.active_tasks.copy()