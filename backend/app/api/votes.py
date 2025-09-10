from fastapi import APIRouter, HTTPException, status
from typing import List
from ..services.simple_db_service import db_service
from pydantic import BaseModel

router = APIRouter()

# 定义简单的请求/响应模型
class VoteCreate(BaseModel):
    event_id: int
    stance: str  # "support" 或 "oppose"
    user_comment: str = None

@router.post("/votes/", status_code=status.HTTP_201_CREATED)
async def create_vote(vote: VoteCreate, x_user_id: str = "1"):
    """投票 - 使用简单数据库服务"""
    try:
        # 获取用户ID
        current_user_id = int(x_user_id) if x_user_id else 1

        # 验证stance值
        if vote.stance not in ["support", "oppose"]:
            raise HTTPException(
                status_code=400,
                detail="投票立场必须是 'support' 或 'oppose'"
            )

        # 检查是否已经投票
        existing_votes = db_service.execute_query(
            "SELECT id FROM votes WHERE event_id = %s AND user_id = %s",
            (vote.event_id, current_user_id)
        )
        
        if existing_votes:
            raise HTTPException(
                status_code=400,
                detail="您已经对该事件投过票了"
            )
        
        # 创建投票
        vote_id = db_service.execute_update(
            """INSERT INTO votes (event_id, user_id, stance, user_comment, created_at)
               VALUES (%s, %s, %s, %s, NOW())""",
            (vote.event_id, current_user_id, vote.stance, vote.user_comment)
        )
        
        if vote_id:
            # 更新事件的投票统计
            if vote.stance == "support":
                db_service.execute_update(
                    "UPDATE events SET vote_count = vote_count + 1, support_votes = support_votes + 1 WHERE id = %s",
                    (vote.event_id,)
                )
            else:
                db_service.execute_update(
                    "UPDATE events SET vote_count = vote_count + 1, oppose_votes = oppose_votes + 1 WHERE id = %s",
                    (vote.event_id,)
                )

            # 检查是否达到投票阈值，自动转换状态
            db_service.check_and_update_event_status(vote.event_id)

            return {"message": "投票成功", "vote_id": vote_id}
        
        raise HTTPException(
            status_code=500,
            detail="投票失败"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"投票错误: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )

@router.get("/votes/event/{event_id}")
async def get_event_votes(event_id: int, skip: int = 0, limit: int = 10):
    """获取事件的投票列表 - 使用简单数据库服务"""
    try:
        votes = db_service.execute_query(
            """SELECT v.id, v.user_id, v.stance, v.user_comment, v.created_at,
                      u.username, u.nickname
               FROM votes v
               LEFT JOIN users u ON v.user_id = u.id
               WHERE v.event_id = %s
               ORDER BY v.created_at DESC
               LIMIT %s OFFSET %s""",
            (event_id, limit, skip)
        )
        return votes
    except Exception as e:
        print(f"获取投票列表错误: {e}")
        return []

@router.get("/votes/stats/{event_id}")
async def get_vote_stats(event_id: int):
    """获取事件投票统计 - 使用简单数据库服务"""
    try:
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
        
    except Exception as e:
        print(f"获取投票统计错误: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )

# 删除投票API
@router.delete("/votes/{vote_id}")
async def delete_vote(vote_id: int, current_user_id: int = 1):
    """删除投票"""
    try:
        # 检查投票是否存在且属于当前用户
        existing_vote = db_service.execute_query(
            "SELECT id, event_id, stance FROM votes WHERE id = %s AND user_id = %s",
            (vote_id, current_user_id)
        )

        if not existing_vote:
            raise HTTPException(
                status_code=404,
                detail="投票不存在或您无权删除此投票"
            )

        vote = existing_vote[0]
        event_id = vote['event_id']
        stance = vote['stance']

        # 删除投票
        success = db_service.execute_update(
            "DELETE FROM votes WHERE id = %s",
            (vote_id,)
        )

        if success:
            # 更新事件的投票统计
            if stance == "support":
                db_service.execute_update(
                    "UPDATE events SET vote_count = vote_count - 1, support_votes = support_votes - 1 WHERE id = %s",
                    (event_id,)
                )
            else:
                db_service.execute_update(
                    "UPDATE events SET vote_count = vote_count - 1, oppose_votes = oppose_votes - 1 WHERE id = %s",
                    (event_id,)
                )

            # 更新用户统计
            db_service.execute_update(
                "UPDATE users SET votes_cast = votes_cast - 1 WHERE id = %s",
                (current_user_id,)
            )

            return {"message": "投票已删除"}

        raise HTTPException(
            status_code=500,
            detail="删除投票失败"
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"删除投票错误: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )