#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤6: AI深度分析
使用Gemini-2.0-flash-exp模型对每篇新闻进行深度分析
"""

import requests
import json
import os
import glob
import time
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def call_glm_analysis_api(content, prompt_template):
    """
    调用GLM API进行新闻分析

    Args:
        content (str): 新闻正文内容
        prompt_template (str): 提示词模板

    Returns:
        tuple: (success, analysis_result, error_message)
    """
    api_url = os.getenv('GLM_API_URL', 'https://open.bigmodel.cn/api/paas/v4/chat/completions')
    api_key = os.getenv('GLM_API_KEY')
    model_id = os.getenv('GLM_MODEL_ID', 'glm-4.5-flash')

    if not api_key:
        raise ValueError("GLM_API_KEY环境变量未设置")

    # 从环境变量获取分析提示词
    analysis_prompt_template = os.getenv('GLM_ANALYSIS_PROMPT', prompt_template)
    # 构建完整的提示词
    full_prompt = analysis_prompt_template.format(content=content)

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    data = {
        "model": model_id,
        "messages": [
            {
                "role": "user",
                "content": full_prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 1024
    }

    try:
        # 确保URL正确
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
                analysis_text = choice['message']['content']
                return True, analysis_text.strip(), None
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

def load_extracted_content(query):
    """
    加载步骤5的正文提取结果
    
    Args:
        query (str): 搜索关键词
    
    Returns:
        dict: 正文提取数据
    """
    # 查找最新的正文提取文件
    pattern = f"processed_data/05_extracted_article_content/{query}_content_*.json"
    files = glob.glob(pattern)
    
    if not files:
        raise FileNotFoundError(f"未找到查询 '{query}' 的正文提取文件")
    
    # 选择最新的文件
    latest_file = max(files, key=os.path.getctime)
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_news_articles(content_data):
    """
    对所有新闻文章进行AI分析
    
    Args:
        content_data (dict): 包含正文内容的数据
    
    Returns:
        dict: 包含分析结果的数据
    """
    # 获取分析提示词模板
    analysis_prompt = os.getenv('GEMINI_ANALYSIS_PROMPT', 
        '请你以专业的视角，为以下新闻撰写一段300到500字的分析摘要。如果原文是外语，请用中文进行分析，并可以适当引用原文关键信息。正文如下：\n\n{content}')
    
    analyzed_items = []
    total_items = len(content_data['news_items'])
    success_count = 0
    failed_count = 0
    
    for idx, news_item in enumerate(content_data['news_items'], 1):
        news_id = news_item['id']
        title = news_item['title']
        content = news_item['content']
        
        print(f"  正在分析第 {idx}/{total_items} 条新闻 (ID: {news_id})...")
        print(f"    标题: {title[:50]}{'...' if len(title) > 50 else ''}")
        
        # 检查内容长度
        if len(content.strip()) < 50:
            print(f"    ✗ 内容太短，跳过分析")
            analyzed_item = news_item.copy()
            analyzed_item['analyzed'] = "内容太短，无法进行有效分析。"
            analyzed_item['analysis_success'] = False
            analyzed_items.append(analyzed_item)
            failed_count += 1
            continue
        
        # 调用AI进行分析
        success, analysis_result, error_msg = call_glm_analysis_api(content, analysis_prompt)
        
        if success and analysis_result:
            analyzed_item = news_item.copy()
            analyzed_item['analyzed'] = analysis_result
            analyzed_item['analysis_success'] = True
            analyzed_items.append(analyzed_item)
            success_count += 1
            
            print(f"    ✓ 分析成功 ({len(analysis_result)} 字符)")
        else:
            analyzed_item = news_item.copy()
            analyzed_item['analyzed'] = f"分析失败: {error_msg}"
            analyzed_item['analysis_success'] = False
            analyzed_items.append(analyzed_item)
            failed_count += 1
            
            print(f"    ✗ 分析失败: {error_msg}")
        
        # 添加延迟，避免API限流
        if idx < total_items:  # 最后一个不需要延迟
            time.sleep(2)
    
    # 更新数据结构
    analyzed_data = content_data.copy()
    analyzed_data['news_items'] = analyzed_items
    analyzed_data['processed_time'] = datetime.now().isoformat()
    analyzed_data['ai_analysis'] = {
        'total_items': total_items,
        'success_count': success_count,
        'failed_count': failed_count,
        'analysis_model': os.getenv('GEMINI_MODEL_ID', 'gemini-2.0-flash-exp')
    }
    
    return analyzed_data

def save_analyzed_data(query, analyzed_data):
    """
    保存AI分析结果
    
    Args:
        query (str): 搜索关键词
        analyzed_data (dict): 包含分析结果的数据
    
    Returns:
        str: 保存的文件路径
    """
    # 创建输出目录
    output_dir = 'processed_data/06_ai_processed_data'
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{query}_analyzed_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    # 保存文件
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(analyzed_data, f, ensure_ascii=False, indent=2)
    
    return filepath

def step6_ai_analysis(query):
    """
    步骤6主函数：AI深度分析
    
    Args:
        query (str): 搜索关键词
    
    Returns:
        str: 保存的文件路径
    """
    print(f"[Step 6/7] Performing AI deep analysis...")
    
    # 加载正文提取结果
    print("  正在加载正文提取结果...")
    content_data = load_extracted_content(query)
    
    total_items = len(content_data['news_items'])
    print(f"  需要分析 {total_items} 条新闻")
    
    # 进行AI分析
    print("  开始AI深度分析...")
    analyzed_data = analyze_news_articles(content_data)
    
    # 保存结果
    filepath = save_analyzed_data(query, analyzed_data)
    
    analysis_stats = analyzed_data['ai_analysis']
    print(f"  步骤6完成！")
    print(f"  成功分析: {analysis_stats['success_count']}/{analysis_stats['total_items']}")
    print(f"  分析失败: {analysis_stats['failed_count']}")
    print(f"  结果已保存到: {filepath}")
    
    return filepath

if __name__ == "__main__":
    # 测试代码
    test_query = "英伟达"
    try:
        result_file = step6_ai_analysis(test_query)
        print(f"测试完成，结果文件: {result_file}")
    except Exception as e:
        print(f"测试失败: {e}")
