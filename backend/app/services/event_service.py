from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from ..models import models, schemas
from ..config import settings

class EventService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_event(self, event: schemas.EventCreate, creator_id: int) -> models.Event:
        """创建新事件"""
        db_event = models.Event(
            **event.dict(),
            creator_id=creator_id,
            status=models.EventStatus.PENDING
        )
        self.db.add(db_event)
        self.db.commit()
        self.db.refresh(db_event)
        return db_event
    
    def get_events(self, skip: int = 0, limit: int = 10, status: Optional[models.EventStatus] = None) -> List[models.Event]:
        """获取事件列表"""
        query = self.db.query(models.Event)
        if status:
            query = query.filter(models.Event.status == status)
        return query.offset(skip).limit(limit).all()
    
    def get_event(self, event_id: int) -> Optional[models.Event]:
        """获取单个事件"""
        return self.db.query(models.Event).filter(models.Event.id == event_id).first()
    
    def get_event_detail(self, event_id: int) -> Optional[dict]:
        """获取事件详情，包含统计信息"""
        event = self.get_event(event_id)
        if not event:
            return None
        
        # 获取投票统计
        vote_stats = self._get_vote_stats(event_id)
        
        # 获取AI分析
        ai_analysis = self.db.query(models.AIAnalysis).filter(
            models.AIAnalysis.event_id == event_id
        ).first()
        
        # 获取信息源
        information_sources = self.db.query(models.InformationSource).filter(
            models.InformationSource.event_id == event_id
        ).all()
        
        # 获取事件详情
        event_detail = self.db.query(models.EventDetail).filter(
            models.EventDetail.event_id == event_id
        ).first()
        
        return {
            **event.__dict__,
            "vote_stats": vote_stats,
            "ai_analysis": ai_analysis,
            "information_sources": information_sources,
            "event_detail": event_detail
        }
    
    def update_event(self, event_id: int, event_update: schemas.EventUpdate, user_id: int) -> Optional[models.Event]:
        """更新事件"""
        event = self.get_event(event_id)
        if not event:
            return None
        
        # 检查权限（只有创建者或管理员可以修改）
        if event.creator_id != user_id:
            # TODO: 检查是否是管理员
            pass
        
        update_data = event_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(event, field, value)
        
        self.db.commit()
        self.db.refresh(event)
        return event
    
    def add_interest(self, event_id: int, user_id: int) -> bool:
        """添加兴趣"""
        # 检查是否已经添加过兴趣
        existing = self.db.query(models.EventInterest).filter(
            and_(models.EventInterest.event_id == event_id, models.EventInterest.user_id == user_id)
        ).first()
        
        if existing:
            return False
        
        # 添加兴趣记录
        interest = models.EventInterest(event_id=event_id, user_id=user_id)
        self.db.add(interest)
        
        # 更新兴趣度计数
        event = self.get_event(event_id)
        if event:
            event.interest_count += 1
            
            # 检查是否达到兴趣度阈值
            if event.interest_count >= settings.interest_threshold and event.status == models.EventStatus.PENDING:
                event.status = models.EventStatus.NOMINATED
        
        self.db.commit()
        return True
    
    def remove_interest(self, event_id: int, user_id: int) -> bool:
        """取消兴趣"""
        interest = self.db.query(models.EventInterest).filter(
            and_(models.EventInterest.event_id == event_id, models.EventInterest.user_id == user_id)
        ).first()
        
        if not interest:
            return False
        
        self.db.delete(interest)
        
        # 更新兴趣度计数
        event = self.get_event(event_id)
        if event and event.interest_count > 0:
            event.interest_count -= 1
        
        self.db.commit()
        return True
    
    def _get_vote_stats(self, event_id: int) -> dict:
        """获取投票统计"""
        total_votes = self.db.query(models.Vote).filter(models.Vote.event_id == event_id).count()
        support_votes = self.db.query(models.Vote).filter(
            and_(models.Vote.event_id == event_id, models.Vote.stance == models.Stance.SUPPORT)
        ).count()
        oppose_votes = total_votes - support_votes
        
        support_percentage = (support_votes / total_votes * 100) if total_votes > 0 else 0
        oppose_percentage = (oppose_votes / total_votes * 100) if total_votes > 0 else 0
        
        return {
            "total_votes": total_votes,
            "support_votes": support_votes,
            "oppose_votes": oppose_votes,
            "support_percentage": support_percentage,
            "oppose_percentage": oppose_percentage
        }