from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, Enum
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

class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"

class Stance(enum.Enum):
    SUPPORT = "support"          # 支持正方
    OPPOSE = "oppose"            # 支持反方
    NEUTRAL = "neutral"          # 中性立场

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)  # 明文存储密码
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
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
    interest_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 关系
    creator = relationship("User", back_populates="created_events")
    information_sources = relationship("InformationSource", back_populates="event")
    votes = relationship("Vote", back_populates="event")
    interests = relationship("EventInterest", back_populates="event")
    ai_analyses = relationship("AIAnalysis", back_populates="event")
    event_detail = relationship("EventDetail", back_populates="event", uselist=False)

class InformationSource(Base):
    __tablename__ = "information_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    url = Column(String(1000), nullable=False)
    title = Column(String(300))
    content = Column(Text)
    stance = Column(Enum(Stance))
    relevance_score = Column(Float, default=0.0)
    ai_summary = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    
    # 关系
    event = relationship("Event", back_populates="information_sources")

class Vote(Base):
    __tablename__ = "votes"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stance = Column(Enum(Stance), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # 关系
    event = relationship("Event", back_populates="votes")
    user = relationship("User", back_populates="votes")

class AIAnalysis(Base):
    __tablename__ = "ai_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    support_arguments = Column(Text)        # 正方论据
    oppose_arguments = Column(Text)         # 反方论据
    ai_judgment = Column(Enum(Stance))      # AI初步判断
    confidence_score = Column(Float, default=0.0)  # 置信度
    created_at = Column(DateTime, server_default=func.now())
    
    # 关系
    event = relationship("Event", back_populates="ai_analyses")

class EventInterest(Base):
    """事件兴趣表 - 用户对事件的关注/点赞"""
    __tablename__ = "event_interests"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # 关系
    event = relationship("Event", back_populates="interests")
    user = relationship("User", back_populates="interests")

class EventDetail(Base):
    """事件详情表 - AI整合后的完整事件阐述"""
    __tablename__ = "event_details"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    background_summary = Column(Text)     # 事件背景摘要
    key_players = Column(Text)           # 关键人物/机构
    timeline = Column(Text)              # 事件时间线
    core_facts = Column(Text)            # 核心事实
    controversy_points = Column(Text)     # 争议焦点
    evidence_summary = Column(Text)       # 证据汇总
    social_impact = Column(Text)         # 社会影响
    expert_opinions = Column(Text)       # 专家观点汇总
    media_coverage = Column(Text)        # 媒体报道汇总
    final_conclusion = Column(Text)      # AI最终结论
    reliability_score = Column(Float, default=0.0)    # 可靠性评分
    completeness_score = Column(Float, default=0.0)   # 完整性评分
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, server_default=func.now())
    
    # 关系
    event = relationship("Event", back_populates="event_detail")