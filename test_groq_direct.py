#!/usr/bin/env python3
"""
直接测试 Groq API 调用
"""
import os
import requests
import json

# 从环境变量读取
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("❌ 请先设置环境变量: export GROQ_API_KEY='your_key'")
    exit(1)

print(f"✓ API Key: {GROQ_API_KEY[:30]}...")
print()

# 测试 1: 简单的聊天补全
print("=" * 70)
print("测试 1: 标准聊天补全")
print("=" * 70)

headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": "llama-3.1-70b-versatile",
    "messages": [
        {"role": "user", "content": "Say hello in one word"}
    ],
    "temperature": 0.1
}

print(f"请求 URL: https://api.groq.com/openai/v1/chat/completions")
print(f"请求体: {json.dumps(payload, indent=2)}")
print()

response = requests.post(
    "https://api.groq.com/openai/v1/chat/completions",
    headers=headers,
    json=payload,
    timeout=30
)

print(f"状态码: {response.status_code}")
print(f"响应头: {dict(response.headers)}")
print()

if response.status_code == 200:
    result = response.json()
    print("✓ 成功!")
    print(f"响应: {json.dumps(result, indent=2)}")
    content = result["choices"][0]["message"]["content"]
    print(f"\n内容: {content}")
else:
    print("❌ 失败!")
    print(f"错误响应: {response.text}")

print()
print("=" * 70)
print("测试 2: JSON 格式输出")
print("=" * 70)

payload2 = {
    "model": "llama-3.1-70b-versatile",
    "messages": [
        {
            "role": "system",
            "content": "You output only valid JSON. Output format: {\"capabilities\": [\"tag1\", \"tag2\"]}"
        },
        {
            "role": "user", 
            "content": "Extract capabilities from: 'I want to read GitHub issues and search the web'"
        }
    ],
    "temperature": 0.1
}

print(f"请求体: {json.dumps(payload2, indent=2)}")
print()

response2 = requests.post(
    "https://api.groq.com/openai/v1/chat/completions",
    headers=headers,
    json=payload2,
    timeout=30
)

print(f"状态码: {response2.status_code}")

if response2.status_code == 200:
    result2 = response2.json()
    print("✓ 成功!")
    content2 = result2["choices"][0]["message"]["content"]
    print(f"内容: {content2}")
    
    # 尝试解析 JSON
    try:
        # 可能包含在 markdown 代码块中
        if "```json" in content2:
            json_str = content2.split("```json")[1].split("```")[0].strip()
        elif "```" in content2:
            json_str = content2.split("```")[1].split("```")[0].strip()
        else:
            json_str = content2.strip()
        
        parsed = json.loads(json_str)
        print(f"✓ JSON 解析成功: {parsed}")
    except Exception as e:
        print(f"⚠️  JSON 解析失败: {e}")
else:
    print("❌ 失败!")
    print(f"错误响应: {response2.text}")

