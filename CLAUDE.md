# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

"真相之镜" (Truth Mirror) is an AI-powered event fact-checking platform that combines SearXNG meta-search, AI content analysis, and crowdsourced voting to verify the truth of events.

**开发理念: 精简、快速、功能完整** - This project prioritizes rapid development with minimal complexity while maintaining full functionality.

## Development Commands

### One-Click Startup (推荐)
```bash
# Python一键启动脚本（智能端口检测，不强制清理）
python start_all.py  # 同时启动前后端，检测现有服务
```

### Backend Development
```bash
cd backend
source venv/Scripts/activate  # Windows
pip install -r init/requirements.txt  # Dependencies are in init/ folder
python run.py  # Starts on port 8002 with hot reload
```

### Frontend Development
```bash
cd frontend
python -m http.server 8080  # Starts on port 8080
# Access: http://127.0.0.1:8080/
```

### Database Setup (Optional)
```bash
# App works without database - graceful failure mode enabled
# Only needed for full functionality
mysql -u username -p -h 115.120.215.107 truthmirror < init/database_init.sql
```

### Testing
```bash
cd backend
pytest  # Framework configured, no project-specific tests yet
pytest -v  # Verbose output
```

## Architecture Overview - Simplified Design

### Core Philosophy: Minimal Validation, Maximum Speed
- **User Registration**: Submit info → Instant account creation (no duplicates check)
- **Event Creation**: Basic info → Immediate event creation
- **Voting**: Simple binary choice → Instant vote recording
- **AI Analysis**: Asynchronous background processing

### 5-Stage Event Lifecycle (Automated)
1. **PENDING** → **NOMINATED** (interest >= 10)
2. **NOMINATED** → **PROCESSING** (AI triggered)
3. **PROCESSING** → **VOTING** (analysis complete)  
4. **VOTING** → **CONFIRMED** (votes >= 10000, margin > 50%)

### Simplified Data Flow
```
User Input → Direct Database → Background AI Processing → Results
(No complex validation, immediate response, async heavy lifting)
```

## Key Implementation Patterns

### Fast Development Approach
- **No Authentication**: All APIs work without login (TODO markers for future auth)
- **No Input Validation**: Database constraints handle data integrity
- **No Error Handling**: Let FastAPI handle errors naturally
- **Plaintext Passwords**: No encryption overhead
- **Direct Database Operations**: Minimal business logic

### Service Layer (Keep It Simple)
- **EventService**: Basic CRUD + status transitions
- **UserService**: Create/read users (no validation)
- **VoteService**: Record votes + count stats
- **SearchService**: Manage sources + AI results

### API Design Pattern
```python
@router.post("/resource/")
async def create_resource(data: Schema, db: Session = Depends(get_db)):
    return service.create(data)  # Direct pass-through
```

## Configuration for Rapid Development

### Environment Setup (.env)
- Remote database configured (no local setup needed)
- Placeholder API keys (replace when needed) 
- Debug mode enabled
- Permissive CORS for frontend development

### Required Environment Variables
```bash
# 创建 backend/.env 文件
DATABASE_URL=mysql+pymysql://username:password@115.120.215.107/truthmirror
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
SECRET_KEY=your-secret-key-change-in-production
```

### Business Logic Thresholds (Easily Adjustable)
- Interest threshold: 10 (small number for testing)
- Vote threshold: 10000 (can be lowered for demos)  
- Victory margin: 50% (simple majority)

## Troubleshooting & Common Issues

### Backend Issues
- **Database connection failed**: App starts without DB, check `.env` configuration
- **Port 8002 occupied**: Change port in `run.py` or kill existing process
- **Missing dependencies**: Run `pip install -r init/requirements.txt` in backend/

### Frontend Issues  
- **CORS errors**: Ensure backend is running and CORS is configured for development
- **API calls fail**: Check backend API is accessible at http://127.0.0.1:8002
- **Port conflicts**: Use different port for frontend HTTP server

### Database Issues
- **Remote DB unavailable**: App runs in offline mode, some features disabled
- **Connection timeout**: Check network connectivity to 115.120.215.107
- **Schema missing**: Run database initialization script from `init/database_init.sql`

## Technical Stack & Dependencies

### Core Framework
- **FastAPI**: Main web framework with automatic OpenAPI docs at `http://localhost:8002/docs`
- **SQLAlchemy**: ORM with MySQL backend (remote database configuration)
- **Uvicorn**: ASGI server with hot reload for development (port 8002)
- **Pydantic**: Data validation and settings management

### Dependencies (Located in `backend/init/requirements.txt`)
- **Core Web**: FastAPI 0.104.1, uvicorn[standard] 0.24.0
- **Database**: SQLAlchemy 2.0.23, PyMySQL 1.1.0, Alembic 1.12.1
- **Async Tasks**: Celery 5.3.4, Redis 5.0.1
- **AI Integration**: OpenAI 1.3.7, Anthropic 0.7.8
- **Testing**: pytest 7.4.3, pytest-asyncio 0.21.1
- **HTTP/Parsing**: requests 2.31.0, httpx 0.25.2, beautifulsoup4 4.12.2

### Database Architecture
- **MySQL 8.0+**: Remote database (115.120.215.107)
- **Connection**: PyMySQL driver with UTF-8 support
- **Schema**: 7 core tables with enum-based status management
- **Auto-migration**: SQLAlchemy creates tables on startup (graceful failure if DB unavailable)

### API Structure
```
/api/v1/
├── events/     # Event CRUD + status transitions
├── users/      # User management (no auth yet)
├── votes/      # Binary voting system
└── search/     # AI source integration
```

### Data Models & Lifecycle
- **EventStatus Enum**: `PENDING` → `NOMINATED` → `PROCESSING` → `VOTING` → `CONFIRMED`
- **Stance Enum**: `SUPPORT` | `OPPOSE` | `NEUTRAL` 
- **Key Tables**: Event, User, Vote, InformationSource, AIAnalysis, EventDetail
- **Automatic Triggers**: Interest count ≥ 10 triggers AI processing

## Project Structure & Development Patterns

### Backend Architecture (Model-Service-API Pattern)
```
backend/
├── app/
│   ├── main.py              # FastAPI app entry, CORS, graceful DB initialization
│   ├── config.py            # Pydantic settings with business thresholds
│   ├── database.py          # SQLAlchemy session management
│   ├── models/
│   │   ├── models.py        # SQLAlchemy ORM models with enum status fields
│   │   └── schemas.py       # Pydantic request/response models
│   ├── api/                 # FastAPI routers (events, users, votes, search)
│   ├── services/            # Business logic layer (minimal validation)
│   ├── tasks/               # Celery async tasks (placeholder)
│   └── utils/               # Utility functions
├── init/
│   ├── requirements.txt     # All dependencies with pinned versions
│   └── database_init.sql    # MySQL schema initialization
├── run.py                   # Development server launcher (port 8002)
└── venv/                    # Python virtual environment
```

### Key Development Files
- **app/main.py:8-14**: Graceful database connection with fallback for offline dev
- **app/config.py:28-31**: Business logic thresholds (easily adjustable for testing)
- **run.py**: Simple uvicorn launcher with hot reload on port 8002

## Frontend Development

### Frontend Architecture (No-Framework Approach)
- **Pure HTML/CSS/JavaScript** - No build tools, no dependencies
- **Single Page Application** - All functionality in one page
- **API Integration** - Connects to backend at `http://localhost:8002/api/v1`
- **Responsive Design** - Works on mobile and desktop
- **Windows Batch Script** - Use `start.bat` for quick Windows startup

### Frontend File Structure
```
frontend/
├── index.html              # 原版主页面（Vue3 + ElementPlus + AI风格）
├── index_simple.html       # 简化版主页（纯HTML/CSS/JS，简约风格）
├── auth.html              # 原版用户认证页面
├── auth_simple.html       # 简化版认证页面（简约设计）
├── event-detail.html      # 原版事件详情页面
├── event-detail_simple.html # 简化版事件详情页面
├── submit-event.html      # 原版事件提交页面
├── submit-event_simple.html # 简化版事件提交页面
├── css/                   # 原版样式文件目录（复杂AI风格）
├── js/                    # JavaScript逻辑文件
├── components/            # 可重用HTML组件
├── start.bat             # Windows快速启动脚本
└── README.md             # 前端文档
```

### Frontend Development Commands
```bash
cd frontend
# Method 1: Python HTTP Server (推荐方式)
python -m http.server 8080  # 前端运行在8080端口

# Method 2: Windows批处理脚本 
start.bat  # 启动3000端口，但实际项目使用8080

# Method 3: 启动指南中的完整流程
# 参考 启动指南.md 中的详细步骤
```

### Frontend Access Points
- **简化版主页**: http://127.0.0.1:8080/index_simple.html （推荐）
- **原版主页**: http://127.0.0.1:8080/ （复杂AI风格）
- **简化版认证**: http://127.0.0.1:8080/auth_simple.html
- **简化版事件详情**: http://127.0.0.1:8080/event-detail_simple.html?id=1
- **简化版提交**: http://127.0.0.1:8080/submit-event_simple.html

### Frontend Design Philosophy
**两套UI设计方案**：
- **原版（复杂AI风格）**: 使用Vue3、ElementPlus、大量emoji、渐变色、玻璃态效果
- **简化版（简约实用）**: 纯HTML/CSS/JS、无emoji、朴素配色、专注功能

**简化版特点**：
- 无第三方框架依赖，纯原生技术栈
- 去除所有emoji符号和AI风格元素
- 使用简约的配色方案（蓝色#2c5aa0为主色调）
- 专注核心功能，界面简洁实用
- 完整的交互逻辑，包含示例数据展示