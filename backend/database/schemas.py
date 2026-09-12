from pydantic import BaseModel, EmailStr
from typing import List, Optional, Any, Dict
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class MessageSchema(BaseModel):
    id: int
    contact_name: str
    message_text: str
    message_type: str
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True

class UrlSchema(BaseModel):
    id: int
    url: str
    platform: str
    content_type: str
    shared_by: Optional[str] = None
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True

class InteractionSchema(BaseModel):
    id: int
    engagement_type: str
    platform: Optional[str] = None
    text_content: Optional[str] = None
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True

class AnalysisResultSchema(BaseModel):
    id: int
    wellbeing_score: float
    risk_level: str
    total_activity_count: int
    sentiment: str
    emotions: List[str]
    summary: Dict[str, Any]
    insights: str
    recommendations: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AccountProfileSchema(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None
    followers_count: int = 0
    following_count: int = 0
    posts_count: int = 0
    bio: Optional[str] = None
    profile_photo: Optional[str] = None
    creation_date: Optional[str] = None

    class Config:
        from_attributes = True

class SearchHistorySchema(BaseModel):
    id: int
    query: str
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True

class PreferenceSchema(BaseModel):
    id: int
    topic: str

    class Config:
        from_attributes = True
