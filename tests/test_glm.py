#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv
import requests

load_dotenv()

api_url = os.getenv('GLM_API_URL', 'https://open.bigmodel.cn/api/paas/v4/')
api_key = os.getenv('GLM_API_KEY')

print(f'API URL: {api_url}')
print(f'API Key: {api_key[:10]}...')

full_url = api_url.rstrip('/') + '/chat/completions'
print(f'Full URL: {full_url}')

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

data = {
    'model': 'glm-4.5-flash',
    'messages': [
        {
            'role': 'user',
            'content': '测试消息，请回复"测试成功"'
        }
    ],
    'temperature': 0.7,
    'max_tokens': 100
}

try:
    response = requests.post(full_url, headers=headers, json=data, timeout=30)
    print(f'Status: {response.status_code}')
    print(f'Response: {response.text}')
    
    if response.status_code == 200:
        result = response.json()
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content']
            print(f'GLM回复: {content}')
        else:
            print('响应格式异常')
    else:
        print('请求失败')
        
except Exception as e:
    print(f'Error: {e}')
