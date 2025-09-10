from pydantic import BaseModel, EmailStr
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from ..models.models import EventStatus, UserRole, Stance

if TYPE_CHECKING:
    from .schemas import EventDetailInfo

# 用户相关模式
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    role: str  # 暂时使用字符串而不是枚举
    is_active: bool
    created_at: datetime
    
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

class Event(EventBase):
    id: int
    status: EventStatus
    interest_count: int
    created_at: datetime
    updated_at: datetime
    creator_id: int
    creator: User
    
    class Config:
        from_attributes = True

# 信息源相关模式
class InformationSourceBase(BaseModel):
    url: str
    title: Optional[str] = None
    content: Optional[str] = None

class InformationSourceCreate(InformationSourceBase):
    event_id: int

class InformationSource(InformationSourceBase):
    id: int
    event_id: int
    stance: Optional[Stance] = None
    relevance_score: float
    ai_summary: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# 投票相关模式
class VoteCreate(BaseModel):
    event_id: int
    stance: Stance

class Vote(BaseModel):
    id: int
    event_id: int
    user_id: int
    stance: Stance
    created_at: datetime
    
    class Config:
        from_attributes = True

# AI分析相关模式
class AIAnalysisCreate(BaseModel):
    event_id: int
    support_arguments: str
    oppose_arguments: str
    ai_judgment: Stance
    confidence_score: float

class AIAnalysis(BaseModel):
    id: int
    event_id: int
    support_arguments: str
    oppose_arguments: str
    ai_judgment: Stance
    confidence_score: float
    created_at: datetime
    
    class Config:
        from_attributes = True

# 事件兴趣相关模式
class EventInterestCreate(BaseModel):
    event_id: int

class EventInterest(BaseModel):
    id: int
    event_id: int
    user_id: int
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

class EventDetail(Event):
    information_sources: List[InformationSource] = []
    vote_stats: Optional[VoteStats] = None
    ai_analysis: Optional[AIAnalysis] = None
    # event_detail: Optional['EventDetailInfo'] = None  # 移除循环引用

# 事件详情相关模式
class EventDetailBase(BaseModel):
    background_summary: Optional[str] = None
    key_players: Optional[str] = None
    timeline: Optional[str] = None
    core_facts: Optional[str] = None
    controversy_points: Optional[str] = None
    evidence_summary: Optional[str] = None
    social_impact: Optional[str] = None
    expert_opinions: Optional[str] = None
    media_coverage: Optional[str] = None
    final_conclusion: Optional[str] = None

class EventDetailCreate(EventDetailBase):
    event_id: int
    reliability_score: float = 0.0
    completeness_score: float = 0.0

class EventDetailUpdate(EventDetailBase):
    reliability_score: Optional[float] = None
    completeness_score: Optional[float] = None

class EventDetailInfo(EventDetailBase):
    id: int
    event_id: int
    reliability_score: float
    completeness_score: float
    last_updated: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True