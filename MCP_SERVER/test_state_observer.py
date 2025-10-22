import asyncio
from ai_services.state_observer import BrowserStateObserver
from models import BrowserState
from core.browser_controller import MockBrowserController


async def test_state_observer():
    """
    Tests the browser state observer.

    This function initializes a BrowserStateObserver with a mock browser
    controller, and then tests the state observation and element finding
    functionality.
    """
    print("Testing Browser State Observer")
    print("="*50)
    
    # Use mock browser controller for testing
    browser_controller = MockBrowserController()
    
    # Create a mock browser state with sample DOM content
    mock_state = BrowserState(
        url="https://example.com",
        title="Example Domain",
        dom_content="""
        <html>
            <head><title>Example Domain</title></head>
            <body>
                <div>
                    <h1>Example Domain</h1>
                    <p>This domain is for use in illustrative examples in documents.</p>
                    <a href="https://www.iana.org/domains/example">More information...</a>
                </div>
                <form>
                    <input type="text" id="search" placeholder="Search...">
                    <input type="password" id="password" placeholder="Password">
                    <button type="submit" id="submit-btn">Submit</button>
                    <button type="button" class="action-btn">Click Me</button>
                </form>
                <select id="options">
                    <option value="1">Option 1</option>
                    <option value="2">Option 2</option>
                </select>
            </body>
        </html>
        """
    )
    
    # Mock the get_page_state method to return our mock state
    async def mock_get_page_state():
        return mock_state
    
    browser_controller.get_page_state = mock_get_page_state
    
    observer = BrowserStateObserver(browser_controller)
    
    # Test state observation
    result = await observer.observe_state()
    
    print(f"Observation Success: {result.success}")
    if result.error:
        print(f"Error: {result.error}")
    
    print(f"Page Title: {result.browser_state.title if result.browser_state else 'N/A'}")
    print(f"Page URL: {result.browser_state.url if result.browser_state else 'N/A'}")
    print(f"Number of Elements Found: {len(result.elements)}")
    print(f"Page Summary: {result.summary}")
    
    print("\nFirst 5 Elements:")
    for i, element in enumerate(result.elements[:5]):
        print(f"  {i+1}. Selector: {element.selector.value}")
        print(f"     Description: {element.selector.description}")
        print(f"     Text: {element.text}")
        print(f"     Attributes: {list(element.attributes.keys())}")
    
    # Test finding element by description
    print("\nTesting element search:")
    search_element = await observer.find_element_by_description("search")
    if search_element:
        print(f"Found search element: {search_element.selector.value} - {search_element.text}")
    else:
        print("No search element found")
    
    password_element = await observer.find_element_by_description("password")
    if password_element:
        print(f"Found password element: {password_element.selector.value} - {password_element.text}")
    else:
        print("No password element found")
    
    submit_element = await observer.find_element_by_description("submit")
    if submit_element:
        print(f"Found submit element: {submit_element.selector.value} - {submit_element.text}")
    else:
        print("No submit element found")


if __name__ == "__main__":
    asyncio.run(test_state_observer())