#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import glob
import os

def test_text_length():
    # 查找最新的分析结果文件
    pattern = "processed_data/06_ai_processed_data/*_analyzed_*.json"
    files = glob.glob(pattern)
    
    if not files:
        print("没有找到分析结果文件")
        return
    
    # 选择最新的文件
    latest_file = max(files, key=os.path.getctime)
    print(f"正在分析文件: {latest_file}")
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        total_length = 0
        successful_analyses = []
        
        for item in data['news_items']:
            if item.get('analysis_success', False) and 'analyzed' in item:
                analysis_text = item['analyzed']
                successful_analyses.append(analysis_text)
                total_length += len(analysis_text)
        
        print(f'成功分析的新闻数量: {len(successful_analyses)}')
        print(f'所有分析文本总长度: {total_length} 字符')
        if successful_analyses:
            print(f'平均每条分析长度: {total_length // len(successful_analyses)} 字符')
        
        # 测试不同的限制
        limits = [8000, 15000, 20000]
        for limit in limits:
            if total_length > limit:
                print(f'超过{limit}字符限制: 是 (超出{total_length - limit}字符)')
            else:
                print(f'超过{limit}字符限制: 否 (剩余{limit - total_length}字符)')
        
        # 显示前几条分析的长度
        print("\n各条分析的长度:")
        for i, analysis in enumerate(successful_analyses[:5], 1):
            print(f'  第{i}条: {len(analysis)} 字符')
        
        if len(successful_analyses) > 5:
            print(f'  ... 还有{len(successful_analyses) - 5}条')
            
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    test_text_length()
