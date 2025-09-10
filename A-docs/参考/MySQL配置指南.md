# 真相之镜 - MySQL数据库配置指南

## 虚拟环境配置

### 1. 激活虚拟环境
```bash
# Windows
venv\Scripts\activate

# 激活后你会看到命令行前面有 (venv) 标识
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 如果安装遇到问题，可以单独安装：
```bash
pip install fastapi uvicorn sqlalchemy PyMySQL mysql-connector-python
pip install celery redis requests beautifulsoup4 lxml
pip install python-dotenv pydantic alembic
```

## MySQL数据库设计

### 数据库创建
```sql
-- 创建数据库
CREATE DATABASE truth_mirror CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户（可选）
CREATE USER 'truth_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON truth_mirror.* TO 'truth_user'@'localhost';
FLUSH PRIVILEGES;
```

### 核心表结构

#### 1. 用户表 (users)
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('user', 'admin') DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    vote_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_users_username (username),
    INDEX idx_users_email (email),
    INDEX idx_users_role (role)
);
```

#### 2. 事件表 (events)
```sql
CREATE TABLE events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    keywords JSON,  -- 存储关键词数组
    status ENUM('pending', 'nominated', 'processing', 'voting', 'confirmed') DEFAULT 'pending',
    interest_count INT DEFAULT 0,
    support_votes INT DEFAULT 0,
    oppose_votes INT DEFAULT 0,
    total_votes INT DEFAULT 0,
    final_result ENUM('support', 'oppose', 'pending') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    creator_id INT,
    
    FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_events_status (status),
    INDEX idx_events_created_at (created_at),
    INDEX idx_events_votes (total_votes DESC),
    INDEX idx_events_creator (creator_id)
);
```

#### 3. 信息源表 (information_sources)
```sql
CREATE TABLE information_sources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    url TEXT NOT NULL,
    title VARCHAR(500),
    content LONGTEXT,
    stance ENUM('support', 'oppose', 'neutral') DEFAULT 'neutral',
    relevance_score DECIMAL(3,2) DEFAULT 0.00,  -- 0.00-1.00
    ai_summary TEXT,
    source_type VARCHAR(50) DEFAULT 'news',  -- 'news', 'blog', 'official'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    INDEX idx_sources_event_id (event_id),
    INDEX idx_sources_stance (stance),
    INDEX idx_sources_relevance (relevance_score DESC),
    INDEX idx_sources_type (source_type)
);
```

#### 4. 投票表 (votes)
```sql
CREATE TABLE votes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    user_id INT NOT NULL,
    stance ENUM('support', 'oppose') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_event_vote (event_id, user_id),
    INDEX idx_votes_event_id (event_id),
    INDEX idx_votes_user_id (user_id),
    INDEX idx_votes_stance (stance)
);
```

#### 5. AI分析表 (ai_analyses)
```sql
CREATE TABLE ai_analyses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    support_arguments JSON,  -- 存储结构化的正方论据
    oppose_arguments JSON,   -- 存储结构化的反方论据
    ai_judgment ENUM('support', 'oppose', 'neutral') DEFAULT 'neutral',
    confidence_score DECIMAL(3,2) DEFAULT 0.00,
    analysis_summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    INDEX idx_ai_analyses_event_id (event_id),
    INDEX idx_ai_analyses_judgment (ai_judgment)
);
```

#### 6. 事件兴趣表 (event_interests)
```sql
CREATE TABLE event_interests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_event_interest (event_id, user_id),
    INDEX idx_interests_event_id (event_id),
    INDEX idx_interests_user_id (user_id)
);
```

## 云数据库推荐

### 1. 阿里云 RDS MySQL
```yaml
配置建议:
  - 开发环境: 2核4GB，20GB存储
  - 生产环境: 4核8GB，100GB存储
  - 版本: MySQL 8.0
  - 价格: 约200-800元/月
```

### 2. 腾讯云 MySQL
```yaml
配置建议:
  - 开发环境: 1核2GB，50GB存储
  - 生产环境: 2核4GB，100GB存储
  - 版本: MySQL 8.0
  - 价格: 约150-600元/月
```

### 3. AWS RDS MySQL
```yaml
实例类型: db.t3.micro (开发) / db.t3.small (生产)
存储: 20-100GB gp2
版本: MySQL 8.0
价格: $15-60/月
```

## Python数据库连接配置

### 1. 环境变量配置 (.env)
```env
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=truth_user
DB_PASSWORD=your_password
DB_NAME=truth_mirror

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# API密钥
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# 应用配置
SECRET_KEY=your_secret_key_here
DEBUG=True
```

### 2. 数据库连接代码 (database.py)
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# MySQL连接字符串
DATABASE_URL = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}?charset=utf8mb4"

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=True  # 开发时显示SQL语句
)

# 创建会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## 开发环境启动步骤

### 1. 启动MySQL服务
```bash
# Windows (如果安装了MySQL服务)
net start mysql

# 或者使用XAMPP、WAMP等集成环境
```

### 2. 启动Redis服务
```bash
# Windows (如果安装了Redis)
redis-server

# 或者使用Docker
docker run -d -p 6379:6379 redis:6-alpine
```

### 3. 初始化数据库
```bash
# 激活虚拟环境
venv\Scripts\activate

# 运行数据库迁移
alembic upgrade head
```

### 4. 启动应用
```bash
# 启动FastAPI应用
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 性能优化建议

### 1. MySQL优化
- 启用查询缓存
- 合理设置innodb_buffer_pool_size
- 为高频查询字段创建复合索引

### 2. 连接池配置
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=20,          # 连接池大小
    max_overflow=30,       # 最大溢出连接数
    pool_pre_ping=True,    # 连接前ping测试
    pool_recycle=3600      # 连接回收时间(秒)
)
```

这个配置可以很好地支持你的"真相之镜"项目。需要我帮你创建具体的数据模型代码吗？
