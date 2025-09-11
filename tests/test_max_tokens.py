#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_glm_max_tokens():
    """测试GLM API的max_tokens设置"""
    
    api_url = os.getenv('GLM_API_URL', 'https://open.bigmodel.cn/api/paas/v4/')
    api_key = os.getenv('GLM_API_KEY')
    model_id = os.getenv('GLM_MODEL_ID', 'glm-4.5-flash')
    
    if not api_key:
        print("GLM_API_KEY环境变量未设置")
        return
    
    # 测试用的长提示词，要求生成长回复
    test_prompt = """
请你作为资深新闻分析师，撰写一份关于"空洞骑士丝之歌"的综合性总结报告。

要求：
1. 概述该主题下的主要动态和核心观点
2. 分析发展趋势和未来展望  
3. 总结报告控制在400-600字
4. 使用专业、客观的语言
5. 包含完整的结构：主要动态、发展趋势、总结

请确保报告完整，不要截断。
"""
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # 测试不同的max_tokens值
    test_cases = [
        ("小值", 512),
        ("中值", 1024), 
        ("大值", 3000)
    ]
    
    for name, max_tokens in test_cases:
        print(f"\n=== 测试 {name} (max_tokens={max_tokens}) ===")
        
        data = {
            'model': model_id,
            'messages': [
                {
                    'role': 'user',
                    'content': test_prompt
                }
            ],
            'temperature': 0.8,
            'max_tokens': max_tokens
        }
        
        try:
            response = requests.post(
                f"{api_url.rstrip('/')}/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    print(f"✓ 成功生成内容")
                    print(f"  长度: {len(content)} 字符")
                    print(f"  是否完整: {'是' if content.endswith('。') or '总结' in content[-100:] else '可能被截断'}")
                    print(f"  预览: {content[:200]}...")
                    if len(content) > 200:
                        print(f"  结尾: ...{content[-100:]}")
                else:
                    print("✗ API响应格式异常")
            else:
                print(f"✗ API请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"✗ 请求出错: {e}")

if __name__ == "__main__":
    test_glm_max_tokens()
