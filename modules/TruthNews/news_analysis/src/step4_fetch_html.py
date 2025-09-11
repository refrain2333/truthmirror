#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤4: 获取原始HTML
访问筛选后的URL，下载完整HTML内容并保存到文件
"""

import requests
import os
import glob
import json
import time
from datetime import datetime
from urllib.parse import urlparse

def load_relevant_news(query):
    """
    加载步骤3的相关性筛选结果
    
    Args:
        query (str): 搜索关键词
    
    Returns:
        dict: 相关性筛选数据
    """
    # 查找最新的相关性筛选文件
    pattern = f"processed_data/03_ai_relevance_filtered/{query}_relevant_*.json"
    files = glob.glob(pattern)
    
    if not files:
        raise FileNotFoundError(f"未找到查询 '{query}' 的相关性筛选文件")
    
    # 选择最新的文件
    latest_file = max(files, key=os.path.getctime)
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def fetch_html_content(url, timeout=30):
    """
    获取单个URL的HTML内容
    
    Args:
        url (str): 要获取的URL
        timeout (int): 超时时间（秒）
    
    Returns:
        tuple: (success, html_content, error_message)
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        
        # 尝试使用响应头中的编码，如果没有则使用UTF-8
        if response.encoding:
            html_content = response.text
        else:
            # 如果没有编码信息，尝试检测编码
            html_content = response.content.decode('utf-8', errors='ignore')
        
        return True, html_content, None
        
    except requests.exceptions.Timeout:
        return False, None, "请求超时"
    except requests.exceptions.ConnectionError:
        return False, None, "连接错误"
    except requests.exceptions.HTTPError as e:
        return False, None, f"HTTP错误: {e.response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, None, f"请求异常: {str(e)}"
    except UnicodeDecodeError as e:
        return False, None, f"编码错误: {str(e)}"
    except Exception as e:
        return False, None, f"未知错误: {str(e)}"

def create_html_folder(query):
    """
    创建HTML文件存储文件夹
    
    Args:
        query (str): 搜索关键词
    
    Returns:
        str: 创建的文件夹路径
    """
    # 创建基础目录
    base_dir = 'processed_data/04_raw_html_pages'
    os.makedirs(base_dir, exist_ok=True)
    
    # 创建专属文件夹
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    folder_name = f"{query}_html_{timestamp}"
    folder_path = os.path.join(base_dir, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    
    return folder_path

def save_html_file(folder_path, news_id, html_content):
    """
    保存HTML文件
    
    Args:
        folder_path (str): 文件夹路径
        news_id (int): 新闻ID
        html_content (str): HTML内容
    
    Returns:
        str: 保存的文件路径
    """
    filename = f"{news_id}.html"
    filepath = os.path.join(folder_path, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return filepath

def step4_fetch_html_pages(query):
    """
    步骤4主函数：获取原始HTML
    
    Args:
        query (str): 搜索关键词
    
    Returns:
        str: HTML文件夹路径
    """
    print(f"[Step 4/7] Fetching raw HTML pages...")
    
    # 加载相关性筛选结果
    print("  正在加载相关性筛选结果...")
    relevant_data = load_relevant_news(query)
    
    news_items = relevant_data['news_items']
    total_count = len(news_items)
    print(f"  需要获取 {total_count} 个网页的HTML内容")
    
    # 创建HTML存储文件夹
    html_folder = create_html_folder(query)
    print(f"  HTML文件将保存到: {html_folder}")
    
    # 获取HTML内容
    success_count = 0
    failed_urls = []
    
    for idx, news_item in enumerate(news_items, 1):
        news_id = news_item['id']
        url = news_item['url']
        title = news_item['title'][:50] + "..." if len(news_item['title']) > 50 else news_item['title']
        
        print(f"  正在获取第 {idx}/{total_count} 个页面 (ID: {news_id})...")
        print(f"    标题: {title}")
        print(f"    URL: {url}")
        
        # 获取HTML内容
        success, html_content, error_msg = fetch_html_content(url)
        
        if success:
            # 保存HTML文件
            html_file = save_html_file(html_folder, news_id, html_content)
            success_count += 1
            print(f"    ✓ 成功获取并保存到: {os.path.basename(html_file)}")
        else:
            failed_urls.append({'id': news_id, 'url': url, 'error': error_msg})
            print(f"    ✗ 获取失败: {error_msg}")
        
        # 添加延迟，避免过于频繁的请求
        if idx < total_count:  # 最后一个不需要延迟
            time.sleep(1)
    
    # 保存获取结果摘要
    summary = {
        'query': query,
        'total_pages': total_count,
        'success_count': success_count,
        'failed_count': len(failed_urls),
        'html_folder': html_folder,
        'failed_urls': failed_urls,
        'processed_time': datetime.now().isoformat()
    }
    
    summary_file = os.path.join(html_folder, 'fetch_summary.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"  步骤4完成！成功获取 {success_count}/{total_count} 个页面的HTML内容")
    if failed_urls:
        print(f"  失败的页面数: {len(failed_urls)}")
    print(f"  HTML文件已保存到: {html_folder}")
    print(f"  获取摘要已保存到: {summary_file}")
    
    return html_folder

if __name__ == "__main__":
    # 测试代码
    test_query = "英伟达"
    try:
        result_folder = step4_fetch_html_pages(test_query)
        print(f"测试完成，HTML文件夹: {result_folder}")
    except Exception as e:
        print(f"测试失败: {e}")
