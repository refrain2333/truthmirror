from fastapi import APIRouter, HTTPException
from typing import List
from ..services.simple_db_service import db_service
from pydantic import BaseModel

router = APIRouter()

# 定义简单的请求/响应模型
class SearchQuery(BaseModel):
    query: str
    event_id: int = None

@router.get("/search/")
async def search_events(q: str = "", limit: int = 10):
    """搜索事件 - 使用简单数据库服务"""
    try:
        if not q:
            # 如果没有查询词，返回最新的事件
            events = db_service.execute_query(
                """SELECT e.id, e.title, e.description, e.keywords, e.status, 
                          e.created_at, u.username, u.nickname
                   FROM events e
                   LEFT JOIN users u ON e.creator_id = u.id
                   ORDER BY e.created_at DESC
                   LIMIT %s""",
                (limit,)
            )
        else:
            # 在标题、描述和关键词中搜索
            search_term = f"%{q}%"
            events = db_service.execute_query(
                """SELECT e.id, e.title, e.description, e.keywords, e.status, 
                          e.created_at, u.username, u.nickname
                   FROM events e
                   LEFT JOIN users u ON e.creator_id = u.id
                   WHERE e.title LIKE %s OR e.description LIKE %s OR e.keywords LIKE %s
                   ORDER BY e.created_at DESC
                   LIMIT %s""",
                (search_term, search_term, search_term, limit)
            )
        
        return {
            "query": q,
            "results": events,
            "total": len(events)
        }
        
    except Exception as e:
        print(f"搜索事件错误: {e}")
        return {
            "query": q,
            "results": [],
            "total": 0
        }

@router.get("/search/sources/{event_id}")
async def get_information_sources(event_id: int):
    """获取事件的信息源 - 使用简单数据库服务"""
    try:
        sources = db_service.execute_query(
            """SELECT id, url, title, website_name, content,
                      ai_summary, relevance_score, created_at
               FROM information_sources
               WHERE event_id = %s
               ORDER BY created_at DESC""",
            (event_id,)
        )
        return sources
    except Exception as e:
        print(f"获取信息源错误: {e}")
        return []

@router.post("/search/sources/")
async def add_information_source(event_id: int, title: str, url: str, website_name: str = None):
    """添加信息源 - 使用简单数据库服务"""
    try:
        source_id = db_service.execute_update(
            """INSERT INTO information_sources
               (event_id, url, title, website_name, created_at)
               VALUES (%s, %s, %s, %s, NOW())""",
            (event_id, url, title, website_name)
        )
        
        if source_id:
            return {"message": "信息源添加成功", "source_id": source_id}
        else:
            raise HTTPException(status_code=500, detail="添加信息源失败")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"添加信息源错误: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )

# 保留其他原有的API端点，但暂时返回未实现
@router.post("/search/ai-analysis/")
async def trigger_ai_analysis(event_id: int):
    """触发AI分析 - 暂未实现"""
    raise HTTPException(status_code=501, detail="AI分析功能暂未实现")

@router.get("/search/ai-results/{event_id}")
async def get_ai_analysis_results(event_id: int):
    """获取AI分析结果 - 暂未实现"""
    raise HTTPException(status_code=501, detail="AI分析结果功能暂未实现")