"""
Social Media Package for AutomateAI
"""
from .models import (
    SocialPlatform, SocialMediaAccount, SocialMediaCredentials, 
    PostContent, ScheduledPost, PostResult, SocialMediaTaskRequest
)
from .controller import SocialMediaScheduler
from .service import router as social_media_router

__all__ = [
    # Models
    "SocialPlatform",
    "SocialMediaAccount", 
    "SocialMediaCredentials", 
    "PostContent", 
    "ScheduledPost", 
    "PostResult",
    "SocialMediaTaskRequest",
    
    # Controller
    "SocialMediaScheduler",
    
    # Service
    "social_media_router"
]