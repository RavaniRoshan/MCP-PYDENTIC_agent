from models import UserPrompt, TaskRequest, BrowserAction, ActionType, ElementSelector, TaskResponse
import uuid

# Test creating a user prompt
user_prompt = UserPrompt(
    prompt="Post this blog post to my LinkedIn account: 'New AI breakthrough in web automation'",
    priority="high",
    timeout=600
)

print("User Prompt Validation:", user_prompt.model_dump())

# Test creating a task request
task_request = TaskRequest(
    id=str(uuid.uuid4()),
    user_prompt=user_prompt,
    target_urls=["https://linkedin.com"],
    expected_outputs=["post published successfully"]
)

print("\nTask Request Validation:", task_request.model_dump())

# Test creating a browser action
action = BrowserAction(
    id=str(uuid.uuid4()),
    type=ActionType.CLICK,
    element=ElementSelector(
        type="css",
        value="button.post-button",
        description="LinkedIn post button"
    ),
    description="Click the LinkedIn post button"
)

print("\nBrowser Action Validation:", action.model_dump())

print("\nAll models validated successfully!")