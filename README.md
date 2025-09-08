# 真相之镜 (Truth Mirror)

基于AI分析和众包验证的事件真相验证平台。

## 项目概述

"真相之镜"通过整合SearXNG元搜索引擎、AI内容分析和用户投票机制，为网络事件提供客观、透明的真相验证服务。

## 核心功能

- **事件提交与管理**: 用户提交待验证事件，系统管理事件生命周期
- **智能搜索**: 通过SearXNG进行多源信息搜索
- **AI内容分析**: 自动分析信息源，生成客观摘要
- **众包投票**: 用户基于AI分析进行投票验证
- **真相确认**: 自动判定事件真相

## 技术栈

- **后端**: FastAPI + Python 3.8+
- **数据库**: MySQL + SQLAlchemy
- **缓存**: Redis
- **异步任务**: Celery
- **AI集成**: OpenAI/Claude API

## 快速开始

### 环境准备

1. **Python环境**
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **环境配置**
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，配置数据库和API密钥
```

4. **数据库设置**
```bash
# 创建数据库
mysql -u root -p
CREATE DATABASE truthmirror CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 运行数据库迁移（如果使用Alembic）
alembic upgrade head
```

### 启动服务

```bash
# 开发模式启动
python run.py

# 或使用uvicorn直接启动
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后，访问：
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## API接口

### 核心接口

- `POST /api/v1/events/` - 创建事件
- `GET /api/v1/events/` - 获取事件列表
- `GET /api/v1/events/{id}` - 获取事件详情
- `POST /api/v1/events/{id}/interest` - 对事件表示兴趣
- `POST /api/v1/votes/` - 投票
- `GET /api/v1/events/{id}/votes/stats` - 获取投票统计

详细API文档请访问: http://localhost:8000/docs

## 数据库模型

### 核心表结构

- **events**: 事件主表
- **users**: 用户表
- **information_sources**: 信息源表
- **votes**: 投票表
- **ai_analyses**: AI分析结果表
- **event_interests**: 事件兴趣表

## 事件生命周期

1. **PENDING**: 待提名状态
2. **NOMINATED**: 已提名，等待达到兴趣阈值
3. **PROCESSING**: 搜索和AI分析中
4. **VOTING**: 投票阶段
5. **CONFIRMED**: 真相已确认

## 开发指南

### 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI应用入口
│   ├── config.py            # 配置管理
│   ├── database.py          # 数据库连接
│   ├── models/              # 数据模型
│   │   ├── __init__.py
│   │   ├── models.py        # SQLAlchemy模型
│   │   └── schemas.py       # Pydantic模式
│   ├── api/                 # API路由
│   │   ├── __init__.py
│   │   ├── events.py        # 事件API
│   │   ├── users.py         # 用户API
│   │   ├── votes.py         # 投票API
│   │   └── search.py        # 搜索API
│   ├── services/            # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── event_service.py
│   │   ├── user_service.py
│   │   ├── vote_service.py
│   │   └── search_service.py
│   ├── tasks/               # Celery异步任务
│   └── utils/               # 工具函数
├── requirements.txt
├── run.py                   # 启动脚本
└── .env.example            # 环境变量模板
```

### 添加新功能

1. 在 `models/models.py` 中定义数据模型
2. 在 `models/schemas.py` 中定义API模式
3. 在 `services/` 中实现业务逻辑
4. 在 `api/` 中创建API端点
5. 在 `main.py` 中注册路由

## 配置说明

### 环境变量

- `DATABASE_URL`: 数据库连接字符串
- `REDIS_URL`: Redis连接字符串
- `OPENAI_API_KEY`: OpenAI API密钥
- `ANTHROPIC_API_KEY`: Anthropic API密钥
- `SEARXNG_URL`: SearXNG搜索引擎URL
- `SECRET_KEY`: JWT签名密钥

### 业务配置

- `INTEREST_THRESHOLD`: 兴趣度阈值（默认10）
- `VOTE_THRESHOLD`: 投票总数阈值（默认10000）
- `VICTORY_MARGIN`: 获胜边际（默认0.5，即50%）

## 待实现功能

- [ ] 用户认证和JWT集成
- [ ] SearXNG搜索集成
- [ ] AI内容分析实现
- [ ] Celery异步任务队列
- [ ] 前端界面开发
- [ ] 实时通知系统
- [ ] 管理员推翻功能

## 许可证

本项目采用 MIT 许可证。