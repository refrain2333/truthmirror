# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

"真相之镜" (Truth Mirror) is an AI-powered event fact-checking platform that combines SearXNG meta-search, AI content analysis, and crowdsourced voting to verify the truth of events.

**开发理念: 精简、快速、功能完整** - This project prioritizes rapid development with minimal complexity while maintaining full functionality.

## Development Commands

### Quick Start (Minimal Setup)
```bash
cd backend
source venv/Scripts/activate  # Windows
pip install -r requirements.txt
python run.py  # Starts immediately, works without database
```

### Database (Only when needed)
```bash
# Initialize database only when ready for full functionality
mysql -u truthmirror -p -h 115.120.215.107 truthmirror < init/database_init.sql
```

### Development Server (Default: Port 8002)
```bash
# Start development server with hot reload
python run.py  # Runs on http://127.0.0.1:8002
```

### Testing
```bash
# Install test dependencies (included in requirements.txt)
pytest  # No specific test files yet, uses pytest framework
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

### Business Logic Thresholds (Easily Adjustable)
- Interest threshold: 10 (small number for testing)
- Vote threshold: 10000 (can be lowered for demos)
- Victory margin: 50% (simple majority)

## Technical Stack & Dependencies

### Core Framework
- **FastAPI**: Main web framework with automatic OpenAPI docs at `/docs`
- **SQLAlchemy**: ORM with MySQL backend (remote database configuration)
- **Uvicorn**: ASGI server with hot reload for development
- **Pydantic**: Data validation and settings management

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

- 该项目应当，以最精简，最快速，在实现功能完整性的同时，最为简便的快速构建该项目