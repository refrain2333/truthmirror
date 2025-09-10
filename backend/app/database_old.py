from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# 创建数据库引擎
engine = create_engine(settings.database_url)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()

# 依赖注入：获取数据库会话
def get_db():
    try:
        db = SessionLocal()
        yield db
    except Exception as e:
        print(f"数据库连接错误: {e}")
        # 即使数据库连接失败也要确保session被关闭
        try:
            db.close()
        except:
            pass
        raise
    finally:
        try:
            db.close()
        except:
            pass