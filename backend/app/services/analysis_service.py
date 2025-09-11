"""
智能分析服务集成
简单直接地集成modules下的智能分析功能
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# 添加智能分析系统路径
project_root = Path(__file__).parent.parent.parent.parent
analysis_path = project_root / "modules" / "TruthNews" / "news_analysis"
sys.path.insert(0, str(analysis_path))

# 设置工作目录为分析系统目录
ANALYSIS_DIR = str(analysis_path)


def run_news_analysis(event_title: str, event_description: str, event_id: int = None) -> Dict[str, Any]:
    """
    运行新闻分析
    
    Args:
        event_title: 事件标题
        event_description: 事件描述
        
    Returns:
        分析结果
    """
    query = f"{event_title} {event_description}".strip()
    original_cwd = os.getcwd()
    
    # 简单状态写入，供前端轮询真实进度
    def _write_status(payload: Dict[str, Any]) -> None:
        try:
            status_file = Path(ANALYSIS_DIR) / f"status_event_{event_id}.json"
            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
        except Exception:
            # 状态写入失败不影响主流程
            pass

    try:
        # 首先切换到分析系统目录
        os.chdir(ANALYSIS_DIR)
        
        # 验证智能分析系统是否可用
        if not (Path(ANALYSIS_DIR) / "main.py").exists():
            raise FileNotFoundError("智能分析系统主程序不存在")
        
        # 检查是否配置了API密钥
        from dotenv import load_dotenv
        # 先尝试从分析系统目录加载环境变量
        env_file = Path(ANALYSIS_DIR) / '.env'
        if env_file.exists():
            load_dotenv(env_file)
        else:
            load_dotenv()  # 加载默认的.env
        
        glm_api_key = os.getenv('GLM_API_KEY')
        print(f"调试: GLM_API_KEY = {'已配置' if glm_api_key else '未找到'}")
        if not glm_api_key or glm_api_key == "请在此处填入您的GLM API密钥":
            # 如果没有配置API密钥，返回提示信息
            return {
                "success": False,
                "error": "需要配置GLM_API_KEY环境变量",
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "config_help": "请配置环境变量：GLM_API_KEY=你的API密钥"
            }
        
        print(f"🤖 [事件{event_id}] 启动AI智能分析: {query}")
        _write_status({
            "status": "started",
            "step": "step1_search",
            "event_id": event_id,
            "raw_count": 0,
            "started_at": datetime.now().isoformat()
        })
        
        # 动态导入分析系统的主程序
        import sys
        if ANALYSIS_DIR not in sys.path:
            sys.path.insert(0, ANALYSIS_DIR)
        
        # 确保每个分析任务有独立的Python路径
        sys.path.insert(0, ANALYSIS_DIR)
        
        # 导入并运行真实的分析流程
        from main import run_news_analysis_pipeline
        
        print(f"🔄 [事件{event_id}] 执行AI分析流程")
        
        # 运行完整的智能分析流程
        try:
            # 重要：搜索应使用"纯查询"，不要拼接事件ID/时间戳以免导致搜索结果为0
            print(f"📝 [事件{event_id}] 使用纯查询进行搜索: {query}")
            result_file = run_news_analysis_pipeline(query)
            
            # 读取最终分析结果
            if result_file and Path(result_file).exists():
                with open(result_file, 'r', encoding='utf-8') as f:
                    detailed_result = json.load(f)
                
                # 根据AI分析结果生成评级
                ai_reliability = generate_reliability_rating(detailed_result)

                # 写入完成状态（包含关键统计）并进行有效性校验
                workflow = detailed_result.get("workflow_summary", {})
                raw_count = int(workflow.get("step1_raw_news") or 0)
                accessible = int(workflow.get("step2_accessible") or 0)
                relevant = int(workflow.get("step3_relevant") or 0)
                analyzed = int(workflow.get("step6_analyzed") or 0)

                if max(raw_count, accessible, relevant, analyzed) <= 0:
                    # 无数据时尝试直连AI兜底
                    _write_status({
                        "status": "running",
                        "step": "step6_direct_ai_attempt",
                        "event_id": event_id,
                        "raw_count": raw_count,
                        "accessible": accessible,
                        "relevant": relevant,
                        "finished_at": datetime.now().isoformat()
                    })
                    # 触发无数据兜底：直接调用真实DeepSeek进行文本分析
                    fallback_summary = _direct_deepseek_analysis(query)
                    if fallback_summary:
                        _write_status({
                            "status": "completed",
                            "step": "finished",
                            "event_id": event_id,
                            "raw_count": raw_count,
                            "accessible": accessible,
                            "relevant": relevant,
                            "mode": "direct_ai",
                            "result_inline": {
                                "final_summary": fallback_summary,
                                "workflow_summary": workflow
                            },
                            "finished_at": datetime.now().isoformat()
                        })
                        return {
                            "success": True,
                            "event_id": event_id,
                            "query": query,
                            "ai_analysis": {
                                "reliability": "insufficient",  # 无外部来源，仅基于文本
                                "summary": fallback_summary,
                                "analysis_statistics": {"sources": 0, "mode": "direct_ai"},
                                "workflow_summary": workflow
                            },
                            "detailed_result": {
                                "final_summary": fallback_summary,
                                "workflow_summary": workflow
                            },
                            "result_file": result_file,
                            "timestamp": datetime.now().isoformat(),
                            "next_step": "REVIEW"
                        }
                    else:
                        return {
                            "success": False,
                            "event_id": event_id,
                            "query": query,
                            "error": "AI未获取到有效数据，请稍后重试或更换关键词",
                            "ai_analysis": {
                                "reliability": "insufficient",
                                "summary": "本次抓取和提取均未获得有效内容，建议调整事件标题/描述后再次分析。",
                                "analysis_statistics": detailed_result.get("analysis_statistics", {}),
                                "workflow_summary": workflow
                            },
                            "detailed_result": detailed_result,
                            "result_file": result_file,
                            "timestamp": datetime.now().isoformat(),
                            "next_step": "RETRY"
                        }

                _write_status({
                    "status": "completed",
                    "step": "step7_summary",
                    "event_id": event_id,
                    "raw_count": raw_count,
                    "accessible": accessible,
                    "relevant": relevant,
                    "result_file": str(Path(result_file).resolve()),
                    "finished_at": datetime.now().isoformat()
                })

                return {
                    "success": True,
                    "event_id": event_id,
                    "query": query,
                    "ai_analysis": {
                        "reliability": ai_reliability,
                        "summary": detailed_result.get("final_summary", ""),
                        "analysis_statistics": detailed_result.get("analysis_statistics", {}),
                        "workflow_summary": workflow
                    },
                    "detailed_result": detailed_result,
                    "result_file": result_file,
                    "timestamp": datetime.now().isoformat(),
                    "next_step": "VOTING"
                }
            else:
                raise FileNotFoundError("分析结果文件未生成")
        
        except Exception as analysis_error:
            print(f"❌ 完整分析流程失败: {analysis_error}")

            # 针对常见文件缺失/抓取为0的情况，直接启用真实AI兜底，避免前端卡死
            err_text = str(analysis_error)
            if "No such file or directory" in err_text or "processed_data/04_raw_html_pages" in err_text:
                fallback_summary = _direct_deepseek_analysis(query)
                if fallback_summary:
                    _write_status({
                        "status": "completed",
                        "step": "step7_summary",
                        "event_id": event_id,
                        "mode": "direct_ai",
                        "result_inline": {
                            "final_summary": fallback_summary,
                            "workflow_summary": {"status": "direct_ai"}
                        },
                        "finished_at": datetime.now().isoformat()
                    })
                    return {
                        "success": True,
                        "event_id": event_id,
                        "query": query,
                        "ai_analysis": {
                            "reliability": "insufficient",
                            "summary": fallback_summary,
                            "analysis_statistics": {"sources": 0, "mode": "direct_ai"},
                            "workflow_summary": {"status": "direct_ai"}
                        },
                        "detailed_result": {"final_summary": fallback_summary},
                        "timestamp": datetime.now().isoformat(),
                        "next_step": "REVIEW"
                    }

            _write_status({
                "status": "failed",
                "step": "exception",
                "event_id": event_id,
                "error": str(analysis_error),
                "finished_at": datetime.now().isoformat()
            })

            # 如果完整分析失败，返回基础分析结果
            return {
                "success": False,
                "event_id": event_id,
                "query": query,
                "error": f"AI分析过程出错: {str(analysis_error)}",
                "error_type": "glm_api_error" if "409" in str(analysis_error) else "analysis_error",
                "suggestion": "请检查GLM/DeepSeek配置或稍后重试",
                "ai_analysis": {
                    "reliability": "insufficient",
                    "summary": f"由于技术问题，无法完成对'{query}'的深度分析。建议手动验证相关信息。",
                    "analysis_statistics": {"error": "analysis_failed"},
                    "workflow_summary": {"status": "failed", "error": str(analysis_error)[:200]}
                },
                "timestamp": datetime.now().isoformat(),
                "next_step": "MANUAL_REVIEW"
            }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "query": query,
            "timestamp": datetime.now().isoformat()
        }
    finally:
        # 恢复原工作目录
        os.chdir(original_cwd)


def generate_reliability_rating(analysis_result: Dict[str, Any]) -> str:
    """
    根据AI分析结果生成可靠性评级
    
    Args:
        analysis_result: AI分析结果
        
    Returns:
        str: 可靠性评级 (reliable/questionable/unreliable/insufficient)
    """
    try:
        # 获取分析统计信息
        stats = analysis_result.get("analysis_statistics", {})
        total_items = stats.get("total_items", 0)
        successful_analyses = stats.get("successful_analyses", 0)
        
        # 计算成功率
        success_rate = successful_analyses / total_items if total_items > 0 else 0
        
        # 获取工作流汇总
        workflow = analysis_result.get("workflow_summary", {})
        relevant_news = workflow.get("step3_relevant", 0)
        analyzed_count = workflow.get("step6_analyzed", 0)
        
        # 评级逻辑
        if total_items >= 10 and success_rate >= 0.8 and relevant_news >= 5:
            return "reliable"  # 可靠：信息充足且分析成功率高
        elif total_items >= 5 and success_rate >= 0.6 and relevant_news >= 3:
            return "questionable"  # 存疑：信息一般，需要进一步验证
        elif total_items >= 3 and analyzed_count > 0:
            return "unreliable"  # 不可靠：信息较少或质量不高
        else:
            return "insufficient"  # 信息不足：无法进行有效分析
            
    except Exception as e:
        print(f"评级生成错误: {e}")
        return "insufficient"


def get_analysis_result(result_file: str) -> Dict[str, Any]:
    """
    获取分析结果内容
    
    Args:
        result_file: 结果文件路径
        
    Returns:
        分析结果内容
    """
    try:
        import json
        with open(result_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return {"error": f"读取结果文件失败: {e}"}


# 直接调用DeepSeek作为兜底（真实AI）
def _direct_deepseek_analysis(text: str) -> str | None:
    try:
        import os, requests
        api_key = os.getenv('DEEPSEEK_API_KEY')
        model_id = os.getenv('DEEPSEEK_MODEL_ID', 'deepseek-chat')
        if not api_key:
            return None
        url = 'https://api.deepseek.com/chat/completions'
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        payload = {
            'model': model_id,
            'messages': [
                { 'role': 'system', 'content': 'You are an investigative news analyst. Provide concise, structured conclusions with caveats when sources are missing.' },
                { 'role': 'user', 'content': f"根据下面事件文本进行事实核验取向的分析。要求：\n- 给出关键事实清单\n- 标注不确定点\n- 给出进一步核验建议\n\n事件文本：{text}" }
            ],
            'temperature': 0.3,
            'max_tokens': 800
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            return data.get('choices', [{}])[0].get('message', {}).get('content')
        return None
    except Exception:
        return None
