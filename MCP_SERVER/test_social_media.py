"""
Test script for Social Media Scheduler functionality
"""
import asyncio
from datetime import datetime, timedelta
from social_media.models import (
    SocialPlatform, SocialMediaCredentials, 
    PostContent, SocialMediaTaskRequest
)
from social_media.controller import SocialMediaScheduler
from agents.automateai_agent import AutomateAIAgent


async def test_linkedin_controller():
    """Test LinkedIn controller functionality"""
    print("Testing LinkedIn controller...")
    
    # Initialize agent and scheduler
    agent = AutomateAIAgent()
    scheduler = SocialMediaScheduler(agent)
    
    # Test credentials (these would be real in a production system)
    credentials = SocialMediaCredentials(
        platform=SocialPlatform.LINKEDIN,
        username="test@example.com",
        password="testpassword"
    )
    
    # Test login
    login_success = await scheduler.platform_controllers[SocialPlatform.LINKEDIN].login(credentials)
    print(f"LinkedIn login success: {login_success}")
    
    # Test posting
    content = PostContent(
        text="This is a test post from AutomateAI!",
        hashtags=["automation", "ai", "testing"],
        images=["https://example.com/image.jpg"]
    )
    
    post_result = await scheduler.platform_controllers[SocialPlatform.LINKEDIN].post_content(content)
    print(f"LinkedIn post result: {post_result.success}, Error: {post_result.error_message}")
    
    # Test scheduling
    future_time = datetime.utcnow() + timedelta(minutes=5)
    scheduled_id = await scheduler.platform_controllers[SocialPlatform.LINKEDIN].schedule_post(content, future_time)
    print(f"LinkedIn scheduled post ID: {scheduled_id}")


async def test_twitter_controller():
    """Test Twitter controller functionality"""
    print("\nTesting Twitter controller...")
    
    # Initialize agent and scheduler
    agent = AutomateAIAgent()
    scheduler = SocialMediaScheduler(agent)
    
    # Test credentials
    credentials = SocialMediaCredentials(
        platform=SocialPlatform.TWITTER,
        username="testuser",
        password="testpassword"
    )
    
    # Test login
    login_success = await scheduler.platform_controllers[SocialPlatform.TWITTER].login(credentials)
    print(f"Twitter login success: {login_success}")
    
    # Test posting
    content = PostContent(
        text="This is a test tweet from AutomateAI! #automation #ai",
        hashtags=["automation", "ai"],
        mentions=["testuser"]
    )
    
    post_result = await scheduler.platform_controllers[SocialPlatform.TWITTER].post_content(content)
    print(f"Twitter post result: {post_result.success}, Error: {post_result.error_message}")
    
    # Test scheduling
    future_time = datetime.utcnow() + timedelta(minutes=5)
    scheduled_id = await scheduler.platform_controllers[SocialPlatform.TWITTER].schedule_post(content, future_time)
    print(f"Twitter scheduled post ID: {scheduled_id}")


async def test_full_scheduler():
    """Test the full scheduler functionality"""
    print("\nTesting full scheduler...")
    
    # Initialize agent and scheduler
    agent = AutomateAIAgent()
    scheduler = SocialMediaScheduler(agent)
    
    # Test content
    content = PostContent(
        text="Testing AutomateAI's social media scheduler!",
        hashtags=["automateai", "socialmedia", "automation"],
        images=["https://example.com/test-image.jpg"]
    )
    
    # Test posting to multiple platforms
    results = await scheduler.post_to_platforms(
        content, 
        [SocialPlatform.LINKEDIN, SocialPlatform.TWITTER]
    )
    
    for result in results:
        print(f"Platform: {result.platform}, Success: {result.success}, Error: {result.error_message}")
    
    # Test scheduling
    future_time = datetime.utcnow() + timedelta(minutes=1)
    scheduled_ids = await scheduler.schedule_post(
        content, 
        [SocialPlatform.LINKEDIN, SocialPlatform.TWITTER], 
        future_time
    )
    
    print(f"Scheduled IDs: {scheduled_ids}")
    
    # Test task execution
    task_request = SocialMediaTaskRequest(
        id="test_task_1",
        user_prompt="Post 'Hello from AutomateAI!' to LinkedIn and Twitter",
        target_platforms=[SocialPlatform.LINKEDIN, SocialPlatform.TWITTER],
        content=content,
        scheduling_time=None  # Post immediately
    )
    
    task_results = await scheduler.execute_social_media_task(task_request)
    
    for result in task_results:
        print(f"Task result - Platform: {result.platform}, Success: {result.success}")


async def main():
    """Run all tests"""
    print("Starting Social Media Scheduler tests...\n")
    
    await test_linkedin_controller()
    await test_twitter_controller()
    await test_full_scheduler()
    
    print("\nAll tests completed!")


if __name__ == "__main__":
    asyncio.run(main())