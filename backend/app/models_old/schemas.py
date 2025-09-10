from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date
from ..models.models import EventStatus, AIRating, Stance

# 用户相关模式
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    nickname: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    birth_date: Optional[date] = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    nickname: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    birth_date: Optional[date] = None
    is_active: Optional[bool] = None

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    role: str
    is_active: bool
    nickname: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    birth_date: Optional[date] = None
    events_created: int = 0
    votes_cast: int = 0
    interests_marked: int = 0
    created_at: datetime
    last_login_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# 事件相关模式
class EventBase(BaseModel):
    title: str
    description: str
    keywords: str

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[str] = None
    status: Optional[EventStatus] = None
    ai_summary: Optional[str] = None
    ai_rating: Optional[AIRating] = None

class Event(EventBase):
    id: int
    status: EventStatus
    interest_count: int = 0
    vote_count: int = 0
    support_votes: int = 0
    oppose_votes: int = 0
    ai_summary: Optional[str] = None
    ai_rating: Optional[AIRating] = None
    nomination_deadline: Optional[datetime] = None
    creator_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# 投票相关模式
class VoteCreate(BaseModel):
    stance: Stance
    ai_good_points: Optional[str] = None
    ai_bad_points: Optional[str] = None
    user_comment: Optional[str] = None

class Vote(BaseModel):
    id: int
    event_id: int
    user_id: int
    stance: Stance
    ai_good_points: Optional[str] = None
    ai_bad_points: Optional[str] = None
    user_comment: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# 事件兴趣相关模式
class EventInterestCreate(BaseModel):
    pass  # 只需要在URL中传递event_id，user_id从认证获取

class EventInterest(BaseModel):
    id: int
    event_id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# 信息来源相关模式
class InformationSourceCreate(BaseModel):
    url: str
    title: Optional[str] = None
    website_name: Optional[str] = None
    content: Optional[str] = None
    ai_summary: Optional[str] = None
    relevance_score: Optional[float] = 0.0

class InformationSource(BaseModel):
    id: int
    event_id: int
    url: str
    title: Optional[str] = None
    website_name: Optional[str] = None
    content: Optional[str] = None
    ai_summary: Optional[str] = None
    relevance_score: float = 0.0
    created_at: datetime
    
    class Config:
        from_attributes = True

# 统计相关模式
class VoteStats(BaseModel):
    total_votes: int
    support_votes: int
    oppose_votes: int
    support_percentage: float
    oppose_percentage: float

# 事件详情响应（包含关联数据）
class EventDetail(Event):
    creator: Optional[User] = None
    information_sources: List[InformationSource] = []
    vote_stats: Optional[VoteStats] = None