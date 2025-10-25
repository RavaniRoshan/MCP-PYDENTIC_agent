import asyncio
from models import ElementSelector
from core.browser_controller import MockBrowserController
from core.compatibility_layer import BrowserCompatibilityLayer, UniversalCompatibilityHandler, CompatibilityRule


async def test_compatibility_layer():
    """
    Tests the universal web compatibility layer.
    """
    print("Testing Universal Web Compatibility Layer")
    print("="*50)
    
    # Test 1: Universal Compatibility Handler
    print("\n1. Testing Universal Compatibility Handler")
    
    handler = UniversalCompatibilityHandler()
    
    print(f"   Loaded {len(handler.rules)} default compatibility rules")
    
    # Add a custom rule
    custom_rule = CompatibilityRule(
        id="custom_test_rule",
        description="Test custom rule for testing purposes",
        selector=".test-element",
        action="wait_additional_time",
        parameters={"wait_time": 1000},
        priority=15,
        applies_to=["example.com"]
    )
    
    handler.add_rule(custom_rule)
    print(f"   Added custom rule. Total rules: {len(handler.rules)}")
    
    # Test detection of compatibility issues
    print("\n2. Testing Compatibility Issue Detection")
    test_html = """
    <html>
        <body data-spa="true">
            <div class="modal-overlay">
                <button class="close">X</button>
            </div>
            <div id="app">Application content</div>
        </body>
    </html>
    """
    
    detected_issues = await handler.detect_compatibility_issues(test_html, "https://example.com")
    print(f"   Detected {len(detected_issues)} issues:")
    for issue in detected_issues:
        print(f"     - {issue.id}: {issue.description}")
    
    # Test 3: Browser Compatibility Layer
    print("\n3. Testing Browser Compatibility Layer")
    
    # Use mock browser controller
    browser_controller = MockBrowserController()
    compatibility_layer = BrowserCompatibilityLayer(browser_controller)
    
    # Test navigation with compatibility handling
    print("   Testing navigation with compatibility handling...")
    nav_result = await compatibility_layer.navigate("https://example.com")
    print(f"   Navigation result: {nav_result}")
    
    # Test clicking with compatibility handling
    print("   Testing click with compatibility handling...")
    element = ElementSelector(type="css", value="button.test-btn")
    click_result = await compatibility_layer.click(element)
    print(f"   Click result: {click_result}")
    
    # Test other operations
    print("   Testing other operations...")
    state = await compatibility_layer.get_page_state()
    print(f"   Page state retrieved: {state.url}")
    
    # Test text extraction
    text_result = await compatibility_layer.extract_text(element)
    print(f"   Text extraction result: {text_result}")
    
    # Test screenshot
    screenshot_result = await compatibility_layer.take_screenshot("test.png")
    print(f"   Screenshot result: {screenshot_result}")
    
    print("\n4. Testing Specific Compatibility Rules")
    
    # Test the overlay blocking element rule
    overlay_rule = next((rule for rule in handler.rules if rule.id == "overlay_blocking_element"), None)
    if overlay_rule:
        print(f"   Testing overlay rule: {overlay_rule.description}")
        result = await handler.apply_compatibility_rule(overlay_rule, browser_controller)
        print(f"   Overlay rule application result: {result}")
    
    print("\n" + "="*50)
    print("Universal web compatibility layer tests completed.")


if __name__ == "__main__":
    asyncio.run(test_compatibility_layer())