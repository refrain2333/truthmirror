from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import schemas, models
from ..services.event_service import EventService

router = APIRouter()

@router.post("/events/", response_model=schemas.Event)
async def create_event(
    event: schemas.EventCreate,
    db: Session = Depends(get_db),
    current_user_id: int = 1  # TODO: 实现用户认证后替换
):
    """创建新事件"""
    event_service = EventService(db)
    return event_service.create_event(event, current_user_id)

@router.get("/events/", response_model=List[schemas.Event])
async def get_events(
    skip: int = 0,
    limit: int = 10,
    status: models.EventStatus = None,
    db: Session = Depends(get_db)
):
    """获取事件列表"""
    event_service = EventService(db)
    return event_service.get_events(skip=skip, limit=limit, status=status)

@router.get("/events/{event_id}", response_model=schemas.EventDetail)
async def get_event(
    event_id: int,
    db: Session = Depends(get_db)
):
    """获取事件详情"""
    event_service = EventService(db)
    event = event_service.get_event_detail(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="事件不存在")
    return event

@router.put("/events/{event_id}", response_model=schemas.Event)
async def update_event(
    event_id: int,
    event_update: schemas.EventUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = 1  # TODO: 实现用户认证后替换
):
    """更新事件"""
    event_service = EventService(db)
    event = event_service.update_event(event_id, event_update, current_user_id)
    if not event:
        raise HTTPException(status_code=404, detail="事件不存在")
    return event

@router.post("/events/{event_id}/interest")
async def add_interest(
    event_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = 1  # TODO: 实现用户认证后替换
):
    """对事件表示兴趣"""
    event_service = EventService(db)
    success = event_service.add_interest(event_id, current_user_id)
    if not success:
        raise HTTPException(status_code=400, detail="无法添加兴趣或已经添加过")
    return {"message": "兴趣添加成功"}

@router.delete("/events/{event_id}/interest")
async def remove_interest(
    event_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = 1  # TODO: 实现用户认证后替换
):
    """取消对事件的兴趣"""
    event_service = EventService(db)
    success = event_service.remove_interest(event_id, current_user_id)
    if not success:
        raise HTTPException(status_code=400, detail="无法取消兴趣")
    return {"message": "兴趣取消成功"}