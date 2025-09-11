#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能新闻分析系统 - 主程序
自动化七步流程：从新闻获取到深度分析的完整链路
"""

import sys
import os
import json
import traceback
from datetime import datetime
from dotenv import load_dotenv

# 导入各个步骤的模块
from src.step1_fetch_news import step1_fetch_and_clean_news
from src.step2_filter_accessible import run_step2
from src.step3_ai_relevance_filter import step3_ai_relevance_filter
from src.step4_fetch_html import step4_fetch_html_pages
from src.step5_extract_content import step5_extract_article_content
from src.step6_ai_analysis import step6_ai_analysis
from src.step7_final_summary import step7_generate_final_summary

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

def print_step_separator():
    """打印步骤分隔符"""
    print("\n" + "="*60 + "\n")

def validate_environment():
    """验证环境变量配置"""
    print("正在验证环境配置...")
    
    required_vars = [
        'GLM_API_KEY',
        'GEMINI_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ 缺少必要的环境变量: {', '.join(missing_vars)}")
        print("请检查 .env 文件或设置相应的环境变量")
        return False
    
    print("✅ 环境配置验证通过")
    return True

def display_final_results(query, final_report_file):
    """显示最终结果"""
    print_step_separator()
    print("🎉 智能新闻分析完成！")
    print_step_separator()
    
    try:
        with open(final_report_file, 'r', encoding='utf-8') as f:
            final_report = json.load(f)
        
        print(f"📊 分析主题: {query}")
        print(f"📅 完成时间: {final_report['generated_time']}")
        print(f"📈 工作流统计:")

        if 'workflow_summary' in final_report:
            workflow = final_report['workflow_summary']
            print(f"   • 原始新闻获取: {workflow['step1_raw_news']} 条")
            print(f"   • 连通性筛选: {workflow['step2_accessible']} 条")
            print(f"   • 相关性筛选: {workflow['step3_relevant']} 条")
            print(f"   • 内容提取成功: {workflow['step5_content_extracted']} 条")
            print(f"   • AI分析成功: {workflow['step6_analyzed']} 条")
        else:
            print(f"   • 总新闻数: {final_report.get('total_news_analyzed', 0)} 条")
            print(f"   • 分析类型: {final_report.get('analysis_type', 'unknown')}")
        
        print(f"\n📝 最终汇总报告:")
        print("-" * 50)
        print(final_report['final_summary'])
        print("-" * 50)
        
        print(f"\n💾 完整报告已保存到: {final_report_file}")
        
    except Exception as e:
        print(f"❌ 读取最终报告时出错: {e}")

def run_news_analysis_pipeline(query):
    """
    运行完整的新闻分析流程
    
    Args:
        query (str): 搜索关键词
    
    Returns:
        str: 最终报告文件路径
    """
    start_time = datetime.now()
    
    try:
        # 步骤1: 获取新闻列表与预清理
        print_step_separator()
        step1_result = step1_fetch_and_clean_news(query)
        
        # 步骤2: 连通性筛选
        print_step_separator()
        step2_result = run_step2(query)
        
        # 步骤3: AI相关性筛选
        print_step_separator()
        step3_result = step3_ai_relevance_filter(query)
        
        # 步骤4: 获取原始HTML
        print_step_separator()
        step4_result = step4_fetch_html_pages(query)
        
        # 步骤5: 提取正文
        print_step_separator()
        step5_result = step5_extract_article_content(query)
        
        # 步骤6: AI深度分析
        print_step_separator()
        step6_result = step6_ai_analysis(query)
        
        # 步骤7: 生成最终汇总报告
        print_step_separator()
        step7_result = step7_generate_final_summary(query)
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print_step_separator()
        print(f"✅ 所有步骤执行完成！")
        print(f"⏱️  总耗时: {duration}")
        
        return step7_result
        
    except Exception as e:
        print(f"\n❌ 执行过程中发生错误: {e}")
        print(f"📍 错误详情:")
        traceback.print_exc()
        raise

def main():
    """主函数"""
    print_banner()
    
    # 加载环境变量
    load_dotenv()
    
    # 验证环境配置
    if not validate_environment():
        sys.exit(1)
    
    # 获取用户输入
    if len(sys.argv) > 1:
        query = sys.argv[1]
    else:
        query = input("\n请输入搜索关键词: ").strip()
    
    if not query:
        print("❌ 搜索关键词不能为空")
        sys.exit(1)
    
    print(f"\n🔍 开始分析主题: '{query}'")
    print(f"🕐 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 运行完整的分析流程
        final_report_file = run_news_analysis_pipeline(query)
        
        # 显示最终结果
        display_final_results(query, final_report_file)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断了程序执行")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 程序执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
