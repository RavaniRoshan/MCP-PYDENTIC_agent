from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import uuid
import asyncio

from core.config import settings
from models import UserPrompt, TaskRequest, TaskResponse, BrowserAction, TaskExecutionPlan
from agents.automateai_agent import AutomateAIAgent

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

@app.get("/")
async def root():
    return {"message": "Welcome to AutomateAI MCP Server", "status": "running"}

@app.post("/prompt", response_model=TaskResponse)
async def handle_prompt(user_prompt: UserPrompt):
    """
    Handle user prompts and initiate task execution
    """
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
    
    # Create and run the agent in the background
    agent = AutomateAIAgent()
    # This would normally be run in the background
    # For now, we'll just update the status
    task_response.status = "executing"
    
    return task_response

@app.post("/execute", response_model=TaskResponse)
async def execute_action(action: BrowserAction):
    """
    Execute a specific browser action
    """
    # This endpoint would execute a single action
    # In a real implementation, this would interact with the browser
    return TaskResponse(
        task_id=action.id,
        status="executing",
        request=TaskRequest(
            id=action.id,
            user_prompt=UserPrompt(
                prompt=f"Execute action: {action.description}",
                priority="normal"
            ),
            target_urls=[],
            expected_outputs=[]
        ),
        results=[]
    )

@app.get("/observe", response_model=Dict)
async def observe_browser():
    """
    Observe current browser state
    """
    # This would return the current browser state
    # For now, returning a placeholder
    return {
        "url": "about:blank",
        "title": "New Tab",
        "dom_content": "<html><head></head><body></body></html>",
        "timestamp": "2023-01-01T00:00:00Z"
    }

@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_status(task_id: str):
    """
    Get the status of a specific task
    """
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return active_tasks[task_id]

@app.get("/tasks", response_model=Dict[str, TaskResponse])
async def get_all_tasks():
    """
    Get all active tasks
    """
    return active_tasks

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