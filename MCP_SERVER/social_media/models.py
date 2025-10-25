"""
Pydantic models for social media scheduler functionality
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class SocialPlatform(str, Enum):
    """Supported social media platforms"""
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"


class SocialMediaAccount(BaseModel):
    """Represents a social media account"""
    id: str
    platform: SocialPlatform
    username: str
    display_name: Optional[str] = None
    profile_url: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class SocialMediaCredentials(BaseModel):
    """Credentials for social media accounts"""
    platform: SocialPlatform
    username: str
    password: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    session_cookies: Optional[Dict[str, str]] = None
    expires_at: Optional[datetime] = None


class PostContent(BaseModel):
    """Content for a social media post"""
    text: str
    title: Optional[str] = None
    images: List[str] = Field(default_factory=list)  # URLs to images
    videos: List[str] = Field(default_factory=list)  # URLs to videos
    links: List[str] = Field(default_factory=list)  # URLs to link in post
    hashtags: List[str] = Field(default_factory=list)
    mentions: List[str] = Field(default_factory=list)  # @mentions
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ScheduledPost(BaseModel):
    """A scheduled social media post"""
    id: str
    account_id: str
    content: PostContent
    scheduled_time: datetime
    status: str = "pending"  # pending, scheduled, posted, failed, cancelled
    posted_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None  # Result of the posting action
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class PostResult(BaseModel):
    """Result of a social media post action"""
    post_id: str
    success: bool
    platform: SocialPlatform
    posted_url: Optional[str] = None
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SocialMediaTaskRequest(BaseModel):
    """Request for social media task execution"""
    id: str
    user_prompt: str
    target_platforms: List[SocialPlatform] = Field(default_factory=list)
    accounts: List[str] = Field(default_factory=list)  # account IDs
    content: PostContent
    scheduling_time: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)