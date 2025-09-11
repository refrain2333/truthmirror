#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv
import requests

load_dotenv()

def test_glm_relevance():
    api_url = os.getenv('GLM_API_URL', 'https://open.bigmodel.cn/api/paas/v4/')
    api_key = os.getenv('GLM_API_KEY')
    model_id = os.getenv('GLM_MODEL_ID', 'glm-4.5-flash')
    
    print(f'API URL: {api_url}')
    print(f'API Key: {api_key[:10]}...')
    print(f'Model: {model_id}')
    
    # 测试用例1：明显相关的新闻
    test_cases = [
        {
            "query": "英伟达",
            "title": "英伟达发布新一代GPU芯片",
            "content": "英伟达公司今日宣布推出最新的RTX 4090 GPU芯片，性能比上一代提升50%。",
            "expected": "相关"
        },
        {
            "query": "OpenAI", 
            "title": "OpenAI推出ChatGPT-5模型",
            "content": "OpenAI公司发布了最新的ChatGPT-5大语言模型，在多项基准测试中表现优异。",
            "expected": "相关"
        },
        {
            "query": "苹果",
            "title": "今日天气预报",
            "content": "明天将有小雨，气温15-20度，请注意保暖。",
            "expected": "不相关"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n=== 测试用例 {i} ===")
        print(f"查询词: {case['query']}")
        print(f"标题: {case['title']}")
        print(f"内容: {case['content']}")
        print(f"期望结果: {case['expected']}")
        
        # 构建提示词
        prompt_template = os.getenv('GLM_RELEVANCE_PROMPT', 
            "判断以下新闻是否与'{query}'相关？\n\n新闻标题：{title}\n\n新闻内容：{content}\n\n请只回答'相关'或'不相关'。")
        
        full_prompt = prompt_template.format(
            query=case['query'],
            title=case['title'],
            content=case['content']
        )
        
        print(f"完整提示词:\n{full_prompt}")
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': model_id,
            'messages': [
                {
                    'role': 'user',
                    'content': full_prompt
                }
            ],
            'temperature': 0.1,
            'max_tokens': 50
        }
        
        try:
            full_url = f"{api_url.rstrip('/')}/chat/completions"
            response = requests.post(full_url, headers=headers, json=data, timeout=30)
            print(f"HTTP状态: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    answer = result['choices'][0]['message']['content'].strip()
                    print(f"GLM回复: '{answer}'")
                    
                    # 判断是否相关
                    answer_lower = answer.lower()
                    is_relevant = ('相关' in answer or 'yes' in answer_lower or 
                                 'relevant' in answer_lower or '是' in answer or
                                 'related' in answer_lower)
                    
                    result_text = "相关" if is_relevant else "不相关"
                    print(f"判断结果: {result_text}")
                    print(f"是否正确: {'✓' if result_text == case['expected'] else '✗'}")
                else:
                    print("API响应格式异常")
            else:
                print(f"API请求失败: {response.text}")
                
        except Exception as e:
            print(f"请求出错: {e}")

if __name__ == "__main__":
    test_glm_relevance()
