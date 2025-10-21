import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field

from models import UserPrompt, TaskExecutionPlan, BrowserAction, BrowserState
from core.config import settings


class VisionLanguageResponse(BaseModel):
    """
    Response from the vision-language model
    """
    success: bool
    actions: List[Dict[str, Any]] = Field(default_factory=list)
    reasoning: str = ""
    error: Optional[str] = None


class VisionLanguageProvider(ABC):
    """
    Abstract interface for vision-language model providers
    """
    
    @abstractmethod
    async def process_request(
        self, 
        user_prompt: UserPrompt, 
        browser_state: BrowserState
    ) -> VisionLanguageResponse:
        """
        Process a user request using the vision-language model
        """
        pass


class GeminiVisionProvider(VisionLanguageProvider):
    """
    Integration with Google's Gemini vision-language model
    """
    
    def __init__(self):
        self.api_key = settings.gemini_api_key
        self.api_url = settings.gemini_api_url
        self.logger = logging.getLogger(__name__)
    
    async def process_request(
        self, 
        user_prompt: UserPrompt, 
        browser_state: BrowserState
    ) -> VisionLanguageResponse:
        """
        Process a user request using the Gemini API
        """
        if not self.api_key:
            return VisionLanguageResponse(
                success=False,
                error="Gemini API key not configured"
            )
        
        # Prepare the request payload
        prompt = self._build_prompt(user_prompt, browser_state)
        
        # In a real implementation, we would make an HTTP request to Gemini
        # For now, we'll simulate the response with a mock
        return await self._mock_gemini_response(user_prompt, browser_state)
    
    def _build_prompt(self, user_prompt: UserPrompt, browser_state: BrowserState) -> str:
        """
        Build the prompt to send to the vision-language model
        """
        return f"""
        User request: {user_prompt.prompt}
        Current page URL: {browser_state.url}
        Current page title: {browser_state.title}
        Current page content: {browser_state.dom_content[:2000]}...  # Truncate to 2000 chars
        
        Based on this information, provide a step-by-step plan to complete the user's request.
        Respond in the following JSON format:
        {{
            "reasoning": "Brief explanation of the plan",
            "actions": [
                {{
                    "type": "click" | "type" | "navigate" | "extract",
                    "selector": {{"type": "css" | "xpath" | "text", "value": "selector_value"}},
                    "value": "text to type" | "url to navigate to",
                    "description": "What this action does"
                }}
            ]
        }}
        """
    
    async def _mock_gemini_response(
        self, 
        user_prompt: UserPrompt, 
        browser_state: BrowserState
    ) -> VisionLanguageResponse:
        """
        Mock response for development purposes
        In production, this would be a real API call to Gemini
        """
        import random
        await asyncio.sleep(0.1)  # Simulate API call delay
        
        try:
            # Simple pattern matching to generate appropriate actions
            prompt_lower = user_prompt.prompt.lower()
            
            actions = []
            
            if "navigate" in prompt_lower or "go to" in prompt_lower:
                # Extract URL if present, otherwise default to example.com
                import re
                urls = re.findall(r'https?://[^\s\'"<>]+', user_prompt.prompt)
                url = urls[0] if urls else "https://example.com"
                
                actions.append({
                    "type": "navigate",
                    "value": url,
                    "description": f"Navigate to {url}"
                })
            
            if "click" in prompt_lower or "button" in prompt_lower or "search" in prompt_lower:
                actions.append({
                    "type": "click",
                    "selector": {"type": "text", "value": "search", "description": "Search button"},
                    "description": "Click search button"
                })
            
            if "type" in prompt_lower or "enter" in prompt_lower or "fill" in prompt_lower:
                # Find text to enter
                import re
                text_matches = re.findall(r'["\']([^"\']+)["\']', user_prompt.prompt)
                text_to_type = text_matches[0] if text_matches else "sample text"
                
                actions.append({
                    "type": "type",
                    "selector": {"type": "css", "value": "input[type='text'], textarea", "description": "Text input field"},
                    "value": text_to_type,
                    "description": f"Type '{text_to_type}' into field"
                })
            
            # Default action if no specific action could be identified
            if not actions:
                actions = [
                    {
                        "type": "navigate",
                        "value": "https://example.com",
                        "description": "Navigate to example.com as default action"
                    }
                ]
            
            reasoning = f"Based on user request: '{user_prompt.prompt}', I plan to execute {len(actions)} actions."
            
            return VisionLanguageResponse(
                success=True,
                actions=actions,
                reasoning=reasoning
            )
        
        except Exception as e:
            return VisionLanguageResponse(
                success=False,
                error=f"Error processing request: {str(e)}"
            )


class OpenAIVisionProvider(VisionLanguageProvider):
    """
    Integration with OpenAI's vision-language model (placeholder implementation)
    """
    
    async def process_request(
        self, 
        user_prompt: UserPrompt, 
        browser_state: BrowserState
    ) -> VisionLanguageResponse:
        """
        Process a user request using OpenAI's API (placeholder)
        """
        # Placeholder implementation - would connect to OpenAI API in real implementation
        return VisionLanguageResponse(
            success=False,
            error="OpenAI vision provider not yet implemented"
        )


class VisionLanguageProcessor:
    """
    Main processor that handles vision-language model integration
    """
    
    def __init__(self):
        self.provider: VisionLanguageProvider = None
        self.logger = logging.getLogger(__name__)
        
        # Initialize the appropriate provider based on configuration
        if settings.gemini_api_key:
            self.provider = GeminiVisionProvider()
        else:
            # Fallback provider that can't process requests but provides helpful error messages
            self.provider = self._create_fallback_provider()
    
    def _create_fallback_provider(self) -> VisionLanguageProvider:
        """
        Create a fallback provider when no API keys are configured
        """
        class FallbackProvider(VisionLanguageProvider):
            async def process_request(self, user_prompt: UserPrompt, browser_state: BrowserState) -> VisionLanguageResponse:
                return VisionLanguageResponse(
                    success=False,
                    error="No vision-language model provider configured. Please set up an API key."
                )
        
        return FallbackProvider()
    
    async def process_user_request(
        self, 
        user_prompt: UserPrompt, 
        browser_state: BrowserState
    ) -> TaskExecutionPlan:
        """
        Process a user request and return an execution plan
        """
        if not self.provider:
            self.logger.error("No vision-language provider configured")
            raise ValueError("No vision-language provider configured")
        
        response = await self.provider.process_request(user_prompt, browser_state)
        
        if not response.success:
            self.logger.error(f"Vision-language processing failed: {response.error}")
            raise ValueError(f"Processing failed: {response.error}")
        
        # Convert the response actions to BrowserAction objects
        browser_actions = []
        for i, action_data in enumerate(response.actions):
            action_id = f"vl_action_{user_prompt.model_dump().get('id', 'unknown')}_{i}"
            
            browser_action = BrowserAction(
                id=action_id,
                type=action_data.get("type", "click"),
                element=action_data.get("selector"),
                value=action_data.get("value"),
                description=action_data.get("description", ""),
                metadata={"source": "vision_language_model"}
            )
            browser_actions.append(browser_action)
        
        # Create and return the execution plan
        plan = TaskExecutionPlan(
            id=f"plan_{user_prompt.model_dump().get('id', 'unknown')}",
            task_id=user_prompt.model_dump().get('id', 'unknown'),
            actions=browser_actions,
            status="pending",
            metadata={
                "reasoning": response.reasoning,
                "source": "vision_language_model"
            }
        )
        
        return plan