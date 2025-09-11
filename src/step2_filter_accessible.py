#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤2: 连通性筛选
使用requests检查URL连通性，筛选出可访问的新闻URL
"""

import requests
import json
import os
import glob
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

def check_url_accessibility(url, timeout=10):
    """
    检查单个URL的可访问性

    Args:
        url (str): 要检查的URL
        timeout (int): 超时时间（秒）

    Returns:
        tuple: (url, is_accessible, status_code)
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True)
        # 认为状态码在200-399范围内的都是可访问的
        is_accessible = 200 <= response.status_code < 400
        return url, is_accessible, response.status_code
    except requests.exceptions.Timeout:
        return url, False, "TIMEOUT"
    except requests.exceptions.ConnectionError:
        return url, False, "CONNECTION_ERROR"
    except requests.exceptions.RequestException as e:
        return url, False, f"REQUEST_ERROR: {str(e)}"
    except Exception as e:
        return url, False, f"ERROR: {str(e)}"

def check_urls_batch(urls, max_workers=5, timeout=10):
    """
    批量检查URL可访问性

    Args:
        urls (list): URL列表
        max_workers (int): 最大并发数
        timeout (int): 超时时间（秒）

    Returns:
        list: 检查结果列表 [(url, is_accessible, status_code), ...]
    """
    results = []

    print(f"  开始检查 {len(urls)} 个URL的可访问性...")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_url = {executor.submit(check_url_accessibility, url, timeout): url for url in urls}

        # 处理完成的任务
        completed_count = 0
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                result = future.result()
                results.append(result)
                completed_count += 1

                # 显示进度
                if completed_count % 5 == 0 or completed_count == len(urls):
                    print(f"    已检查 {completed_count}/{len(urls)} 个URL")

            except Exception as e:
                print(f"    检查URL {url} 时发生异常: {e}")
                results.append((url, False, f"EXCEPTION: {str(e)}"))
                completed_count += 1

    return results

def load_raw_search_results(query):
    """
    加载步骤1的原始搜索结果
    
    Args:
        query (str): 搜索关键词
    
    Returns:
        dict: 原始搜索结果数据
    """
    # 查找最新的原始搜索结果文件
    pattern = f"processed_data/01_raw_search_results/{query}_raw_*.json"
    files = glob.glob(pattern)
    
    if not files:
        raise FileNotFoundError(f"未找到查询 '{query}' 的原始搜索结果文件")
    
    # 选择最新的文件
    latest_file = max(files, key=os.path.getctime)
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def filter_accessible_news(raw_data, accessibility_results):
    """
    根据可访问性结果筛选新闻
    
    Args:
        raw_data (dict): 原始新闻数据
        accessibility_results (list): URL可访问性检查结果
    
    Returns:
        dict: 筛选后的新闻数据
    """
    # 创建URL到可访问性的映射
    url_accessibility = {url: is_accessible for url, is_accessible, _ in accessibility_results}
    
    # 筛选可访问的新闻
    accessible_news = []
    for news_item in raw_data['news_items']:
        url = news_item['url']
        if url_accessibility.get(url, False):
            accessible_news.append(news_item)
    
    # 更新数据结构
    filtered_data = raw_data.copy()
    filtered_data['news_items'] = accessible_news
    filtered_data['total_count'] = len(accessible_news)
    filtered_data['processed_time'] = datetime.now().isoformat()
    filtered_data['accessibility_check'] = {
        'total_checked': len(accessibility_results),
        'accessible_count': len(accessible_news),
        'inaccessible_count': len(accessibility_results) - len(accessible_news)
    }
    
    return filtered_data

def save_accessible_urls(query, filtered_data):
    """
    保存可访问URL的筛选结果
    
    Args:
        query (str): 搜索关键词
        filtered_data (dict): 筛选后的数据
    
    Returns:
        str: 保存的文件路径
    """
    # 创建输出目录
    output_dir = 'processed_data/02_filtered_accessible_urls'
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{query}_accessible_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    # 保存文件
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=2)
    
    return filepath

def step2_filter_accessible_urls(query):
    """
    步骤2主函数：连通性筛选

    Args:
        query (str): 搜索关键词

    Returns:
        str: 保存的文件路径
    """
    print(f"[Step 2/7] Filtering accessible URLs...")

    # 加载原始搜索结果
    print("  正在加载原始搜索结果...")
    raw_data = load_raw_search_results(query)

    # 提取所有URL
    urls = [item['url'] for item in raw_data['news_items']]
    print(f"  需要检查 {len(urls)} 个URL的可访问性")

    # 检查URL可访问性
    print("  正在检查URL可访问性...")
    accessibility_results = check_urls_batch(urls, max_workers=5, timeout=10)

    # 筛选可访问的新闻
    print("  正在筛选可访问的新闻...")
    filtered_data = filter_accessible_news(raw_data, accessibility_results)

    # 保存结果
    filepath = save_accessible_urls(query, filtered_data)

    accessible_count = filtered_data['accessibility_check']['accessible_count']
    total_count = filtered_data['accessibility_check']['total_checked']

    print(f"  步骤2完成！从 {total_count} 条新闻中筛选出 {accessible_count} 条可访问的新闻")
    print(f"  结果已保存到: {filepath}")

    return filepath

def run_step2(query):
    """
    运行步骤2的同步包装函数

    Args:
        query (str): 搜索关键词

    Returns:
        str: 保存的文件路径
    """
    return step2_filter_accessible_urls(query)

if __name__ == "__main__":
    # 测试代码
    test_query = "英伟达"
    try:
        result_file = run_step2(test_query)
        print(f"测试完成，结果文件: {result_file}")
    except Exception as e:
        print(f"测试失败: {e}")
