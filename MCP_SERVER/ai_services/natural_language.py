import re
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel
from models import UserPrompt, BrowserAction, ElementSelector, ActionType
from enum import Enum


class IntentType(str, Enum):
    """
    Types of user intents we can recognize
    """
    NAVIGATION = "navigation"
    CLICK = "click"
    TYPE = "type"
    EXTRACT = "extract"
    SCHEDULE = "schedule"
    MONITOR = "monitor"
    UNKNOWN = "unknown"


class NEREntity(BaseModel):
    """
    Named Entity Recognition result
    """
    text: str
    label: str  # URL, EMAIL, DATE, TIME, etc.
    start: int
    end: int


class IntentRecognitionResult(BaseModel):
    """
    Result of intent recognition
    """
    intent: IntentType
    confidence: float
    entities: List[NEREntity] = []
    action_type: Optional[ActionType] = None
    target: Optional[str] = None
    value: Optional[str] = None


class NaturalLanguageProcessor:
    """
    Processes natural language requests and extracts structured information
    """
    
    def __init__(self):
        self.intents_patterns = {
            IntentType.NAVIGATION: [
                r"navigate to (.+)",
                r"go to (.+)",
                r"visit (.+)",
                r"open (.+)",
                r"show me (.+)",
            ],
            IntentType.CLICK: [
                r"click on (.+)",
                r"click (.+)",
                r"press (.+)",
                r"select (.+)",
                r"choose (.+)",
            ],
            IntentType.TYPE: [
                r"type (.+) into (.+)",
                r"enter (.+) in (.+)",
                r"fill (.+) with (.+)",
                r"input (.+) to (.+)",
            ],
            IntentType.EXTRACT: [
                r"extract (.+) from (.+)",
                r"get (.+) from (.+)",
                r"find (.+) on (.+)",
                r"scrape (.+) from (.+)",
            ],
            IntentType.SCHEDULE: [
                r"schedule (.+)",
                r"plan (.+)",
                r"set up (.+)",
                r"arrange (.+)",
            ],
            IntentType.MONITOR: [
                r"monitor (.+)",
                r"watch (.+)",
                r"track (.+)",
                r"check (.+) for changes",
            ]
        }
        
        # Common action words that map to specific action types
        self.action_keywords = {
            "click": ActionType.CLICK,
            "press": ActionType.CLICK,
            "tap": ActionType.CLICK,
            "type": ActionType.TYPE,
            "enter": ActionType.TYPE,
            "fill": ActionType.TYPE,
            "input": ActionType.TYPE,
            "go to": ActionType.NAVIGATE,
            "visit": ActionType.NAVIGATE,
            "navigate": ActionType.NAVIGATE,
            "extract": ActionType.EXTRACT,
            "get": ActionType.EXTRACT,
            "find": ActionType.EXTRACT,
            "scrape": ActionType.EXTRACT,
        }
        
        # Common element selectors in natural language
        self.element_selectors = {
            "button": "css:button",
            "link": "css:a",
            "input": "css:input",
            "text field": "css:input[type='text'], textarea",
            "form": "css:form",
            "search": "css:[role='search'], input[type='search'], input[name*='search'], input[placeholder*='search']",
            "submit": "css:input[type='submit'], button[type='submit'], button[type='button']",
        }
    
    async def process_prompt(self, user_prompt: UserPrompt) -> IntentRecognitionResult:
        """
        Process a user prompt and extract intent and entities
        """
        text = user_prompt.prompt.lower().strip()
        
        # Extract intent
        intent_result = self._extract_intent(text)
        
        # Extract entities
        entities = self._extract_entities(text)
        
        # Enhance with additional processing
        enhanced_result = self._enhance_intent(intent_result, text)
        
        return IntentRecognitionResult(
            intent=enhanced_result.intent,
            confidence=enhanced_result.confidence,
            entities=entities,
            action_type=enhanced_result.action_type,
            target=enhanced_result.target,
            value=enhanced_result.value
        )
    
    def _extract_intent(self, text: str) -> IntentRecognitionResult:
        """
        Extract intent from the text using pattern matching
        """
        best_match = (None, 0, None)  # (intent, confidence, match)
        
        for intent, patterns in self.intents_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    # Calculate confidence based on pattern match certainty
                    confidence = 0.8  # Base confidence for a match
                    
                    # If this is a better match than previous, update
                    if confidence > best_match[1]:
                        best_match = (intent, confidence, match)
        
        # If no pattern matches, try to classify based on action keywords
        if best_match[0] is None:
            for keyword, action_type in self.action_keywords.items():
                if keyword in text:
                    best_match = (IntentType.UNKNOWN, 0.6, None)
                    break
        
        # Default to unknown if no match found
        if best_match[0] is None:
            return IntentRecognitionResult(
                intent=IntentType.UNKNOWN,
                confidence=0.0
            )
        
        intent, confidence, match = best_match
        
        # Extract target and value from match groups if available
        target = None
        value = None
        
        if match and len(match.groups()) >= 1:
            target = match.group(1)
            if len(match.groups()) > 1:
                value = match.group(2)
        
        # Determine action type based on intent
        action_type = self._intent_to_action_type(intent)
        
        return IntentRecognitionResult(
            intent=intent,
            confidence=confidence,
            action_type=action_type,
            target=target,
            value=value
        )
    
    def _enhance_intent(self, result: IntentRecognitionResult, text: str) -> IntentRecognitionResult:
        """
        Enhance the intent result with additional context
        """
        # If the intent is unknown but we have keywords, try to improve it
        if result.intent == IntentType.UNKNOWN:
            for keyword, action_type in self.action_keywords.items():
                if keyword in text:
                    # Determine intent based on action type
                    intent_map = {
                        ActionType.NAVIGATE: IntentType.NAVIGATION,
                        ActionType.CLICK: IntentType.CLICK,
                        ActionType.TYPE: IntentType.TYPE,
                        ActionType.EXTRACT: IntentType.EXTRACT,
                    }
                    
                    enhanced_intent = intent_map.get(action_type, IntentType.UNKNOWN)
                    return IntentRecognitionResult(
                        intent=enhanced_intent,
                        confidence=result.confidence,
                        action_type=action_type,
                        target=result.target,
                        value=result.value,
                        entities=result.entities
                    )
        
        # If we have a type but no specific intent, infer from the type
        if result.action_type and result.intent == IntentType.UNKNOWN:
            intent_map = {
                ActionType.NAVIGATE: IntentType.NAVIGATION,
                ActionType.CLICK: IntentType.CLICK,
                ActionType.TYPE: IntentType.TYPE,
                ActionType.EXTRACT: IntentType.EXTRACT,
            }
            enhanced_intent = intent_map.get(result.action_type, IntentType.UNKNOWN)
            result.intent = enhanced_intent
        
        return result
    
    def _extract_entities(self, text: str) -> List[NEREntity]:
        """
        Extract named entities from the text
        """
        entities = []
        
        # Extract URLs
        url_pattern = r'https?://[^\s\'"<>]+'
        for match in re.finditer(url_pattern, text):
            entities.append(NEREntity(
                text=match.group(),
                label="URL",
                start=match.start(),
                end=match.end()
            ))
        
        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        for match in re.finditer(email_pattern, text):
            entities.append(NEREntity(
                text=match.group(),
                label="EMAIL",
                start=match.start(),
                end=match.end()
            ))
        
        # Extract dates (simple pattern)
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b'
        for match in re.finditer(date_pattern, text):
            entities.append(NEREntity(
                text=match.group(),
                label="DATE",
                start=match.start(),
                end=match.end()
            ))
        
        # Extract times
        time_pattern = r'\b\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?\b'
        for match in re.finditer(time_pattern, text):
            entities.append(NEREntity(
                text=match.group(),
                label="TIME",
                start=match.start(),
                end=match.end()
            ))
        
        return entities
    
    def _intent_to_action_type(self, intent: IntentType) -> Optional[ActionType]:
        """
        Map intent to action type
        """
        intent_map = {
            IntentType.NAVIGATION: ActionType.NAVIGATE,
            IntentType.CLICK: ActionType.CLICK,
            IntentType.TYPE: ActionType.TYPE,
            IntentType.EXTRACT: ActionType.EXTRACT,
        }
        
        return intent_map.get(intent)
    
    async def generate_browser_action(self, recognition_result: IntentRecognitionResult) -> Optional[BrowserAction]:
        """
        Generate a browser action from the recognition result
        """
        if recognition_result.intent == IntentType.UNKNOWN:
            return None
        
        # Generate appropriate action based on intent
        if recognition_result.action_type == ActionType.NAVIGATE:
            # Extract URL from target or entities
            url = recognition_result.target
            if not url:
                # Look for URL entity
                for entity in recognition_result.entities:
                    if entity.label == "URL":
                        url = entity.text
                        break
            
            if url:
                return BrowserAction(
                    id="generated_action",
                    type=ActionType.NAVIGATE,
                    value=url,
                    description=f"Navigate to {url}"
                )
        
        elif recognition_result.action_type == ActionType.CLICK:
            # Find appropriate element selector
            element_value = recognition_result.target or "default"
            
            # Try to map to known element types
            selector_type = "text"  # Default
            selector_value = element_value
            
            for elem_name, selector in self.element_selectors.items():
                if elem_name in element_value:
                    if ':' in selector:
                        selector_type, selector_value = selector.split(':', 1)
                    else:
                        selector_type = "css"
                        selector_value = selector
                    break
            
            return BrowserAction(
                id="generated_action",
                type=ActionType.CLICK,
                element=ElementSelector(
                    type=selector_type,
                    value=selector_value,
                    description=element_value
                ),
                description=f"Click on {element_value}"
            )
        
        elif recognition_result.action_type == ActionType.TYPE:
            # For "type X into Y", X is the value to type and Y is the element
            value_to_type = recognition_result.target  # First captured group is the text to type
            element_value = recognition_result.value   # Second captured group is the element
            
            # Clean up the value to type (remove quotes if present)
            if value_to_type:
                value_to_type = value_to_type.strip().strip("'\"")
            
            if element_value:
                element_value = element_value.strip()
            
            # Handle other patterns like "fill X with Y" where X is element, Y is value
            if (not element_value or not value_to_type) and recognition_result.target:
                if " with " in recognition_result.target:
                    parts = recognition_result.target.split(" with ")
                    if len(parts) == 2:
                        element_value = parts[0].strip()
                        value_to_type = parts[1].strip().strip("'\"")
            
            if element_value and value_to_type:
                return BrowserAction(
                    id="generated_action",
                    type=ActionType.TYPE,
                    element=ElementSelector(
                        type="css",
                        value="input[type='text'], textarea",
                        description=element_value
                    ),
                    value=value_to_type,
                    description=f"Type '{value_to_type}' into {element_value}"
                )
            elif value_to_type:
                # If we only have the value, create a general input action
                return BrowserAction(
                    id="generated_action",
                    type=ActionType.TYPE,
                    element=ElementSelector(
                        type="css",
                        value="input[type='text'], textarea",
                        description="text input field"
                    ),
                    value=value_to_type,
                    description=f"Type '{value_to_type}' into text field"
                )
            elif element_value:
                # If we only have the element, create an empty input action
                return BrowserAction(
                    id="generated_action",
                    type=ActionType.TYPE,
                    element=ElementSelector(
                        type="css",
                        value="input[type='text'], textarea",
                        description=element_value
                    ),
                    value="",
                    description=f"Focus on {element_value}"
                )
        
        elif recognition_result.action_type == ActionType.EXTRACT:
            # Extract information from target element
            element_value = recognition_result.target
            return BrowserAction(
                id="generated_action",
                type=ActionType.EXTRACT,
                element=ElementSelector(
                    type="text",
                    value=element_value,
                    description=element_value
                ),
                description=f"Extract information from {element_value}"
            )
        
        return None