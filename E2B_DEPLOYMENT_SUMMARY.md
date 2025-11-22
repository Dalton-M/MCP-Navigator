# 📦 E2B 部署总结

## 🎯 你要做的事

**目标：** 将 API Server 部署到 E2B，让前端通过 HTTP POST 调用

**架构：**
```
前端 → E2B URL (https://xxx-8000.e2b.dev) → API Server → Groq/GitHub
```

---

## ⚡ 3步快速部署

### 1️⃣ 在 E2B 创建 Sandbox

```bash
# 访问 E2B
https://e2b.dev/dashboard

# 创建 Python Sandbox
- 选择 Python 3.11+
- 暴露端口: 8000
- 设置环境变量: GROQ_API_KEY, GITHUB_TOKEN
```

### 2️⃣ 在 E2B Terminal 执行

```bash
# 克隆项目
git clone https://github.com/YOUR_USERNAME/MCP-Navigator.git
cd MCP-Navigator

# 安装并启动（一键）
pip install -r requirements.txt
chmod +x start_api_e2b.sh
./start_api_e2b.sh
```

### 3️⃣ 获取 URL 并测试

```bash
# 在 E2B Dashboard 找到你的 URL
https://YOUR_SANDBOX_ID-8000.e2b.dev

# 测试
curl https://YOUR_SANDBOX_ID-8000.e2b.dev/health
```

---

## 🌐 前端调用方式

### JavaScript
```javascript
const API_URL = "https://YOUR_SANDBOX_ID-8000.e2b.dev";

fetch(`${API_URL}/api/v1/compose`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    description: "I want an agent that reads GitHub issues",
    top_k: 3
  })
})
.then(res => res.json())
.then(data => console.log(data));
```

### 使用提供的 Demo
```bash
# 打开 frontend_example.html
# 修改 API URL
# 开始测试
```

---

## 🔑 必需的环境变量

在 E2B Dashboard → Settings → Environment Variables 设置：

```bash
# 必需
GROQ_API_KEY=gsk_...

# 可选（用于真实 demo）
GITHUB_TOKEN=ghp_...
BRAVE_API_KEY=BSA_...
```

---

## 📁 新增的文件

为了方便你部署，我创建了这些文件：

| 文件 | 用途 |
|------|------|
| **E2B_API_DEPLOYMENT.md** | 详细部署指南（完整版） |
| **DEPLOY_TO_E2B_QUICKSTART.md** | 快速部署指南（精简版） |
| **start_api_e2b.sh** | 一键启动 API Server |
| **stop_api_e2b.sh** | 停止 API Server |
| **test_api.sh** | 测试 API 是否正常 |
| **frontend_example.html** | 前端调用示例（可直接使用） |
| **E2B_DEPLOYMENT_SUMMARY.md** | 本文件 |

---

## 🛠️ 常用命令

```bash
# 启动服务
./start_api_e2b.sh

# 停止服务
./stop_api_e2b.sh

# 查看日志
tail -f api_server.log

# 测试 API
./test_api.sh https://YOUR_URL

# 重启服务
./stop_api_e2b.sh && ./start_api_e2b.sh
```

---

## 📊 API 端点

你的 API 暴露这些端点：

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/docs` | GET | Swagger UI（可视化 API 文档） |
| `/api/v1/compose` | POST | 完整编排（主要端点） |
| `/api/v1/analyze` | POST | 仅分析需求 |
| `/api/v1/recommend` | POST | 仅推荐 MCP |
| `/api/v1/call` | POST | 调用 MCP |
| `/api/v1/mcps` | GET | 列出所有 MCP |

---

## ✅ 验证部署成功

运行这些检查：

```bash
# 1. 健康检查
curl https://YOUR_URL/health
# ✅ 返回: {"status":"healthy",...}

# 2. 查看文档
# 浏览器访问: https://YOUR_URL/docs
# ✅ 看到 Swagger UI

# 3. 测试 Compose API
curl -X POST https://YOUR_URL/api/v1/compose \
  -H "Content-Type: application/json" \
  -d '{"description":"test","top_k":3}'
# ✅ 返回 JSON 响应

# 4. 前端调用
# 打开 frontend_example.html
# 输入 URL，点击按钮
# ✅ 看到推荐结果
```

---

## 🐛 问题排查

### 问题1: 无法访问 URL
```bash
# 检查服务是否运行
ps aux | grep api_server

# 查看日志
cat api_server.log

# 重启服务
./start_api_e2b.sh
```

### 问题2: CORS 错误
- ✅ 已配置 `allow_origins=["*"]`
- 检查浏览器控制台的具体错误

### 问题3: 环境变量未生效
```bash
# 验证
echo $GROQ_API_KEY

# 如果为空，在 E2B Dashboard 重新设置
```

---

## 🎬 完整工作流

```
1. 用户在前端输入需求
   ↓
2. 前端发送 POST 请求到 E2B URL
   ↓
3. API Server (在 E2B) 处理请求
   ↓
4. 调用 Groq API 分析需求
   ↓
5. 匹配 MCP 服务器
   ↓
6. 生成配置代码
   ↓
7. 可选：演示 MCP 调用
   ↓
8. 返回完整结果给前端
   ↓
9. 前端展示推荐的 MCP 和代码
```

---

## 📚 文档索引

- **新手：** 先看 [DEPLOY_TO_E2B_QUICKSTART.md](./DEPLOY_TO_E2B_QUICKSTART.md)
- **详细：** 再看 [E2B_API_DEPLOYMENT.md](./E2B_API_DEPLOYMENT.md)
- **API 文档：** 查看 [README_API.md](./README_API.md)
- **项目总览：** 查看 [README.md](./README.md)

---

## 💡 关键点

1. **必须在 E2B 上运行** - 这是 Hackathon 要求
2. **端口必须是 8000** - 已在 api_server.py 配置
3. **必须暴露端口** - 在创建 Sandbox 时勾选
4. **CORS 已配置** - 允许所有域名调用
5. **Mock 模式** - 没有 API key 也能运行（用于演示）

---

## 🚀 现在开始！

```bash
# 1. 前往 E2B
https://e2b.dev/

# 2. 创建 Sandbox (Python 3.11+, Port 8000)

# 3. 在 Terminal 执行
git clone YOUR_REPO
cd MCP-Navigator
pip install -r requirements.txt
./start_api_e2b.sh

# 4. 复制 URL，更新前端

# 5. 开始使用！
```

---

**部署完成后，你的前端就可以调用 POST /api/v1/compose 端点了！** 🎉

有问题查看详细文档或日志文件。

