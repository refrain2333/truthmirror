from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import schemas
from ..services.user_service import UserService

router = APIRouter()

@router.post("/users/", response_model=schemas.User)
async def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    """创建新用户 - 快速注册，无验证"""
    user_service = UserService(db)
    return user_service.create_user(user)

@router.get("/users/", response_model=List[schemas.User])
async def get_users(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """获取用户列表"""
    user_service = UserService(db)
    return user_service.get_users(skip=skip, limit=limit)

@router.get("/users/{user_id}", response_model=schemas.User)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """获取用户信息"""
    user_service = UserService(db)
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user

@router.put("/users/{user_id}", response_model=schemas.User)
async def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = 1  # TODO: 实现用户认证后替换
):
    """更新用户信息"""
    user_service = UserService(db)
    user = user_service.update_user(user_id, user_update, current_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user