#!/usr/bin/env python3
"""
测试 Groq API 连接的诊断脚本
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import Config
import requests

print("=" * 70)
print("Groq API 诊断测试")
print("=" * 70)
print()

# 检查 API key
if not Config.GROQ_API_KEY:
    print("❌ GROQ_API_KEY 未设置")
    print("   请在 .env 文件中设置 GROQ_API_KEY")
    sys.exit(1)

print(f"✓ API Key 已配置: {Config.GROQ_API_KEY[:20]}...")
print(f"✓ API Base URL: {Config.GROQ_API_BASE}")
print(f"✓ Model: {Config.GROQ_MODEL}")
print()

# 测试简单的 API 调用
print("测试 Groq API 连接...")
headers = {
    "Authorization": f"Bearer {Config.GROQ_API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": Config.GROQ_MODEL,
    "messages": [
        {"role": "user", "content": "Say 'hello' in JSON format: {\"message\": \"hello\"}"}
    ],
    "temperature": 0.1
}

try:
    response = requests.post(
        f"{Config.GROQ_API_BASE}/chat/completions",
        headers=headers,
        json=payload,
        timeout=30
    )
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ 请求失败")
        print(f"响应: {response.text[:500]}")
        sys.exit(1)
    
    result = response.json()
    content = result["choices"][0]["message"]["content"]
    
    print("✓ API 调用成功！")
    print(f"响应内容: {content}")
    print()
    print("=" * 70)
    print("✅ Groq API 工作正常")
    print("=" * 70)
    
except requests.exceptions.RequestException as e:
    print(f"❌ 网络错误: {e}")
    sys.exit(1)
except KeyError as e:
    print(f"❌ 响应格式错误: {e}")
    print(f"完整响应: {response.text}")
    sys.exit(1)
except Exception as e:
    print(f"❌ 未知错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

