from fastapi import APIRouter, HTTPException, status
from typing import List
from ..services.simple_db_service import db_service
from pydantic import BaseModel

router = APIRouter()

# 定义简单的请求/响应模型
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    nickname: str = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    nickname: str = None
    role: str = "user"

class UserUpdate(BaseModel):
    nickname: str = None
    email: str = None
    bio: str = None

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/users/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """创建新用户 - 使用简单数据库服务"""
    try:
        # 检查用户名是否已存在
        existing_users = db_service.execute_query(
            "SELECT id FROM users WHERE username = %s OR email = %s",
            (user.username, user.email)
        )
        
        if existing_users:
            raise HTTPException(
                status_code=400,
                detail="用户名或邮箱已存在"
            )
        
        # 创建用户
        user_id = db_service.execute_update(
            """INSERT INTO users (username, email, password, nickname, role, created_at)
               VALUES (%s, %s, %s, %s, 'user', NOW())""",
            (user.username, user.email, user.password, user.nickname or user.username)
        )
        
        if user_id:
            # 获取创建的用户信息
            new_user = db_service.execute_query(
                "SELECT id, username, email, nickname, role FROM users WHERE username = %s",
                (user.username,)
            )
            if new_user:
                return new_user[0]
        
        raise HTTPException(
            status_code=500,
            detail="创建用户失败"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"创建用户错误: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )

@router.get("/users/")
async def get_users(skip: int = 0, limit: int = 10):
    """获取用户列表 - 使用简单数据库服务"""
    try:
        users = db_service.execute_query(
            "SELECT id, username, email, nickname, role, created_at FROM users ORDER BY created_at DESC LIMIT %s OFFSET %s",
            (limit, skip)
        )
        return users
    except Exception as e:
        print(f"获取用户列表错误: {e}")
        return []

@router.get("/users/{user_id}")
async def get_user(user_id: int):
    """获取用户详情 - 使用简单数据库服务"""
    try:
        users = db_service.execute_query(
            "SELECT id, username, email, nickname, role, created_at FROM users WHERE id = %s",
            (user_id,)
        )
        
        if not users:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        return users[0]
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取用户详情错误: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )

# 简单登录接口：与前端 /users/login 对齐
@router.post("/users/login")
async def login(payload: LoginRequest):
    """用户登录校验。
    注意：当前为简化实现，密码以明文对比，后续可替换为加密校验。
    返回字段需包含 id/username/email/nickname/role，前端将其缓存为 currentUser。
    """
    try:
        users = db_service.execute_query(
            "SELECT id, username, email, nickname, role, password FROM users WHERE username = %s",
            (payload.username,)
        )
        if not users:
            raise HTTPException(status_code=401, detail="用户名或密码错误")

        user = users[0]
        if (user.get("password") or "") != payload.password:
            raise HTTPException(status_code=401, detail="用户名或密码错误")

        # 构造响应，去掉密码字段
        return {
            "id": user["id"],
            "username": user["username"],
            "email": user.get("email"),
            "nickname": user.get("nickname"),
            "role": user.get("role", "user")
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"登录失败: {e}")
        raise HTTPException(status_code=500, detail="登录失败")

# 更新用户信息
@router.put("/users/{user_id}")
async def update_user(user_id: int, user_update: UserUpdate):
    """更新用户信息"""
    try:
        # 检查用户是否存在
        existing_user = db_service.execute_query(
            "SELECT id, username, email, nickname, bio FROM users WHERE id = %s",
            (user_id,)
        )

        if not existing_user:
            raise HTTPException(status_code=404, detail="用户不存在")

        # 构建更新语句
        update_fields = []
        update_values = []

        if user_update.nickname is not None:
            update_fields.append("nickname = %s")
            update_values.append(user_update.nickname)

        if user_update.email is not None:
            # 检查邮箱是否已被其他用户使用
            email_check = db_service.execute_query(
                "SELECT id FROM users WHERE email = %s AND id != %s",
                (user_update.email, user_id)
            )
            if email_check:
                raise HTTPException(status_code=400, detail="邮箱已被其他用户使用")

            update_fields.append("email = %s")
            update_values.append(user_update.email)

        if user_update.bio is not None:
            update_fields.append("bio = %s")
            update_values.append(user_update.bio)

        if not update_fields:
            raise HTTPException(status_code=400, detail="没有提供要更新的字段")

        # 执行更新
        update_values.append(user_id)
        update_sql = f"UPDATE users SET {', '.join(update_fields)}, updated_at = NOW() WHERE id = %s"

        result = db_service.execute_update(update_sql, tuple(update_values))

        if result:
            # 返回更新后的用户信息
            updated_user = db_service.execute_query(
                "SELECT id, username, email, nickname, role, bio, created_at, updated_at FROM users WHERE id = %s",
                (user_id,)
            )
            if updated_user:
                return updated_user[0]

        raise HTTPException(status_code=500, detail="更新用户信息失败")

    except HTTPException:
        raise
    except Exception as e:
        print(f"更新用户信息错误: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )

@router.delete("/users/{user_id}")
async def delete_user(user_id: int):
    """删除用户 - 暂未实现"""
    raise HTTPException(status_code=501, detail="功能暂未实现")