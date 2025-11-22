#!/usr/bin/env python3
"""
E2B 生产环境部署 - 最大超时 + 自动重启
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

def deploy_api_server(timeout=3600):
    """
    部署 API Server 到 E2B
    
    Args:
        timeout: Sandbox 超时时间（秒）
                 - Hobby 用户: 最大 3600 (1小时)
                 - Pro 用户: 最大 86400 (24小时)
    """
    
    print(f"🚀 Creating E2B Sandbox with {timeout}s ({timeout//60} minutes) timeout...")
    
    # 创建 Sandbox，设置最大超时
    sandbox = Sandbox.create(timeout=timeout)
    
    print(f"✅ Sandbox created: {sandbox.sandbox_id}")
    
    # 获取公网 URL
    try:
        host = sandbox.get_host(8000)
        public_url = f"https://{host}"
        print(f"🌐 Public URL: {public_url}")
        print(f"📝 Frontend can access this URL!\n")
    except Exception as e:
        print(f"⚠️  Could not get public host: {e}\n")
        public_url = None
    
    # 上传文件
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
        "app/__init__.py",
        "data/mcp_catalog.json",
    ]
    
    for filepath in files_to_upload:
        if os.path.exists(filepath):
            files_content[filepath] = read_and_encode_file(filepath)
            print(f"  ✓ {filepath}")
    
    # 上传代码
    upload_code = "import os\nimport base64\nfiles = {}\n"
    for filepath, content in files_content.items():
        upload_code += f'files["{filepath}"] = "{content}"\n'
    
    upload_code += """
for filepath, content in files.items():
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(filepath, 'wb') as f:
        f.write(base64.b64decode(content))
    print(f"✓ {filepath}")
print("\\n✅ All files uploaded")
"""
    
    print("\n📤 Uploading...")
    result = sandbox.run_code(upload_code, timeout=120)
    if result.text:
        print(result.text)
    
    # 安装依赖
    print("\n📚 Installing dependencies...")
    install_code = """
import subprocess
import sys
print("Installing packages...")
result = subprocess.run(
    [sys.executable, '-m', 'pip', 'install', '-q', '-r', 'requirements.txt'],
    capture_output=True, text=True
)
if result.returncode == 0:
    print("✅ Dependencies installed")
else:
    print(f"❌ Error: {result.stderr}")
"""
    result = sandbox.run_code(install_code, timeout=180)
    if result.text:
        print(result.text)
    
    # 启动 API Server
    print("\n🚀 Starting API Server...")
    start_code = f"""
import os
import subprocess
os.environ['GROQ_API_KEY'] = '{GROQ_API_KEY}'
os.environ['GITHUB_TOKEN'] = '{GITHUB_TOKEN}'

with open('start_api.sh', 'w') as f:
    f.write('#!/bin/bash\\nnohup python api_server.py > api.log 2>&1 &\\necho $! > api.pid')
subprocess.run(['chmod', '+x', 'start_api.sh'])
subprocess.run(['./start_api.sh'])

import time
time.sleep(5)

try:
    with open('api.pid', 'r') as f:
        print(f"✅ API Server started (PID: {{f.read().strip()}})")
except:
    print("✅ API Server starting...")
"""
    
    result = sandbox.run_code(start_code, timeout=30)
    if result.text:
        print(result.text)
    
    # 等待并测试
    print("\n⏳ Waiting 15s for API startup...")
    time.sleep(15)
    
    print("🧪 Testing API...")
    test_code = """
import requests
for i in range(5):
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print(f"✅ API is healthy: {response.json()}")
            break
    except Exception as e:
        print(f"⏳ Attempt {i+1}/5...")
        import time
        time.sleep(3)
"""
    result = sandbox.run_code(test_code, timeout=30)
    if result.text:
        print(result.text)
    
    # 保存配置
    if public_url:
        with open('e2b_url.txt', 'w') as f:
            f.write(f"{public_url}\n")
            f.write(f"Sandbox ID: {sandbox.sandbox_id}\n")
            f.write(f"Expires in: {timeout} seconds ({timeout//60} minutes)\n")
    
    print("\n" + "="*70)
    print("🎉 Deployment Complete!")
    print("="*70)
    print(f"\n📋 Sandbox ID: {sandbox.sandbox_id}")
    print(f"⏰ Timeout: {timeout}s ({timeout//60} minutes)")
    
    if public_url:
        print(f"\n🌐 Public URL: {public_url}")
        print(f"   • API: {public_url}/api/v1/compose")
        print(f"   • Health: {public_url}/health")
        print(f"   • Docs: {public_url}/docs")
    
    return sandbox, public_url


def keep_alive_with_restart(initial_sandbox, public_url, timeout=3600):
    """
    保持 Sandbox 运行，超时前自动重启
    
    Args:
        initial_sandbox: 初始 Sandbox 实例
        public_url: 公网 URL
        timeout: Sandbox 超时时间
    """
    sandbox = initial_sandbox
    restart_before = 60  # 在超时前 60 秒重启
    next_restart = time.time() + timeout - restart_before
    
    print(f"\n🔄 Auto-restart enabled (will restart every {timeout//60} minutes)")
    print(f"💡 Press Ctrl+C to stop\n")
    
    try:
        while True:
            current_time = time.time()
            
            # 检查是否需要重启
            if current_time >= next_restart:
                print(f"\n{'='*70}")
                print("🔄 Sandbox timeout approaching - Creating new sandbox...")
                print("="*70)
                
                try:
                    # 创建新 Sandbox
                    new_sandbox, new_url = deploy_api_server(timeout=timeout)
                    
                    # 关闭旧 Sandbox
                    try:
                        sandbox.close()
                        print("✅ Old sandbox closed")
                    except:
                        pass
                    
                    # 更新引用
                    sandbox = new_sandbox
                    public_url = new_url
                    next_restart = time.time() + timeout - restart_before
                    
                    print(f"\n✅ New sandbox ready!")
                    print(f"🌐 Public URL: {public_url}")
                    print(f"⏰ Next restart in {timeout//60} minutes\n")
                    
                except Exception as e:
                    print(f"❌ Restart failed: {e}")
                    print("Waiting 60s before retry...")
                    time.sleep(60)
                    next_restart = time.time() + 60
                    continue
            
            # 发送 keepalive
            try:
                sandbox.run_code("print('keepalive')", timeout=5)
                remaining = int(next_restart - time.time())
                print(f"💓 [{time.strftime('%H:%M:%S')}] Keepalive | Next restart in {remaining//60}m {remaining%60}s")
            except Exception as e:
                print(f"⚠️  Keepalive failed: {e}")
            
            time.sleep(60)  # 每分钟 ping 一次
            
    except KeyboardInterrupt:
        print("\n\n👋 Stopping...")
        try:
            sandbox.close()
        except:
            pass


if __name__ == "__main__":
    if not E2B_API_KEY:
        print("❌ E2B_API_KEY not set")
        exit(1)
    
    if not GROQ_API_KEY:
        print("❌ GROQ_API_KEY not set")
        exit(1)
    
    print("="*70)
    print("🚀 E2B Production Deployment")
    print("="*70)
    print(f"\n✅ E2B_API_KEY: {E2B_API_KEY[:10]}...")
    print(f"✅ GROQ_API_KEY: {GROQ_API_KEY[:10]}...")
    
    # 设置超时（根据你的账户类型）
    TIMEOUT = 3600  # 1 小时 (Hobby 用户最大值)
    # TIMEOUT = 86400  # 24 小时 (Pro 用户最大值)
    
    print(f"\n⏰ Sandbox timeout: {TIMEOUT}s ({TIMEOUT//60} minutes)")
    print(f"💡 Will auto-restart before timeout\n")
    
    try:
        sandbox, public_url = deploy_api_server(timeout=TIMEOUT)
        
        # 启动自动重启循环
        keep_alive_with_restart(sandbox, public_url, timeout=TIMEOUT)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

