# 🚀 MCP Stack Composer - API 版本快速开始

## 📋 目录结构

```
MCP-Navigator/
├── api_server.py          # FastAPI 服务器（新）
├── start_api.sh           # 启动脚本
├── API_GUIDE.md           # 详细 API 文档
├── run.py                 # CLI 版本（原有）
└── app/                   # 核心逻辑（共享）
```

---

## 🎯 快速启动（3 步）

### Step 1: 启动 API 服务

```bash
cd /Users/lizhuolun/cursor/MCP-Navigator

# 方式 1：使用启动脚本（推荐）
./start_api.sh

# 方式 2：手动启动
export GROQ_API_KEY="your_groq_key_here"
export GITHUB_TOKEN="your_github_token_here"
python3 api_server.py
```

**看到这个输出说明成功**：
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

🔗 Endpoints:
   • Health: http://localhost:8000/health
   • Compose: POST http://localhost:8000/api/v1/compose
   • List MCPs: http://localhost:8000/api/v1/mcps
```

### Step 2: 打开 Swagger UI

在浏览器访问：**http://localhost:8000/docs**

你会看到：
- ✅ 自动生成的 API 文档
- ✅ 可交互测试的界面
- ✅ 所有 endpoints 和参数说明

### Step 3: 测试 API

#### 方式 A：Swagger UI 测试（最简单）

1. 在 Swagger UI 找到 **POST /api/v1/compose**
2. 点击 "Try it out"
3. 输入：
   ```json
   {
     "description": "I want an agent that monitors GitHub issues and auto-responds",
     "top_k": 3
   }
   ```
4. 点击 "Execute"
5. 查看响应！

#### 方式 B：curl 测试

```bash
curl -X POST "http://localhost:8000/api/v1/compose" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "I want an agent that monitors GitHub issues",
    "top_k": 3
  }'
```

---

## 🎬 Hackathon Demo 流程

### 演示脚本（2 分钟）

**开场（10 秒）**：
> "传统的 MCP 集成需要手动配置，查文档，写代码。我们的 MCP Stack Composer 把这个过程变成**一个 API 调用**。"

**演示（90 秒）**：

1. **打开 Swagger UI** (15 秒)
   - 访问 `http://localhost:8000/docs`
   - 展示自动生成的 API 文档

2. **调用 Compose API** (30 秒)
   - 找到 `POST /api/v1/compose`
   - 点击 "Try it out"
   - 输入需求：
     ```json
     {
       "description": "I want an agent that monitors GitHub issues, searches for solutions, and posts daily summaries",
       "top_k": 3
     }
     ```
   - 点击 "Execute"

3. **展示响应** (45 秒)
   
   **高亮这些点**：
   
   a) **Groq 分析结果** ✅
   ```json
   "capabilities": {
     "capabilities": ["code_hosting.read_issues", "web_search", "notify.slack"],
     "confidence": 0.95,
     "reasoning": "真实的 LLM 分析..."
   }
   ```
   
   b) **推荐的 MCP** ✅
   ```json
   "recommended_mcps": [
     {
       "mcp_id": "github",
       "score": 5.0,
       "docker_image": "mcp/github"
     }
   ]
   ```
   
   c) **生成的代码** ✅
   ```json
   "code_snippet": {
     "markdown": "完整的环境配置 + Docker 命令 + Python 代码"
   }
   ```
   
   d) **真实调用结果** ⭐ **（重点）**
   ```json
   "demo_call": {
     "mcp_id": "github",
     "success": true,
     "result": [
       {
         "number": 278970,
         "title": "VS Code crashes when Github Copilot...",
         "url": "https://github.com/microsoft/vscode/issues/278970"
       }
     ]
   }
   ```

**收尾（10 秒）**：
> "一个 API 调用，完成了：需求理解、MCP 选择、代码生成、真实验证。这就是我们说的**智能编排**。"

---

## 💡 核心价值（向评委说）

### 1️⃣ **端到端自动化**
> "从自然语言 → 可执行代码 → 真实调用，全自动。"

### 2️⃣ **真实可验证**
> "不是生成假代码，Step 4 的 demo_call 是**此刻**从 GitHub 拉取的真实数据。"

**证明方式**：
- 打开 https://github.com/microsoft/vscode/issues/278970
- 和 API 返回的 issue 对比 ✅

### 3️⃣ **可集成性**
> "这是 RESTful API，可以集成到任何系统：CI/CD、Slack Bot、内部工具..."

### 4️⃣ **技术深度**
> "我们整合了：
> - ✅ Groq (LLM 推理)
> - ✅ Docker MCP Hub (10+ MCP 服务器)
> - ✅ E2B (云端部署)
> - ✅ FastAPI (生产级 API)
> - ✅ 真实 GitHub API 调用"

---

## 📊 API vs CLI 对比

| 维度 | CLI 版本 | API 版本 | 赢家 |
|------|---------|---------|------|
| **演示效果** | 终端输出 | Swagger UI | 🏆 API |
| **可集成性** | 需手动运行 | RESTful API | 🏆 API |
| **专业度** | 脚本工具 | 企业级服务 | 🏆 API |
| **并发支持** | 单线程 | 多用户 | 🏆 API |
| **文档** | Markdown | 自动生成 | 🏆 API |
| **部署** | 本地 | 可云端 | 🏆 API |

**结论**：API 版本更适合 Hackathon 演示和实际使用！

---

## 🔧 主要 Endpoints

| Endpoint | 方法 | 说明 | 用途 |
|----------|------|------|------|
| `/api/v1/compose` | POST | **一站式编排** | 完整工作流 |
| `/api/v1/analyze` | POST | 分析需求 | Step 1 |
| `/api/v1/recommend` | POST | 推荐 MCP | Step 2 |
| `/api/v1/generate` | POST | 生成代码 | Step 3 |
| `/api/v1/call` | POST | 调用 MCP | Step 4 |
| `/api/v1/mcps` | GET | 列出所有 MCP | 查询 |
| `/health` | GET | 健康检查 | 监控 |

**推荐**：Demo 时只用 `/api/v1/compose`，展示完整流程。

---

## 🎯 测试用例（复制粘贴即用）

### 用例 1：GitHub Issue 监控
```json
{
  "description": "I want an agent that monitors GitHub issues for bugs and auto-labels them",
  "top_k": 3
}
```

### 用例 2：多 MCP 协作
```json
{
  "description": "I want to read GitHub issues, search Stack Overflow for solutions, and post summaries to Slack",
  "top_k": 5
}
```

### 用例 3：数据库监控
```json
{
  "description": "Monitor MongoDB for slow queries and send alerts to Grafana",
  "top_k": 3
}
```

---

## 🚀 部署到 E2B

```bash
# 在 E2B Sandbox 中
git clone <your-repo>
cd MCP-Navigator
pip install -r requirements.txt

# 设置环境变量（通过 E2B UI）
# GROQ_API_KEY
# GITHUB_TOKEN

# 启动服务
python3 api_server.py
```

访问：`https://your-sandbox.e2b.dev:8000/docs`

---

## 🎁 额外功能

### 分步 API（高级用户）

如果用户想分步控制：

1. **POST /api/v1/analyze** - 只做需求分析
2. **POST /api/v1/recommend** - 只推荐 MCP
3. **POST /api/v1/generate** - 只生成代码
4. **POST /api/v1/call** - 只调用 MCP

### 查询 API

- **GET /api/v1/mcps** - 浏览所有可用 MCP
- **GET /api/v1/mcps/{mcp_id}** - 查看特定 MCP 详情

---

## 📚 相关文档

- `API_GUIDE.md` - 详细 API 文档
- `README.md` - 项目概述
- `E2B_DEPLOYMENT_GUIDE.md` - 云端部署
- `DEMO_VIDEO_GUIDE.md` - 录制视频指南

---

## 🎉 总结

**你现在有**：
- ✅ 完整的 RESTful API
- ✅ 自动生成的 Swagger UI
- ✅ 真实的 MCP 调用
- ✅ 可部署到 E2B
- ✅ 适合 Hackathon 演示

**启动命令**：
```bash
./start_api.sh
```

**测试地址**：
http://localhost:8000/docs

**开始演示吧！** 🚀

