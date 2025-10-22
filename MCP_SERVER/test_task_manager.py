import asyncio
import json
from models import UserPrompt
from ai_services.task_manager import TaskManager
from core.browser_controller import MockBrowserController


async def mock_send_func(update_data):
    """
    A mock function to simulate sending updates to WebSocket clients.
    """
    print(f"WebSocket update: {json.dumps(update_data, indent=2, default=str)[:200]}...")


async def test_task_manager():
    """
    Tests the task management system with real-time updates.

    This function initializes a TaskManager with a mock browser controller,
    subscribes to task updates, and then creates several test tasks to ensure
    that they are processed correctly and that the status updates are sent.
    """
    print("Testing Task Management System")
    print("="*50)
    
    # Use mock browser controller for testing
    browser_controller = MockBrowserController()
    
    # Create the task manager
    task_manager = TaskManager(browser_controller)
    
    # Start the task manager
    await task_manager.start()
    
    # Subscribe to task updates
    await task_manager.subscribe_to_task_updates("test_client_1", mock_send_func)
    
    print("Creating tasks...")
    
    # Create a few test tasks
    tasks_to_create = [
        "Navigate to https://example.com",
        "Go to https://httpbin.org and click on something",
        "Search for 'python automation' on google.com"
    ]
    
    task_ids = []
    for i, prompt in enumerate(tasks_to_create):
        user_prompt = UserPrompt(prompt=prompt, priority="normal", timeout=120)
        task_id = await task_manager.create_task(user_prompt, user_id=f"user_{i}")
        task_ids.append(task_id)
        print(f"Created task {i+1}: {task_id}")
        
        # Brief pause to allow processing
        await asyncio.sleep(0.5)
    
    print(f"\nRetrieved {len(task_ids)} tasks")
    
    # Get individual task status
    for i, task_id in enumerate(task_ids):
        print(f"\nTask {i+1} ({task_id}) status:")
        status = await task_manager.get_task_status(task_id)
        if status:
            print(f"  Status: {status.status}")
            print(f"  Created: {status.started_at}")
            print(f"  Actions executed: {len(status.results)}")
            if status.error:
                print(f"  Error: {status.error}")
        else:
            print("  Task not found")
    
    # Get recent tasks
    print(f"\nRecent tasks:")
    recent_tasks = await task_manager.get_recent_tasks(limit=10)
    for i, task in enumerate(recent_tasks):
        print(f"  {i+1}. {task.task_id}: {task.status}")
    
    # Get statistics
    print(f"\nTask statistics:")
    stats = await task_manager.get_task_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Allow some time for tasks to complete
    print("\nWaiting for tasks to complete...")
    await asyncio.sleep(2)
    
    # Check final status of tasks
    print(f"\nFinal status of created tasks:")
    for i, task_id in enumerate(task_ids):
        status = await task_manager.get_task_status(task_id)
        if status:
            print(f"  Task {i+1}: {status.status} (completed: {status.completed_at is not None})")
        else:
            print(f"  Task {i+1}: Not found")
    
    # Stop the task manager
    await task_manager.stop()
    print("\nTask manager stopped")
    print("Task management system test completed!")


if __name__ == "__main__":
    asyncio.run(test_task_manager())