import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Callable, Awaitable
from datetime import datetime
from uuid import uuid4

from models import UserPrompt, TaskRequest, TaskResponse, TaskExecutionPlan, ActionResult
from ai_services.action_execution import ActionExecutionFramework
from core.browser_controller import BrowserControllerInterface


class TaskUpdateSubscriber:
    """
    Interface for task update subscribers (e.g., WebSocket connections)
    """
    def __init__(self, subscriber_id: str, send_func: Callable[[Dict[str, Any]], Awaitable[None]]):
        self.id = subscriber_id
        self.send_func = send_func
        self.tasks_subscribed = set()  # Task IDs this subscriber is interested in


class TaskManager:
    """
    Manages tasks and provides real-time updates to subscribers
    """
    
    def __init__(self, browser_controller: BrowserControllerInterface):
        self.browser_controller = browser_controller
        self.action_framework = ActionExecutionFramework(browser_controller)
        self.tasks: Dict[str, TaskResponse] = {}
        self.subscribers: Dict[str, TaskUpdateSubscriber] = {}
        self.task_queues: Dict[str, asyncio.Queue] = {}  # Per-user task queues
        self.logger = logging.getLogger(__name__)
        
        # Start the task processor
        self._processor_task = None
        self._stop_event = asyncio.Event()
    
    async def start(self):
        """
        Start the task manager
        """
        self._processor_task = asyncio.create_task(self._task_processor())
        self.logger.info("Task manager started")
    
    async def stop(self):
        """
        Stop the task manager
        """
        self._stop_event.set()
        if self._processor_task:
            await self._processor_task
        self.logger.info("Task manager stopped")
    
    async def _task_processor(self):
        """
        Background task processor that handles tasks from queues
        """
        while not self._stop_event.is_set():
            # Process tasks from all queues
            for user_id, queue in self.task_queues.items():
                try:
                    # Check if there are tasks to process (non-blocking)
                    if not queue.empty():
                        task_request = queue.get_nowait()
                        await self._process_single_task(task_request)
                except asyncio.QueueEmpty:
                    # No tasks to process right now
                    pass
                except Exception as e:
                    self.logger.error(f"Error processing task: {e}")
            
            # Sleep briefly to prevent busy-waiting
            await asyncio.sleep(0.1)
    
    async def _process_single_task(self, task_request: TaskRequest):
        """
        Process a single task request and update its status
        """
        try:
            # Update task status to processing
            task_id = task_request.id
            if task_id in self.tasks:
                self.tasks[task_id].status = "processing"
                await self._notify_subscribers(task_id, self.tasks[task_id])
            
            # Process the task using the action execution framework
            response = await self.action_framework.process_user_request(task_request.user_prompt)
            
            # Update the stored task response
            self.tasks[task_id] = response
            
            # Notify all subscribers of the final result
            await self._notify_subscribers(task_id, response)
            
        except Exception as e:
            self.logger.error(f"Error processing task {task_request.id}: {e}")
            
            # Update task with error
            error_response = TaskResponse(
                task_id=task_request.id,
                status="failed",
                request=task_request,
                error=str(e),
                started_at=task_request.created_at,
                completed_at=datetime.utcnow()
            )
            
            self.tasks[task_request.id] = error_response
            await self._notify_subscribers(task_request.id, error_response)
    
    async def create_task(self, user_prompt: UserPrompt, user_id: str = "default") -> str:
        """
        Create a new task and add it to the appropriate queue
        """
        task_id = str(uuid4())
        
        task_request = TaskRequest(
            id=task_id,
            user_prompt=user_prompt,
            target_urls=[],
            expected_outputs=[],
            created_at=datetime.utcnow()
        )
        
        # Initialize the task response
        initial_response = TaskResponse(
            task_id=task_id,
            status="queued",
            request=task_request,
            started_at=task_request.created_at
        )
        
        self.tasks[task_id] = initial_response
        
        # Add to user's queue
        if user_id not in self.task_queues:
            self.task_queues[user_id] = asyncio.Queue()
        
        await self.task_queues[user_id].put(task_request)
        
        # Notify subscribers that the task is queued
        await self._notify_subscribers(task_id, initial_response)
        
        return task_id
    
    async def get_task_status(self, task_id: str) -> Optional[TaskResponse]:
        """
        Get the status of a specific task
        """
        return self.tasks.get(task_id)
    
    async def get_user_tasks(self, user_id: str) -> List[TaskResponse]:
        """
        Get all tasks for a specific user
        """
        user_tasks = []
        for task in self.tasks.values():
            if task.request.model_dump().get('user_id') == user_id:
                user_tasks.append(task)
        return user_tasks
    
    async def subscribe_to_task_updates(self, subscriber_id: str, send_func: Callable[[Dict[str, Any]], Awaitable[None]]) -> None:
        """
        Subscribe to task updates
        """
        self.subscribers[subscriber_id] = TaskUpdateSubscriber(subscriber_id, send_func)
    
    async def unsubscribe_from_task_updates(self, subscriber_id: str) -> None:
        """
        Unsubscribe from task updates
        """
        if subscriber_id in self.subscribers:
            del self.subscribers[subscriber_id]
    
    async def _notify_subscribers(self, task_id: str, task_response: TaskResponse):
        """
        Notify all subscribers about a task update
        """
        for subscriber in list(self.subscribers.values()):
            try:
                # Convert the task response to a serializable format
                update_data = {
                    "type": "task_update",
                    "task_id": task_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": task_response.model_dump()
                }
                
                await subscriber.send_func(update_data)
            except Exception as e:
                self.logger.error(f"Error notifying subscriber {subscriber.id}: {e}")
                # Remove broken subscribers
                del self.subscribers[subscriber.id]
    
    async def get_recent_tasks(self, limit: int = 10) -> List[TaskResponse]:
        """
        Get the most recent tasks
        """
        sorted_tasks = sorted(
            self.tasks.values(),
            key=lambda t: t.started_at or datetime.min,
            reverse=True
        )
        return sorted_tasks[:limit]
    
    async def get_task_statistics(self) -> Dict[str, Any]:
        """
        Get overall task statistics
        """
        total_tasks = len(self.tasks)
        completed_tasks = len([t for t in self.tasks.values() if t.status == "completed"])
        failed_tasks = len([t for t in self.tasks.values() if t.status == "failed"])
        running_tasks = len([t for t in self.tasks.values() if t.status in ["queued", "processing"]])
        
        success_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "running_tasks": running_tasks,
            "success_rate": success_rate
        }


class TaskWebSocketHandler:
    """
    WebSocket handler that integrates with the task manager
    """
    
    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager
        self.active_connections: Dict[str, Any] = {}  # connection_id -> websocket
    
    async def connect(self, websocket: Any, user_id: str):
        """
        Handle a new WebSocket connection
        """
        await websocket.accept()
        connection_id = f"{user_id}_{uuid4()}"
        self.active_connections[connection_id] = websocket
        
        # Subscribe to task updates
        async def send_update(update_data: Dict[str, Any]):
            try:
                await websocket.send_text(json.dumps(update_data))
            except:
                # Connection probably closed, remove it
                if connection_id in self.active_connections:
                    del self.active_connections[connection_id]
        
        await self.task_manager.subscribe_to_task_updates(connection_id, send_update)
        
        # Send recent tasks to the new connection
        recent_tasks = await self.task_manager.get_recent_tasks(limit=5)
        for task in recent_tasks:
            await send_update({
                "type": "task_history",
                "task_id": task.task_id,
                "timestamp": datetime.utcnow().isoformat(),
                "data": task.model_dump()
            })
    
    async def disconnect(self, connection_id: str):
        """
        Handle WebSocket disconnection
        """
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        await self.task_manager.unsubscribe_from_task_updates(connection_id)
    
    async def handle_create_task(self, user_id: str, prompt: str):
        """
        Handle a request to create a new task
        """
        user_prompt = UserPrompt(prompt=prompt, priority="normal", timeout=300)
        task_id = await self.task_manager.create_task(user_prompt, user_id)
        return task_id