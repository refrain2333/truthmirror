from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from ..models import models, schemas
from ..config import settings

class VoteService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_vote(self, vote: schemas.VoteCreate, user_id: int) -> models.Vote:
        """创建投票"""
        db_vote = models.Vote(
            event_id=vote.event_id,
            user_id=user_id,
            stance=vote.stance
        )
        self.db.add(db_vote)
        
        # 检查是否达到投票阈值和获胜条件
        self._check_vote_completion(vote.event_id)
        
        self.db.commit()
        self.db.refresh(db_vote)
        return db_vote
    
    def get_event_votes(self, event_id: int, skip: int = 0, limit: int = 100) -> List[models.Vote]:
        """获取事件的投票列表"""
        return self.db.query(models.Vote).filter(
            models.Vote.event_id == event_id
        ).offset(skip).limit(limit).all()
    
    def get_user_vote(self, event_id: int, user_id: int) -> Optional[models.Vote]:
        """获取用户对特定事件的投票"""
        return self.db.query(models.Vote).filter(
            and_(models.Vote.event_id == event_id, models.Vote.user_id == user_id)
        ).first()
    
    def get_vote_stats(self, event_id: int) -> dict:
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
    
    def update_vote(self, vote_id: int, vote_update: schemas.VoteCreate, user_id: int) -> Optional[models.Vote]:
        """修改投票"""
        vote = self.db.query(models.Vote).filter(models.Vote.id == vote_id).first()
        if not vote or vote.user_id != user_id:
            return None
        
        vote.stance = vote_update.stance
        
        # 重新检查投票完成条件
        self._check_vote_completion(vote.event_id)
        
        self.db.commit()
        self.db.refresh(vote)
        return vote
    
    def delete_vote(self, vote_id: int, user_id: int) -> bool:
        """删除投票"""
        vote = self.db.query(models.Vote).filter(models.Vote.id == vote_id).first()
        if not vote or vote.user_id != user_id:
            return False
        
        event_id = vote.event_id
        self.db.delete(vote)
        
        # 重新检查投票完成条件
        self._check_vote_completion(event_id)
        
        self.db.commit()
        return True
    
    def _check_vote_completion(self, event_id: int):
        """检查投票是否完成，如果满足条件则更新事件状态"""
        stats = self.get_vote_stats(event_id)
        
        # 检查是否达到投票阈值
        if stats["total_votes"] >= settings.vote_threshold:
            # 检查是否有明显的获胜方（差距超过50%）
            if abs(stats["support_percentage"] - stats["oppose_percentage"]) > settings.victory_margin * 100:
                # 更新事件状态为已确认
                event = self.db.query(models.Event).filter(models.Event.id == event_id).first()
                if event and event.status == models.EventStatus.VOTING:
                    event.status = models.EventStatus.CONFIRMED