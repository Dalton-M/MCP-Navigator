#!/usr/bin/env python3
"""
E2B 部署脚本 - 带公网 URL 暴露
使用 sandbox.get_host() 获取可访问的公网地址
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
    
    # 获取公网访问地址
    try:
        # 尝试获取 host（可能是公网地址）
        host = sandbox.get_host(8000)
        print(f"🌐 Public URL: https://{host}")
        print(f"📝 This URL should be accessible from frontend!\n")
    except Exception as e:
        print(f"⚠️  Could not get public host: {e}")
        print(f"📝 Sandbox URL: https://{sandbox.sandbox_id}.e2b.dev\n")
    
    # 上传项目文件
    print("📦 Uploading project files...")
    
    files_content = {}
    files_to_upload = [
        "api_server.py",
        "requirements.txt",
        "app/config.py",
        "app/planner.py",
        "app/matcher.py",
        "app/snippet_generator.py",
        "app/mcp_client.py",
        "app/workflow_templates.py",  # NEW!
        "app/cost_estimator.py",      # NEW!
        "app/mermaid_generator.py",   # NEW!
        "app/__init__.py",
        "data/mcp_catalog.json",
    ]
    
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
    
    for filepath, content in files_content.items():
        upload_code += f'\nfiles["{filepath}"] = "{content}"'
    
    upload_code += """

# 创建目录和写入文件
for filepath, content in files.items():
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    
    with open(filepath, 'wb') as f:
        f.write(base64.b64decode(content))
    print(f"✓ Wrote {filepath}")

print("\\n✅ All files uploaded")
"""
    
    print("\n📤 Executing upload...")
    result = sandbox.run_code(upload_code, timeout=120)
    
    # Check result
    if result.logs and result.logs.stdout:
        for line in result.logs.stdout:
            print(line, end='')
    if result.logs and result.logs.stderr:
        print("Stderr:", result.logs.stderr)
    if result.error:
        print(f"❌ Upload error: {result.error}")
        raise Exception(f"Upload failed: {result.error}")
    
    print("✅ Upload completed")
    
    # 安装依赖
    print("\n📚 Installing dependencies...")
    install_code = """
import subprocess
import sys

print("Installing packages...")
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
    
    if result.logs and result.logs.stdout:
        for line in result.logs.stdout:
            print(line, end='')
    if result.error:
        print(f"❌ Install error: {result.error}")
        raise Exception(f"Dependencies installation failed: {result.error}")
    
    print("✅ Dependencies installed")
    
    # 修改 api_server.py 监听所有接口
    print("\n🔧 Configuring API Server to listen on 0.0.0.0...")
    
    config_code = """
# 确保 API Server 监听 0.0.0.0（允许外部访问）
import re

with open('api_server.py', 'r') as f:
    content = f.read()

# 确保 host="0.0.0.0"
if 'host="0.0.0.0"' not in content:
    content = re.sub(
        r'host="localhost"',
        'host="0.0.0.0"',
        content
    )
    
with open('api_server.py', 'w') as f:
    f.write(content)

print("✅ API Server configured for external access")
"""
    
    result = sandbox.run_code(config_code, timeout=10)
    if result.text:
        print(result.text)
    else:
        print("API Server configuration executed")
    
    # 启动 API Server
    print("\n🚀 Starting API Server...")
    
    start_code = f"""
import os
import subprocess
import sys

# 设置环境变量
os.environ['GROQ_API_KEY'] = '{GROQ_API_KEY}'
os.environ['GITHUB_TOKEN'] = '{GITHUB_TOKEN}'

# 后台启动 API Server
with open('start_api.sh', 'w') as f:
    f.write('#!/bin/bash\\nnohup python api_server.py > api.log 2>&1 &\\necho $! > api.pid')

subprocess.run(['chmod', '+x', 'start_api.sh'])
subprocess.run(['./start_api.sh'])

print("✅ API Server starting...")
print("📝 Logs: api.log")

# 等待启动
import time
time.sleep(5)

try:
    with open('api.pid', 'r') as f:
        pid = f.read().strip()
    print(f"📋 PID: {{pid}}")
except:
    pass
"""
    
    result = sandbox.run_code(start_code, timeout=30)
    
    if result.logs and result.logs.stdout:
        for line in result.logs.stdout:
            print(line, end='')
    if result.error:
        print(f"❌ Start error: {result.error}")
    else:
        print("✅ API Server start command executed")
    
    # 等待服务完全启动
    print("\n⏳ Waiting for API to start (20s)...")
    time.sleep(20)
    
    # 测试 API
    print("🧪 Testing API...")
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
    except Exception as e:
        print(f"⏳ Attempt {i+1}/10: {str(e)[:50]}")
        time.sleep(3)
else:
    print("⚠️  Check logs:")
    try:
        with open('api.log', 'r') as f:
            print(f.read()[-500:])
    except:
        pass
"""
    
    result = sandbox.run_code(test_code, timeout=90)
    
    if result.logs and result.logs.stdout:
        for line in result.logs.stdout:
            print(line, end='')
    if result.logs and result.logs.stderr:
        for line in result.logs.stderr:
            print(line, end='')
    if result.error:
        print(f"❌ Test error: {result.error}")
    
    # Also check if API server process is running
    print("\n🔍 Checking if API server process is running...")
    check_code = """
import subprocess
result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
if 'api_server' in result.stdout:
    print("✅ API server process found")
    for line in result.stdout.split('\\n'):
        if 'api_server' in line:
            print(line)
else:
    print("❌ API server process not found")
    print("\\nChecking api.log:")
    try:
        with open('api.log', 'r') as f:
            print(f.read())
    except:
        print("No api.log file found")
"""
    result = sandbox.run_code(check_code, timeout=10)
    if result.logs and result.logs.stdout:
        for line in result.logs.stdout:
            print(line, end='')
    
    # 获取所有可能的访问 URL
    print("\n" + "="*70)
    print("🎉 Deployment Complete!")
    print("="*70)
    
    print(f"\n📋 Sandbox ID: {sandbox.sandbox_id}")
    
    # 尝试获取不同端口的 host
    print(f"\n🌐 Access URLs:")
    try:
        host_8000 = sandbox.get_host(8000)
        print(f"   • API Server: https://{host_8000}")
        print(f"   • Swagger UI: https://{host_8000}/docs")
        print(f"   • Health Check: https://{host_8000}/health")
        
        # 保存 URL 到文件
        with open('e2b_url.txt', 'w') as f:
            f.write(f"https://{host_8000}\n")
        print(f"\n✅ URL saved to e2b_url.txt")
        
    except Exception as e:
        print(f"   ⚠️  Could not get public host: {e}")
        print(f"   📝 Try: https://{sandbox.sandbox_id}.e2b.dev")
    
    print(f"\n💡 Test from your browser or curl:")
    try:
        host = sandbox.get_host(8000)
        print(f"   curl https://{host}/health")
    except:
        print(f"   curl http://localhost:8000/health  (inside sandbox)")
    
    print(f"\n💡 To connect to sandbox:")
    print(f"   e2b sandbox connect {sandbox.sandbox_id}")
    
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
        print("   (Sandbox will timeout without keepalive)\n")
        
        while True:
            time.sleep(60)
            try:
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

