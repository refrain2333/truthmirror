from fastapi import APIRouter, HTTPException, status, Header, Query
from typing import List, Optional
from ..services.simple_db_service import db_service
from pydantic import BaseModel

router = APIRouter()

# 定义简单的请求/响应模型
class EventCreate(BaseModel):
    title: str
    description: str
    keywords: str
    creator_id: Optional[int] = None  # 允许前端传递创建者ID

@router.post("/events/", status_code=status.HTTP_201_CREATED)
async def create_event(event: EventCreate, x_user_id: Optional[str] = Header(None)):
    """创建新事件 - 使用简单数据库服务"""
    print(f"API: 收到创建事件请求")
    print(f"API: 事件数据: title='{event.title}', description='{event.description[:50] if event.description else 'None'}...', keywords='{event.keywords}'")
    print(f"API: 请求头 x-user-id: {x_user_id}")
    print(f"API: 事件中的creator_id: {event.creator_id}")

    try:
        # 确定创建者ID的优先级：
        # 1. 请求体中的creator_id
        # 2. 请求头中的x-user-id
        # 3. 默认值1（admin）
        creator_id = event.creator_id
        if creator_id is None and x_user_id:
            try:
                creator_id = int(x_user_id)
            except ValueError:
                creator_id = 1
        if creator_id is None:
            creator_id = 1

        print(f"API: 创建事件，创建者ID: {creator_id}")

        result = db_service.create_event(
            title=event.title,
            description=event.description,
            keywords=event.keywords,
            creator_id=creator_id
        )
        
        if result:
            return result
        else:
            raise HTTPException(
                status_code=500,
                detail="创建事件失败"
            )
    except Exception as e:
        print(f"创建事件错误: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )

@router.get("/events/")
async def get_events(skip: int = 0, limit: int = 10, status: str = None):
    """获取事件列表 - 使用简单数据库服务"""
    print("=" * 50)
    print("API: 进入get_events函数")
    print(f"API: 参数 - skip={skip}, limit={limit}, status={status}")
    print("=" * 50)

    try:
        # 获取事件列表和总数
        events = db_service.get_events(skip=skip, limit=limit, status=status)
        total_count = db_service.get_events_count(status=status)

        print(f"API: 从数据库获取了 {len(events)} 个事件，总共 {total_count} 个事件")

        # 转换datetime对象为字符串，确保JSON序列化
        for event in events:
            if event.get('created_at'):
                event['created_at'] = str(event['created_at'])
            if event.get('updated_at'):
                event['updated_at'] = str(event['updated_at'])
            if event.get('nomination_deadline'):
                event['nomination_deadline'] = str(event['nomination_deadline']) if event['nomination_deadline'] else None

        print(f"API: 返回事件列表，第一个事件: {events[0]['title'] if events else 'None'}")

        # 返回包含事件列表和总数的对象
        return {
            "events": events,
            "total": total_count,
            "page": (skip // limit) + 1,
            "pageSize": limit,
            "totalPages": (total_count + limit - 1) // limit  # 向上取整
        }

    except Exception as e:
        print(f"API: 获取事件列表错误: {e}")
        import traceback
        traceback.print_exc()
        return []

@router.get("/events/{event_id}")
async def get_event(event_id: int, x_user_id: str = Header(None)):
    """获取事件详情 - 使用简单数据库服务"""
    try:
        # 获取用户ID
        current_user_id = int(x_user_id) if x_user_id else None

        event = db_service.get_event_detail(event_id, current_user_id)
        if not event:
            raise HTTPException(status_code=404, detail="事件不存在")
        return event
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取事件详情错误: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )

# 保留其他原有的API端点，但暂时返回未实现
@router.put("/events/{event_id}")
async def update_event(event_id: int, current_user_id: int = 1):
    """更新事件 - 暂未实现"""
    raise HTTPException(status_code=501, detail="功能暂未实现")

@router.post("/events/{event_id}/interest")
async def add_interest(event_id: int, x_user_id: str = Header(None)):
    """对事件表示兴趣"""
    try:
        # 获取用户ID
        current_user_id = int(x_user_id) if x_user_id else 1

        # 检查事件是否存在
        event = db_service.get_event_detail(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="事件不存在")

        # 添加兴趣
        success = db_service.add_event_interest(event_id, current_user_id)

        if success:
            # 检查是否达到关注阈值，自动触发AI分析
            db_service.check_and_update_event_status(event_id)
            return {"message": "成功表示兴趣"}
        else:
            raise HTTPException(status_code=400, detail="您已经对该事件表示过兴趣了")

    except HTTPException:
        raise
    except Exception as e:
        print(f"添加兴趣错误: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )

@router.delete("/events/{event_id}/interest")
async def remove_interest(event_id: int, x_user_id: str = Header(None)):
    """取消对事件的兴趣"""
    try:
        # 获取用户ID
        current_user_id = int(x_user_id) if x_user_id else 1

        # 检查事件是否存在
        event = db_service.get_event_detail(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="事件不存在")

        # 移除兴趣
        success = db_service.remove_event_interest(event_id, current_user_id)

        if success:
            return {"message": "成功取消兴趣"}
        else:
            raise HTTPException(status_code=400, detail="您尚未对该事件表示兴趣")

    except HTTPException:
        raise
    except Exception as e:
        print(f"移除兴趣错误: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )

@router.get("/events/{event_id}/interest")
async def check_interest(event_id: int, current_user_id: int = 1):
    """检查用户是否对事件表示过兴趣"""
    try:
        # 检查事件是否存在
        event = db_service.get_event_detail(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="事件不存在")

        # 检查兴趣状态
        has_interest = db_service.check_user_interest(event_id, current_user_id)

        return {"has_interest": has_interest}

    except HTTPException:
        raise
    except Exception as e:
        print(f"检查兴趣状态错误: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )

@router.get("/events/{event_id}/votes/stats")
async def get_event_vote_stats(event_id: int):
    """获取事件投票统计"""
    try:
        # 检查事件是否存在
        event = db_service.get_event_detail(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="事件不存在")

        # 获取投票统计
        stats = db_service.execute_query(
            """SELECT
                COUNT(*) as total_votes,
                SUM(CASE WHEN stance = 'support' THEN 1 ELSE 0 END) as support_votes,
                SUM(CASE WHEN stance = 'oppose' THEN 1 ELSE 0 END) as oppose_votes
               FROM votes WHERE event_id = %s""",
            (event_id,)
        )

        if stats:
            result = stats[0]
            total = result['total_votes'] or 0
            support = result['support_votes'] or 0
            oppose = result['oppose_votes'] or 0

            return {
                "total_votes": total,
                "support_votes": support,
                "oppose_votes": oppose,
                "support_percentage": (support / total * 100) if total > 0 else 0,
                "oppose_percentage": (oppose / total * 100) if total > 0 else 0
            }

        return {
            "total_votes": 0,
            "support_votes": 0,
            "oppose_votes": 0,
            "support_percentage": 0,
            "oppose_percentage": 0
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"获取投票统计错误: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )

@router.post("/events/{event_id}/start-ai-processing")
async def start_ai_processing(event_id: int):
    """开始AI处理"""
    try:
        success = db_service.start_ai_processing(event_id)
        if success:
            return {"message": "AI处理已开始"}
        else:
            raise HTTPException(status_code=400, detail="无法开始AI处理，请检查事件状态")
    except HTTPException:
        raise
    except Exception as e:
        print(f"开始AI处理失败: {e}")
        raise HTTPException(status_code=500, detail="开始AI处理失败")

@router.post("/events/{event_id}/complete-ai-processing")
async def complete_ai_processing(
    event_id: int,
    ai_summary: str = Query(None),
    ai_rating: float = Query(None)
):
    """完成AI处理"""
    try:
        success = db_service.complete_ai_processing(event_id, ai_summary, ai_rating)
        if success:
            return {"message": "AI处理已完成，进入投票阶段"}
        else:
            raise HTTPException(status_code=400, detail="无法完成AI处理，请检查事件状态")
    except HTTPException:
        raise
    except Exception as e:
        print(f"完成AI处理失败: {e}")
        raise HTTPException(status_code=500, detail="完成AI处理失败")

@router.post("/events/{event_id}/approve")
async def approve_event(event_id: int):
    """审核通过事件（从pending状态转为nominated）"""
    try:
        # 检查当前状态
        event = db_service.get_event_detail(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="事件不存在")

        if event['status'] != 'pending':
            raise HTTPException(status_code=400, detail=f"事件当前状态为{event['status']}，无法审核")

        # 更新状态为nominated
        success = db_service.update_event_status(event_id, 'nominated')
        if success:
            return {"message": "事件审核通过，已进入提名阶段"}
        else:
            raise HTTPException(status_code=500, detail="审核失败")

    except HTTPException:
        raise
    except Exception as e:
        print(f"审核事件失败: {e}")
        raise HTTPException(status_code=500, detail="审核事件失败")

@router.post("/events/{event_id}/reset-status")
async def reset_event_status(event_id: int, new_status: str = Query(...)):
    """重置事件状态（管理员功能）"""
    try:
        # 验证状态值
        valid_statuses = ['pending', 'nominated', 'processing', 'voting', 'confirmed']
        if new_status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"无效的状态值，必须是: {', '.join(valid_statuses)}")

        # 检查事件是否存在
        event = db_service.get_event_detail(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="事件不存在")

        # 更新状态
        success = db_service.update_event_status(event_id, new_status)
        if success:
            return {"message": f"事件状态已重置为: {new_status}"}
        else:
            raise HTTPException(status_code=500, detail="状态重置失败")

    except HTTPException:
        raise
    except Exception as e:
        print(f"重置事件状态失败: {e}")
        raise HTTPException(status_code=500, detail="重置事件状态失败")