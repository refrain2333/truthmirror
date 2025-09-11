#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

def test_glm():
    api_url = 'https://open.bigmodel.cn/api/paas/v4/chat/completions'
    api_key = 'ee48c93917ad49b98cb16179e345bf20.qc8IVIZmcOVd6hfu'
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # 简单测试
    data = {
        'model': 'glm-4.5-flash',
        'messages': [
            {
                'role': 'user',
                'content': '请判断新闻"英伟达发布新GPU"是否与"英伟达"相关？只回答相关或不相关。'
            }
        ],
        'temperature': 0.1,
        'max_tokens': 50
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=data, timeout=30)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                answer = result['choices'][0]['message']['content'].strip()
                print(f"GLM回复: '{answer}'")
            else:
                print("响应格式异常")
        
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    test_glm()
