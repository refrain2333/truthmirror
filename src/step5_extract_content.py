#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤5: 提取正文
使用Beautiful Soup解析HTML，提取新闻正文内容
"""

import os
import glob
import json
from datetime import datetime
from bs4 import BeautifulSoup
import re

def load_relevant_news_data(query):
    """
    加载步骤3的相关性筛选结果作为基础结构
    
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

def find_html_folder(query):
    """
    查找最新的HTML文件夹
    
    Args:
        query (str): 搜索关键词
    
    Returns:
        str: HTML文件夹路径
    """
    base_dir = 'processed_data/04_raw_html_pages'
    pattern = f"{query}_html_*"
    
    folders = []
    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)
        if os.path.isdir(item_path) and item.startswith(f"{query}_html_"):
            folders.append(item_path)
    
    if not folders:
        raise FileNotFoundError(f"未找到查询 '{query}' 的HTML文件夹")
    
    # 选择最新的文件夹
    return max(folders, key=os.path.getctime)

def clean_text(text):
    """
    清理提取的文本
    
    Args:
        text (str): 原始文本
    
    Returns:
        str: 清理后的文本
    """
    if not text:
        return ""
    
    # 移除多余的空白字符
    text = re.sub(r'\s+', ' ', text)
    
    # 移除首尾空白
    text = text.strip()
    
    # 移除常见的无用内容
    patterns_to_remove = [
        r'广告|Advertisement|AD|推广',
        r'点击查看|查看更多|阅读全文',
        r'分享到|Share|转发|Forward',
        r'评论|Comment|留言',
        r'订阅|Subscribe|关注',
        r'版权所有|Copyright|All rights reserved',
        r'免责声明|Disclaimer',
        r'相关阅读|相关新闻|Related',
        r'热门推荐|推荐阅读|Recommended'
    ]
    
    for pattern in patterns_to_remove:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    return text.strip()

def extract_article_content(html_content):
    """
    从HTML中提取新闻正文内容
    
    Args:
        html_content (str): HTML内容
    
    Returns:
        str: 提取的正文内容
    """
    if not html_content:
        return ""
    
    try:
        soup = BeautifulSoup(html_content, 'lxml')
        
        # 移除脚本和样式标签
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()
        
        # 常见的正文内容选择器（按优先级排序）
        content_selectors = [
            # 通用的文章内容选择器
            'article',
            '[class*="article"]',
            '[class*="content"]',
            '[class*="post"]',
            '[class*="story"]',
            '[class*="news"]',
            '[class*="text"]',
            '[class*="body"]',
            '[id*="article"]',
            '[id*="content"]',
            '[id*="post"]',
            '[id*="story"]',
            '[id*="news"]',
            '[id*="text"]',
            '[id*="body"]',
            
            # 中文网站常见选择器
            '.article-content',
            '.post-content',
            '.news-content',
            '.content-body',
            '.article-body',
            '.main-content',
            '.text-content',
            
            # 英文网站常见选择器
            '.entry-content',
            '.post-body',
            '.article-text',
            '.story-body',
            '.content-wrapper',
            
            # 通用标签
            'main',
            '.main',
            '#main'
        ]
        
        extracted_content = ""
        
        # 尝试使用不同的选择器提取内容
        for selector in content_selectors:
            try:
                elements = soup.select(selector)
                if elements:
                    # 选择最长的内容
                    best_element = max(elements, key=lambda x: len(x.get_text()))
                    content = best_element.get_text()
                    
                    # 如果内容足够长，认为找到了正文
                    if len(content.strip()) > 200:
                        extracted_content = content
                        break
            except:
                continue
        
        # 如果上述方法都没有找到合适的内容，尝试提取所有段落
        if not extracted_content or len(extracted_content.strip()) < 200:
            paragraphs = soup.find_all('p')
            if paragraphs:
                # 合并所有段落内容
                paragraph_texts = [p.get_text() for p in paragraphs]
                # 过滤掉太短的段落
                meaningful_paragraphs = [p for p in paragraph_texts if len(p.strip()) > 20]
                extracted_content = '\n'.join(meaningful_paragraphs)
        
        # 如果还是没有内容，使用整个body的文本
        if not extracted_content or len(extracted_content.strip()) < 100:
            body = soup.find('body')
            if body:
                extracted_content = body.get_text()
        
        # 清理文本
        cleaned_content = clean_text(extracted_content)
        
        return cleaned_content
        
    except Exception as e:
        print(f"    解析HTML时发生错误: {e}")
        return ""

def extract_content_from_html_files(query, news_data, html_folder):
    """
    从HTML文件中提取所有新闻的正文内容
    
    Args:
        query (str): 搜索关键词
        news_data (dict): 新闻数据
        html_folder (str): HTML文件夹路径
    
    Returns:
        dict: 更新后的新闻数据
    """
    updated_news_items = []
    
    for news_item in news_data['news_items']:
        news_id = news_item['id']
        html_file = os.path.join(html_folder, f"{news_id}.html")
        
        print(f"  正在提取新闻 {news_id} 的正文内容...")
        
        if os.path.exists(html_file):
            # 读取HTML文件
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # 提取正文内容
            article_content = extract_article_content(html_content)
            
            if article_content and len(article_content.strip()) > 50:
                # 更新content字段为完整正文
                updated_item = news_item.copy()
                updated_item['content'] = article_content
                updated_item['content_extracted'] = True
                updated_item['original_summary'] = news_item['content']  # 保存原始摘要
                updated_news_items.append(updated_item)
                
                print(f"    ✓ 成功提取正文 ({len(article_content)} 字符)")
            else:
                # 如果提取失败，保留原始摘要
                updated_item = news_item.copy()
                updated_item['content_extracted'] = False
                updated_news_items.append(updated_item)
                
                print(f"    ✗ 正文提取失败，保留原始摘要")
        else:
            # HTML文件不存在
            updated_item = news_item.copy()
            updated_item['content_extracted'] = False
            updated_news_items.append(updated_item)
            
            print(f"    ✗ HTML文件不存在: {html_file}")
    
    # 更新数据结构
    updated_data = news_data.copy()
    updated_data['news_items'] = updated_news_items
    updated_data['processed_time'] = datetime.now().isoformat()
    updated_data['content_extraction'] = {
        'total_items': len(updated_news_items),
        'extracted_count': sum(1 for item in updated_news_items if item.get('content_extracted', False)),
        'failed_count': sum(1 for item in updated_news_items if not item.get('content_extracted', False))
    }
    
    return updated_data

def save_extracted_content(query, content_data):
    """
    保存提取的正文内容
    
    Args:
        query (str): 搜索关键词
        content_data (dict): 包含正文的数据
    
    Returns:
        str: 保存的文件路径
    """
    # 创建输出目录
    output_dir = 'processed_data/05_extracted_article_content'
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{query}_content_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    # 保存文件
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(content_data, f, ensure_ascii=False, indent=2)
    
    return filepath

def step5_extract_article_content(query):
    """
    步骤5主函数：提取正文
    
    Args:
        query (str): 搜索关键词
    
    Returns:
        str: 保存的文件路径
    """
    print(f"[Step 5/7] Extracting article content...")
    
    # 加载相关性筛选结果作为基础结构
    print("  正在加载新闻数据...")
    news_data = load_relevant_news_data(query)
    
    # 查找HTML文件夹
    print("  正在查找HTML文件夹...")
    html_folder = find_html_folder(query)
    print(f"  HTML文件夹: {html_folder}")
    
    # 提取正文内容
    print(f"  开始提取 {len(news_data['news_items'])} 条新闻的正文内容...")
    content_data = extract_content_from_html_files(query, news_data, html_folder)
    
    # 保存结果
    filepath = save_extracted_content(query, content_data)
    
    extraction_stats = content_data['content_extraction']
    print(f"  步骤5完成！")
    print(f"  成功提取正文: {extraction_stats['extracted_count']}/{extraction_stats['total_items']}")
    print(f"  提取失败: {extraction_stats['failed_count']}")
    print(f"  结果已保存到: {filepath}")
    
    return filepath

if __name__ == "__main__":
    # 测试代码
    test_query = "英伟达"
    try:
        result_file = step5_extract_article_content(test_query)
        print(f"测试完成，结果文件: {result_file}")
    except Exception as e:
        print(f"测试失败: {e}")
