# E2B API Server 部署指南

> 将 MCP Stack Composer API 部署到 E2B，让前端可以通过 HTTP 调用

---

## 📋 部署概述

**目标：** 在 E2B 云端运行 FastAPI 服务器，暴露端口给前端调用

**架构：**
```
前端应用 → E2B Public URL → FastAPI Server (port 8000) → Groq/GitHub APIs
```

---

## 第 1 步：注册 E2B 并创建 Sandbox

### 1.1 注册账号
```bash
# 访问 E2B 官网
https://e2b.dev/

# 或使用 CLI 安装
npm install -g @e2b/cli
e2b login
```

### 1.2 创建 API Sandbox
```bash
# 使用 E2B CLI 创建
e2b sandbox create \
  --name mcp-api-server \
  --template python \
  --port 8000
```

**或在 Web UI 创建：**
1. 登录 https://e2b.dev/dashboard
2. 点击 "New Sandbox"
3. 选择 **Python 3.11+**
4. 勾选 **"Expose ports"** 选项
5. 添加端口：`8000`

---

## 第 2 步：配置环境变量

在 E2B Dashboard → Settings → Environment Variables 添加：

```bash
# 必需 - Groq API
GROQ_API_KEY=gsk_your_groq_api_key_here

# 可选 - 用于 Demo 调用
GITHUB_TOKEN=ghp_your_github_token_here
BRAVE_API_KEY=BSA_your_brave_api_key_here

# API Server 配置
API_HOST=0.0.0.0
API_PORT=8000
ALLOW_ORIGINS=*  # 生产环境应该设置具体域名
```

---

## 第 3 步：上传代码到 E2B

### 方式 A：从 GitHub 部署（推荐）

```bash
# 1. 推送代码到 GitHub
cd /Users/lizhuolun/cursor/MCP-Navigator
git add .
git commit -m "Add E2B API deployment"
git push origin main

# 2. 在 E2B Sandbox 终端执行
git clone https://github.com/YOUR_USERNAME/MCP-Navigator.git
cd MCP-Navigator
```

### 方式 B：使用 E2B CLI 直接上传

```bash
# 在本地项目目录
cd /Users/lizhuolun/cursor/MCP-Navigator
e2b sandbox upload --sandbox-id YOUR_SANDBOX_ID
```

---

## 第 4 步：安装依赖

在 E2B Sandbox 终端执行：

```bash
cd MCP-Navigator

# 升级 pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
```

---

## 第 5 步：修改 API Server 配置（已完成）

你的 `api_server.py` 已经配置好了 CORS，但需要确保监听所有接口：

```python
# api_server.py (line 407-412)
uvicorn.run(
    app,
    host="0.0.0.0",  # ✅ 已设置为 0.0.0.0
    port=8000,
    log_level="info"
)
```

---

## 第 6 步：启动 API Server

### 6.1 测试启动（前台）

```bash
cd MCP-Navigator
python3 api_server.py
```

看到以下输出表示成功：
```
======================================================================
🚀 MCP Stack Composer API Server
======================================================================

✓ Server starting...
✓ Groq API: Configured
✓ GitHub Token: Configured

📚 Documentation:
   • Swagger UI: http://localhost:8000/docs
   • ReDoc: http://localhost:8000/redoc

INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 6.2 后台运行（生产模式）

创建启动脚本：

```bash
#!/bin/bash
# start_api_e2b.sh

nohup python3 api_server.py > api_server.log 2>&1 &
echo $! > api_server.pid
echo "API Server started with PID: $(cat api_server.pid)"
```

使用：
```bash
chmod +x start_api_e2b.sh
./start_api_e2b.sh

# 查看日志
tail -f api_server.log

# 停止服务
kill $(cat api_server.pid)
```

---

## 第 7 步：获取 E2B 公网 URL

### 7.1 在 E2B Dashboard 查找

1. 进入你的 Sandbox
2. 查看 **"Exposed Ports"** 或 **"URLs"** 部分
3. 找到类似这样的 URL：
   ```
   https://YOUR_SANDBOX_ID-8000.e2b.dev
   ```

### 7.2 使用 E2B CLI 查询

```bash
e2b sandbox list
e2b sandbox info YOUR_SANDBOX_ID
```

### 7.3 测试 URL

```bash
# 测试健康检查
curl https://YOUR_SANDBOX_ID-8000.e2b.dev/health

# 应返回：
# {"status":"healthy","groq_configured":true,"github_configured":true,"mock_mode":false}
```

---

## 第 8 步：前端调用示例

### 8.1 JavaScript/TypeScript (Fetch API)

```typescript
// frontend/src/api/mcpComposer.ts

const E2B_API_URL = "https://YOUR_SANDBOX_ID-8000.e2b.dev";

interface ComposeRequest {
  description: string;
  top_k?: number;
}

async function composeMCPAgent(request: ComposeRequest) {
  const response = await fetch(`${E2B_API_URL}/api/v1/compose`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }

  return await response.json();
}

// 使用示例
async function example() {
  try {
    const result = await composeMCPAgent({
      description: "I want an agent that reads GitHub issues and searches for solutions",
      top_k: 3,
    });

    console.log("Capabilities:", result.capabilities);
    console.log("Recommended MCPs:", result.recommended_mcps);
    console.log("Code Snippet:", result.code_snippet.markdown);
    console.log("Demo Call Result:", result.demo_call);
  } catch (error) {
    console.error("Failed to compose agent:", error);
  }
}
```

### 8.2 React 示例

```tsx
// frontend/src/components/MCPComposer.tsx
import React, { useState } from 'react';

const MCPComposer: React.FC = () => {
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch(
        'https://YOUR_SANDBOX_ID-8000.e2b.dev/api/v1/compose',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ description, top_k: 3 }),
        }
      );

      if (!response.ok) throw new Error('API request failed');

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>MCP Stack Composer</h1>
      
      <form onSubmit={handleSubmit}>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Describe your agent requirements..."
          rows={4}
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Composing...' : 'Compose Agent'}
        </button>
      </form>

      {error && <div className="error">{error}</div>}

      {result && (
        <div className="results">
          <h2>Recommended MCPs:</h2>
          <ul>
            {result.recommended_mcps.map((mcp) => (
              <li key={mcp.mcp_id}>
                <strong>{mcp.display_name}</strong> (Score: {mcp.score})
                <p>{mcp.description}</p>
              </li>
            ))}
          </ul>

          <h2>Generated Code:</h2>
          <pre>{result.code_snippet.markdown}</pre>

          {result.demo_call && (
            <>
              <h2>Demo Call Result:</h2>
              <pre>{JSON.stringify(result.demo_call, null, 2)}</pre>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default MCPComposer;
```

### 8.3 cURL 测试

```bash
curl -X POST https://YOUR_SANDBOX_ID-8000.e2b.dev/api/v1/compose \
  -H "Content-Type: application/json" \
  -d '{
    "description": "I want an agent that reads GitHub issues and searches for solutions",
    "top_k": 3
  }'
```

---

## 第 9 步：CORS 配置（重要）

如果前端和 API 不在同一个域名，需要配置 CORS。

你的 `api_server.py` 已经配置了：

```python
# api_server.py (line 32-38)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**生产环境建议：**
```python
# 只允许你的前端域名
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend-domain.com",
        "http://localhost:3000",  # 本地开发
    ],
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)
```

---

## 第 10 步：监控和日志

### 查看实时日志

```bash
# 在 E2B Sandbox 终端
tail -f api_server.log

# 或使用 journalctl（如果是 systemd）
journalctl -u mcp-api-server -f
```

### 健康检查

```bash
# 定期 ping 健康检查端点
curl https://YOUR_SANDBOX_ID-8000.e2b.dev/health
```

### 性能监控

可以添加简单的监控端点：

```python
# 在 api_server.py 添加
from datetime import datetime

start_time = datetime.now()
request_count = 0

@app.get("/stats")
async def get_stats():
    uptime = (datetime.now() - start_time).total_seconds()
    return {
        "uptime_seconds": uptime,
        "total_requests": request_count,
        "status": "running"
    }
```

---

## 🔒 安全最佳实践

### 1. API Key 保护
```bash
# ❌ 不要在前端直接暴露 GROQ_API_KEY
# ✅ 所有 API 调用在后端完成
```

### 2. 速率限制（可选）
```python
# 安装: pip install slowapi
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/v1/compose")
@limiter.limit("10/minute")  # 每分钟最多10次
async def compose_agent(request: AgentRequest):
    ...
```

### 3. 输入验证
```python
# Pydantic 自动验证，但可以添加额外检查
if len(request.description) > 1000:
    raise HTTPException(400, "Description too long")
```

---

## 🐛 故障排查

### 问题 1：无法访问 E2B URL

**可能原因：**
- 端口未正确暴露
- 服务未启动
- 防火墙问题

**解决方案：**
```bash
# 检查服务是否运行
ps aux | grep api_server

# 检查端口
netstat -tlnp | grep 8000

# 重启服务
pkill -f api_server.py
python3 api_server.py
```

### 问题 2：CORS 错误

**浏览器错误：**
```
Access to fetch at 'https://...' has been blocked by CORS policy
```

**解决方案：**
- 确认 `allow_origins` 包含你的前端域名
- 检查是否返回了正确的 CORS headers
- 使用浏览器开发者工具查看 Network 面板

### 问题 3：API 响应慢

**原因：**
- Groq API 调用需要时间
- Cold start 延迟

**解决方案：**
```python
# 添加超时设置
payload = {
    "model": Config.GROQ_MODEL,
    "messages": [...],
    "temperature": 0.1,
    "max_tokens": 1000  # 限制 token 数量
}
```

---

## 📊 完整部署检查清单

- [ ] E2B Sandbox 创建并运行
- [ ] 环境变量配置（GROQ_API_KEY 等）
- [ ] 代码上传到 E2B
- [ ] 依赖安装成功
- [ ] API Server 启动成功
- [ ] 端口 8000 暴露
- [ ] 获取公网 URL
- [ ] 健康检查通过 (`/health`)
- [ ] API 文档可访问 (`/docs`)
- [ ] 测试 POST `/api/v1/compose` 成功
- [ ] CORS 配置正确
- [ ] 前端可以成功调用
- [ ] 日志记录正常

---

## 🚀 快速开始命令汇总

```bash
# 1. 在 E2B Sandbox 执行
git clone https://github.com/YOUR_USERNAME/MCP-Navigator.git
cd MCP-Navigator
pip install -r requirements.txt

# 2. 启动服务（后台）
nohup python3 api_server.py > api_server.log 2>&1 &

# 3. 获取 PID
echo $! > api_server.pid

# 4. 查看日志
tail -f api_server.log

# 5. 测试 API
curl https://YOUR_SANDBOX_ID-8000.e2b.dev/health

# 6. 查看 Swagger UI
# 浏览器访问: https://YOUR_SANDBOX_ID-8000.e2b.dev/docs
```

---

## 📚 相关资源

- [E2B 官方文档](https://e2b.dev/docs)
- [FastAPI 部署指南](https://fastapi.tiangolo.com/deployment/)
- [Uvicorn 配置](https://www.uvicorn.org/settings/)
- [项目 GitHub](https://github.com/YOUR_USERNAME/MCP-Navigator)

---

## 💡 提示

1. **E2B URL 格式：** `https://{sandbox-id}-{port}.e2b.dev`
2. **Swagger UI：** 部署后访问 `/docs` 可以直接在浏览器测试 API
3. **日志监控：** 定期检查 `api_server.log` 发现问题
4. **保持运行：** 使用 `nohup` 或 `systemd` 确保服务持续运行

---

部署成功后，前端就可以通过 E2B 提供的公网 URL 调用你的 API 了！🎉

