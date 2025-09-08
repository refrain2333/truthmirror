from sqlalchemy.orm import Session
from typing import List, Optional
from ..models import models, schemas

class SearchService:
    def __init__(self, db: Session):
        self.db = db
    
    async def trigger_search_and_analysis(self, event_id: int) -> bool:
        """触发事件的搜索和AI分析流程"""
        event = self.db.query(models.Event).filter(models.Event.id == event_id).first()
        if not event or event.status != models.EventStatus.NOMINATED:
            return False
        
        # 更新事件状态为处理中
        event.status = models.EventStatus.PROCESSING
        self.db.commit()
        
        # TODO: 这里应该启动异步任务进行搜索和分析
        # 暂时返回True，实际实现需要集成Celery
        return True
    
    def get_event_sources(self, event_id: int, skip: int = 0, limit: int = 20) -> List[models.InformationSource]:
        """获取事件的信息源"""
        return self.db.query(models.InformationSource).filter(
            models.InformationSource.event_id == event_id
        ).offset(skip).limit(limit).all()
    
    def get_event_analysis(self, event_id: int) -> Optional[models.AIAnalysis]:
        """获取事件的AI分析结果"""
        return self.db.query(models.AIAnalysis).filter(
            models.AIAnalysis.event_id == event_id
        ).first()
    
    def add_information_source(self, source: schemas.InformationSourceCreate) -> models.InformationSource:
        """添加信息源"""
        db_source = models.InformationSource(**source.dict())
        self.db.add(db_source)
        self.db.commit()
        self.db.refresh(db_source)
        return db_source
    
    def create_ai_analysis(self, analysis: schemas.AIAnalysisCreate) -> models.AIAnalysis:
        """创建AI分析结果"""
        db_analysis = models.AIAnalysis(**analysis.dict())
        self.db.add(db_analysis)
        
        # 分析完成后，更新事件状态为投票阶段
        event = self.db.query(models.Event).filter(models.Event.id == analysis.event_id).first()
        if event:
            event.status = models.EventStatus.VOTING
        
        self.db.commit()
        self.db.refresh(db_analysis)
        return db_analysis
    
    def get_event_detail(self, event_id: int) -> Optional[models.EventDetail]:
        """获取事件详情"""
        return self.db.query(models.EventDetail).filter(
            models.EventDetail.event_id == event_id
        ).first()
    
    def create_event_detail(self, detail: schemas.EventDetailCreate) -> models.EventDetail:
        """创建事件详情"""
        db_detail = models.EventDetail(**detail.dict())
        self.db.add(db_detail)
        self.db.commit()
        self.db.refresh(db_detail)
        return db_detail
    
    def update_event_detail(self, event_id: int, detail_update: schemas.EventDetailUpdate) -> Optional[models.EventDetail]:
        """更新事件详情"""
        detail = self.get_event_detail(event_id)
        if not detail:
            return None
        
        update_data = detail_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(detail, field, value)
        
        self.db.commit()
        self.db.refresh(detail)
        return detail