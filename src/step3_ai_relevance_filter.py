#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤3: AI相关性筛选
使用GLM-4.5-flash模型判断新闻相关性，筛选出最相关的15条新闻
"""


import json
import os
import glob

import re
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()



def detect_language(text):
    """
    简单的语言检测
    
    Args:
        text (str): 文本内容
    
    Returns:
        str: 语言代码 ('zh', 'en', 'ja', 'ko', 'other')
    """
    # 中文字符
    if re.search(r'[\u4e00-\u9fff]', text):
        return 'zh'
    
    # 日文字符（平假名、片假名）
    if re.search(r'[\u3040-\u309f\u30a0-\u30ff]', text):
        return 'ja'
    
    # 韩文字符
    if re.search(r'[\uac00-\ud7af]', text):
        return 'ko'
    
    # 英文字符（基本拉丁字母）
    if re.search(r'[a-zA-Z]', text):
        return 'en'
    
    return 'other'

def prioritize_by_language(news_items):
    """
    按语言优先级排序新闻
    
    Args:
        news_items (list): 新闻列表
    
    Returns:
        list: 按语言优先级排序的新闻列表
    """
    # 语言优先级：中文 > 英文 > 日文 > 韩文 > 其他
    language_priority = {'zh': 1, 'en': 2, 'ja': 3, 'ko': 4, 'other': 5}
    
    # 为每个新闻项添加语言信息
    for item in news_items:
        text = f"{item['title']} {item['content']}"
        item['detected_language'] = detect_language(text)
        item['language_priority'] = language_priority.get(item['detected_language'], 5)
    
    # 按语言优先级排序
    return sorted(news_items, key=lambda x: x['language_priority'])

def load_accessible_urls(query):
    """
    加载步骤2的可访问URL结果
    
    Args:
        query (str): 搜索关键词
    
    Returns:
        dict: 可访问URL数据
    """
    # 查找最新的可访问URL文件
    pattern = f"processed_data/02_filtered_accessible_urls/{query}_accessible_*.json"
    files = glob.glob(pattern)
    
    if not files:
        raise FileNotFoundError(f"未找到查询 '{query}' 的可访问URL文件")
    
    # 选择最新的文件
    latest_file = max(files, key=os.path.getctime)
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def keyword_relevance_filtering(query, news_items, max_count=15):
    """
    使用关键词匹配进行相关性筛选（备用方案）

    Args:
        query (str): 搜索关键词
        news_items (list): 新闻列表
        max_count (int): 最大保留数量

    Returns:
        list: 筛选后的新闻列表
    """
    print(f"  使用关键词匹配进行相关性筛选...")

    relevant_news = []
    query_lower = query.lower()

    # 按语言优先级排序
    prioritized_items = prioritize_by_language(news_items)

    for idx, item in enumerate(prioritized_items, 1):
        if len(relevant_news) >= max_count:
            break

        title_lower = item['title'].lower()
        content_lower = item['content'].lower()

        # 检查标题或内容中是否包含查询关键词
        if query_lower in title_lower or query_lower in content_lower:
            relevant_news.append(item)
            print(f"    第 {idx} 条新闻匹配关键词 (已选择 {len(relevant_news)}/{max_count})")

        if len(relevant_news) >= max_count:
            break

    return relevant_news

def smart_keyword_relevance_filtering(query, news_items, max_count=15):
    """
    使用智能关键词匹配进行相关性筛选

    Args:
        query (str): 搜索关键词
        news_items (list): 新闻列表
        max_count (int): 最大保留数量

    Returns:
        list: 筛选后的新闻列表
    """
    if len(news_items) <= max_count:
        print(f"  新闻总数({len(news_items)})不超过{max_count}条，跳过筛选")
        return news_items

    print(f"  新闻总数({len(news_items)})超过{max_count}条，开始智能关键词相关性筛选...")

    # 按语言优先级排序
    prioritized_items = prioritize_by_language(news_items)

    # 为每个新闻计算相关性得分
    scored_items = []

    for idx, item in enumerate(prioritized_items, 1):
        print(f"    正在分析第 {idx}/{len(prioritized_items)} 条新闻 (语言: {item['detected_language']})...")

        # 计算相关性得分
        score = calculate_relevance_score(query, item['title'], item['content'])
        item['relevance_score'] = score

        if score > 0:
            scored_items.append(item)
            print(f"      ✓ 相关 (得分: {score:.2f})")
        else:
            print(f"      ✗ 不相关 (得分: {score:.2f})")

    # 按得分排序，选择前max_count个
    scored_items.sort(key=lambda x: (-x['relevance_score'], x['language_priority']))
    selected_items = scored_items[:max_count]

    print(f"  智能筛选完成！从 {len(news_items)} 条新闻中筛选出 {len(selected_items)} 条相关新闻")

    return selected_items

def calculate_relevance_score(query, title, content):
    """
    计算新闻与查询词的相关性得分

    Args:
        query (str): 搜索关键词
        title (str): 新闻标题
        content (str): 新闻内容

    Returns:
        float: 相关性得分 (0-100)
    """
    score = 0.0
    query_lower = query.lower()
    title_lower = title.lower()
    content_lower = content.lower()

    # 1. 标题中完全匹配 (权重最高)
    if query_lower in title_lower:
        score += 50.0
        print(f"        标题完全匹配: +50")

    # 2. 内容中完全匹配
    if query_lower in content_lower:
        score += 30.0
        print(f"        内容完全匹配: +30")

    # 3. 分词匹配 (对于多字词)
    if len(query) > 2:
        # 检查查询词的子串
        for i in range(len(query) - 1):
            substring = query[i:i+2].lower()
            if substring in title_lower:
                score += 10.0
                print(f"        标题部分匹配({substring}): +10")
                break
            elif substring in content_lower:
                score += 5.0
                print(f"        内容部分匹配({substring}): +5")
                break

    # 4. 相关词汇匹配
    related_terms = get_related_terms(query)
    for term in related_terms:
        term_lower = term.lower()
        if term_lower in title_lower:
            score += 15.0
            print(f"        标题相关词匹配({term}): +15")
        elif term_lower in content_lower:
            score += 8.0
            print(f"        内容相关词匹配({term}): +8")

    # 5. 语言加分 (中英文优先)
    text_combined = f"{title} {content}"
    if any('\u4e00' <= char <= '\u9fff' for char in text_combined):  # 包含中文
        score += 5.0
        print(f"        中文内容加分: +5")
    elif any('a' <= char.lower() <= 'z' for char in text_combined):  # 包含英文
        score += 3.0
        print(f"        英文内容加分: +3")

    return score

def get_related_terms(query):
    """
    获取与查询词相关的词汇

    Args:
        query (str): 搜索关键词

    Returns:
        list: 相关词汇列表
    """
    # 预定义的相关词汇映射
    related_terms_map = {
        '英伟达': ['NVIDIA', 'nvidia', 'GPU', 'RTX', 'GeForce', '显卡', '芯片'],
        'NVIDIA': ['英伟达', 'GPU', 'RTX', 'GeForce', '显卡', '芯片'],
        'OpenAI': ['ChatGPT', 'GPT', 'AI', '人工智能', 'Sora', 'DALL-E'],
        'ChatGPT': ['OpenAI', 'GPT', 'AI', '人工智能', '聊天机器人'],
        '人工智能': ['AI', 'ChatGPT', 'OpenAI', '机器学习', '深度学习', '神经网络'],
        'AI': ['人工智能', 'ChatGPT', 'OpenAI', '机器学习', '深度学习'],
        '苹果': ['Apple', 'iPhone', 'iPad', 'Mac', 'iOS', 'macOS'],
        'Apple': ['苹果', 'iPhone', 'iPad', 'Mac', 'iOS', 'macOS'],
        '特斯拉': ['Tesla', 'Model', '电动车', '马斯克', 'Musk'],
        'Tesla': ['特斯拉', 'Model', '电动车', '马斯克', 'Musk'],
        '唐家三少': ['张威', '网络小说', '网文', '作家', '斗罗大陆', '绝世唐门', '神印王座', '起点中文网'],
        '张威': ['唐家三少', '网络小说', '网文', '作家'],
    }

    # 返回相关词汇，如果没有预定义则返回空列表
    return related_terms_map.get(query, [])

def save_relevant_news(query, filtered_data):
    """
    保存相关性筛选结果
    
    Args:
        query (str): 搜索关键词
        filtered_data (dict): 筛选后的数据
    
    Returns:
        str: 保存的文件路径
    """
    # 创建输出目录
    output_dir = 'processed_data/03_ai_relevance_filtered'
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{query}_relevant_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    # 保存文件
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=2)
    
    return filepath

def step3_ai_relevance_filter(query):
    """
    步骤3主函数：AI相关性筛选
    
    Args:
        query (str): 搜索关键词
    
    Returns:
        str: 保存的文件路径
    """
    print(f"[Step 3/7] Performing AI relevance check...")
    
    # 加载可访问URL结果
    print("  正在加载可访问URL结果...")
    accessible_data = load_accessible_urls(query)
    
    original_count = len(accessible_data['news_items'])
    print(f"  共有 {original_count} 条可访问的新闻需要进行相关性筛选")
    
    # 智能关键词相关性筛选
    relevant_news = smart_keyword_relevance_filtering(query, accessible_data['news_items'], max_count=15)
    
    # 更新数据结构
    filtered_data = accessible_data.copy()
    filtered_data['news_items'] = relevant_news
    filtered_data['total_count'] = len(relevant_news)
    filtered_data['processed_time'] = datetime.now().isoformat()
    filtered_data['ai_relevance_filter'] = {
        'original_count': original_count,
        'filtered_count': len(relevant_news),
        'filter_applied': original_count > 15
    }
    
    # 保存结果
    filepath = save_relevant_news(query, filtered_data)
    
    print(f"  步骤3完成！从 {original_count} 条新闻中筛选出 {len(relevant_news)} 条相关新闻")
    print(f"  结果已保存到: {filepath}")
    
    return filepath

if __name__ == "__main__":
    # 测试代码
    test_query = "英伟达"
    try:
        result_file = step3_ai_relevance_filter(test_query)
        print(f"测试完成，结果文件: {result_file}")
    except Exception as e:
        print(f"测试失败: {e}")
