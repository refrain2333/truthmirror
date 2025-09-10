import requests
import json

# 测试用户更新API
url = "http://127.0.0.1:8000/api/v1/users/1"
data = {
    "nickname": "测试昵称",
    "bio": "测试简介"
}

try:
    response = requests.put(url, json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    if response.status_code == 200:
        print("✅ 更新成功")
        result = response.json()
        print(f"更新后的用户信息: {json.dumps(result, indent=2, ensure_ascii=False)}")
    else:
        print("❌ 更新失败")
        
except Exception as e:
    print(f"请求错误: {e}")
