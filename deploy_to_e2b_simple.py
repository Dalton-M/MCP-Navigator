#!/usr/bin/env python3
"""
简化版 E2B 部署脚本
使用 run_code() 方法上传文件
"""
import os
import time
import base64
from e2b_code_interpreter import Sandbox

E2B_API_KEY = os.getenv("E2B_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

def read_and_encode_file(filepath):
    """读取文件并 base64 编码"""
    with open(filepath, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def deploy_api_server():
    """部署 API Server 到 E2B"""
    
    print("🚀 Creating E2B Sandbox...")
    sandbox = Sandbox.create()
    
    print(f"✅ Sandbox created: {sandbox.sandbox_id}")
    print(f"🌐 Sandbox URL: https://{sandbox.sandbox_id}.e2b.dev\n")
    
    # 方法 1: 通过 run_code 创建文件
    print("📦 Uploading project files via code execution...")
    
    files_content = {}
    files_to_upload = [
        "api_server.py",
        "requirements.txt",
        "app/config.py",
        "app/planner.py",
        "app/matcher.py",
        "app/snippet_generator.py",
        "app/mcp_client.py",
        "app/__init__.py",
        "data/mcp_catalog.json",
    ]
    
    # 读取所有文件
    for filepath in files_to_upload:
        if os.path.exists(filepath):
            files_content[filepath] = read_and_encode_file(filepath)
            print(f"  ✓ Read {filepath}")
    
    # 创建上传脚本
    upload_code = """
import os
import base64

files = {}
"""
    
    # 添加文件内容
    for filepath, content in files_content.items():
        upload_code += f'\nfiles["{filepath}"] = "{content}"'
    
    # 添加解码和写入逻辑
    upload_code += """

# 创建目录和写入文件
for filepath, content in files.items():
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    
    # 解码并写入
    with open(filepath, 'wb') as f:
        f.write(base64.b64decode(content))
    print(f"✓ Wrote {filepath}")

print("\\n✅ All files uploaded")
"""
    
    print("\n📤 Executing upload...")
    result = sandbox.run_code(upload_code, timeout=120)
    print(result.text)
    
    # 安装依赖
    print("\n📚 Installing dependencies...")
    install_code = """
import subprocess
import sys

print("Installing packages from requirements.txt...")
result = subprocess.run(
    [sys.executable, '-m', 'pip', 'install', '-q', '-r', 'requirements.txt'],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("✅ Dependencies installed")
else:
    print(f"❌ Error: {result.stderr}")
"""
    
    result = sandbox.run_code(install_code, timeout=180)
    print(result.text)
    
    # 启动 API Server
    print("\n🚀 Starting API Server...")
    
    start_code = f"""
import os
import subprocess
import sys

# 设置环境变量
os.environ['GROQ_API_KEY'] = '{GROQ_API_KEY}'
os.environ['GITHUB_TOKEN'] = '{GITHUB_TOKEN}'

# 启动 API Server（后台）
with open('start_api.sh', 'w') as f:
    f.write('#!/bin/bash\\nnohup python api_server.py > api.log 2>&1 &\\necho $! > api.pid')

subprocess.run(['chmod', '+x', 'start_api.sh'])
result = subprocess.run(['./start_api.sh'], capture_output=True, text=True)

print("✅ API Server starting...")
print("📝 Logs will be in api.log")

# 等待启动
import time
time.sleep(5)

# 读取 PID
try:
    with open('api.pid', 'r') as f:
        pid = f.read().strip()
    print(f"📋 API Server PID: {{pid}}")
except:
    print("⚠️  Could not read PID file")
"""
    
    result = sandbox.run_code(start_code, timeout=30)
    print(result.text)
    
    # 测试 API
    print("\n🧪 Testing API (waiting 10s for startup)...")
    time.sleep(10)
    
    test_code = """
import requests
import time

for i in range(10):
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print(f"✅ API is healthy!")
            print(f"Response: {response.json()}")
            break
        else:
            print(f"Status: {response.status_code}")
    except Exception as e:
        print(f"⏳ Attempt {i+1}/10: {str(e)[:50]}")
        time.sleep(3)
else:
    print("⚠️  API not responding. Check logs:")
    try:
        with open('api.log', 'r') as f:
            print(f.read()[-1000:])
    except:
        print("Could not read api.log")
"""
    
    result = sandbox.run_code(test_code, timeout=60)
    print(result.text)
    
    print("\n" + "="*70)
    print("🎉 Deployment Complete!")
    print("="*70)
    print(f"\n📋 Sandbox ID: {sandbox.sandbox_id}")
    print(f"\n💡 To connect to sandbox:")
    print(f"   e2b sandbox connect {sandbox.sandbox_id}")
    print(f"\n💡 Inside sandbox, test API:")
    print(f"   curl http://localhost:8000/health")
    print(f"   curl http://localhost:8000/docs")
    print(f"\n⚠️  Note: API runs on localhost:8000 inside sandbox")
    print(f"   For external access, you need port forwarding or E2B network features")
    
    return sandbox


if __name__ == "__main__":
    if not E2B_API_KEY:
        print("❌ E2B_API_KEY not set")
        exit(1)
    
    if not GROQ_API_KEY:
        print("❌ GROQ_API_KEY not set")
        exit(1)
    
    print(f"✅ E2B_API_KEY: {E2B_API_KEY[:10]}...")
    print(f"✅ GROQ_API_KEY: {GROQ_API_KEY[:10]}...\n")
    
    try:
        sandbox = deploy_api_server()
        
        print("\n🔄 Keeping sandbox alive (Ctrl+C to stop)...")
        while True:
            time.sleep(60)
            try:
                # Keep sandbox alive
                sandbox.run_code("print('keepalive')", timeout=5)
                print(f"💓 [{time.strftime('%H:%M:%S')}] Keepalive")
            except Exception as e:
                print(f"❌ Error: {e}")
                break
                
    except KeyboardInterrupt:
        print("\n\n👋 Stopping...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

