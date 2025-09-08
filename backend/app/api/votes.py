from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import schemas
from ..services.vote_service import VoteService

router = APIRouter()

@router.post("/votes/", response_model=schemas.Vote)
async def create_vote(
    vote: schemas.VoteCreate,
    db: Session = Depends(get_db),
    current_user_id: int = 1  # TODO: 实现用户认证后替换
):
    """投票"""
    vote_service = VoteService(db)
    
    # 检查用户是否已经投票
    existing_vote = vote_service.get_user_vote(vote.event_id, current_user_id)
    if existing_vote:
        raise HTTPException(status_code=400, detail="您已经对此事件投过票")
    
    return vote_service.create_vote(vote, current_user_id)

@router.get("/events/{event_id}/votes", response_model=List[schemas.Vote])
async def get_event_votes(
    event_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取事件的投票列表"""
    vote_service = VoteService(db)
    return vote_service.get_event_votes(event_id, skip=skip, limit=limit)

@router.get("/events/{event_id}/votes/stats", response_model=schemas.VoteStats)
async def get_vote_stats(
    event_id: int,
    db: Session = Depends(get_db)
):
    """获取事件投票统计"""
    vote_service = VoteService(db)
    return vote_service.get_vote_stats(event_id)

@router.put("/votes/{vote_id}", response_model=schemas.Vote)
async def update_vote(
    vote_id: int,
    vote_update: schemas.VoteCreate,
    db: Session = Depends(get_db),
    current_user_id: int = 1  # TODO: 实现用户认证后替换
):
    """修改投票"""
    vote_service = VoteService(db)
    vote = vote_service.update_vote(vote_id, vote_update, current_user_id)
    if not vote:
        raise HTTPException(status_code=404, detail="投票不存在或无权限修改")
    return vote

@router.delete("/votes/{vote_id}")
async def delete_vote(
    vote_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = 1  # TODO: 实现用户认证后替换
):
    """删除投票"""
    vote_service = VoteService(db)
    success = vote_service.delete_vote(vote_id, current_user_id)
    if not success:
        raise HTTPException(status_code=404, detail="投票不存在或无权限删除")
    return {"message": "投票删除成功"}