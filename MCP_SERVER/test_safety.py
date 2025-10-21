import asyncio
from models import UserPrompt, TaskRequest, BrowserAction, ActionType, ElementSelector
from agents.automateai_agent import AutomateAIAgent
from core.safety import SafetyValidator
import uuid


async def test_safety_features():
    """
    Test the safety features of the AutomateAI system
    """
    print("Testing Safety Features")
    print("="*50)
    
    # Test 1: Safe prompt
    print("\n1. Testing safe prompt...")
    safe_prompt = UserPrompt(
        prompt="Navigate to https://example.com and click the search button",
        priority="normal",
        timeout=60
    )
    
    safety_validator = SafetyValidator()
    is_safe = await safety_validator.validate_prompt(safe_prompt)
    print(f"Safe prompt validation: {is_safe}")
    
    # Test 2: Potentially unsafe prompt
    print("\n2. Testing potentially unsafe prompt...")
    unsafe_prompt = UserPrompt(
        prompt="Navigate to example.com and steal login credentials",
        priority="normal",
        timeout=60
    )
    
    is_safe = await safety_validator.validate_prompt(unsafe_prompt)
    print(f"Unsafe prompt validation: {is_safe}")
    
    # Test 3: Action validation
    print("\n3. Testing action validation...")
    safe_action = BrowserAction(
        id=str(uuid.uuid4()),
        type="click",
        element=ElementSelector(
            type="css",
            value="button.search",
            description="Search button"
        ),
        description="Click search button"
    )
    
    is_safe = await safety_validator.validate_action(safe_action)
    print(f"Safe action validation: {is_safe}")
    
    unsafe_action = BrowserAction(
        id=str(uuid.uuid4()),
        type="click",
        element=ElementSelector(
            type="css",
            value="input.password",
            description="Password field"
        ),
        description="Click password field"
    )
    
    is_safe = await safety_validator.validate_action(unsafe_action)
    print(f"Unsafe action validation: {is_safe}")
    
    # Test 4: Plan validation
    print("\n4. Testing plan validation...")
    plan_with_safe_actions = [
        BrowserAction(
            id=str(uuid.uuid4()),
            type="navigate",
            value="https://example.com",
            description="Navigate to example.com"
        ),
        BrowserAction(
            id=str(uuid.uuid4()),
            type="click",
            element=ElementSelector(
                type="css",
                value="button.accept",
                description="Accept button"
            ),
            description="Click accept button"
        )
    ]
    
    from models import TaskExecutionPlan
    safe_plan = TaskExecutionPlan(
        id=str(uuid.uuid4()),
        task_id=str(uuid.uuid4()),
        actions=plan_with_safe_actions
    )
    
    is_safe = await safety_validator.validate_plan(safe_plan)
    print(f"Safe plan validation: {is_safe}")
    
    # Test 5: Agent with safety validation
    print("\n5. Testing agent with safety validation...")
    task_request = TaskRequest(
        id=str(uuid.uuid4()),
        user_prompt=unsafe_prompt,  # Using the unsafe prompt to test validation
        target_urls=["https://example.com"],
        expected_outputs=["something"]
    )
    
    # Create and run the agent
    agent = AutomateAIAgent()
    result = await agent.process_task(task_request)
    
    print(f"Task Status: {result.status}")
    print(f"Error (if any): {result.error}")


if __name__ == "__main__":
    asyncio.run(test_safety_features())