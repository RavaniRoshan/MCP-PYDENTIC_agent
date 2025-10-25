import asyncio
from models import (
    UserPrompt,
    ElementSelector,
    BrowserAction,
    ActionType,
    FormField,
    FormDefinition,
    FormData,
    FormAction,
    FormActionType,
    FormActionModel
)
from ai_services.action_execution import ActionExecutionFramework
from core.browser_controller import MockBrowserController


async def test_form_automation():
    """
    Tests the form automation capabilities.
    """
    print("Testing Form Automation Capabilities")
    print("="*50)
    
    # Use mock browser controller for testing
    browser_controller = MockBrowserController()
    
    # Create the framework
    framework = ActionExecutionFramework(browser_controller)
    
    print("1. Testing Form Detection")
    
    # Test 1: Detect form fields
    print("\n  Test 1.1: Detect Form Fields")
    form_selector = ElementSelector(
        type="css",
        value="form#contact-form",
        description="Contact form"
    )
    
    detect_action = BrowserAction(
        id="detect_form_fields",
        type=ActionType.DETECT_FORM,
        element=form_selector
    )
    
    result = await framework.execute_action(detect_action)
    print(f"     Success: {result.success}")
    if result.success and result.result:
        fields = result.result
        print(f"     Detected {len(fields)} fields:")
        for field in fields:
            print(f"       - {field.name} ({field.type}) - Required: {field.required}")
    else:
        print(f"     Error: {result.error}")
    
    print("\n2. Testing Form Filling")
    
    # Test 2: Fill form
    print("\n  Test 2.1: Fill Form")
    
    fill_action = BrowserAction(
        id="fill_form_action",
        type=ActionType.FILL_FORM,
        element=form_selector,
        field_data={
            "name": "John Doe",
            "email": "john@example.com",
            "message": "Hello, this is a test message!"
        }
    )
    
    result = await framework.execute_action(fill_action)
    print(f"     Success: {result.success}")
    print(f"     Result: {result.result}")
    if result.error:
        print(f"     Error: {result.error}")
    
    print("\n3. Testing Form Submission")
    
    # Test 3: Submit form
    print("\n  Test 3.1: Submit Form")
    
    submit_action = BrowserAction(
        id="submit_form_action",
        type=ActionType.SUBMIT_FORM,
        element=form_selector
    )
    
    result = await framework.execute_action(submit_action)
    print(f"     Success: {result.success}")
    print(f"     Result: {result.result}")
    if result.error:
        print(f"     Error: {result.error}")
    
    print("\n4. Testing Form Value Extraction")
    
    # Test 4: Get form values
    print("\n  Test 4.1: Get Form Values")
    
    # First fill the form with values
    await framework.execute_action(fill_action)
    
    get_values_action = BrowserAction(
        id="get_form_values",
        type=ActionType.EXTRACT,
        method="form_data",  # This would require updating the extract method handling
        element=form_selector
    )
    
    # Actually, let's create a custom test for form value extraction:
    print("     Testing with direct browser controller method...")
    form_values = await browser_controller.get_form_values(form_selector)
    print(f"     Form values: {form_values}")
    
    print("\n5. Testing Form Validation")
    
    # Test 5: Form validation
    print("\n  Test 5.1: Validate Form")
    
    validate_action = BrowserAction(
        id="validate_form_action",
        type=ActionType.VALIDATE_FORM,
        element=form_selector
    )
    
    result = await framework.execute_action(validate_action)
    print(f"     Success: {result.success}")
    print(f"     Result: {result.result}")
    if result.error:
        print(f"     Error: {result.error}")
    
    print("\n6. Testing Form Action Model")
    
    # Test 6: FormActionModel
    print("\n  Test 6.1: FormActionModel")
    
    form_action = FormActionModel(
        id="test_form_action",
        type=ActionType.FILL_FORM,
        form_selector=form_selector,
        field_data={
            "name": "Jane Smith",
            "email": "jane@example.com"
        }
    )
    
    result = await framework.execute_action(form_action)
    print(f"     Success: {result.success}")
    print(f"     Result: {result.result}")
    
    print("\n" + "="*50)
    print("Form automation tests completed.")


if __name__ == "__main__":
    asyncio.run(test_form_automation())