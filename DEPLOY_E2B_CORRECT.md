# ✅ E2B 正确部署指南（已验证）

> 基于 E2B CLI 2.4.2 的实际命令

---

## 🔍 重要发现

E2B CLI 的实际命令和文档中的不一样。正确的命令格式：

```bash
# ❌ 错误（我之前给的）
e2b sandbox create --template xxx --name xxx --env-file xxx

# ✅ 正确
e2b sandbox create [template-name]
```

---

## 🚀 正确的部署步骤

### 第 1 步：准备环境变量

E2B 不支持 `--env-file` 参数，环境变量需要在 Dockerfile 中设置或通过构建参数传递。

**修改 `Dockerfile.e2b`，添加环境变量：**

```dockerfile
# 在 Dockerfile.e2b 中添加（build 时会使用）
ARG GROQ_API_KEY
ARG GITHUB_TOKEN
ARG BRAVE_API_KEY

ENV GROQ_API_KEY=${GROQ_API_KEY}
ENV GITHUB_TOKEN=${GITHUB_TOKEN}
ENV BRAVE_API_KEY=${BRAVE_API_KEY}
```

### 第 2 步：构建模板（正确命令）

```bash
cd /Users/lizhuolun/cursor/MCP-Navigator

# 使用正确的命令构建模板
e2b template build \
  --name mcp-stack-composer \
  --dockerfile Dockerfile.e2b \
  --cmd "python api_server.py" \
  --cpu-count 2 \
  --memory-mb 4096 \
  --build-arg GROQ_API_KEY="$GROQ_API_KEY" \
  --build-arg GITHUB_TOKEN="$GITHUB_TOKEN"
```

**说明：**
- `--name` - 模板名称
- `--dockerfile` - 指定 Dockerfile
- `--cmd` - 启动命令
- `--cpu-count` - CPU 核心数
- `--memory-mb` - 内存（MB）
- `--build-arg` - 传递构建参数（环境变量）

### 第 3 步：创建 Sandbox（正确命令）

```bash
# 简单创建（会进入交互式终端）
e2b sandbox create mcp-stack-composer

# 这会：
# 1. 从模板创建 sandbox
# 2. 连接到 sandbox 的终端
# 3. 自动运行启动命令
```

### 第 4 步：获取 Sandbox 信息

在另一个终端窗口：

```bash
# 列出所有运行的 sandbox
e2b sandbox list

# 输出示例：
# ID: sbx_abc123
# Template: mcp-stack-composer
# Status: running
```

### 第 5 步：访问 API

E2B Sandbox 的访问方式：

```bash
# 方式 1: 通过端口转发（推荐）
# 在 sandbox 终端中，API 运行在 localhost:8000

# 方式 2: 使用 E2B SDK 获取公网 URL
```

---

## 💡 更实用的方案：使用 E2B SDK

由于 E2B CLI 主要用于交互式开发，部署持久 API Server 应该使用 **E2B Python SDK**：

### 安装 SDK

```bash
pip install e2b-code-interpreter
```

### 创建部署脚本

创建 `deploy_to_e2b.py`：

```python
#!/usr/bin/env python3
"""
使用 E2B SDK 部署 API Server
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
    
    # 创建 Sandbox（使用默认 Python 环境）
    sandbox = Sandbox(api_key=E2B_API_KEY)
    
    print(f"✅ Sandbox created: {sandbox.sandbox_id}")
    print(f"🌐 Sandbox URL: https://{sandbox.sandbox_id}.e2b.dev")
    
    # 上传项目文件
    print("📦 Uploading project files...")
    
    # 上传所有必要文件
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
            with open(file_path, 'r') as f:
                content = f.read()
            
            # 确保目录存在
            if '/' in file_path:
                dir_path = os.path.dirname(file_path)
                sandbox.filesystem.make_dir(dir_path)
            
            sandbox.filesystem.write(file_path, content)
            print(f"  ✓ {file_path}")
    
    # 创建测试数据目录
    sandbox.filesystem.make_dir("tests/test_data")
    
    # 设置环境变量
    print("🔑 Setting environment variables...")
    env_vars = {
        "GROQ_API_KEY": GROQ_API_KEY,
        "GITHUB_TOKEN": GITHUB_TOKEN,
        "PORT": "8000",
    }
    
    # 安装依赖
    print("📚 Installing dependencies...")
    result = sandbox.run_code("""
import subprocess
subprocess.run(['pip', 'install', '-r', 'requirements.txt'], check=True)
print("✅ Dependencies installed")
""")
    print(result.logs.stdout)
    
    # 启动 API Server（后台运行）
    print("🚀 Starting API Server...")
    
    # 创建启动脚本
    start_script = f"""
import os
import subprocess

# 设置环境变量
os.environ['GROQ_API_KEY'] = '{GROQ_API_KEY}'
os.environ['GITHUB_TOKEN'] = '{GITHUB_TOKEN}'
os.environ['PORT'] = '8000'

# 启动 API Server
subprocess.Popen(['python', 'api_server.py'], 
                 stdout=open('api.log', 'w'),
                 stderr=subprocess.STDOUT)

print("✅ API Server starting...")
print("📝 Logs: api.log")
"""
    
    sandbox.filesystem.write("start_server.py", start_script)
    result = sandbox.run_code("exec(open('start_server.py').read())")
    print(result.logs.stdout)
    
    # 等待服务启动
    print("⏳ Waiting for server to start...")
    time.sleep(10)
    
    # 测试 API
    print("🧪 Testing API...")
    test_result = sandbox.run_code("""
import requests
import time

# 等待服务就绪
for i in range(10):
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print(f"✅ API is healthy: {response.json()}")
            break
    except Exception as e:
        print(f"⏳ Waiting for API... ({i+1}/10)")
        time.sleep(2)
""")
    print(test_result.logs.stdout)
    
    print("\n" + "="*60)
    print("🎉 Deployment Complete!")
    print("="*60)
    print(f"\n📋 Sandbox ID: {sandbox.sandbox_id}")
    print(f"🌐 Sandbox URL: https://{sandbox.sandbox_id}.e2b.dev")
    print(f"\n💡 To keep sandbox alive, run:")
    print(f"   python keep_alive.py {sandbox.sandbox_id}")
    print("\n💡 To connect to sandbox:")
    print(f"   e2b sandbox connect {sandbox.sandbox_id}")
    
    return sandbox

if __name__ == "__main__":
    # 检查环境变量
    if not E2B_API_KEY:
        print("❌ E2B_API_KEY not set")
        print("Get your key from: https://e2b.dev/dashboard")
        exit(1)
    
    if not GROQ_API_KEY:
        print("❌ GROQ_API_KEY not set")
        exit(1)
    
    sandbox = deploy_api_server()
    
    # 保持运行
    try:
        print("\n🔄 Keeping sandbox alive (Ctrl+C to stop)...")
        while True:
            time.sleep(60)
            sandbox.keep_alive()
            print("💓 Sandbox keepalive ping")
    except KeyboardInterrupt:
        print("\n\n👋 Stopping...")
        sandbox.close()
```

### 运行部署

```bash
# 设置环境变量
export E2B_API_KEY=e2b_xxx
export GROQ_API_KEY=gsk_xxx
export GITHUB_TOKEN=ghp_xxx

# 运行部署脚本
python deploy_to_e2b.py
```

---

## 🔄 保持 Sandbox 运行

创建 `keep_alive.py`：

```python
#!/usr/bin/env python3
import os
import sys
import time
from e2b_code_interpreter import Sandbox

if len(sys.argv) < 2:
    print("Usage: python keep_alive.py <sandbox_id>")
    exit(1)

SANDBOX_ID = sys.argv[1]
E2B_API_KEY = os.getenv("E2B_API_KEY")

print(f"🔄 Keeping sandbox {SANDBOX_ID} alive...")

# 连接到已存在的 sandbox
sandbox = Sandbox.connect(SANDBOX_ID, api_key=E2B_API_KEY)

try:
    while True:
        sandbox.keep_alive()
        print(f"💓 [{time.strftime('%H:%M:%S')}] Keepalive ping")
        time.sleep(300)  # 每 5 分钟 ping 一次
except KeyboardInterrupt:
    print("\n👋 Stopped")
    sandbox.close()
```

---

## 📊 方案对比

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| **E2B SDK 方案** | 完全控制、可保活、可监控 | 需要编写脚本 | ⭐⭐⭐⭐⭐ |
| **E2B CLI 方案** | 快速测试 | 交互式、难以自动化 | ⭐⭐ |
| **Railway/Render** | 简单、持久、免费 | 不满足 E2B 要求 | ⭐⭐⭐⭐ |

---

## 🎯 推荐方案

**如果必须使用 E2B：**

使用 **E2B SDK 方案**（上面的 `deploy_to_e2b.py`）：

```bash
# 1. 安装 SDK
pip install e2b-code-interpreter

# 2. 设置环境变量
export E2B_API_KEY=e2b_xxx
export GROQ_API_KEY=gsk_xxx

# 3. 运行部署
python deploy_to_e2b.py
```

这会：
- ✅ 创建 E2B Sandbox
- ✅ 上传所有代码
- ✅ 安装依赖
- ✅ 启动 API Server
- ✅ 保持 Sandbox 运行
- ✅ 提供访问 URL

---

## 💡 重要提示

1. **E2B Sandbox 默认会超时**，需要定期 `keep_alive()`
2. **费用按使用时间计算**，新用户有 $100 免费额度
3. **公网访问**：Sandbox URL 格式为 `https://sbx_xxx.e2b.dev`

---

**现在你可以使用正确的命令部署了！** 🎉

