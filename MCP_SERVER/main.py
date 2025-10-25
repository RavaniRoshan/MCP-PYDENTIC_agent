from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import uuid
import asyncio

from core.config import settings
from models import UserPrompt, TaskRequest, TaskResponse, BrowserAction, TaskExecutionPlan
from agents.automateai_agent import AutomateAIAgent
from social_media.service import router as social_media_router
from ai_services.action_execution import ActionExecutionFramework
from core.playwright_controller import PlaywrightBrowserController
from core.safety import SafetyValidator, SafetyConfirmation

# Create the FastAPI app
app = FastAPI(
    title="AutomateAI MCP Server",
    description="The First AI That Works the Web For You. Hands-Free.",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for tasks (in production, use a proper database)
active_tasks: Dict[str, TaskResponse] = {}

# Global instances of services
browser_controller = None
action_framework = None

@app.on_event("startup")
async def startup_event():
    """
    Initialize services on startup.
    """
    global browser_controller, action_framework
    
    # Initialize browser controller
    browser_controller = PlaywrightBrowserController()
    await browser_controller.initialize()
    
    # Initialize action execution framework
    action_framework = ActionExecutionFramework(browser_controller)

@app.get("/")
async def root():
    """
    The root endpoint of the MCP Server.
    """
    return {"message": "Welcome to AutomateAI MCP Server", "status": "running"}

@app.post("/prompt", response_model=TaskResponse)
async def handle_prompt(user_prompt: UserPrompt):
    """
    Handles user prompts and initiates task execution.

    Args:
        user_prompt (UserPrompt): The user's prompt.

    Returns:
        TaskResponse: The response to the user's prompt.
    """
    if not action_framework:
        raise HTTPException(status_code=500, detail="Action framework not initialized")
    
    task_id = str(uuid.uuid4())
    
    # Create a task request
    task_request = TaskRequest(
        id=task_id,
        user_prompt=user_prompt,
        target_urls=[],
        expected_outputs=[]
    )
    
    # Initialize task response
    task_response = TaskResponse(
        task_id=task_id,
        status="pending",
        request=task_request,
        started_at=task_request.created_at
    )
    
    # Store the task
    active_tasks[task_id] = task_response
    
    # Process the user request using the real action execution framework
    task_response = await action_framework.process_user_request(user_prompt)
    
    # Update the active tasks with the updated response
    active_tasks[task_id] = task_response
    
    return task_response

@app.post("/execute", response_model=TaskResponse)
async def execute_action(action: BrowserAction):
    """
    Executes a specific browser action.

    Args:
        action (BrowserAction): The action to be executed.

    Returns:
        TaskResponse: The response to the action.
    """
    if not action_framework:
        raise HTTPException(status_code=500, detail="Action framework not initialized")
    
    # Execute the single action using the framework
    result = await action_framework.execute_action(action)
    
    return TaskResponse(
        task_id=action.id,
        status="completed" if result.success else "failed",
        request=TaskRequest(
            id=action.id,
            user_prompt=UserPrompt(
                prompt=f"Execute action: {action.description}",
                priority="normal"
            ),
            target_urls=[],
            expected_outputs=[]
        ),
        results=[result] if result else []
    )

@app.get("/observe", response_model=Dict)
async def observe_browser():
    """
    Observes the current browser state.

    Returns:
        Dict: A dictionary representing the current browser state.
    """
    if not browser_controller:
        raise HTTPException(status_code=500, detail="Browser controller not initialized")
    
    # Get the actual browser state
    browser_state = await browser_controller.get_page_state()
    
    return {
        "url": browser_state.url,
        "title": browser_state.title,
        "dom_content": browser_state.dom_content,
        "viewport_size": browser_state.viewport_size,
        "timestamp": browser_state.timestamp.isoformat() if browser_state.timestamp else None
    }

@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_status(task_id: str):
    """
    Gets the status of a specific task.

    Args:
        task_id (str): The ID of the task.

    Returns:
        TaskResponse: The status of the task.
    """
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return active_tasks[task_id]

@app.get("/tasks", response_model=Dict[str, TaskResponse])
async def get_all_tasks():
    """
    Gets all active tasks.

    Returns:
        Dict[str, TaskResponse]: A dictionary of all active tasks.
    """
    return active_tasks

# Include social media router
app.include_router(social_media_router)

def main():
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.server_debug
    )


if __name__ == "__main__":
    main()