from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, Enum, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..database import Base

class EventStatus(enum.Enum):
    PENDING = "pending"           # 待提名
    NOMINATED = "nominated"       # 已提名，等待兴趣度
    PROCESSING = "processing"     # 进行中（搜索和分析阶段）
    VOTING = "voting"            # 投票阶段
    CONFIRMED = "confirmed"      # 已确认真相

class AIRating(enum.Enum):
    RELIABLE = "reliable"         # 可靠
    QUESTIONABLE = "questionable" # 存疑
    UNRELIABLE = "unreliable"     # 不可靠
    INSUFFICIENT = "insufficient" # 信息不足

class Stance(enum.Enum):
    SUPPORT = "support"          # 支持
    OPPOSE = "oppose"            # 反对

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), default="user")
    is_active = Column(Boolean, default=True)
    
    # 基本信息
    nickname = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    location = Column(String(100), nullable=True)
    birth_date = Column(Date, nullable=True)
    
    # 统计信息
    events_created = Column(Integer, default=0)
    votes_cast = Column(Integer, default=0)
    interests_marked = Column(Integer, default=0)
    
    created_at = Column(DateTime, server_default=func.now())
    last_login_at = Column(DateTime, nullable=True)
    
    # 关系
    created_events = relationship("Event", back_populates="creator")
    votes = relationship("Vote", back_populates="user")
    interests = relationship("EventInterest", back_populates="user")

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    keywords = Column(String(500), nullable=False)
    status = Column(Enum(EventStatus), default=EventStatus.PENDING, index=True)
    
    # 统计信息
    interest_count = Column(Integer, default=0)
    vote_count = Column(Integer, default=0)
    support_votes = Column(Integer, default=0)
    oppose_votes = Column(Integer, default=0)
    
    # AI分析结果（简化）
    ai_summary = Column(Text, nullable=True)
    ai_rating = Column(Enum(AIRating), nullable=True)
    
    # 时间信息
    nomination_deadline = Column(DateTime, nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关系
    creator = relationship("User", back_populates="created_events")
    information_sources = relationship("InformationSource", back_populates="event")
    votes = relationship("Vote", back_populates="event")
    interests = relationship("EventInterest", back_populates="event")

class InformationSource(Base):
    __tablename__ = "information_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    url = Column(String(1000), nullable=False)
    title = Column(String(300), nullable=True)
    website_name = Column(String(100), nullable=True)
    content = Column(Text, nullable=True)
    ai_summary = Column(Text, nullable=True)
    relevance_score = Column(Float, default=0.00)
    created_at = Column(DateTime, server_default=func.now())
    
    # 关系
    event = relationship("Event", back_populates="information_sources")

class Vote(Base):
    __tablename__ = "votes"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stance = Column(Enum(Stance), nullable=False)
    ai_good_points = Column(Text, nullable=True)
    ai_bad_points = Column(Text, nullable=True)
    user_comment = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # 关系
    event = relationship("Event", back_populates="votes")
    user = relationship("User", back_populates="votes")

class EventInterest(Base):
    """事件兴趣表 - 用户对事件的关注"""
    __tablename__ = "event_interests"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # 关系
    event = relationship("Event", back_populates="interests")
    user = relationship("User", back_populates="interests")