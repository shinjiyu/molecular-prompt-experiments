"""
Long CoT 分子结构提示词工程对比实验 - 多 API 测试

尝试多个 API Key 找到可用的
"""

import requests
import time

# 测试所有可用的 API
APIS = [
    {
        "name": "DeepSeek-1",
        "url": "https://api.deepseek.com/chat/completions",
        "key": "sk-0dad5c34545a4012ab263f1af62ef316",
        "model": "deepseek-chat"
    },
    {
        "name": "DeepSeek-2",
        "url": "https://api.deepseek.com/chat/completions",
        "key": "sk-2c07601a8cb94749b9db3eb6a87b4b38",
        "model": "deepseek-chat"
    },
    {
        "name": "DeepSeek-3",
        "url": "https://api.deepseek.com/chat/completions",
        "key": "sk-455b94f75f054a78ab274679956f530f",
        "model": "deepseek-chat"
    },
]

def test_api(api):
    """测试 API 是否可用"""
    headers = {
        "Authorization": f"Bearer {api['key']}",
        "Content-Type": "application/json",
    }
    
    data = {
        "model": api['model'],
        "messages": [{"role": "user", "content": "Hello, just say 'OK'"}],
        "max_tokens": 10,
    }
    
    try:
        response = requests.post(api['url'], headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "response": result['choices'][0]['message']['content'][:50]
            }
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            return {
                "success": False,
                "error": str(error_data)[:100]
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)[:100]
        }

print("="*60)
print("测试所有可用的 API")
print("="*60)

available_apis = []

for api in APIS:
    print(f"\n测试 {api['name']}...")
    result = test_api(api)
    
    if result['success']:
        print(f"  ✓ 可用！响应: {result['response']}")
        available_apis.append(api)
    else:
        print(f"  ✗ 不可用: {result['error']}")

print("\n" + "="*60)
print(f"可用的 API 数量: {len(available_apis)}")
if available_apis:
    print("可用的 API:")
    for api in available_apis:
        print(f"  - {api['name']}: {api['key'][:20]}...")
else:
    print("没有可用的 API！")
print("="*60)
