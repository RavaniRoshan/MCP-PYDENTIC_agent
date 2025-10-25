from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import logging

from models import (
    ScrapingTask, 
    ScrapingResult, 
    ExtractedData, 
    ExtractionPattern,
    ExtractAction,
    ElementSelector,
    ActionType,
    ExtractMethod,
    ExtractionFormat
)
from core.browser_controller import BrowserControllerInterface
from ai_services.action_execution import ActionExecutionFramework


class ScrapingService:
    """
    A service for handling complex web scraping tasks.
    """
    
    def __init__(self, action_execution_framework: ActionExecutionFramework, browser_controller: BrowserControllerInterface):
        self.action_execution_framework = action_execution_framework
        self.browser_controller = browser_controller
        self.logger = logging.getLogger(__name__)
        
    async def execute_scraping_task(self, scraping_task: ScrapingTask) -> ScrapingResult:
        """
        Executes a comprehensive scraping task with multiple extraction patterns.
        
        Args:
            scraping_task: The scraping task to execute.
            
        Returns:
            ScrapingResult containing the results of the scraping task.
        """
        start_time = datetime.utcnow()
        results = []
        errors = []
        error_count = 0
        
        try:
            # Navigate to the start URLs
            for url in scraping_task.start_urls:
                # Navigate to the URL
                from models import BrowserAction
                nav_action = BrowserAction(
                    id=f"nav_{url.replace('https://', '').replace('http://', '').replace('/', '_')}",
                    type=ActionType.NAVIGATE,
                    value=url
                )
                
                nav_result = await self.action_execution_framework.execute_action(nav_action)
                if not nav_result.success:
                    error_count += 1
                    errors.append({"url": url, "error": f"Navigation failed: {nav_result.error}"})
                    continue
                
                # Apply extraction patterns to the current page
                page_results = await self._extract_from_page(scraping_task.extraction_patterns)
                results.extend(page_results)
                
                # Handle pagination if specified
                if scraping_task.extraction_patterns and scraping_task.max_pages:
                    await self._handle_pagination(scraping_task)
            
            # Calculate success rate
            total_attempts = len(scraping_task.start_urls)
            success_count = total_attempts - error_count
            success_rate = success_count / total_attempts if total_attempts > 0 else 0.0
            
            # Calculate total items extracted
            total_items = sum([len(result.extracted_content) if isinstance(result.extracted_content, list) 
                              else 1 for result in results])
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            return ScrapingResult(
                task_id=scraping_task.id,
                results=results,
                total_items_extracted=total_items,
                success_rate=success_rate,
                duration=duration,
                error_count=error_count,
                errors=errors
            )
            
        except Exception as e:
            self.logger.error(f"Error executing scraping task {scraping_task.id}: {str(e)}")
            return ScrapingResult(
                task_id=scraping_task.id,
                results=[],
                total_items_extracted=0,
                success_rate=0.0,
                duration=(datetime.utcnow() - start_time).total_seconds(),
                error_count=1,
                errors=[{"task": scraping_task.name, "error": str(e)}]
            )
    
    async def _extract_from_page(self, extraction_patterns: List[ExtractionPattern]) -> List[ExtractedData]:
        """
        Extracts data from the current page based on the provided patterns.
        
        Args:
            extraction_patterns: List of extraction patterns to apply to the page.
            
        Returns:
            List of extracted data objects.
        """
        extracted_data = []
        
        for pattern in extraction_patterns:
            for rule in pattern.rules:
                try:
                    # Create an extract action based on the rule
                    element_selector = ElementSelector(
                        type="css",  # Could be determined from the selector format
                        value=rule.selector,
                        description=f"Extract {rule.field_name}"
                    )
                    
                    # Determine the extraction method based on the rule
                    extract_method = pattern.method
                    if extract_method == ExtractMethod.ATTRIBUTE and rule.attribute:
                        action = ExtractAction(
                            id=f"extract_{rule.field_name}",
                            method=ExtractMethod.ATTRIBUTE,
                            selector=element_selector,
                            attribute_name=rule.attribute
                        )
                    elif extract_method == ExtractMethod.TABLE:
                        action = ExtractAction(
                            id=f"extract_{rule.field_name}",
                            method=ExtractMethod.TABLE,
                            selector=element_selector
                        )
                    else:
                        action = ExtractAction(
                            id=f"extract_{rule.field_name}",
                            method=extract_method,
                            selector=element_selector
                        )
                    
                    # Execute the extraction action
                    result = await self.action_execution_framework.execute_action(action)
                    
                    if result.success:
                        extracted_data.append(ExtractedData(
                            id=action.id,
                            extracted_content=result.result,
                            method_used=action.method,
                            source_url=(await self.browser_controller.get_page_state()).url,
                            success=True,
                            metadata={"field_name": rule.field_name, "pattern_name": pattern.name}
                        ))
                except Exception as e:
                    self.logger.error(f"Error extracting with pattern {pattern.name}: {str(e)}")
                    extracted_data.append(ExtractedData(
                        id=f"error_{pattern.name}",
                        extracted_content={},
                        method_used=pattern.method,
                        source_url=(await self.browser_controller.get_page_state()).url,
                        success=False,
                        error_message=str(e)
                    ))
        
        return extracted_data
    
    async def _handle_pagination(self, scraping_task: ScrapingTask):
        """
        Handles pagination by clicking through pages if specified in the task.
        
        Args:
            scraping_task: The scraping task that may include pagination settings.
        """
        if not scraping_task.extraction_patterns:
            return
            
        # Find the first pattern with pagination settings
        pagination_pattern = next(
            (p for p in scraping_task.extraction_patterns if p.pagination_selector), 
            None
        )
        
        if not pagination_pattern or not pagination_pattern.pagination_selector:
            return
        
        # Create an action to click the pagination element
        try:
            element_selector = ElementSelector(
                type="css",
                value=pagination_pattern.pagination_selector,
                description="Pagination element"
            )
            
            click_action = ExtractAction(
                id="pagination_click",
                type=ActionType.CLICK,
                element=element_selector
            )
            
            result = await self.action_execution_framework.execute_action(click_action)
            
            if result.success and scraping_task.delay_between_requests:
                await asyncio.sleep(scraping_task.delay_between_requests)
                
        except Exception as e:
            self.logger.error(f"Error handling pagination: {str(e)}")
    
    async def validate_extraction_pattern(self, pattern: ExtractionPattern) -> List[str]:
        """
        Validates an extraction pattern for correctness.
        
        Args:
            pattern: The extraction pattern to validate.
            
        Returns:
            List of validation errors, empty if valid.
        """
        errors = []
        
        if not pattern.name:
            errors.append("Pattern name is required")
        
        if not pattern.rules:
            errors.append("At least one extraction rule is required")
        
        for i, rule in enumerate(pattern.rules):
            if not rule.field_name:
                errors.append(f"Rule {i+1}: field_name is required")
            if not rule.selector:
                errors.append(f"Rule {i+1}: selector is required")
        
        return errors