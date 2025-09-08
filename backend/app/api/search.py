from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import schemas
from ..services.search_service import SearchService

router = APIRouter()

@router.post("/search/trigger/{event_id}")
async def trigger_search_and_analysis(
    event_id: int,
    db: Session = Depends(get_db)
):
    """触发事件的搜索和AI分析流程"""
    search_service = SearchService(db)
    success = await search_service.trigger_search_and_analysis(event_id)
    if not success:
        raise HTTPException(status_code=400, detail="无法触发搜索分析")
    return {"message": "搜索和分析已开始"}

@router.get("/events/{event_id}/sources", response_model=List[schemas.InformationSource])
async def get_event_sources(
    event_id: int,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """获取事件的信息源"""
    search_service = SearchService(db)
    return search_service.get_event_sources(event_id, skip=skip, limit=limit)

@router.get("/events/{event_id}/analysis", response_model=schemas.AIAnalysis)
async def get_event_analysis(
    event_id: int,
    db: Session = Depends(get_db)
):
    """获取事件的AI分析结果"""
    search_service = SearchService(db)
    analysis = search_service.get_event_analysis(event_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="分析结果不存在")
    return analysis

@router.get("/events/{event_id}/detail", response_model=schemas.EventDetailInfo)
async def get_event_detail(
    event_id: int,
    db: Session = Depends(get_db)
):
    """获取事件详情"""
    search_service = SearchService(db)
    detail = search_service.get_event_detail(event_id)
    if not detail:
        raise HTTPException(status_code=404, detail="事件详情不存在")
    return detail

@router.post("/events/{event_id}/detail", response_model=schemas.EventDetailInfo)
async def create_event_detail(
    event_id: int,
    detail: schemas.EventDetailCreate,
    db: Session = Depends(get_db)
):
    """创建事件详情"""
    search_service = SearchService(db)
    # 确保event_id匹配
    detail.event_id = event_id
    return search_service.create_event_detail(detail)

@router.put("/events/{event_id}/detail", response_model=schemas.EventDetailInfo)
async def update_event_detail(
    event_id: int,
    detail_update: schemas.EventDetailUpdate,
    db: Session = Depends(get_db)
):
    """更新事件详情"""
    search_service = SearchService(db)
    detail = search_service.update_event_detail(event_id, detail_update)
    if not detail:
        raise HTTPException(status_code=404, detail="事件详情不存在")
    return detail