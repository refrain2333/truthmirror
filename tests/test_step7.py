#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import glob
import os
from datetime import datetime

def test_step7():
    # 查找最新的分析结果文件
    pattern = "processed_data/06_ai_processed_data/*_analyzed_*.json"
    files = glob.glob(pattern)
    
    if not files:
        print("没有找到分析结果文件")
        return
    
    # 选择最新的文件
    latest_file = max(files, key=os.path.getctime)
    print(f"正在测试文件: {latest_file}")
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 提取成功的分析结果
        successful_analyses = []
        for item in data['news_items']:
            if item.get('analysis_success', False) and 'analyzed' in item:
                successful_analyses.append(item['analyzed'])
        
        # 拼接所有分析文本
        all_analyzed_texts = '\n\n'.join(successful_analyses)
        
        print(f"成功分析的新闻数量: {len(successful_analyses)}")
        print(f"所有分析文本总长度: {len(all_analyzed_texts)} 字符")
        
        # 测试新的15000字符限制
        max_length = 15000
        if len(all_analyzed_texts) > max_length:
            print(f"分析文本过长({len(all_analyzed_texts)}字符)，需要截断到{max_length}字符")
            truncated_text = all_analyzed_texts[:max_length] + "...\n\n[注：由于内容过长，部分分析已省略]"
            print(f"截断后长度: {len(truncated_text)} 字符")
        else:
            print(f"分析文本长度({len(all_analyzed_texts)}字符)在{max_length}字符限制内，无需截断")
            truncated_text = all_analyzed_texts
        
        # 显示前500字符作为预览
        print(f"\n文本预览（前500字符）:")
        print("-" * 50)
        print(truncated_text[:500])
        print("-" * 50)
        
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    test_step7()
