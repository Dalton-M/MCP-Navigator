# MCP Stack Composer - API 使用指南

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动 API 服务

```bash
# 设置环境变量
export GROQ_API_KEY="your_groq_key"
export GITHUB_TOKEN="your_github_token"

# 启动服务
python3 api_server.py
```

服务启动后访问：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📡 API Endpoints

### 1. 一站式编排 API（推荐）

**POST** `/api/v1/compose`

完整的工作流：需求分析 → MCP 推荐 → 代码生成 → 演示调用

**请求示例**：
```bash
curl -X POST "http://localhost:8000/api/v1/compose" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "I want an agent that reads GitHub issues and searches the web for solutions",
    "top_k": 3
  }'
```

**Swagger UI 测试**：
1. 打开 http://localhost:8000/docs
2. 找到 `POST /api/v1/compose`
3. 点击 "Try it out"
4. 输入：
   ```json
   {
     "description": "I want an agent that monitors GitHub issues",
     "top_k": 3
   }
   ```
5. 点击 "Execute"

**响应示例**：
```json
{
  "request": "I want an agent that monitors GitHub issues",
  "capabilities": {
    "capabilities": ["code_hosting.read_issues", "monitoring.metrics"],
    "reasoning": "The agent needs to read GitHub issues...",
    "confidence": 0.95
  },
  "recommended_mcps": [
    {
      "mcp_id": "github",
      "display_name": "GitHub Official MCP",
      "score": 5.0,
      "exact_matches": ["code_hosting.read_issues"],
      "env_vars": ["GITHUB_TOKEN"],
      "docker_image": "mcp/github"
    }
  ],
  "code_snippet": {
    "markdown": "## 🎯 Why These MCPs?...",
    "env_vars": ["GITHUB_TOKEN"]
  },
  "demo_call": {
    "mcp_id": "github",
    "tool": "list_issues",
    "success": true,
    "result": [...]
  },
  "status": "success"
}
```

---

### 2. 分步 API

#### 2.1 分析需求

**POST** `/api/v1/analyze`

提取 capability 标签

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "I want to read GitHub issues and search the web"
  }'
```

#### 2.2 推荐 MCP

**POST** `/api/v1/recommend`

根据 capabilities 推荐 MCP

```bash
curl -X POST "http://localhost:8000/api/v1/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "capabilities": ["code_hosting.read_issues", "web_search"],
    "top_k": 5
  }'
```

#### 2.3 生成代码

**POST** `/api/v1/generate`

为选定的 MCP 生成配置和代码

```bash
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Monitor GitHub issues",
    "mcp_ids": ["github", "slack"]
  }'
```

#### 2.4 调用 MCP

**POST** `/api/v1/call`

真实调用 MCP 工具

```bash
curl -X POST "http://localhost:8000/api/v1/call" \
  -H "Content-Type: application/json" \
  -d '{
    "mcp_id": "github",
    "tool": "list_issues",
    "args": {
      "owner": "microsoft",
      "repo": "vscode",
      "per_page": 3
    }
  }'
```

---

### 3. 查询 API

#### 3.1 列出所有 MCP

**GET** `/api/v1/mcps`

```bash
curl "http://localhost:8000/api/v1/mcps"
```

#### 3.2 查看特定 MCP

**GET** `/api/v1/mcps/{mcp_id}`

```bash
curl "http://localhost:8000/api/v1/mcps/github"
```

#### 3.3 健康检查

**GET** `/health`

```bash
curl "http://localhost:8000/health"
```

---

## 🎬 Swagger UI 使用流程

### 方式 1：一键测试（推荐）

1. 访问 http://localhost:8000/docs
2. 找到 **POST /api/v1/compose**
3. 点击 "Try it out"
4. 输入测试数据：
   ```json
   {
     "description": "I want an agent that reads GitHub issues, searches web, and sends Slack notifications",
     "top_k": 3
   }
   ```
5. 点击 "Execute"
6. 查看完整响应

### 方式 2：分步测试

**Step 1: 分析需求**
- Endpoint: `POST /api/v1/analyze`
- 输入: `{"description": "..."}`
- 获取: `capabilities`

**Step 2: 推荐 MCP**
- Endpoint: `POST /api/v1/recommend`
- 输入: 从 Step 1 获取的 `capabilities`
- 获取: `recommended_mcps`

**Step 3: 生成代码**
- Endpoint: `POST /api/v1/generate`
- 输入: `mcp_ids` 从 Step 2 选择
- 获取: `code_snippet`

**Step 4: 真实调用**
- Endpoint: `POST /api/v1/call`
- 输入: 选择一个 MCP 和工具
- 获取: 真实调用结果

---

## 🎯 Demo 场景

### 场景 1：GitHub Issue 监控

```json
POST /api/v1/compose

{
  "description": "I want an agent that monitors GitHub issues for bugs and auto-labels them"
}
```

**响应包含**：
- ✅ Groq 分析的 capabilities
- ✅ 推荐 GitHub MCP
- ✅ 生成的 Python 代码
- ✅ 真实的 VS Code issues 数据

### 场景 2：Web 搜索 + 通知

```json
POST /api/v1/compose

{
  "description": "I want to search Stack Overflow daily and post summaries to Slack"
}
```

### 场景 3：数据库监控

```json
POST /api/v1/compose

{
  "description": "Monitor MongoDB for slow queries and alert via Grafana"
}
```

---

## 🔧 配置与部署

### 本地开发

```bash
# 启动开发服务器（自动重载）
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

### 生产部署

```bash
# 使用多个 worker
uvicorn api_server:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker 部署

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "api_server.py"]
```

```bash
# 构建和运行
docker build -t mcp-stack-composer .
docker run -p 8000:8000 \
  -e GROQ_API_KEY=$GROQ_API_KEY \
  -e GITHUB_TOKEN=$GITHUB_TOKEN \
  mcp-stack-composer
```

### E2B 部署

在 E2B sandbox 中：
```bash
git clone <your-repo>
cd MCP-Navigator
pip install -r requirements.txt
python3 api_server.py
```

访问：`https://your-e2b-sandbox.e2b.dev:8000/docs`

---

## 📊 性能与限制

| 指标 | 值 |
|------|------|
| 响应时间 | 2-5 秒（含 Groq 调用） |
| 并发支持 | 取决于 Groq API 限制 |
| Groq 免费配额 | 14,400 requests/day |
| GitHub API 限制 | 5,000 requests/hour |

---

## 🐛 故障排查

### 问题 1：Swagger UI 打不开

**解决**：
```bash
# 检查服务是否启动
curl http://localhost:8000/health

# 查看日志
# 确保没有端口冲突
```

### 问题 2：API 返回 500 错误

**检查**：
1. 环境变量是否设置
2. Groq API key 是否有效
3. 查看服务器日志

```bash
# 测试 Groq API
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{"description": "test"}'
```

### 问题 3：MCP 调用失败

**解决**：
- 检查 `GITHUB_TOKEN` 是否配置
- 系统会自动 fallback 到 mock 数据
- 不影响演示效果

---

## 🎬 Hackathon 演示建议

### 演示流程（2 分钟）

1. **打开 Swagger UI** (10 秒)
   - 展示专业的 API 文档

2. **调用 /compose API** (30 秒)
   - 输入需求
   - 点击 Execute
   - 展示完整响应

3. **高亮关键点** (60 秒)
   - Groq 真实分析结果
   - 匹配的 MCP 列表
   - 生成的代码
   - **真实的 GitHub issues 数据**

4. **说明价值** (20 秒)
   - 一个 API 调用 = 完整的工作流
   - 可集成到任何应用
   - 支持 CI/CD 自动化

---

## 🚀 相比 CLI 的优势

| 维度 | CLI 版本 | API 版本 |
|------|---------|---------|
| 集成性 | 手动运行 | 可编程调用 |
| 演示效果 | 终端输出 | Swagger UI |
| 可扩展性 | 单机 | 可部署到云端 |
| 并发支持 | 无 | 支持多用户 |
| 文档 | Markdown | 自动生成 |
| 专业度 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 📚 相关文档

- `README.md` - 项目概述
- `QUICKSTART.md` - CLI 快速开始
- `API_GUIDE.md` - 本文档
- `E2B_DEPLOYMENT_GUIDE.md` - 云端部署

---

**现在你有一个完整的 RESTful API 服务，通过 Swagger UI 演示更专业！** 🎉

