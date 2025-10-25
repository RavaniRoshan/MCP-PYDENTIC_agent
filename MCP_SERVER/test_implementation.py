#!/usr/bin/env python3
"""
Test script to verify that the AutomateAI implementation works with real components.
"""
import asyncio
from models import UserPrompt
from ai_services.action_execution import ActionExecutionFramework
from core.playwright_controller import PlaywrightBrowserController


async def test_implementation():
    """Test the implementation with real components."""
    print("Testing AutomateAI implementation with real components...")
    
    # Initialize browser controller
    browser_controller = PlaywrightBrowserController()
    await browser_controller.initialize()
    print("[OK] Browser controller initialized")
    
    # Initialize action execution framework
    action_framework = ActionExecutionFramework(browser_controller)
    print("[OK] Action execution framework initialized")
    
    # Create a simple user prompt
    user_prompt = UserPrompt(
        prompt="Navigate to https://example.com and describe the page",
        priority="normal"
    )
    print(f"[OK] Created user prompt: {user_prompt.prompt}")
    
    # Process the user request
    try:
        task_response = await action_framework.process_user_request(user_prompt)
        print(f"[OK] Task processed successfully: {task_response.status}")
        print(f"[OK] Task ID: {task_response.task_id}")
        print(f"[OK] Plan created: {task_response.plan is not None}")
        if task_response.plan:
            print(f"[OK] Number of actions in plan: {len(task_response.plan.actions)}")
        
    except Exception as e:
        print(f"[ERROR] Error processing task: {e}")
    
    # Close the browser
    await browser_controller.close()
    print("[OK] Browser closed")
    
    print("\nImplementation test completed!")


if __name__ == "__main__":
    asyncio.run(test_implementation())