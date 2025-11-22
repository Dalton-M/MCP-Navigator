#!/usr/bin/env python3
"""
使用 E2B SDK 部署 MCP Stack Composer API Server
运行方式: python deploy_to_e2b.py
"""
import os
import time
from e2b_code_interpreter import Sandbox

# 环境变量
E2B_API_KEY = os.getenv("E2B_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

def deploy_api_server():
    """部署 API Server 到 E2B"""
    
    print("🚀 Creating E2B Sandbox...")
    
    # 创建 Sandbox（新版 API 使用 create() 方法）
    # API Key 从环境变量 E2B_API_KEY 自动读取
    sandbox = Sandbox.create()
    
    print(f"✅ Sandbox created: {sandbox.sandbox_id}")
    print(f"🌐 Access URL will be available after setup")
    
    # 上传项目文件
    print("\n📦 Uploading project files...")
    
    # 所有需要上传的文件
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
    
    for file_path in files_to_upload:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 确保目录存在
                if '/' in file_path:
                    dir_path = os.path.dirname(file_path)
                    try:
                        sandbox.filesystem.make_dir(dir_path)
                    except:
                        pass  # 目录可能已存在
                
                sandbox.filesystem.write(file_path, content)
                print(f"  ✓ {file_path}")
            except Exception as e:
                print(f"  ✗ {file_path}: {e}")
        else:
            print(f"  ⚠️  {file_path} not found")
    
    # 创建测试数据目录
    try:
        sandbox.filesystem.make_dir("tests")
        sandbox.filesystem.make_dir("tests/test_data")
    except:
        pass
    
    # 安装依赖
    print("\n📚 Installing dependencies...")
    result = sandbox.run_code("""
import subprocess
import sys

print("Installing packages...")
result = subprocess.run(
    [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("✅ Dependencies installed successfully")
else:
    print(f"❌ Installation failed: {result.stderr}")
""", timeout=120)
    
    print(result.logs.stdout)
    if result.error:
        print(f"Error: {result.error}")
    
    # 启动 API Server（后台运行）
    print("\n🚀 Starting API Server...")
    
    # 创建启动脚本
    start_script = f"""
import os
import subprocess
import sys

# 设置环境变量
os.environ['GROQ_API_KEY'] = '{GROQ_API_KEY}'
os.environ['GITHUB_TOKEN'] = '{GITHUB_TOKEN}'

print("Starting API Server...")

# 后台启动
proc = subprocess.Popen(
    [sys.executable, 'api_server.py'],
    stdout=open('api.log', 'w'),
    stderr=subprocess.STDOUT,
    env=os.environ.copy()
)

print(f"✅ API Server started with PID: {{proc.pid}}")
print("📝 Check logs: api.log")
"""
    
    sandbox.filesystem.write("start_server.py", start_script)
    result = sandbox.run_code("exec(open('start_server.py').read())")
    print(result.logs.stdout)
    
    # 等待服务启动
    print("\n⏳ Waiting for server to start...")
    time.sleep(15)
    
    # 测试 API
    print("🧪 Testing API...")
    test_result = sandbox.run_code("""
import requests
import time

# 等待服务就绪
for i in range(15):
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print(f"✅ API is healthy!")
            print(f"Response: {response.json()}")
            break
        else:
            print(f"Status: {response.status_code}")
    except Exception as e:
        print(f"⏳ Waiting for API... ({i+1}/15): {e}")
        time.sleep(3)
else:
    print("⚠️  API may not be ready yet. Check logs:")
    try:
        with open('api.log', 'r') as f:
            print(f.read()[-500:])  # 最后 500 字符
    except:
        print("Could not read api.log")
""", timeout=60)
    
    print(test_result.logs.stdout)
    
    print("\n" + "="*70)
    print("🎉 Deployment Complete!")
    print("="*70)
    print(f"\n📋 Sandbox ID: {sandbox.sandbox_id}")
    print(f"\n⚠️  Important: E2B Sandbox will timeout without keepalive")
    print(f"\n💡 Access your API:")
    print(f"   1. Connect to sandbox: e2b sandbox connect {sandbox.sandbox_id}")
    print(f"   2. Test locally: curl http://localhost:8000/health")
    print(f"   3. For external access, you need to set up port forwarding or use E2B's network features")
    
    print(f"\n💡 To keep sandbox alive:")
    print(f"   python keep_alive.py {sandbox.sandbox_id}")
    
    print(f"\n💡 To view logs:")
    print(f"   e2b sandbox connect {sandbox.sandbox_id}")
    print(f"   Then: cat api.log")
    
    return sandbox


if __name__ == "__main__":
    # 检查环境变量
    if not E2B_API_KEY:
        print("❌ E2B_API_KEY not set")
        print("\nGet your key from: https://e2b.dev/dashboard")
        print("Then run: export E2B_API_KEY=e2b_xxx")
        exit(1)
    
    if not GROQ_API_KEY:
        print("❌ GROQ_API_KEY not set")
        print("\nGet your key from: https://console.groq.com/")
        print("Then run: export GROQ_API_KEY=gsk_xxx")
        exit(1)
    
    print(f"✅ E2B_API_KEY: {E2B_API_KEY[:10]}...")
    print(f"✅ GROQ_API_KEY: {GROQ_API_KEY[:10]}...")
    if GITHUB_TOKEN:
        print(f"✅ GITHUB_TOKEN: {GITHUB_TOKEN[:10]}...")
    
    try:
        sandbox = deploy_api_server()
        
        # 保持运行
        print("\n🔄 Keeping sandbox alive (Ctrl+C to stop)...")
        print("   This prevents the sandbox from timing out")
        
        while True:
            time.sleep(60)
            try:
                sandbox.keep_alive()
                print(f"💓 [{time.strftime('%H:%M:%S')}] Keepalive ping sent")
            except Exception as e:
                print(f"❌ Keepalive failed: {e}")
                print("Sandbox may have been closed. Exiting...")
                break
                
    except KeyboardInterrupt:
        print("\n\n👋 Stopping...")
        if 'sandbox' in locals():
            sandbox.close()
        print("Sandbox closed.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

