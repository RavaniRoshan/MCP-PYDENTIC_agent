"""
Social Media Service for AutomateAI
Integrates social media functionality with the main MCP server
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List
from datetime import datetime

from models import UserPrompt
from .models import (
    SocialMediaCredentials, PostContent, ScheduledPost, 
    PostResult, SocialMediaTaskRequest, SocialPlatform
)
from .controller import SocialMediaScheduler
from agents.automateai_agent import AutomateAIAgent


# Create router for social media endpoints
router = APIRouter(prefix="/social", tags=["social-media"])


# In-memory storage for scheduled posts (in production, use a proper database)
scheduled_posts: Dict[str, ScheduledPost] = {}
social_accounts: Dict[str, dict] = {}  # Store account info per user


@router.post("/authenticate", summary="Authenticate a social media account")
async def authenticate_account(credentials: SocialMediaCredentials) -> Dict[str, bool]:
    """
    Authenticate a social media account
    """
    try:
        # Initialize the agent
        agent = AutomateAIAgent()
        
        # Initialize the scheduler
        scheduler = SocialMediaScheduler(agent)
        
        # Authenticate the account
        success = await scheduler.authenticate_account(credentials)
        
        if success:
            # Store account info (in a real system, store securely)
            account_key = f"{credentials.platform.value}_{credentials.username}"
            social_accounts[account_key] = {
                "platform": credentials.platform,
                "username": credentials.username,
                "authenticated_at": datetime.utcnow()
            }
            
            return {"success": True}
        else:
            return {"success": False}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")


@router.post("/post", summary="Post content to social media platforms")
async def post_to_social_media(content: PostContent, platforms: List[SocialPlatform]) -> List[PostResult]:
    """
    Post content to specified social media platforms
    """
    try:
        # Initialize the agent
        agent = AutomateAIAgent()
        
        # Initialize the scheduler
        scheduler = SocialMediaScheduler(agent)
        
        # Post to platforms
        results = await scheduler.post_to_platforms(content, platforms)
        
        return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Posting failed: {str(e)}")


@router.post("/schedule", summary="Schedule a social media post")
async def schedule_social_media_post(
    content: PostContent, 
    platforms: List[SocialPlatform], 
    scheduled_time: datetime
) -> Dict[SocialPlatform, str]:
    """
    Schedule a post for later publication on social media platforms
    """
    try:
        # Initialize the agent
        agent = AutomateAIAgent()
        
        # Initialize the scheduler
        scheduler = SocialMediaScheduler(agent)
        
        # Schedule the post
        scheduled_ids = await scheduler.schedule_post(content, platforms, scheduled_time)
        
        # Store the scheduled post for tracking
        post_id = f"scheduled_{int(scheduled_time.timestamp())}"
        scheduled_post = ScheduledPost(
            id=post_id,
            account_id="default_account",  # Would come from authenticated user
            content=content,
            scheduled_time=scheduled_time,
            status="scheduled"
        )
        
        scheduled_posts[post_id] = scheduled_post
        
        return scheduled_ids
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scheduling failed: {str(e)}")


@router.post("/task", summary="Execute a social media task")
async def execute_social_media_task(task_request: SocialMediaTaskRequest) -> List[PostResult]:
    """
    Execute a comprehensive social media task
    """
    try:
        # Initialize the agent
        agent = AutomateAIAgent()
        
        # Initialize the scheduler
        scheduler = SocialMediaScheduler(agent)
        
        # Execute the task
        results = await scheduler.execute_social_media_task(task_request)
        
        return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task execution failed: {str(e)}")


@router.get("/scheduled/{post_id}", response_model=ScheduledPost)
async def get_scheduled_post(post_id: str):
    """
    Get information about a scheduled post
    """
    if post_id not in scheduled_posts:
        raise HTTPException(status_code=404, detail="Scheduled post not found")
    
    return scheduled_posts[post_id]


@router.get("/scheduled", response_model=Dict[str, ScheduledPost])
async def get_all_scheduled_posts():
    """
    Get all scheduled posts
    """
    return scheduled_posts


@router.post("/execute-scheduled", summary="Execute all scheduled posts at the right time")
async def execute_scheduled_posts():
    """
    Execute scheduled posts that are due
    This would typically be called by a scheduler/cron job
    """
    current_time = datetime.utcnow()
    executed_results = []
    
    # Find posts that are scheduled for now or in the past
    due_posts = [
        post_id for post_id, post in scheduled_posts.items()
        if post.status == "scheduled" and post.scheduled_time <= current_time
    ]
    
    if due_posts:
        # Initialize the agent
        agent = AutomateAIAgent()
        
        # Initialize the scheduler
        scheduler = SocialMediaScheduler(agent)
        
        for post_id in due_posts:
            scheduled_post = scheduled_posts[post_id]
            
            # Execute the post on the specified platforms
            # This is simplified - in reality, we'd track which specific platform each post is for
            results = await scheduler.post_to_platforms(
                scheduled_post.content,
                [SocialPlatform.LINKEDIN, SocialPlatform.TWITTER]  # Default to these for demo
            )
            
            # Update the scheduled post status
            scheduled_post.status = "posted" if all(r.success for r in results) else "failed"
            scheduled_post.posted_at = current_time
            scheduled_post.result = {"results": [r.dict() for r in results]}
            
            executed_results.extend(results)
    
    return executed_results