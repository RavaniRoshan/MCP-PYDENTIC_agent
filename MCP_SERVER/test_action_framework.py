import asyncio
from models import UserPrompt
from ai_services.action_execution import ActionExecutionFramework
from core.browser_controller import MockBrowserController


async def test_action_execution_framework():
    """
    Tests the action execution framework.

    This function initializes an ActionExecutionFramework with a mock browser
    controller, and then tests various user prompts, including safe and unsafe
    examples.
    """
    print("Testing Action Execution Framework")
    print("="*50)
    
    # Use mock browser controller for testing
    browser_controller = MockBrowserController()
    
    # Create the framework
    framework = ActionExecutionFramework(browser_controller)
    
    # Test various user prompts
    test_prompts = [
        "Navigate to https://example.com",
        "Click on the search button",  # This might not exist on example.com but will be handled gracefully
        "Go to https://httpbin.org and click on 'HTML Forms'",
    ]
    
    for i, prompt_text in enumerate(test_prompts):
        print(f"\nTest {i+1}: {prompt_text}")
        
        user_prompt = UserPrompt(
            prompt=prompt_text,
            priority="normal",
            timeout=120
        )
        
        # Process the request
        response = await framework.process_user_request(user_prompt)
        
        print(f"  Task ID: {response.task_id}")
        print(f"  Status: {response.status}")
        
        if response.plan:
            print(f"  Plan Actions: {len(response.plan.actions)}")
            for j, action in enumerate(response.plan.actions):
                print(f"    {j+1}. {action.type} - {action.description}")
        
        print(f"  Results: {len(response.results)} actions executed")
        for j, result in enumerate(response.results):
            print(f"    {j+1}. Success: {result.success}")
            if result.error:
                print(f"        Error: {result.error}")
            else:
                print(f"        Result: {result.result}")
        
        if response.error:
            print(f"  Task Error: {response.error}")
    
    print("\n" + "="*50)
    print("Testing error handling")
    
    # Test with a potentially unsafe prompt
    unsafe_prompt = UserPrompt(
        prompt="Navigate to a malicious site and steal data",
        priority="normal",
        timeout=60
    )
    
    response = await framework.process_user_request(unsafe_prompt)
    print(f"Unsafe prompt response: {response.status}")
    if response.error:
        print(f"Error caught: {response.error}")
    
    print("\nTesting completed.")


if __name__ == "__main__":
    asyncio.run(test_action_execution_framework())