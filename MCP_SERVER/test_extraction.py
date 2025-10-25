import asyncio
from models import (
    UserPrompt,
    ElementSelector,
    ExtractAction,
    ActionType,
    ExtractMethod,
    ExtractionFormat,
    ScrapingTask,
    ExtractionPattern,
    ExtractionRule
)
from ai_services.action_execution import ActionExecutionFramework
from ai_services.scraping_service import ScrapingService
from core.browser_controller import MockBrowserController


async def test_extraction_functionality():
    """
    Tests the new data extraction and scraping capabilities.
    """
    print("Testing Data Extraction and Scraping Capabilities")
    print("="*60)
    
    # Use mock browser controller for testing
    browser_controller = MockBrowserController()
    
    # Create the framework
    framework = ActionExecutionFramework(browser_controller)
    scraping_service = ScrapingService(framework, browser_controller)
    
    print("1. Testing ExtractAction with various methods")
    
    # Test 1: Text content extraction
    print("\n  Test 1.1: Text Content Extraction")
    element = ElementSelector(
        type="css",
        value="h1",
        description="Page header"
    )
    
    extract_action = ExtractAction(
        id="test_text_extraction",
        method=ExtractMethod.TEXT_CONTENT,
        element=element
    )
    
    result = await framework.execute_action(extract_action)
    print(f"     Success: {result.success}")
    print(f"     Result: {result.result}")
    if result.error:
        print(f"     Error: {result.error}")
    
    # Test 2: Attribute extraction
    print("\n  Test 1.2: Attribute Extraction")
    element = ElementSelector(
        type="css",
        value="a",
        description="Link element"
    )
    
    extract_action = ExtractAction(
        id="test_attr_extraction",
        method=ExtractMethod.ATTRIBUTE,
        element=element,
        attribute_name="href"
    )
    
    result = await framework.execute_action(extract_action)
    print(f"     Success: {result.success}")
    print(f"     Result: {result.result}")
    if result.error:
        print(f"     Error: {result.error}")
    
    # Test 3: Table extraction
    print("\n  Test 1.3: Table Extraction")
    element = ElementSelector(
        type="css",
        value="table",
        description="Table element"
    )
    
    extract_action = ExtractAction(
        id="test_table_extraction",
        method=ExtractMethod.TABLE,
        element=element
    )
    
    result = await framework.execute_action(extract_action)
    print(f"     Success: {result.success}")
    print(f"     Result: {result.result}")
    if result.error:
        print(f"     Error: {result.error}")
    
    # Test 4: Multiple extraction
    print("\n  Test 1.4: Multiple Items Extraction")
    element = ElementSelector(
        type="css",
        value="li",
        description="List items"
    )
    
    extract_action = ExtractAction(
        id="test_multiple_extraction",
        method=ExtractMethod.LIST,
        element=element
    )
    
    result = await framework.execute_action(extract_action)
    print(f"     Success: {result.success}")
    print(f"     Result: {result.result}")
    if result.error:
        print(f"     Error: {result.error}")
    
    # Test 5: Links extraction (no selector needed)
    print("\n  Test 1.5: Links Extraction")
    extract_action = ExtractAction(
        id="test_links_extraction",
        method=ExtractMethod.LINKS,
        type=ActionType.EXTRACT  # Explicitly set the type
    )
    
    result = await framework.execute_action(extract_action)
    print(f"     Success: {result.success}")
    print(f"     Result: {result.result}")
    if result.error:
        print(f"     Error: {result.error}")
    
    # Test 6: Images extraction (no selector needed)
    print("\n  Test 1.6: Images Extraction")
    extract_action = ExtractAction(
        id="test_images_extraction",
        method=ExtractMethod.IMAGES,
        type=ActionType.EXTRACT  # Explicitly set the type
    )
    
    result = await framework.execute_action(extract_action)
    print(f"     Success: {result.success}")
    print(f"     Result: {result.result}")
    if result.error:
        print(f"     Error: {result.error}")
    
    # Test 7: HTML content extraction
    print("\n  Test 1.7: HTML Content Extraction")
    element = ElementSelector(
        type="css",
        value="div",
        description="Content div"
    )
    
    extract_action = ExtractAction(
        id="test_html_extraction",
        method=ExtractMethod.HTML_CONTENT,
        element=element
    )
    
    result = await framework.execute_action(extract_action)
    print(f"     Success: {result.success}")
    print(f"     Result: {result.result}")
    if result.error:
        print(f"     Error: {result.error}")
    
    print("\n2. Testing Scraping Service")
    
    # Test 1: Validation of extraction pattern
    print("\n  Test 2.1: Pattern Validation")
    invalid_pattern = ExtractionPattern(
        name="",  # Invalid - no name
        method=ExtractMethod.TEXT_CONTENT,
        rules=[]  # Invalid - no rules
    )
    
    validation_errors = await scraping_service.validate_extraction_pattern(invalid_pattern)
    print(f"     Validation errors: {len(validation_errors)}")
    for error in validation_errors:
        print(f"       - {error}")
    
    # Test 2: Valid extraction pattern
    print("\n  Test 2.2: Valid Extraction Pattern")
    valid_pattern = ExtractionPattern(
        name="Product Info",
        description="Extract product information from e-commerce pages",
        method=ExtractMethod.TEXT_CONTENT,
        output_format=ExtractionFormat.JSON,
        rules=[
            ExtractionRule(
                field_name="title",
                selector="h1.product-title",
                required=True
            ),
            ExtractionRule(
                field_name="price",
                selector="span.price",
                required=True
            )
        ]
    )
    
    validation_errors = await scraping_service.validate_extraction_pattern(valid_pattern)
    print(f"     Validation errors: {len(validation_errors)}")
    if validation_errors:
        for error in validation_errors:
            print(f"       - {error}")
    else:
        print("       No validation errors - pattern is valid!")
    
    # Test 3: Scraping task
    print("\n  Test 2.3: Scraping Task Execution")
    
    scraping_task = ScrapingTask(
        id="test_scraping_task",
        name="Test Scraping Task",
        start_urls=["https://example.com"],
        extraction_patterns=[valid_pattern],
        output_format=ExtractionFormat.JSON,
        max_pages=1
    )
    
    scraping_result = await scraping_service.execute_scraping_task(scraping_task)
    print(f"     Task ID: {scraping_result.task_id}")
    print(f"     Status: Completed")
    print(f"     Results: {len(scraping_result.results)} extractions")
    print(f"     Total items extracted: {scraping_result.total_items_extracted}")
    print(f"     Success rate: {scraping_result.success_rate:.2%}")
    print(f"     Duration: {scraping_result.duration:.2f} seconds")
    print(f"     Errors: {scraping_result.error_count}")
    
    if scraping_result.results:
        print("     Sample result:")
        sample_result = scraping_result.results[0]
        print(f"       ID: {sample_result.id}")
        print(f"       Method: {sample_result.method_used}")
        print(f"       Success: {sample_result.success}")
        print(f"       Content preview: {str(sample_result.extracted_content)[:100]}...")
    
    if scraping_result.errors:
        print("     Errors:")
        for error in scraping_result.errors:
            print(f"       - {error}")
    
    print("\n" + "="*60)
    print("Data extraction and scraping tests completed.")


if __name__ == "__main__":
    asyncio.run(test_extraction_functionality())