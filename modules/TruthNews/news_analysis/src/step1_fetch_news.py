#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤1: 获取新闻列表与预清理
从SearXNG API获取新闻数据，合并5页结果，进行数据清理和结构化处理
"""

import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def fetch_news_from_searxng(query, page_num=1):
    """
    从SearXNG API获取指定页面的新闻数据
    
    Args:
        query (str): 搜索关键词
        page_num (int): 页码
    
    Returns:
        dict: API返回的JSON数据
    """
    api_url = os.getenv('SEARXNG_API_URL', 'http://115.120.215.107:8888/search')
    
    params = {
        'q': query,
        'categories': 'news',
        'format': 'json',
        'pageno': page_num
    }
    
    try:
        print(f"  正在获取第 {page_num} 页数据...")
        response = requests.get(api_url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"  获取第 {page_num} 页数据失败: {e}")
        return None

def clean_and_structure_news_data(query, all_results):
    """
    清理和结构化新闻数据
    
    Args:
        query (str): 搜索关键词
        all_results (list): 所有页面的新闻结果列表
    
    Returns:
        dict: 结构化的新闻数据
    """
    # 合并所有新闻条目
    all_news_items = []
    for page_result in all_results:
        if page_result and 'results' in page_result:
            all_news_items.extend(page_result['results'])
    
    # 为每个新闻条目添加唯一ID并清理数据
    cleaned_news_items = []
    for idx, item in enumerate(all_news_items, 1):
        cleaned_item = {
            'id': idx,
            'title': item.get('title', ''),
            'content': item.get('content', ''),  # 这里是摘要
            'url': item.get('url', ''),
            'engine': item.get('engine', ''),
            'metadata': {
                'publishedDate': item.get('publishedDate', ''),
                'img_src': item.get('img_src', ''),
                'thumbnail': item.get('thumbnail', ''),
                'category': item.get('category', ''),
                'score': item.get('score', 0)
            }
        }
        
        # 只保留有效的新闻条目（必须有标题和URL）
        if cleaned_item['title'] and cleaned_item['url']:
            cleaned_news_items.append(cleaned_item)
    
    # 构建最终的结构化数据
    structured_data = {
        'query': query,
        'total_count': len(cleaned_news_items),
        'processed_time': datetime.now().isoformat(),
        'pages_fetched': 5,
        'news_items': cleaned_news_items
    }
    
    return structured_data

def save_raw_search_results(query, structured_data):
    """
    保存原始搜索结果到文件
    
    Args:
        query (str): 搜索关键词
        structured_data (dict): 结构化的新闻数据
    
    Returns:
        str: 保存的文件路径
    """
    # 创建输出目录
    output_dir = 'processed_data/01_raw_search_results'
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{query}_raw_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    # 保存文件
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(structured_data, f, ensure_ascii=False, indent=2)
    
    return filepath

def step1_fetch_and_clean_news(query):
    """
    步骤1主函数：获取新闻列表与预清理
    
    Args:
        query (str): 搜索关键词
    
    Returns:
        str: 保存的文件路径
    """
    print(f"[Step 1/7] Fetching and cleaning news for query: '{query}'...")
    
    # 获取5页数据
    all_results = []
    for page in range(1, 6):
        result = fetch_news_from_searxng(query, page)
        if result:
            all_results.append(result)
    
    if not all_results:
        raise Exception("无法获取任何新闻数据")
    
    print(f"  成功获取 {len(all_results)} 页数据")
    
    # 清理和结构化数据
    print("  正在清理和结构化数据...")
    structured_data = clean_and_structure_news_data(query, all_results)
    
    # 保存结果
    filepath = save_raw_search_results(query, structured_data)
    
    print(f"  步骤1完成！共获取 {structured_data['total_count']} 条新闻")
    print(f"  结果已保存到: {filepath}")
    
    return filepath

if __name__ == "__main__":
    # 测试代码
    test_query = "英伟达"
    try:
        result_file = step1_fetch_and_clean_news(test_query)
        print(f"测试完成，结果文件: {result_file}")
    except Exception as e:
        print(f"测试失败: {e}")
