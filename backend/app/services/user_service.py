from sqlalchemy.orm import Session
from typing import List, Optional
from ..models import models, schemas

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user: schemas.UserCreate) -> models.User:
        """创建新用户"""
        db_user = models.User(
            username=user.username,
            email=user.email,
            password=user.password,  # 明文存储
            role=models.UserRole.USER,
            is_active=True
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def get_users(self, skip: int = 0, limit: int = 10) -> List[models.User]:
        """获取用户列表"""
        return self.db.query(models.User).offset(skip).limit(limit).all()
    
    def get_user(self, user_id: int) -> Optional[models.User]:
        """获取单个用户"""
        return self.db.query(models.User).filter(models.User.id == user_id).first()
    
    def get_user_by_username(self, username: str) -> Optional[models.User]:
        """根据用户名获取用户"""
        return self.db.query(models.User).filter(models.User.username == username).first()
    
    def get_user_by_email(self, email: str) -> Optional[models.User]:
        """根据邮箱获取用户"""
        return self.db.query(models.User).filter(models.User.email == email).first()
    
    def update_user(self, user_id: int, user_update: schemas.UserUpdate, current_user_id: int) -> Optional[models.User]:
        """更新用户信息"""
        user = self.get_user(user_id)
        if not user:
            return None
        
        # 检查权限（只能修改自己的信息，除非是管理员）
        if user_id != current_user_id:
            # TODO: 检查是否是管理员
            pass
        
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def verify_password(self, plain_password: str, stored_password: str) -> bool:
        """验证密码（明文对比）"""
        return plain_password == stored_password
    
    def authenticate_user(self, username: str, password: str) -> Optional[models.User]:
        """用户认证"""
        user = self.get_user_by_username(username)
        if not user:
            return None
        if not self.verify_password(password, user.password):
            return None
        return user