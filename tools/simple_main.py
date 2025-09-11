#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能新闻分析系统 - 简化版主程序
仅使用Python标准库的基本版本
"""

import sys
import os
import json
import urllib.request
import urllib.parse
import urllib.error
import time
from datetime import datetime

def print_banner():
    """打印程序横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    智能新闻分析系统                          ║
║                 Intelligent News Analysis System             ║
║                                                              ║
║  自动化七步流程：新闻获取 → 筛选 → 分析 → 汇总报告          ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def fetch_news_simple(query, page=1):
    """
    使用标准库获取新闻数据
    """
    api_url = "http://115.120.215.107:8888/search"
    
    params = {
        'q': query,
        'categories': 'news',
        'format': 'json',
        'pageno': page
    }
    
    # 构建URL
    url = f"{api_url}?{urllib.parse.urlencode(params)}"
    
    try:
        print(f"  正在获取第 {page} 页数据...")
        
        # 设置请求头
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        # 发送请求
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read().decode('utf-8')
            return json.loads(data)
            
    except urllib.error.URLError as e:
        print(f"  获取第 {page} 页数据失败: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"  解析第 {page} 页数据失败: {e}")
        return None
    except Exception as e:
        print(f"  获取第 {page} 页数据时发生错误: {e}")
        return None

def check_url_simple(url):
    """
    简单检查URL可访问性
    """
    try:
        req = urllib.request.Request(url, method='HEAD')
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            return 200 <= response.status < 400
    except:
        return False

def simple_analysis_pipeline(query):
    """
    简化的分析流程
    """
    print(f"\n🔍 开始分析主题: '{query}'")
    print(f"🕐 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 步骤1: 获取新闻数据
    print("\n" + "="*60)
    print("[Step 1/3] 获取新闻数据...")
    
    all_news = []
    for page in range(1, 4):  # 获取3页数据
        result = fetch_news_simple(query, page)
        if result and 'results' in result:
            all_news.extend(result['results'])
        time.sleep(1)  # 避免请求过快
    
    if not all_news:
        print("❌ 无法获取新闻数据")
        return
    
    print(f"✅ 成功获取 {len(all_news)} 条新闻")
    
    # 步骤2: 简单筛选
    print("\n" + "="*60)
    print("[Step 2/3] 筛选有效新闻...")
    
    valid_news = []
    for idx, news in enumerate(all_news[:20], 1):  # 只处理前20条
        if news.get('title') and news.get('url'):
            print(f"  检查第 {idx} 条新闻...")
            if check_url_simple(news['url']):
                valid_news.append({
                    'id': len(valid_news) + 1,
                    'title': news['title'],
                    'url': news['url'],
                    'content': news.get('content', ''),
                    'engine': news.get('engine', '')
                })
                print(f"    ✅ 有效")
            else:
                print(f"    ❌ 无法访问")
        
        if len(valid_news) >= 10:  # 最多保留10条
            break
    
    print(f"✅ 筛选出 {len(valid_news)} 条有效新闻")
    
    # 步骤3: 保存结果
    print("\n" + "="*60)
    print("[Step 3/3] 保存分析结果...")
    
    # 创建输出目录
    os.makedirs('processed_data/simple_results', exist_ok=True)
    
    # 生成报告
    report = {
        'query': query,
        'generated_time': datetime.now().isoformat(),
        'total_news_found': len(all_news),
        'valid_news_count': len(valid_news),
        'news_items': valid_news,
        'summary': f"关于'{query}'的新闻分析：共找到{len(all_news)}条相关新闻，其中{len(valid_news)}条可以正常访问。"
    }
    
    # 保存文件
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"processed_data/simple_results/{query}_simple_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 结果已保存到: {filename}")
    
    # 显示摘要
    print("\n" + "="*60)
    print("📊 分析完成！")
    print("="*60)
    print(f"📝 主题: {query}")
    print(f"📅 时间: {report['generated_time']}")
    print(f"📈 统计:")
    print(f"   • 总新闻数: {report['total_news_found']}")
    print(f"   • 有效新闻: {report['valid_news_count']}")
    print(f"\n📄 新闻列表:")
    for news in valid_news:
        print(f"   {news['id']}. {news['title'][:60]}{'...' if len(news['title']) > 60 else ''}")
    
    print(f"\n💾 完整报告: {filename}")

def main():
    """主函数"""
    print_banner()
    
    # 获取用户输入
    if len(sys.argv) > 1:
        query = sys.argv[1]
    else:
        query = input("\n请输入搜索关键词: ").strip()
    
    if not query:
        print("❌ 搜索关键词不能为空")
        sys.exit(1)
    
    try:
        # 运行简化的分析流程
        simple_analysis_pipeline(query)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断了程序执行")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 程序执行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
