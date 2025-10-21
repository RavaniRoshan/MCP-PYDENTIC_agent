import asyncio
from models import UserPrompt, TaskRequest, BrowserAction, ActionType, ElementSelector
from agents.automateai_agent import AutomateAIAgent
import uuid


async def test_agent_with_proper_cleanup():
    """
    Test the AutomateAI agent with proper resource management
    """
    # Create a sample user prompt
    user_prompt = UserPrompt(
        prompt="Navigate to https://example.com",
        priority="normal",
        timeout=60
    )
    
    # Create a task request
    task_request = TaskRequest(
        id=str(uuid.uuid4()),
        user_prompt=user_prompt,
        target_urls=["https://example.com"],
        expected_outputs=["page loaded successfully"]
    )
    
    # Create and run the agent
    agent = AutomateAIAgent()
    result = await agent.process_task(task_request)
    
    print(f"Task Status: {result.status}")
    print(f"Number of Actions: {len(result.results)}")
    for i, action_result in enumerate(result.results):
        print(f"Action {i+1}: {action_result.result}")
        print(f"Success: {action_result.success}")
        
        if action_result.error:
            print(f"Error: {action_result.error}")
    
    if result.error:
        print(f"Task Error: {result.error}")
    
    # Properly close the browser controller
    if agent._browser_controller:
        await agent._browser_controller.close()


if __name__ == "__main__":
    asyncio.run(test_agent_with_proper_cleanup())