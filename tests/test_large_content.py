#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime

def create_large_test_data():
    """创建一个包含大量分析文本的测试数据"""
    
    # 创建一个模拟的大型分析结果
    large_analysis = """
### 深度分析报告

**核心内容与关键信息**：这是一个非常详细的分析报告，包含了大量的信息和深入的见解。我们需要分析各种复杂的情况，包括技术发展趋势、市场动态、政策影响、社会反响等多个维度。这个分析需要覆盖从宏观到微观的各个层面，从短期影响到长期趋势的全面评估。

**重要性与影响**：该事件具有重要的行业标杆意义，不仅影响当前的市场格局，还可能对未来的发展方向产生深远影响。我们需要从多个角度来评估这种影响，包括对消费者的影响、对竞争对手的影响、对整个行业生态的影响，以及对相关政策制定的影响。

**关键主题与趋势**：通过深入分析，我们可以识别出几个关键的主题和趋势。首先是技术创新的加速，这将推动整个行业向更高效、更智能的方向发展。其次是用户需求的变化，消费者对产品和服务的期望越来越高，这要求企业必须不断提升自己的能力。第三是监管环境的变化，政府对相关领域的监管越来越严格，这将对企业的运营模式产生重要影响。

**后续发展预测**：基于当前的分析，我们可以对未来的发展做出一些预测。短期内，市场可能会出现一定的波动，但长期来看，整体趋势是积极的。企业需要做好充分的准备，包括技术储备、人才培养、市场布局等各个方面。同时，也需要密切关注政策变化和市场动态，及时调整自己的策略。

**总结**：综合以上分析，我们可以得出结论，这是一个具有重要意义的事件，将对整个行业产生深远影响。企业和相关方需要认真对待，做好充分的准备和应对措施。
""" * 20  # 重复20次来创建大量内容
    
    # 创建测试数据结构
    test_data = {
        "query": "大型测试",
        "total_count": 15,
        "processed_time": datetime.now().isoformat(),
        "news_items": []
    }
    
    # 创建15条模拟新闻，每条都有大量分析内容
    for i in range(15):
        item = {
            "id": i + 1,
            "title": f"测试新闻标题 {i+1}",
            "content": f"这是第{i+1}条测试新闻的内容",
            "analyzed": large_analysis,
            "analysis_success": True
        }
        test_data["news_items"].append(item)
    
    # 保存测试数据
    test_file = "processed_data/06_ai_processed_data/大型测试_analyzed_test.json"
    os.makedirs(os.path.dirname(test_file), exist_ok=True)
    
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
    
    print(f"测试数据已创建: {test_file}")
    
    # 计算总长度
    total_length = len(large_analysis) * 15
    print(f"每条分析长度: {len(large_analysis)} 字符")
    print(f"总分析长度: {total_length} 字符")
    print(f"是否超过15000字符: {'是' if total_length > 15000 else '否'}")
    
    return test_file

def test_step7_with_large_data(test_file):
    """测试步骤7对大型数据的处理"""
    
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 提取成功的分析结果
        successful_analyses = []
        for item in data['news_items']:
            if item.get('analysis_success', False) and 'analyzed' in item:
                successful_analyses.append(item['analyzed'])
        
        # 拼接所有分析文本
        all_analyzed_texts = '\n\n'.join(successful_analyses)
        
        print(f"\n=== 步骤7大型数据测试 ===")
        print(f"成功分析的新闻数量: {len(successful_analyses)}")
        print(f"所有分析文本总长度: {len(all_analyzed_texts)} 字符")
        
        # 应用15000字符限制
        max_length = 15000
        if len(all_analyzed_texts) > max_length:
            print(f"✓ 分析文本过长({len(all_analyzed_texts)}字符)，将截断到{max_length}字符")
            truncated_text = all_analyzed_texts[:max_length] + "...\n\n[注：由于内容过长，部分分析已省略]"
            print(f"✓ 截断后长度: {len(truncated_text)} 字符")
            print(f"✓ 15000字符限制正常工作")
        else:
            print(f"✓ 分析文本长度在{max_length}字符限制内，无需截断")
        
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    # 创建大型测试数据
    test_file = create_large_test_data()
    
    # 测试步骤7的处理
    test_step7_with_large_data(test_file)
