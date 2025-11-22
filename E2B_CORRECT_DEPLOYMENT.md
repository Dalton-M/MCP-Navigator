# E2B 正确部署方案

> 根据 [E2B 官方文档](https://e2b.dev/docs/quickstart)，E2B 是按需沙盒服务，不是持久部署平台

---

## ⚠️ 重要说明

**E2B 的实际工作方式：**
- ❌ 不是传统云平台（没有 Web UI Dashboard）
- ❌ 不适合部署长期运行的 API Server
- ✅ 是按需创建的临时沙盒环境
- ✅ 适合代码执行、AI Agent 运行等场景

**Sandbox 特点：**
- 默认存活时间：5 分钟
- 通过 SDK 创建和管理
- 快速启动（~150ms）
- 按使用量计费

---

## 🎯 两种部署方案

### 方案 A：传统云部署（强烈推荐）

如果你需要**持久运行的 API Server**，建议使用：

#### 1. Railway.app（最简单）

```bash
# 1. 注册 https://railway.app/
# 2. 连接 GitHub 仓库
# 3. 自动检测 Python 项目
# 4. 设置环境变量
# 5. 一键部署
```

**优点：**
- ✅ 免费 $5/月额度
- ✅ 自动 HTTPS
- ✅ GitHub 自动部署
- ✅ 有 Web UI

#### 2. Render.com

```bash
# 1. 注册 https://render.com/
# 2. New → Web Service
# 3. 连接 GitHub
# 4. 配置：
#    - Build Command: pip install -r requirements.txt
#    - Start Command: python api_server.py
# 5. 添加环境变量
# 6. 部署
```

#### 3. Fly.io

```bash
# 安装 CLI
curl -L https://fly.io/install.sh | sh

# 登录
fly auth login

# 部署
cd /Users/lizhuolun/cursor/MCP-Navigator
fly launch --name mcp-api-server

# 设置环境变量
fly secrets set GROQ_API_KEY=your_key
fly secrets set GITHUB_TOKEN=your_token

# 部署
fly deploy
```

---

### 方案 B：正确使用 E2B（如果必须用）

**适用场景：**
- ✅ 按需执行代码
- ✅ AI Agent 临时运行
- ✅ 用户触发的一次性任务
- ❌ 不适合持久 API Server

#### 架构设计

```
前端
  ↓ HTTP POST
中间服务器（Railway/Render 等）
  ↓ 创建 E2B Sandbox
E2B Sandbox（临时）
  ↓ 执行任务
返回结果
  ↓
前端
```

#### 实现步骤

**1. 安装 E2B SDK**

```bash
pip install e2b-code-interpreter
```

**2. 创建中间服务器（部署在 Railway 等平台）**

```python
# e2b_wrapper.py
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from e2b_code_interpreter import Sandbox

app = FastAPI()

E2B_API_KEY = os.getenv("E2B_API_KEY")  # 从 E2B 获取

class ExecuteRequest(BaseModel):
    code: str
    description: str

@app.post("/execute")
async def execute_in_e2b(request: ExecuteRequest):
    """
    创建 E2B Sandbox 执行代码
    """
    try:
        # 创建临时 Sandbox
        with Sandbox(api_key=E2B_API_KEY) as sandbox:
            # 执行你的逻辑
            result = sandbox.run_code(request.code)
            
            return {
                "success": True,
                "logs": result.logs,
                "error": result.error
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/compose")
async def compose_agent(request: dict):
    """
    完整的 MCP 编排流程，在 E2B 中执行
    """
    try:
        with Sandbox(api_key=E2B_API_KEY) as sandbox:
            # 上传你的项目代码
            sandbox.filesystem.write("/app/api_server.py", open("api_server.py").read())
            sandbox.filesystem.write("/app/requirements.txt", open("requirements.txt").read())
            
            # 安装依赖
            sandbox.run_code("!pip install -r /app/requirements.txt")
            
            # 运行你的逻辑
            result = sandbox.run_code(f"""
import sys
sys.path.append('/app')
from app.planner import get_capabilities_from_description
from app.matcher import load_catalog, match_mcp

description = {repr(request.get('description'))}
capabilities = get_capabilities_from_description(description)
catalog = load_catalog()
matched = match_mcp(capabilities.get('capabilities', []), catalog)

print(matched[:3])
""")
            
            return {
                "success": True,
                "result": result.logs
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**3. 部署中间服务器到 Railway/Render**

```bash
# 部署到 Railway
railway up

# 设置环境变量
railway variables set E2B_API_KEY=your_e2b_key
railway variables set GROQ_API_KEY=your_groq_key
```

**4. 前端调用**

```javascript
const response = await fetch('https://your-railway-app.com/compose', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    description: "I want an agent that reads GitHub issues"
  })
});

const result = await response.json();
```

---

## 📊 方案对比

| 特性 | 方案 A (Railway 等) | 方案 B (E2B) |
|------|---------------------|--------------|
| **部署难度** | ⭐ 简单 | ⭐⭐⭐ 复杂 |
| **持久运行** | ✅ 是 | ❌ 否（5分钟） |
| **成本** | 免费/低 | 按使用量 |
| **启动速度** | 快 | 非常快（150ms） |
| **适用场景** | API Server | 临时执行 |
| **管理界面** | ✅ Web UI | ❌ 仅 SDK |

---

## 🚀 推荐方案总结

### 如果你的 Hackathon 要求必须使用 E2B：

**使用混合方案：**
```
1. 中间 API Server → 部署在 Railway/Render
2. 代码执行层 → 使用 E2B Sandbox
```

**优点：**
- ✅ 满足 E2B 使用要求
- ✅ API Server 持久运行
- ✅ E2B 用于安全的代码执行

### 如果不强制要求 E2B：

**直接使用 Railway.app：**
```bash
# 3 分钟部署
1. 注册 Railway
2. 连接 GitHub
3. 添加环境变量
4. 一键部署
5. 获得 URL: https://your-app.railway.app
```

---

## 📝 正确的 E2B 使用场景

E2B 设计用于：

1. **AI Agent 代码执行**
   ```python
   # AI 生成代码，在 E2B 安全执行
   with Sandbox() as sbx:
       result = sbx.run_code(ai_generated_code)
   ```

2. **数据分析任务**
   ```python
   # 用户上传数据，E2B 中分析
   with Sandbox() as sbx:
       sbx.filesystem.write("/data.csv", user_file)
       result = sbx.run_code("import pandas as pd; df = pd.read_csv('/data.csv'); print(df.describe())")
   ```

3. **临时计算任务**
   ```python
   # 按需执行重计算
   with Sandbox() as sbx:
       result = sbx.run_code("complex_calculation()")
   ```

**不适合：**
- ❌ 持久运行的 Web Server
- ❌ 需要长期状态的应用
- ❌ 实时响应的 API

---

## 🛠️ Railway.app 快速部署（推荐）

```bash
# 1. 注册
https://railway.app/

# 2. New Project → Deploy from GitHub
选择你的 MCP-Navigator 仓库

# 3. 配置
Build Command: pip install -r requirements.txt
Start Command: python api_server.py

# 4. 环境变量
GROQ_API_KEY=xxx
GITHUB_TOKEN=xxx

# 5. 部署完成！
获得 URL: https://mcp-navigator-production.railway.app
```

**前端调用：**
```javascript
fetch('https://mcp-navigator-production.railway.app/api/v1/compose', {
  method: 'POST',
  body: JSON.stringify({description: "..."})
})
```

---

## 💡 最终建议

**如果 Hackathon 要求使用 E2B：**
1. 使用 **Railway 部署 API Server**（持久运行）
2. 在 API Server 中**调用 E2B SDK**（按需执行）
3. 这样既满足 E2B 要求，又能正常工作

**如果不强制 E2B：**
1. 直接用 **Railway/Render** 部署（5分钟搞定）
2. 前端调用更简单、更稳定

---

## 📚 参考资源

- [E2B 官方文档](https://e2b.dev/docs/quickstart)
- [Railway 部署指南](https://docs.railway.app/deploy/deployments)
- [Render 部署教程](https://render.com/docs/deploy-fastapi)
- [Fly.io Python 指南](https://fly.io/docs/languages-and-frameworks/python/)

---

**结论：** E2B 是很棒的沙盒执行环境，但不适合部署持久 API Server。使用 Railway 等平台更合适！

