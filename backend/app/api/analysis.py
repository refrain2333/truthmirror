"""
智能分析API端点
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from ..services.simple_db_service import db_service
from ..config import settings
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime
from pathlib import Path
import json

from ..services.analysis_service import run_news_analysis, get_analysis_result

router = APIRouter()


class AnalysisRequest(BaseModel):
    """分析请求模型"""
    event_title: str
    event_description: str
    event_id: int = None  # 事件ID，用于状态管理


@router.post("/analyze")
async def analyze_event(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    分析事件 - 真正的后台AI分析
    
    Args:
        request: 分析请求
        background_tasks: FastAPI后台任务
        
    Returns:
        立即返回启动状态，真正的AI分析在后台运行
    """
    try:
        event_id = request.event_id or 999
        # 后端前置校验：关注人数≥10 或已通过管理员审核，否则拒绝启动
        try:
            event = db_service.get_event_detail(event_id)
            interest_count = int(event.get('interest_count') or 0)
            status_val = event.get('status')
            min_interest = int(getattr(settings, 'interest_threshold', 10))
            if interest_count < min_interest and status_val == 'pending':
                return {
                    "success": False,
                    "event_id": event_id,
                    "error": f"关注人数不足{min_interest}且未审核，暂不启动AI分析",
                    "ai_analysis": {"reliability": "insufficient", "summary": "请等待更多人关注或管理员审核通过后再试"},
                    "next_step": "WAITING_FOR_INTEREST_OR_APPROVAL",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception:
            pass
        query = f"{request.event_title} {request.event_description}"
        
        print(f"🚀 [事件{event_id}] 启动真实AI分析: {query[:50]}...")
        
        # 预写入一个“已启动”的状态，避免前端在任务排队时看到 idle
        try:
            status_file = Path(__file__).resolve().parents[2] / 'modules' / 'TruthNews' / 'news_analysis' / f'status_event_{event_id}.json'
            status_file.parent.mkdir(parents=True, exist_ok=True)
            with open(status_file, 'w', encoding='utf-8') as sf:
                json.dump({
                    "status": "started",
                    "step": "step1_search",
                    "event_id": event_id,
                    "raw_count": 0,
                    "started_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }, sf, ensure_ascii=False, indent=2)
        except Exception:
            pass

        # 定义后台分析任务
        def background_ai_analysis():
            print(f"🤖 [事件{event_id}] 开始后台AI分析...")
            try:
                result = run_news_analysis(
                    event_title=request.event_title,
                    event_description=request.event_description,
                    event_id=event_id
                )
                print(f"✅ [事件{event_id}] AI分析完成: {result.get('success', False)}")
                if result.get('success'):
                    print(f"📊 [事件{event_id}] AI评级: {result.get('ai_analysis', {}).get('reliability', 'unknown')}")
                    print(f"📝 [事件{event_id}] 摘要长度: {len(result.get('ai_analysis', {}).get('summary', ''))}")
                else:
                    print(f"❌ [事件{event_id}] 分析失败: {result.get('error', 'unknown')}")
            except Exception as e:
                print(f"💥 [事件{event_id}] 后台分析异常: {str(e)}")
        
        # 添加到后台任务队列
        background_tasks.add_task(background_ai_analysis)
        
        # 立即返回启动状态
        return {
            "success": True,
            "event_id": event_id,
            "query": query,
            "status": "analysis_started", 
            "message": "🚀 真实AI分析已在后台启动！",
            "ai_analysis": {
                "reliability": "processing",
                "summary": f"正在对'{request.event_title}'进行7步智能分析...\n\n📊 分析过程：\n1. 🔍 搜索相关新闻\n2. 🌐 检测链接可用性\n3. 🤖 AI筛选相关内容\n4. 📄 抓取网页内容\n5. 📝 提取正文信息\n6. 🧠 GLM/DeepSeek深度分析\n7. 📋 生成最终报告\n\n⏳ 请等待1-2分钟，可在终端查看实时进度。",
                "analysis_statistics": {
                    "status": "background_processing",
                    "steps_total": 7,
                    "models_used": ["GLM-4.5-flash", "DeepSeek(备选)"],
                    "started_at": datetime.now().isoformat()
                },
                "workflow_summary": {
                    "status": "started",
                    "background_task": True,
                    "check_terminal": "查看终端输出了解分析进度"
                }
            },
            "timestamp": datetime.now().isoformat(),
            "next_step": "BACKGROUND_PROCESSING",
            "note": "🔥 注意：这次是真正的AI分析！请查看终端输出了解实时进度。"
        }
        
    except Exception as e:
        print(f"❌ 启动AI分析失败: {str(e)}")
        return {
            "success": False,
            "event_id": request.event_id or 999,
            "query": f"{request.event_title} {request.event_description}",
            "error": f"无法启动AI分析: {str(e)}",
            "ai_analysis": {
                "reliability": "insufficient", 
                "summary": "❌ 系统无法启动AI分析，请检查配置或稍后重试。",
                "analysis_statistics": {"error": "startup_failed"},
                "workflow_summary": {"status": "failed", "error": str(e)[:100]}
            },
            "timestamp": datetime.now().isoformat(),
            "next_step": "RETRY"
        }


@router.post("/test")
async def test_analysis():
    """
    测试分析功能 - 快速响应
    """
    return {
        "message": "✅ 分析API测试成功",
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "note": "API端点正常工作，可以接收分析请求"
    }


@router.post("/run-full-analysis")
async def run_full_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    执行完整的AI分析（后台任务）
    """
    def background_analysis():
        try:
            print(f"🚀 开始后台AI分析...")
            result = run_news_analysis(
                event_title=request.event_title,
                event_description=request.event_description,
                event_id=request.event_id
            )
            print(f"✅ 后台AI分析完成: {result.get('success', False)}")
        except Exception as e:
            print(f"❌ 后台AI分析失败: {str(e)}")
    
    # 添加后台任务
    background_tasks.add_task(background_analysis)
    
    return {
        "message": "后台分析任务已启动",
        "event_id": request.event_id,
        "status": "background_processing"
    }


@router.get("/result/{event_id}")
async def get_final_result(event_id: int):
    """返回最终结果：若状态文件包含 result_file 或内联结果，优先读取并返回"""
    try:
        from pathlib import Path
        import json
        status_file = Path(__file__).resolve().parents[2] / 'modules' / 'TruthNews' / 'news_analysis' / f'status_event_{event_id}.json'
        if status_file.exists():
            with open(status_file, 'r', encoding='utf-8') as f:
                status = json.load(f)
            if status.get('result_inline'):
                return {"success": True, "event_id": event_id, "detailed_result": status['result_inline']}
            if status.get('result_file') and Path(status['result_file']).exists():
                with open(status['result_file'], 'r', encoding='utf-8') as rf:
                    detailed = json.load(rf)
                return {"success": True, "event_id": event_id, "detailed_result": detailed}
        return {"success": False, "event_id": event_id, "error": "result_not_ready"}
    except Exception as e:
        return {"success": False, "event_id": event_id, "error": str(e)}


@router.get("/status/{event_id}")
async def get_analysis_status(event_id: int):
    """返回后端写入的真实进度状态文件"""
    try:
        status_file = Path(__file__).resolve().parents[2] / 'modules' / 'TruthNews' / 'news_analysis' / f'status_event_{event_id}.json'
        if status_file.exists():
            with open(status_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return {"success": True, **data}
        return {"success": True, "status": "idle", "event_id": event_id}
    except Exception as e:
        return {"success": False, "status": "error", "error": str(e), "event_id": event_id}


@router.get("/status")
async def get_all_analysis_status():
    """聚合返回所有事件的分析状态（便于首页统一展示）。"""
    try:
        base = Path(__file__).resolve().parents[2] / 'modules' / 'TruthNews' / 'news_analysis'
        results = []
        if base.exists():
            for f in base.glob('status_event_*.json'):
                try:
                    with open(f, 'r', encoding='utf-8') as rf:
                        data = json.load(rf)
                        # 从文件名提取事件ID
                        try:
                            eid = int(f.stem.replace('status_event_', ''))
                        except Exception:
                            eid = data.get('event_id')
                        data['event_id'] = data.get('event_id') or eid
                        results.append({
                            'event_id': data.get('event_id'),
                            'status': data.get('status'),
                            'step': data.get('step'),
                            'raw_count': data.get('raw_count'),
                            'accessible': data.get('accessible'),
                            'relevant': data.get('relevant'),
                            'updated_at': data.get('updated_at') or data.get('finished_at')
                        })
                except Exception:
                    continue
        return {"success": True, "items": results}
    except Exception as e:
        return {"success": False, "error": str(e)}