#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统测试脚本
"""

import sys
import os

def test_imports():
    """测试所有模块导入"""
    print("测试模块导入...")
    
    try:
        import requests
        print("✅ requests 导入成功")
    except ImportError as e:
        print(f"❌ requests 导入失败: {e}")
        return False
    
    try:
        import aiohttp
        print("✅ aiohttp 导入成功")
    except ImportError as e:
        print(f"❌ aiohttp 导入失败: {e}")
        return False
    
    try:
        from bs4 import BeautifulSoup
        print("✅ BeautifulSoup 导入成功")
    except ImportError as e:
        print(f"❌ BeautifulSoup 导入失败: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv 导入成功")
    except ImportError as e:
        print(f"❌ python-dotenv 导入失败: {e}")
        return False
    
    return True

def test_step_imports():
    """测试步骤模块导入"""
    print("\n测试步骤模块导入...")
    
    steps = [
        'step1_fetch_news',
        'step2_filter_accessible', 
        'step3_ai_relevance_filter',
        'step4_fetch_html',
        'step5_extract_content',
        'step6_ai_analysis',
        'step7_final_summary'
    ]
    
    for step in steps:
        try:
            __import__(step)
            print(f"✅ {step} 导入成功")
        except ImportError as e:
            print(f"❌ {step} 导入失败: {e}")
            return False
        except Exception as e:
            print(f"❌ {step} 导入时发生错误: {e}")
            return False
    
    return True

def test_environment():
    """测试环境变量"""
    print("\n测试环境变量...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        'GLM_API_KEY',
        'GEMINI_API_KEY',
        'SEARXNG_API_URL'
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: 已设置")
        else:
            print(f"❌ {var}: 未设置")
            return False
    
    return True

def test_directories():
    """测试目录结构"""
    print("\n测试目录结构...")
    
    required_dirs = [
        'processed_data',
        'processed_data/01_raw_search_results',
        'processed_data/02_filtered_accessible_urls',
        'processed_data/03_ai_relevance_filtered',
        'processed_data/04_raw_html_pages',
        'processed_data/05_extracted_article_content',
        'processed_data/06_ai_processed_data',
        'processed_data/07_final_summary_reports'
    ]
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            print(f"✅ {dir_path}: 存在")
        else:
            print(f"❌ {dir_path}: 不存在")
            return False
    
    return True

def main():
    """主测试函数"""
    print("=" * 50)
    print("智能新闻分析系统 - 系统测试")
    print("=" * 50)
    
    all_passed = True
    
    # 测试基础依赖导入
    if not test_imports():
        all_passed = False
    
    # 测试步骤模块导入
    if not test_step_imports():
        all_passed = False
    
    # 测试环境变量
    if not test_environment():
        all_passed = False
    
    # 测试目录结构
    if not test_directories():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有测试通过！系统准备就绪。")
        print("可以运行: python main.py \"英伟达\"")
    else:
        print("❌ 部分测试失败，请检查上述错误。")
    print("=" * 50)

if __name__ == "__main__":
    main()
