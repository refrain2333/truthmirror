#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤7: 生成最终汇总报告
整合所有分析结果，生成综合性总结报告
"""

import requests
import json
import os
import glob
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def call_glm_summary_api(query, all_analyzed_texts):
    """
    调用GLM API生成最终汇总报告

    Args:
        query (str): 搜索关键词
        all_analyzed_texts (str): 所有分析文本的拼接

    Returns:
        tuple: (success, summary_result, error_message)
    """
    api_url = os.getenv('GLM_API_URL', 'https://open.bigmodel.cn/api/paas/v4/')
    api_key = os.getenv('GLM_API_KEY')
    model_id = os.getenv('GLM_MODEL_ID', 'glm-4.5-flash')

    if not api_key:
        raise ValueError("GLM_API_KEY环境变量未设置")

    # 获取汇总提示词模板
    summary_prompt_template = os.getenv('GLM_SUMMARY_PROMPT',
        '你是一位资深新闻分析师。请根据以下关于\'{query}\'的新闻分析，撰写一份综合性总结报告。\n\n分析内容：\n{analyzed_content}')

    # 构建完整的提示词
    full_prompt = summary_prompt_template.format(
        query=query,
        analyzed_content=all_analyzed_texts
    )

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    data = {
        'model': model_id,
        'messages': [
            {
                'role': 'user',
                'content': full_prompt
            }
        ],
        'temperature': 0.8,
        'max_tokens': 3000
    }
    
    try:
        # 构建完整的API URL
        full_url = f"{api_url.rstrip('/')}/chat/completions"

        response = requests.post(
            full_url,
            headers=headers,
            json=data,
            timeout=60
        )
        response.raise_for_status()

        result = response.json()

        # 解析GLM API的响应格式
        if 'choices' in result and len(result['choices']) > 0:
            choice = result['choices'][0]
            if 'message' in choice and 'content' in choice['message']:
                summary_text = choice['message']['content']
                return True, summary_text.strip(), None
            else:
                return False, None, f"API响应格式异常: {result}"
        else:
            return False, None, f"API返回无有效选择结果: {result}"

    except requests.exceptions.Timeout:
        return False, None, "API请求超时"
    except requests.exceptions.RequestException as e:
        return False, None, f"API请求失败: {str(e)}"
    except json.JSONDecodeError as e:
        return False, None, f"API响应JSON解析失败: {str(e)}"
    except Exception as e:
        return False, None, f"未知错误: {str(e)}"

def load_analyzed_data(query):
    """
    加载步骤6的AI分析结果
    
    Args:
        query (str): 搜索关键词
    
    Returns:
        dict: AI分析数据
    """
    # 查找最新的AI分析文件
    pattern = f"processed_data/06_ai_processed_data/{query}_analyzed_*.json"
    files = glob.glob(pattern)
    
    if not files:
        raise FileNotFoundError(f"未找到查询 '{query}' 的AI分析文件")
    
    # 选择最新的文件
    latest_file = max(files, key=os.path.getctime)
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_basic_summary(query, analyzed_data):
    """
    生成基础汇总报告（不依赖AI分析）

    Args:
        query (str): 搜索关键词
        analyzed_data (dict): 分析数据

    Returns:
        dict: 基础汇总报告
    """
    news_items = analyzed_data.get('news_items', [])
    total_news = len(news_items)

    # 按语言分类
    language_stats = {}
    for item in news_items:
        lang = item.get('detected_language', 'unknown')
        language_stats[lang] = language_stats.get(lang, 0) + 1

    # 提取新闻标题和摘要
    news_summaries = []
    for item in news_items:
        summary = {
            "id": item.get('id'),
            "title": item.get('title', ''),
            "url": item.get('url', ''),
            "language": item.get('detected_language', 'unknown'),
            "content_extracted": item.get('content_extracted', False),
            "content_length": len(item.get('content', '')) if item.get('content') else 0
        }
        news_summaries.append(summary)

    # 生成基础分析
    basic_analysis = f"""基于搜索关键词"{query}"的新闻分析报告：

本次分析共收集到{total_news}条相关新闻。

新闻来源语言分布：
{chr(10).join([f"- {lang}: {count}条" for lang, count in language_stats.items()])}

主要新闻标题：
{chr(10).join([f"- {item['title']}" for item in news_summaries[:10]])}

这些新闻涵盖了{query}相关的最新动态和发展趋势，为了解该主题提供了全面的信息视角。"""

    # 构建基础报告
    basic_report = {
        'query': query,
        'final_summary': basic_analysis,
        'generated_time': datetime.now().isoformat(),
        'analysis_type': 'basic_summary',
        'total_news_analyzed': total_news,
        'language_distribution': language_stats,
        'news_summaries': news_summaries
    }

    return basic_report

def extract_successful_analyses(analyzed_data):
    """
    提取成功分析的内容
    
    Args:
        analyzed_data (dict): AI分析数据
    
    Returns:
        tuple: (successful_analyses, analysis_summary)
    """
    successful_analyses = []
    failed_count = 0
    
    for news_item in analyzed_data['news_items']:
        if news_item.get('analysis_success', False):
            analysis_text = news_item.get('analyzed', '')
            if analysis_text and len(analysis_text.strip()) > 20:
                # 添加新闻标题作为上下文
                formatted_analysis = f"【{news_item['title']}】\n{analysis_text}"
                successful_analyses.append(formatted_analysis)
        else:
            failed_count += 1
    
    analysis_summary = {
        'total_items': len(analyzed_data['news_items']),
        'successful_analyses': len(successful_analyses),
        'failed_analyses': failed_count
    }
    
    return successful_analyses, analysis_summary

def generate_final_summary(query, analyzed_data):
    """
    生成最终汇总报告
    
    Args:
        query (str): 搜索关键词
        analyzed_data (dict): AI分析数据
    
    Returns:
        dict: 最终汇总报告数据
    """
    print("  正在提取成功的分析结果...")
    successful_analyses, analysis_summary = extract_successful_analyses(analyzed_data)
    
    if not successful_analyses:
        print("  没有成功的AI分析结果，生成基础汇总报告...")
        return generate_basic_summary(query, analyzed_data)
    
    print(f"  找到 {len(successful_analyses)} 个成功的分析结果")
    
    # 拼接所有分析文本
    all_analyzed_texts = '\n\n'.join(successful_analyses)
    
    # 如果文本太长，进行截断（保留前面的内容）
    max_length = 15000  # GLM-4.5-flash可以处理更长文本，提高限制
    if len(all_analyzed_texts) > max_length:
        print(f"  分析文本过长({len(all_analyzed_texts)}字符)，截断到{max_length}字符")
        all_analyzed_texts = all_analyzed_texts[:max_length] + "...\n\n[注：由于内容过长，部分分析已省略]"
    
    print("  正在调用AI生成最终汇总报告...")
    
    # 调用AI生成汇总报告
    success, summary_result, error_msg = call_glm_summary_api(query, all_analyzed_texts)
    
    if not success:
        raise Exception(f"生成汇总报告失败: {error_msg}")
    
    # 构建最终报告数据
    final_report = {
        'query': query,
        'final_summary': summary_result,
        'generated_time': datetime.now().isoformat(),
        'source_analysis_count': len(successful_analyses),
        'total_news_analyzed': analysis_summary['total_items'],
        'analysis_statistics': analysis_summary,
        'generation_model': os.getenv('GEMINI_MODEL_ID', 'gemini-2.0-flash-exp'),
        'workflow_summary': {
            'step1_raw_news': analyzed_data.get('total_count', 0),
            'step2_accessible': analyzed_data.get('accessibility_check', {}).get('accessible_count', 0),
            'step3_relevant': analyzed_data.get('ai_relevance_filter', {}).get('filtered_count', 0),
            'step4_html_fetched': analyzed_data.get('total_count', 0),
            'step5_content_extracted': analyzed_data.get('content_extraction', {}).get('extracted_count', 0),
            'step6_analyzed': analysis_summary['successful_analyses'],
            'step7_final_summary': 1 if success else 0
        }
    }
    
    return final_report

def save_final_summary(query, final_report):
    """
    保存最终汇总报告
    
    Args:
        query (str): 搜索关键词
        final_report (dict): 最终汇总报告数据
    
    Returns:
        str: 保存的文件路径
    """
    # 创建输出目录
    output_dir = 'processed_data/07_final_summary_reports'
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{query}_summary_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    # 保存文件
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(final_report, f, ensure_ascii=False, indent=2)
    
    return filepath

def step7_generate_final_summary(query):
    """
    步骤7主函数：生成最终汇总报告
    
    Args:
        query (str): 搜索关键词
    
    Returns:
        str: 保存的文件路径
    """
    print(f"[Step 7/7] Generating final summary report...")
    
    # 加载AI分析结果
    print("  正在加载AI分析结果...")
    analyzed_data = load_analyzed_data(query)
    
    # 生成最终汇总报告
    final_report = generate_final_summary(query, analyzed_data)
    
    # 保存结果
    filepath = save_final_summary(query, final_report)
    
    # 输出统计信息
    print(f"  步骤7完成！最终汇总报告已生成")
    if 'workflow_summary' in final_report:
        workflow_stats = final_report['workflow_summary']
        print(f"  工作流统计:")
        print(f"    原始新闻: {workflow_stats['step1_raw_news']}")
        print(f"    可访问: {workflow_stats['step2_accessible']}")
        print(f"    相关筛选: {workflow_stats['step3_relevant']}")
        print(f"    内容提取: {workflow_stats['step5_content_extracted']}")
        print(f"    成功分析: {workflow_stats['step6_analyzed']}")
    else:
        print(f"  基础汇总报告统计:")
        print(f"    总新闻数: {final_report.get('total_news_analyzed', 0)}")
        print(f"    分析类型: {final_report.get('analysis_type', 'unknown')}")
    print(f"  最终报告长度: {len(final_report['final_summary'])} 字符")
    print(f"  结果已保存到: {filepath}")
    
    return filepath

if __name__ == "__main__":
    # 测试代码
    test_query = "英伟达"
    try:
        result_file = step7_generate_final_summary(test_query)
        print(f"测试完成，结果文件: {result_file}")
    except Exception as e:
        print(f"测试失败: {e}")
