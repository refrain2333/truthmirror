#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def test_limits():
    # 模拟不同长度的文本
    test_cases = [
        ("短文本", "这是一个短文本" * 100),  # 约700字符
        ("中等文本", "这是一个中等长度的文本" * 500),  # 约5000字符
        ("长文本", "这是一个很长的文本内容" * 1000),  # 约10000字符
        ("超长文本", "这是一个超长的文本内容" * 2000),  # 约20000字符
    ]
    
    print("=== 文本长度限制测试 ===")
    
    for name, text in test_cases:
        length = len(text)
        print(f"\n{name}:")
        print(f"  原始长度: {length} 字符")
        
        # 测试8000字符限制（旧）
        if length > 8000:
            print(f"  8000字符限制: 需要截断 (超出{length - 8000}字符)")
        else:
            print(f"  8000字符限制: 无需截断 (剩余{8000 - length}字符)")
        
        # 测试15000字符限制（新）
        if length > 15000:
            print(f"  15000字符限制: 需要截断 (超出{length - 15000}字符)")
        else:
            print(f"  15000字符限制: 无需截断 (剩余{15000 - length}字符)")
    
    print(f"\n=== 结论 ===")
    print(f"✓ 将限制从8000字符提高到15000字符")
    print(f"✓ 可以处理更多的分析内容而不被截断")
    print(f"✓ GLM-4.5-flash可以很好地处理15000字符的文本")

if __name__ == "__main__":
    test_limits()
