import asyncio
from models import UserPrompt, TaskRequest, BrowserAction, ActionType, ElementSelector
from agents.automateai_agent import AutomateAIAgent
import uuid


async def test_agent():
    """
    Test the AutomateAI agent with a simple task
    """
    # Create a sample user prompt
    user_prompt = UserPrompt(
        prompt="Navigate to https://example.com and click the search button",
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
    
    if result.error:
        print(f"Error: {result.error}")


if __name__ == "__main__":
    asyncio.run(test_agent())